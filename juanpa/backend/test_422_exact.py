#!/usr/bin/env python3
"""
Test para reproducir exactamente el error 422 del frontend
"""

import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app

def test_422_exact():
    """Reproducir el error 422 exacto que está viendo el frontend"""
    client = TestClient(app)
    
    print("=== REPRODUCIENDO ERROR 422 EXACTO ===")
    print()
    
    # Test 1: Request sin deck_name (debería fallar con 422)
    print("📍 Test 1: deck_id = -1 SIN deck_name (debería dar 422)")
    payload_bad = {
        'topic': 'Test Topic',
        'num_cards': 2,
        'deck_id': -1
        # ❌ Falta deck_name - esto debería fallar
    }
    
    print(f"   Payload: {payload_bad}")
    response = client.post('/api/v1/gemini/generate-cards', json=payload_bad)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}...")
    print()
    
    # Test 2: Request con deck_name vacío (debería fallar con 422)
    print("📍 Test 2: deck_id = -1 CON deck_name vacío (debería dar 422)")
    payload_bad2 = {
        'topic': 'Test Topic',
        'num_cards': 2,
        'deck_id': -1,
        'deck_name': ''  # ❌ deck_name vacío - esto debería fallar
    }
    
    print(f"   Payload: {payload_bad2}")
    response = client.post('/api/v1/gemini/generate-cards', json=payload_bad2)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}...")
    print()
    
    # Test 3: Request con deck_name solo espacios (debería fallar con 422)
    print("📍 Test 3: deck_id = -1 CON deck_name solo espacios (debería dar 422)")
    payload_bad3 = {
        'topic': 'Test Topic',
        'num_cards': 2,
        'deck_id': -1,
        'deck_name': '   '  # ❌ deck_name solo espacios - esto debería fallar
    }
    
    print(f"   Payload: {payload_bad3}")
    response = client.post('/api/v1/gemini/generate-cards', json=payload_bad3)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}...")
    print()
    
    # Test 4: Request con deck_name válido (debería funcionar)
    print("📍 Test 4: deck_id = -1 CON deck_name válido (debería funcionar)")
    payload_good = {
        'topic': 'Test Topic',
        'num_cards': 2,
        'deck_id': -1,
        'deck_name': 'Mazo de Prueba Válido'  # ✅ deck_name válido
    }
    
    print(f"   Payload: {payload_good}")
    response = client.post('/api/v1/gemini/generate-cards', json=payload_good)
    print(f"   Status: {response.status_code}")
    if response.status_code == 422:
        print(f"   Response: {response.text}")
    else:
        result = response.json()
        print(f"   Success: {result.get('success', False)}")
        print(f"   Tarjetas: {len(result.get('cards_created', []))}")
    print()
    
    print("🎯 CONCLUSIÓN:")
    print("   El error 422 ocurre cuando:")
    print("   - deck_id = -1 (crear mazo nuevo)")
    print("   - PERO deck_name está ausente, vacío o solo espacios")
    print("   - El validador de Pydantic correctamente rechaza el request")
    print()
    print("💡 SOLUCIÓN:")
    print("   El frontend debe enviar deck_name cuando deck_id = -1")

if __name__ == "__main__":
    test_422_exact() 