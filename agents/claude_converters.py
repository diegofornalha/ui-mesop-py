"""
Conversores de mensagens entre formatos A2A e Claude.
Garante compatibilidade total entre os protocolos.
"""

import json
import uuid
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

# Importar tipos A2A
from a2a.types import (
    Message,
    Part,
    TextPart,
    FilePart,
    DataPart,
    Role,
    FileWithUri,
    FileWithBytes
)

logger = logging.getLogger(__name__)


# ============================================================================
# CONVERTERS: A2A ↔ CLAUDE
# ============================================================================

def claude_content_from_message(message: Message) -> Dict[str, Any]:
    """
    Converte uma mensagem A2A para formato Claude.
    
    Args:
        message: Mensagem no formato A2A Protocol
        
    Returns:
        Dict no formato esperado pelo Claude
    """
    try:
        # Extrair conteúdo das parts
        content_parts = []
        
        if message.parts:
            for part in message.parts:
                if isinstance(part, TextPart):
                    content_parts.append({
                        "type": "text",
                        "text": part.text
                    })
                elif isinstance(part, FilePart):
                    # Converter arquivo para texto descritivo
                    file_info = f"[Arquivo: {part.file.name if hasattr(part.file, 'name') else 'arquivo'}]"
                    if hasattr(part.file, 'mime_type'):
                        file_info += f" ({part.file.mime_type})"
                    content_parts.append({
                        "type": "text",
                        "text": file_info
                    })
                elif isinstance(part, DataPart):
                    # Converter dados para JSON string
                    try:
                        data_str = json.dumps(part.data, indent=2)
                        content_parts.append({
                            "type": "text",
                            "text": f"```json\n{data_str}\n```"
                        })
                    except:
                        content_parts.append({
                            "type": "text",
                            "text": str(part.data)
                        })
                else:
                    # Tipo desconhecido, converter para string
                    content_parts.append({
                        "type": "text",
                        "text": str(part)
                    })
        
        # Determinar role
        role = "user"
        if hasattr(message, 'role'):
            if message.role == Role.agent or str(message.role).lower() in ['agent', 'assistant']:
                role = "assistant"
            elif message.role == Role.system or str(message.role).lower() == 'system':
                role = "system"
        
        # Construir mensagem Claude
        claude_message = {
            "role": role,
            "content": content_parts if content_parts else [{"type": "text", "text": ""}],
            "metadata": {
                "message_id": message.messageId if hasattr(message, 'messageId') else str(uuid.uuid4()),
                "context_id": message.contextId if hasattr(message, 'contextId') else None,
                "task_id": getattr(message, 'taskId', None),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return claude_message
        
    except Exception as e:
        logger.error(f"Erro ao converter mensagem A2A para Claude: {e}")
        return {
            "role": "user",
            "content": [{"type": "text", "text": str(message)}],
            "metadata": {"error": str(e)}
        }


def claude_content_to_message(content: Union[str, Dict, List]) -> Message:
    """
    Converte conteúdo Claude para mensagem A2A.
    
    Args:
        content: Conteúdo no formato Claude (string, dict ou lista)
        
    Returns:
        Message no formato A2A Protocol
    """
    try:
        parts = []
        
        # Se for string simples
        if isinstance(content, str):
            parts.append(TextPart(text=content))
        
        # Se for lista de content blocks
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        parts.append(TextPart(text=item.get("text", "")))
                    elif item.get("type") == "file":
                        # Criar FilePart
                        file_data = item.get("file", {})
                        file_part = FilePart(
                            file=FileWithUri(
                                uri=file_data.get("uri", ""),
                                name=file_data.get("name", "file"),
                                mime_type=file_data.get("mime_type", "application/octet-stream")
                            )
                        )
                        parts.append(file_part)
                    elif item.get("type") == "data":
                        # Criar DataPart
                        parts.append(DataPart(data=item.get("data", {})))
                    else:
                        # Tipo desconhecido, adicionar como texto
                        parts.append(TextPart(text=str(item)))
                else:
                    parts.append(TextPart(text=str(item)))
        
        # Se for dict com estrutura Claude
        elif isinstance(content, dict):
            role_str = content.get("role", "user")
            role = Role.user
            if role_str in ["assistant", "agent"]:
                role = Role.agent
            elif role_str == "system":
                role = Role.system
            
            # Processar conteúdo
            content_data = content.get("content", [])
            if isinstance(content_data, str):
                parts.append(TextPart(text=content_data))
            elif isinstance(content_data, list):
                for item in content_data:
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(TextPart(text=item.get("text", "")))
                    else:
                        parts.append(TextPart(text=str(item)))
            
            # Extrair metadados
            metadata = content.get("metadata", {})
            message_id = metadata.get("message_id", str(uuid.uuid4()))
            context_id = metadata.get("context_id", "")
            
            # Criar mensagem com metadados
            message = Message(
                messageId=message_id,
                contextId=context_id,
                role=role,
                parts=parts
            )
            
            # Adicionar task_id se existir
            if "task_id" in metadata:
                message.taskId = metadata["task_id"]
            
            return message
        
        # Se não tiver parts, criar uma vazia
        if not parts:
            parts = [TextPart(text="")]
        
        # Criar mensagem A2A
        message = Message(
            messageId=str(uuid.uuid4()),
            contextId="",
            role=Role.agent,  # Assumir agent para respostas Claude
            parts=parts
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Erro ao converter conteúdo Claude para A2A: {e}")
        # Retornar mensagem de erro
        return Message(
            messageId=str(uuid.uuid4()),
            contextId="",
            role=Role.agent,
            parts=[TextPart(text=f"Erro na conversão: {str(e)}")]
        )


# ============================================================================
# BATCH CONVERTERS
# ============================================================================

def batch_convert_to_claude(messages: List[Message]) -> List[Dict[str, Any]]:
    """
    Converte lista de mensagens A2A para formato Claude.
    
    Args:
        messages: Lista de mensagens A2A
        
    Returns:
        Lista de mensagens no formato Claude
    """
    claude_messages = []
    
    for message in messages:
        try:
            claude_msg = claude_content_from_message(message)
            claude_messages.append(claude_msg)
        except Exception as e:
            logger.error(f"Erro ao converter mensagem {message.messageId}: {e}")
            # Adicionar mensagem de fallback
            claude_messages.append({
                "role": "user",
                "content": [{"type": "text", "text": str(message)}]
            })
    
    return claude_messages


def batch_convert_from_claude(claude_messages: List[Dict]) -> List[Message]:
    """
    Converte lista de mensagens Claude para formato A2A.
    
    Args:
        claude_messages: Lista de mensagens Claude
        
    Returns:
        Lista de mensagens A2A
    """
    a2a_messages = []
    
    for claude_msg in claude_messages:
        try:
            a2a_msg = claude_content_to_message(claude_msg)
            a2a_messages.append(a2a_msg)
        except Exception as e:
            logger.error(f"Erro ao converter mensagem Claude: {e}")
            # Adicionar mensagem de fallback
            a2a_messages.append(Message(
                messageId=str(uuid.uuid4()),
                contextId="",
                role=Role.agent,
                parts=[TextPart(text=str(claude_msg))]
            ))
    
    return a2a_messages


# ============================================================================
# CONTEXT BUILDERS
# ============================================================================

def build_claude_context(messages: List[Message], max_messages: int = 10) -> str:
    """
    Constrói contexto de conversa para Claude a partir de mensagens A2A.
    
    Args:
        messages: Lista de mensagens A2A
        max_messages: Número máximo de mensagens a incluir
        
    Returns:
        String de contexto formatada
    """
    # Pegar últimas N mensagens
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
    
    context_parts = []
    for msg in recent_messages:
        # Determinar role
        role = "User"
        if hasattr(msg, 'role'):
            if msg.role == Role.agent or str(msg.role).lower() in ['agent', 'assistant']:
                role = "Assistant"
            elif msg.role == Role.system:
                role = "System"
        
        # Extrair texto
        text_parts = []
        if msg.parts:
            for part in msg.parts:
                if isinstance(part, TextPart):
                    text_parts.append(part.text)
                elif isinstance(part, DataPart):
                    text_parts.append(f"[Data: {json.dumps(part.data, indent=2)}]")
                elif isinstance(part, FilePart):
                    text_parts.append(f"[File: {getattr(part.file, 'name', 'file')}]")
        
        if text_parts:
            context_parts.append(f"{role}: {' '.join(text_parts)}")
    
    return "\n\n".join(context_parts)


def extract_text_from_message(message: Message) -> str:
    """
    Extrai texto puro de uma mensagem A2A.
    
    Args:
        message: Mensagem A2A
        
    Returns:
        Texto extraído
    """
    text_parts = []
    
    if message.parts:
        for part in message.parts:
            if isinstance(part, TextPart):
                text_parts.append(part.text)
            elif isinstance(part, DataPart):
                try:
                    text_parts.append(json.dumps(part.data))
                except:
                    text_parts.append(str(part.data))
            elif isinstance(part, FilePart):
                if hasattr(part.file, 'name'):
                    text_parts.append(f"[Arquivo: {part.file.name}]")
                else:
                    text_parts.append("[Arquivo]")
    
    return " ".join(text_parts) if text_parts else ""


# ============================================================================
# TESTE DOS CONVERSORES
# ============================================================================

def test_converters():
    """Testa os conversores."""
    print("🧪 Testando Conversores Claude...")
    
    # Criar mensagem A2A de teste
    a2a_message = Message(
        messageId="test-123",
        contextId="context-456",
        role=Role.user,
        parts=[
            TextPart(text="Olá Claude!"),
            DataPart(data={"key": "value"})
        ]
    )
    
    print(f"\n📥 Mensagem A2A original:")
    print(f"  ID: {a2a_message.messageId}")
    print(f"  Role: {a2a_message.role}")
    print(f"  Parts: {len(a2a_message.parts)}")
    
    # Converter para Claude
    claude_format = claude_content_from_message(a2a_message)
    print(f"\n🔄 Convertido para Claude:")
    print(f"  Role: {claude_format['role']}")
    print(f"  Content: {claude_format['content']}")
    
    # Converter de volta para A2A
    a2a_back = claude_content_to_message(claude_format)
    print(f"\n🔄 Convertido de volta para A2A:")
    print(f"  ID: {a2a_back.messageId}")
    print(f"  Role: {a2a_back.role}")
    print(f"  Parts: {len(a2a_back.parts)}")
    
    # Testar contexto
    messages = [a2a_message, a2a_back]
    context = build_claude_context(messages)
    print(f"\n📝 Contexto construído:")
    print(context)
    
    print("\n✅ Testes de conversão concluídos!")


if __name__ == "__main__":
    test_converters()