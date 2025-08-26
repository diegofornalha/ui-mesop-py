"""
Claude Artifact Manager - Implementação mínima para compatibilidade
"""

import logging
from typing import Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ArtifactChunk:
    """Chunk de um artifact."""
    index: int
    total: int
    data: str


class ClaudeArtifactManager:
    """Gerenciador mínimo de artifacts."""
    
    def __init__(self):
        self._artifacts = {}
        logger.info("✅ ClaudeArtifactManager inicializado (versão mínima)")
    
    def chunk_artifact(self, artifact: Any, chunk_size: int = 10000) -> List[ArtifactChunk]:
        """Divide um artifact em chunks (implementação mínima)."""
        # Por agora, retorna lista vazia (sem chunking)
        return []
    
    def store_artifact(self, artifact_id: str, artifact: Any):
        """Armazena um artifact."""
        self._artifacts[artifact_id] = artifact
    
    def get_artifact(self, artifact_id: str) -> Optional[Any]:
        """Obtém um artifact."""
        return self._artifacts.get(artifact_id)
    
    def close(self):
        """Fecha o manager."""
        self._artifacts.clear()


# Singleton global
_artifact_manager = None

def get_artifact_manager() -> ClaudeArtifactManager:
    """Obtém a instância singleton do artifact manager."""
    global _artifact_manager
    if _artifact_manager is None:
        _artifact_manager = ClaudeArtifactManager()
    return _artifact_manager