"""
Claude Artifact Manager - Implementação completa para compatibilidade com ADK
"""

import logging
import json
import base64
import hashlib
from typing import Any, List, Optional, Dict, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class ArtifactType(Enum):
    """Tipos de artifacts suportados."""
    TEXT = "text"
    CODE = "code"
    JSON = "json"
    BINARY = "binary"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


@dataclass
class Artifact:
    """Artifact completo com metadados."""
    id: str
    name: str
    type: str
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    checksum: str = ""
    size: int = 0
    compressed: bool = False


@dataclass
class ArtifactChunk:
    """Chunk de um artifact para transmissão eficiente."""
    artifact_id: str
    chunk_id: str
    index: int
    total: int
    data: str
    checksum: str
    size: int


class ClaudeArtifactManager:
    """Gerenciador completo de artifacts com chunking, compressão e cache."""
    
    def __init__(self, chunk_size: int = 10000, cache_size: int = 100):
        self._artifacts: Dict[str, Artifact] = {}
        self._chunks: Dict[str, List[ArtifactChunk]] = {}
        self._cache: Dict[str, Any] = {}
        self._chunk_size = chunk_size
        self._cache_size = cache_size
        self._stats = {
            "stored": 0,
            "retrieved": 0,
            "chunked": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        logger.info("✅ ClaudeArtifactManager inicializado (versão completa)")
    
    def create_artifact(
        self,
        name: str,
        content: Any,
        artifact_type: Union[str, ArtifactType] = ArtifactType.TEXT,
        metadata: Dict[str, Any] = None
    ) -> Artifact:
        """Cria um novo artifact com metadados completos."""
        artifact_id = str(uuid.uuid4())
        
        # Determinar tipo
        if isinstance(artifact_type, ArtifactType):
            type_str = artifact_type.value
        else:
            type_str = artifact_type
        
        # Calcular tamanho
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        elif isinstance(content, bytes):
            content_bytes = content
        else:
            content_bytes = str(content).encode('utf-8')
        
        size = len(content_bytes)
        checksum = hashlib.sha256(content_bytes).hexdigest()
        
        # Criar artifact
        artifact = Artifact(
            id=artifact_id,
            name=name,
            type=type_str,
            content=content,
            metadata=metadata or {},
            checksum=checksum,
            size=size
        )
        
        # Armazenar
        self.store_artifact(artifact_id, artifact)
        
        return artifact
    
    def chunk_artifact(self, artifact: Union[Artifact, Any], chunk_size: int = None) -> List[ArtifactChunk]:
        """
        Divide um artifact em chunks para transmissão eficiente.
        """
        chunk_size = chunk_size or self._chunk_size
        
        # Obter conteúdo
        if isinstance(artifact, Artifact):
            artifact_id = artifact.id
            content = artifact.content
        else:
            artifact_id = str(uuid.uuid4())
            content = artifact
        
        # Converter para string se necessário
        if isinstance(content, bytes):
            content_str = base64.b64encode(content).decode('utf-8')
        elif not isinstance(content, str):
            content_str = json.dumps(content)
        else:
            content_str = content
        
        # Dividir em chunks
        chunks = []
        total_chunks = (len(content_str) + chunk_size - 1) // chunk_size
        
        for i in range(total_chunks):
            start = i * chunk_size
            end = min((i + 1) * chunk_size, len(content_str))
            chunk_data = content_str[start:end]
            
            chunk = ArtifactChunk(
                artifact_id=artifact_id,
                chunk_id=f"{artifact_id}-{i}",
                index=i,
                total=total_chunks,
                data=chunk_data,
                checksum=hashlib.md5(chunk_data.encode()).hexdigest(),
                size=len(chunk_data)
            )
            chunks.append(chunk)
        
        # Armazenar chunks
        self._chunks[artifact_id] = chunks
        self._stats["chunked"] += 1
        
        logger.info(f"📦 Artifact {artifact_id} dividido em {len(chunks)} chunks")
        return chunks
    
    def reassemble_chunks(self, artifact_id: str) -> Optional[str]:
        """Reconstrói um artifact a partir de seus chunks."""
        if artifact_id not in self._chunks:
            return None
        
        chunks = self._chunks[artifact_id]
        # Ordenar por índice
        chunks.sort(key=lambda c: c.index)
        
        # Reunir dados
        data_parts = [chunk.data for chunk in chunks]
        reassembled = "".join(data_parts)
        
        logger.info(f"🔄 Artifact {artifact_id} reconstituído de {len(chunks)} chunks")
        return reassembled
    
    def store_artifact(self, artifact_id: str, artifact: Any):
        """Armazena um artifact com cache."""
        # Armazenar
        if isinstance(artifact, Artifact):
            self._artifacts[artifact_id] = artifact
        else:
            # Criar artifact básico
            self._artifacts[artifact_id] = Artifact(
                id=artifact_id,
                name=f"artifact_{artifact_id}",
                type="unknown",
                content=artifact
            )
        
        # Adicionar ao cache
        self._add_to_cache(artifact_id, artifact)
        
        self._stats["stored"] += 1
        logger.debug(f"💾 Artifact {artifact_id} armazenado")
    
    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        """Obtém um artifact com cache."""
        # Verificar cache primeiro
        if artifact_id in self._cache:
            self._stats["cache_hits"] += 1
            logger.debug(f"🎯 Cache hit para artifact {artifact_id}")
            return self._cache[artifact_id]
        
        # Buscar no armazenamento
        self._stats["cache_misses"] += 1
        artifact = self._artifacts.get(artifact_id)
        
        if artifact:
            self._add_to_cache(artifact_id, artifact)
            self._stats["retrieved"] += 1
        
        return artifact
    
    def update_artifact(self, artifact_id: str, content: Any = None, metadata: Dict[str, Any] = None):
        """Atualiza um artifact existente."""
        if artifact_id not in self._artifacts:
            logger.warning(f"⚠️ Artifact {artifact_id} não encontrado para atualização")
            return
        
        artifact = self._artifacts[artifact_id]
        
        if content is not None:
            artifact.content = content
            # Recalcular checksum e tamanho
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, bytes):
                content_bytes = content
            else:
                content_bytes = str(content).encode('utf-8')
            
            artifact.size = len(content_bytes)
            artifact.checksum = hashlib.sha256(content_bytes).hexdigest()
        
        if metadata is not None:
            artifact.metadata.update(metadata)
        
        artifact.updated_at = datetime.now()
        
        # Invalidar cache
        if artifact_id in self._cache:
            del self._cache[artifact_id]
        
        logger.info(f"📝 Artifact {artifact_id} atualizado")
    
    def delete_artifact(self, artifact_id: str):
        """Remove um artifact."""
        if artifact_id in self._artifacts:
            del self._artifacts[artifact_id]
        
        if artifact_id in self._chunks:
            del self._chunks[artifact_id]
        
        if artifact_id in self._cache:
            del self._cache[artifact_id]
        
        logger.info(f"🗑️ Artifact {artifact_id} removido")
    
    def list_artifacts(self) -> List[Dict[str, Any]]:
        """Lista todos os artifacts com seus metadados."""
        return [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "size": a.size,
                "created_at": a.created_at.isoformat(),
                "updated_at": a.updated_at.isoformat(),
                "has_chunks": a.id in self._chunks
            }
            for a in self._artifacts.values()
        ]
    
    def _add_to_cache(self, artifact_id: str, artifact: Any):
        """Adiciona artifact ao cache com limite de tamanho."""
        # Limpar cache se necessário
        if len(self._cache) >= self._cache_size:
            # Remover item mais antigo (FIFO)
            oldest_id = next(iter(self._cache))
            del self._cache[oldest_id]
        
        self._cache[artifact_id] = artifact
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do gerenciador."""
        return {
            **self._stats,
            "total_artifacts": len(self._artifacts),
            "total_chunks": sum(len(chunks) for chunks in self._chunks.values()),
            "cache_size": len(self._cache)
        }
    
    def clear_cache(self):
        """Limpa o cache."""
        self._cache.clear()
        logger.info("🧹 Cache de artifacts limpo")
    
    def close(self):
        """Fecha o manager e limpa recursos."""
        self._artifacts.clear()
        self._chunks.clear()
        self._cache.clear()
        logger.info("🔒 ClaudeArtifactManager fechado")


# Singleton global
_artifact_manager = None

def get_artifact_manager() -> ClaudeArtifactManager:
    """Obtém a instância singleton do artifact manager."""
    global _artifact_manager
    if _artifact_manager is None:
        _artifact_manager = ClaudeArtifactManager()
    return _artifact_manager