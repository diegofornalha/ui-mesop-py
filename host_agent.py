"""
Módulo HostAgent com integração real ao Google ADK.
"""

from typing import Any, Callable, List, Optional
import httpx
import os
from google.adk import Agent as ADKAgent
from google.adk.agents import LlmAgent
from google.genai import Client
from google.genai.types import GenerateContentConfig, SafetySetting, HarmCategory, HarmBlockThreshold


class HostAgent:
    """Agente host para gerenciar conversas usando Google ADK."""
    
    def __init__(self, agents: List[Any], http_client: httpx.AsyncClient, task_callback: Callable):
        self.agents = agents
        self.http_client = http_client
        self.task_callback = task_callback
        self.client = Client()
    
    def create_agent(self) -> ADKAgent:
        """Cria um agente LLM usando Google ADK."""
        # Configurar modelo
        model_name = os.environ.get('GOOGLE_GENAI_MODEL', 'gemini-1.5-flash')
        
        # Configurações de segurança
        safety_settings = [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
        ]
        
        # Criar agente LLM
        agent = LlmAgent(
            name="AssistantAgent",
            description="Agente assistente inteligente",
            model=model_name,
            instruction="""Você é um assistente útil e prestativo. 
            Responda de forma clara, precisa e educada.
            Se não souber algo, seja honesto sobre isso.""",
            generate_content_config=GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
                safety_settings=safety_settings
            )
        )
        
        return agent


# Manter compatibilidade com imports existentes
from google.adk import Runner  # Re-exportar o Runner real do ADK

# Para compatibilidade com código legado
class BasicAgent:
    """Agente básico para compatibilidade."""
    
    def __init__(self):
        self.name = "BasicAgent"
        self.description = "Agente básico para execução de tarefas"
    
    async def execute(self, task: Any):
        """Executa uma tarefa."""
        return {"status": "completed", "result": "Task executed successfully"}