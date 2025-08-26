"""
Cliente real do Claude V2 - Baseado na implementação do app-terminal.
NÃO precisa de API key - usa 'claude' CLI local já autenticado!
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional, List
from dataclasses import dataclass, field
import uuid
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClaudeCodeOptions:
    """Options for Claude Code SDK configuration"""
    system_prompt: Optional[str] = None
    max_turns: int = 5
    max_thinking_tokens: Optional[int] = None
    cwd: Optional[str] = None
    permission_mode: str = 'acceptEdits'
    allowed_tools: List[str] = field(default_factory=lambda: [
        "Read", "Write", "Edit", "MultiEdit", 
        "Bash", "Glob", "Grep", "LS", "WebFetch", "TodoWrite"
    ])
    disallowed_tools: List[str] = None
    mcp_servers: Optional[Dict[str, Any]] = None
    resume: Optional[str] = None  # Session ID to resume
    model: Optional[str] = None  # Claude model to use
    verbose: bool = False


class ClaudeClientRealV2:
    """
    Cliente real do Claude V2 usando CLI subprocess.
    Baseado na implementação profissional do app-terminal.
    """
    
    def __init__(self, options: Optional[ClaudeCodeOptions] = None):
        self.options = options or ClaudeCodeOptions()
        self.process = None
        self.session_id = self.options.resume or str(uuid.uuid4())
        self.is_connected = False
        self.sdk_available = True  # Claude CLI está instalado
        
    async def initialize(self):
        """Initialize connection to Claude Code SDK"""
        if self.is_connected:
            return
            
        # Build command
        cmd = ["claude"]
        
        # Add options
        if self.options.system_prompt:
            cmd.extend(["--system-prompt", self.options.system_prompt])
        if self.options.max_turns:
            cmd.extend(["--max-turns", str(self.options.max_turns)])
        if self.options.cwd:
            cmd.extend(["--cwd", self.options.cwd])
        if self.options.permission_mode:
            cmd.extend(["--permission-mode", self.options.permission_mode])
        if self.options.model:
            cmd.extend(["--model", self.options.model])
            
        # Add allowed tools
        for tool in self.options.allowed_tools:
            cmd.extend(["--allowedTools", tool])
            
        # Output format for parsing
        cmd.extend(["--output-format", "stream-json"])
        cmd.extend(["--input-format", "stream-json"])
        
        logger.info(f"🚀 Starting Claude with: {' '.join(cmd[:5])}...")
        
        try:
            # Start process
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.options.cwd
            )
            
            self.is_connected = True
            logger.info("✅ Claude CLI connected (no API key needed!)")
            
        except FileNotFoundError:
            logger.error("❌ Claude CLI not found. Install Claude Code extension.")
            self.sdk_available = False
            self.is_connected = False
            
    async def send_message(self, prompt: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message to Claude and stream the response.
        """
        if not self.sdk_available:
            # Fallback
            yield {
                "type": "text",
                "content": f"[FALLBACK] Claude CLI not available. Response for: {prompt[:50]}..."
            }
            return
            
        if not self.is_connected:
            await self.initialize()
            
        # Format message for Claude
        message = {
            "type": "user",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            },
            "session_id": self.session_id
        }
        
        # Send to Claude
        message_json = json.dumps(message) + "\n"
        self.process.stdin.write(message_json.encode())
        await self.process.stdin.drain()
        
        logger.info(f"📤 Sent to Claude: {prompt[:50]}...")
        
        # Read response
        buffer = ""
        response_count = 0
        
        while True:
            try:
                # Read line by line
                line = await asyncio.wait_for(
                    self.process.stdout.readline(),
                    timeout=30.0
                )
                
                if not line:
                    break
                    
                # Parse JSON
                try:
                    data = json.loads(line.decode())
                    response_count += 1
                    
                    # Handle different message types
                    if data.get("type") == "text":
                        yield {
                            "type": "text",
                            "content": data.get("content", "")
                        }
                    elif data.get("type") == "assistant":
                        # Assistant message with content blocks
                        if "content" in data:
                            for block in data["content"]:
                                if block.get("type") == "text":
                                    yield {
                                        "type": "text",
                                        "content": block.get("text", "")
                                    }
                    elif data.get("type") == "result":
                        # End of response
                        logger.info(f"✅ Response complete: {response_count} messages")
                        break
                    elif data.get("type") == "system":
                        # System message (init, etc)
                        if data.get("subtype") == "init":
                            logger.info(f"📋 Session initialized: {data.get('session_id', 'unknown')[:8]}")
                        
                except json.JSONDecodeError:
                    # Not JSON, might be plain text
                    text = line.decode().strip()
                    if text:
                        yield {
                            "type": "text",
                            "content": text
                        }
                        
            except asyncio.TimeoutError:
                logger.warning("⏱️ Timeout waiting for Claude response")
                break
            except Exception as e:
                logger.error(f"❌ Error reading response: {e}")
                break
                
    async def cleanup(self):
        """Disconnect from Claude"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
        self.is_connected = False
        
    async def __aenter__(self):
        """Context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.cleanup()
        
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            "available": self.sdk_available,
            "connected": self.is_connected,
            "type": "claude_cli_v2",
            "session_id": self.session_id,
            "uses_cli": True,
            "needs_api_key": False
        }


# Convenience function for one-shot queries
async def query(prompt: str, options: Optional[ClaudeCodeOptions] = None) -> AsyncGenerator[Dict[str, Any], None]:
    """
    One-shot query to Claude (stateless).
    """
    async with ClaudeClientRealV2(options) as client:
        async for message in client.send_message(prompt):
            yield message