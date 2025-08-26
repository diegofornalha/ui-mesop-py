"""
Serviços In-Memory para Claude - Compatíveis com ADK Services.
Implementa SessionService, MemoryService, ArtifactService e sistema de Eventos.
"""

import json
import uuid
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# SISTEMA DE EVENTOS (Compatível com ADKEvent)
# ============================================================================

@dataclass
class ClaudeEvent:
    """
    Evento compatível com ADKEvent.
    Implementa o método new_id() e estrutura similar ao Google ADK.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    session_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Campos adicionais para compatibilidade com ADKEvent
    author: str = "claude_agent"
    invocation_id: Optional[str] = field(default_factory=lambda: str(uuid.uuid4()))
    actions: Optional['ClaudeEventActions'] = None
    
    @staticmethod
    def new_id() -> str:
        """Gera novo ID único (compatível com ADKEvent.new_id())."""
        return str(uuid.uuid4())
    
    @classmethod
    def create(cls, type: str, session_id: Optional[str] = None, 
               content: Any = None, author: str = "claude_agent",
               state_delta: Optional[Dict] = None, **kwargs) -> "ClaudeEvent":
        """Factory method para criar eventos com state_delta opcional."""
        actions = None
        if state_delta:
            actions = ClaudeEventActions(state_delta=state_delta)
        
        return cls(
            id=cls.new_id(),
            type=type,
            session_id=session_id,
            content=content,
            metadata=kwargs,
            author=author,
            invocation_id=cls.new_id(),
            actions=actions
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário."""
        result = {
            "id": self.id,
            "type": self.type,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "content": self.content,
            "metadata": self.metadata,
            "author": self.author,
            "invocation_id": self.invocation_id
        }
        if self.actions:
            result["actions"] = {
                "state_delta": self.actions.state_delta,
                "events": [e.to_dict() for e in self.actions.events]
            }
        return result


@dataclass
class ClaudeEventActions:
    """
    Event Actions compatível com ADKEventActions.
    Gerencia mudanças de estado através de eventos.
    """
    state_delta: Dict[str, Any] = field(default_factory=dict)
    events: List[ClaudeEvent] = field(default_factory=list)
    
    def add_event(self, event: ClaudeEvent):
        """Adiciona um evento à lista."""
        self.events.append(event)
    
    def update_state(self, key: str, value: Any):
        """Atualiza o state_delta."""
        self.state_delta[key] = value
    
    def get_state_changes(self) -> Dict[str, Any]:
        """Retorna as mudanças de estado."""
        return self.state_delta.copy()
    
    def clear(self):
        """Limpa eventos e mudanças de estado."""
        self.events.clear()
        self.state_delta.clear()


# ============================================================================
# SESSION SERVICE (Compatível com InMemorySessionService)
# ============================================================================

class ClaudeSessionService:
    """
    Serviço de sessão in-memory compatível com ADK InMemorySessionService.
    Implementa: get_session(), create_session(), list_sessions(), append_event()
    """
    
    def __init__(self):
        """Inicializa o serviço de sessão."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._events: Dict[str, List[ClaudeEvent]] = {}
        self._lock = asyncio.Lock()
        logger.info("ClaudeSessionService inicializado")
    
    async def initialize(self):
        """Inicialização assíncrona (se necessário)."""
        logger.info("SessionService pronto")
        return self
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém uma sessão pelo ID (compatível com ADK).
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dados da sessão ou None se não existe
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                # Incluir eventos da sessão
                session["events"] = self._events.get(session_id, [])
            return session
    
    async def create_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria uma nova sessão (compatível com ADK).
        
        Args:
            session_id: ID opcional da sessão (gera se None)
            
        Returns:
            Dados da nova sessão
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        async with self._lock:
            session = {
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "history": [],
                "metadata": {},
                "state": "active"
            }
            
            self._sessions[session_id] = session
            self._events[session_id] = []
            
            logger.info(f"Sessão criada: {session_id}")
            return session
    
    async def list_sessions(self) -> List[str]:
        """
        Lista IDs de todas as sessões (compatível com ADK).
        
        Returns:
            Lista de IDs de sessão
        """
        async with self._lock:
            return list(self._sessions.keys())
    
    async def append_event(self, session_id: str, event: Union[ClaudeEvent, Dict]) -> bool:
        """
        Adiciona evento a uma sessão (compatível com ADK append_event).
        
        Args:
            session_id: ID da sessão
            event: Evento a adicionar
            
        Returns:
            True se sucesso, False se sessão não existe
        """
        async with self._lock:
            if session_id not in self._sessions:
                logger.warning(f"Sessão não encontrada: {session_id}")
                return False
            
            # Converter dict para ClaudeEvent se necessário
            if isinstance(event, dict):
                event = ClaudeEvent(**event)
            
            # Adicionar aos eventos
            if session_id not in self._events:
                self._events[session_id] = []
            self._events[session_id].append(event)
            
            # Atualizar timestamp da sessão
            self._sessions[session_id]["updated_at"] = datetime.now().isoformat()
            
            # Adicionar ao histórico se for mensagem
            if event.type in ["user_input", "agent_response"]:
                self._sessions[session_id]["history"].append({
                    "role": "user" if event.type == "user_input" else "assistant",
                    "content": event.content,
                    "timestamp": event.timestamp
                })
            
            return True
    
    def close(self):
        """Fecha o serviço e limpa recursos."""
        self._sessions.clear()
        self._events.clear()
        logger.info("SessionService fechado")


# ============================================================================
# MEMORY SERVICE (Compatível com InMemoryMemoryService)
# ============================================================================

class ClaudeMemoryService:
    """
    Serviço de memória in-memory compatível com ADK InMemoryMemoryService.
    Implementa: store(), retrieve(), delete(), list_keys()
    """
    
    def __init__(self):
        """Inicializa o serviço de memória."""
        self._memory: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        logger.info("ClaudeMemoryService inicializado")
    
    async def initialize(self):
        """Inicialização assíncrona."""
        logger.info("MemoryService pronto")
        return self
    
    async def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """
        Armazena valor na memória.
        
        Args:
            key: Chave para armazenar
            value: Valor a armazenar
            metadata: Metadados opcionais
            
        Returns:
            True se sucesso
        """
        async with self._lock:
            self._memory[key] = value
            self._metadata[key] = {
                "stored_at": datetime.now().isoformat(),
                "type": type(value).__name__,
                **(metadata or {})
            }
            logger.debug(f"Valor armazenado: {key}")
            return True
    
    async def retrieve(self, key: str) -> Optional[Any]:
        """
        Recupera valor da memória.
        
        Args:
            key: Chave para recuperar
            
        Returns:
            Valor armazenado ou None
        """
        async with self._lock:
            value = self._memory.get(key)
            if value is not None:
                # Atualizar último acesso
                if key in self._metadata:
                    self._metadata[key]["last_accessed"] = datetime.now().isoformat()
            return value
    
    async def delete(self, key: str) -> bool:
        """
        Remove valor da memória.
        
        Args:
            key: Chave para remover
            
        Returns:
            True se removido, False se não existia
        """
        async with self._lock:
            if key in self._memory:
                del self._memory[key]
                if key in self._metadata:
                    del self._metadata[key]
                logger.debug(f"Valor removido: {key}")
                return True
            return False
    
    async def list_keys(self) -> List[str]:
        """
        Lista todas as chaves armazenadas.
        
        Returns:
            Lista de chaves
        """
        async with self._lock:
            return list(self._memory.keys())
    
    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Obtém metadados de uma chave.
        
        Args:
            key: Chave para obter metadados
            
        Returns:
            Metadados ou None
        """
        async with self._lock:
            return self._metadata.get(key)
    
    def close(self):
        """Fecha o serviço e limpa recursos."""
        self._memory.clear()
        self._metadata.clear()
        logger.info("MemoryService fechado")


# ============================================================================
# ARTIFACT SERVICE (Compatível com InMemoryArtifactService)
# ============================================================================

@dataclass
class ClaudeArtifact:
    """Representa um artefato armazenado."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""
    name: str = ""
    content: Any = None
    mime_type: str = "application/octet-stream"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return asdict(self)


class ClaudeArtifactService:
    """
    Serviço de artefatos in-memory compatível com ADK InMemoryArtifactService.
    Implementa: save_artifact(), get_artifact(), list_artifacts(), delete_artifact()
    """
    
    def __init__(self):
        """Inicializa o serviço de artefatos."""
        self._artifacts: Dict[str, ClaudeArtifact] = {}
        self._lock = asyncio.Lock()
        logger.info("ClaudeArtifactService inicializado")
    
    async def initialize(self):
        """Inicialização assíncrona."""
        logger.info("ArtifactService pronto")
        return self
    
    async def save_artifact(self, artifact: Union[ClaudeArtifact, Dict]) -> str:
        """
        Salva um artefato.
        
        Args:
            artifact: Artefato a salvar
            
        Returns:
            ID do artefato salvo
        """
        async with self._lock:
            # Converter dict para ClaudeArtifact se necessário
            if isinstance(artifact, dict):
                artifact = ClaudeArtifact(**artifact)
            
            # Garantir que tem ID
            if not artifact.id:
                artifact.id = str(uuid.uuid4())
            
            self._artifacts[artifact.id] = artifact
            logger.info(f"Artefato salvo: {artifact.id} ({artifact.type})")
            return artifact.id
    
    async def get_artifact(self, artifact_id: str) -> Optional[ClaudeArtifact]:
        """
        Obtém um artefato pelo ID.
        
        Args:
            artifact_id: ID do artefato
            
        Returns:
            Artefato ou None
        """
        async with self._lock:
            return self._artifacts.get(artifact_id)
    
    async def list_artifacts(self, type_filter: Optional[str] = None) -> List[ClaudeArtifact]:
        """
        Lista artefatos, opcionalmente filtrados por tipo.
        
        Args:
            type_filter: Tipo para filtrar (opcional)
            
        Returns:
            Lista de artefatos
        """
        async with self._lock:
            artifacts = list(self._artifacts.values())
            if type_filter:
                artifacts = [a for a in artifacts if a.type == type_filter]
            return artifacts
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """
        Remove um artefato.
        
        Args:
            artifact_id: ID do artefato
            
        Returns:
            True se removido, False se não existia
        """
        async with self._lock:
            if artifact_id in self._artifacts:
                del self._artifacts[artifact_id]
                logger.info(f"Artefato removido: {artifact_id}")
                return True
            return False
    
    async def update_artifact(self, artifact_id: str, updates: Dict[str, Any]) -> bool:
        """
        Atualiza um artefato existente.
        
        Args:
            artifact_id: ID do artefato
            updates: Campos a atualizar
            
        Returns:
            True se atualizado, False se não existe
        """
        async with self._lock:
            if artifact_id in self._artifacts:
                artifact = self._artifacts[artifact_id]
                for key, value in updates.items():
                    if hasattr(artifact, key):
                        setattr(artifact, key, value)
                logger.info(f"Artefato atualizado: {artifact_id}")
                return True
            return False
    
    def close(self):
        """Fecha o serviço e limpa recursos."""
        self._artifacts.clear()
        logger.info("ArtifactService fechado")


# ============================================================================
# TESTE DOS SERVIÇOS
# ============================================================================

async def test_services():
    """Testa todos os serviços."""
    print("🧪 Testando Serviços Claude...")
    
    # Testar SessionService
    print("\n📁 Testando SessionService...")
    session_service = ClaudeSessionService()
    await session_service.initialize()
    
    session = await session_service.create_session()
    session_id = session["id"]
    print(f"  ✅ Sessão criada: {session_id}")
    
    event = ClaudeEvent.create("test_event", session_id, "Teste")
    await session_service.append_event(session_id, event)
    print(f"  ✅ Evento adicionado")
    
    retrieved = await session_service.get_session(session_id)
    print(f"  ✅ Sessão recuperada com {len(retrieved['events'])} eventos")
    
    # Testar MemoryService
    print("\n🧠 Testando MemoryService...")
    memory_service = ClaudeMemoryService()
    await memory_service.initialize()
    
    await memory_service.store("test_key", {"data": "test_value"})
    print("  ✅ Valor armazenado")
    
    value = await memory_service.retrieve("test_key")
    print(f"  ✅ Valor recuperado: {value}")
    
    # Testar ArtifactService
    print("\n📦 Testando ArtifactService...")
    artifact_service = ClaudeArtifactService()
    await artifact_service.initialize()
    
    artifact = ClaudeArtifact(type="text", name="test.txt", content="Hello World")
    artifact_id = await artifact_service.save_artifact(artifact)
    print(f"  ✅ Artefato salvo: {artifact_id}")
    
    retrieved_artifact = await artifact_service.get_artifact(artifact_id)
    print(f"  ✅ Artefato recuperado: {retrieved_artifact.name}")
    
    print("\n✅ Todos os testes passaram!")


if __name__ == "__main__":
    asyncio.run(test_services())