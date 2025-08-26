"""
Conversor de mensagens entre formatos A2A e API.
"""

import logging
from typing import List, Dict, Any
from a2a.types import Message, Role

logger = logging.getLogger(__name__)


def convert_messages_for_api(messages: List[Message]) -> List[Dict[str, Any]]:
    """
    Converte mensagens A2A (dataclass) para formato dict compatível com API.
    IMPORTANTE: NÃO adicionar campo 'content' pois será processado pelo convert_message_to_state
    que extrai content das parts usando extract_content().
    """
    converted = []
    
    for msg in messages:
        try:
            # Extrair campos básicos
            msg_dict = {
                "messageId": getattr(msg, "messageId", ""),
                "contextId": getattr(msg, "contextId", ""),
                "role": str(getattr(msg, "role", "user")),
                "parts": []
                # NÃO adicionar 'content' aqui! Será processado por extract_content()
            }
            
            # Converter parts
            parts = getattr(msg, "parts", [])
            for part in parts:
                # Detectar TextPart especificamente
                if hasattr(part, '__class__') and part.__class__.__name__ == 'TextPart':
                    text_content = getattr(part, 'text', '')
                    if text_content:
                        msg_dict["parts"].append({"text": text_content, "kind": "text"})
                elif hasattr(part, "text"):
                    msg_dict["parts"].append({"text": part.text, "kind": "text"})
                elif hasattr(part, "file"):
                    msg_dict["parts"].append({"file": {
                        "mime_type": getattr(part.file, "mime_type", ""),
                        "uri": getattr(part.file, "uri", "")
                    }, "kind": "file"})
                elif hasattr(part, "data"):
                    msg_dict["parts"].append({"data": part.data, "kind": "data"})
                elif isinstance(part, dict):
                    msg_dict["parts"].append(part)
            
            # Garantir que role seja string
            if isinstance(msg_dict["role"], Role):
                msg_dict["role"] = msg_dict["role"].value
            
            converted.append(msg_dict)
            
        except Exception as e:
            logger.error(f"Erro ao converter mensagem: {e}")
            logger.debug(f"Mensagem problemática: {msg}")
            
    return converted


def ensure_role_string(role: Any) -> str:
    """Garante que role seja uma string."""
    if isinstance(role, Role):
        return role.value
    elif isinstance(role, str):
        return role
    else:
        return "user"  # Default