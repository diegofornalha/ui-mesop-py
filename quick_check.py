#!/usr/bin/env python3
import httpx
import asyncio
import json

async def quick_check():
    conv_id = "0ebde9fc-04a3-4ec7-9679-d84bd8df798b"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8888/message/list",
            json={"jsonrpc": "2.0", "method": "message/list", "params": conv_id, "id": 1}
        )
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('result', [])
            
            print(f"\n🔍 Conversa {conv_id[:8]}...")
            print(f"Total: {len(messages)} mensagem(s)\n")
            
            for i, msg in enumerate(messages):
                print(f"Mensagem {i+1}:")
                print(f"  Role: {msg.get('role')}")
                print(f"  Parts: {msg.get('parts')}")
                print(f"  Content: {msg.get('content')}")
                print(f"  MessageId: {msg.get('messageId', 'NO_ID')[:12]}...")
                print()

asyncio.run(quick_check())