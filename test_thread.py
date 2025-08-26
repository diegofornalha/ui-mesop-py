#!/usr/bin/env python3
"""
Teste para verificar se o thread está funcionando
"""

import asyncio
import threading
import time

def thread_task():
    """Tarefa executada em thread."""
    print(f"🔵 Thread iniciada: {threading.current_thread().name}")
    time.sleep(2)
    print(f"✅ Thread concluída: {threading.current_thread().name}")
    return "Thread OK"

async def async_task():
    """Tarefa assíncrona."""
    print("🔵 Async task iniciada")
    await asyncio.sleep(1)
    print("✅ Async task concluída")
    return "Async OK"

def test_threading():
    """Testa threading."""
    print("\n=== Teste de Threading ===")
    
    # Criar e iniciar thread
    t = threading.Thread(target=thread_task)
    t.start()
    print("Thread lançada, aguardando...")
    t.join()
    print("Thread finalizada")
    
    # Testar com asyncio
    print("\n=== Teste de Asyncio + Threading ===")
    loop = asyncio.new_event_loop()
    
    def run_async_in_thread():
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_task())
        print(f"Resultado async: {result}")
    
    t2 = threading.Thread(target=run_async_in_thread)
    t2.start()
    t2.join()
    
    print("\n✅ Todos os testes passaram")

if __name__ == "__main__":
    test_threading()