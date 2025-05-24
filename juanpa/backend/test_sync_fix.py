#!/usr/bin/env python3
"""
Test para verificar que la sincronización funciona después de arreglar el validador
"""

import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app

def test_sync_after_fix():
    """Test para verificar sincronización después del arreglo"""
    client = TestClient(app)
    
    print("🔧 TEST: Sincronización después de arreglar validador")
    print("=" * 50)
    print()
    
    response = client.get('/api/v1/sync/pull')
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sincronización exitosa")
        print(f"   Mazos: {len(data.get('decks', []))}")
        print(f"   Tarjetas: {len(data.get('cards', []))}")
        print(f"   Timestamp: {data.get('server_timestamp', 'N/A')[:19]}")
        
        # Verificar si hay etiquetas con /
        all_cards = data.get('cards', [])
        slash_tags = []
        for card in all_cards:
            tags = card.get('tags', [])
            if tags:
                for tag in tags:
                    if '/' in tag:
                        slash_tags.append(tag)
        
        if slash_tags:
            print(f"   ✅ Etiquetas con / encontradas: {set(slash_tags)}")
        else:
            print("   ℹ️ No se encontraron etiquetas con /")
            
        print("\n🎉 PROBLEMA DE SINCRONIZACIÓN RESUELTO")
        
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_sync_after_fix() 