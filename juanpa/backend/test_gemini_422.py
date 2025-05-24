#!/usr/bin/env python3
"""
Script para diagnosticar el error 422 en el endpoint de Gemini
"""

import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app

def test_gemini_422():
    """Probar diferentes payloads para identificar el error 422"""
    client = TestClient(app)
    
    print("=== DIAGNÓSTICO ERROR 422 EN GEMINI ===")
    print()
    
    # Test 1: Payload mínimo
    print("📍 Test 1: Payload mínimo")
    test_payload_1 = {
        'topic': 'Test Topic',
        'num_cards': 2,
        'deck_id': -1,
        'deck_name': 'Test Deck'
    }
    
    print(f"   Payload: {test_payload_1}")
    response = client.post('/api/v1/gemini/generate-cards', json=test_payload_1)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    print()
    
    # Test 2: Payload completo
    print("📍 Test 2: Payload completo")
    test_payload_2 = {
        'topic': 'Matemáticas básicas',
        'num_cards': 3,
        'difficulty': 'easy',
        'card_type': 'standard',
        'language': 'es',
        'context': None,
        'deck_id': -1,
        'deck_name': 'Test Full Deck',
        'deck_description': 'Test description'
    }
    
    print(f"   Payload: {test_payload_2}")
    response = client.post('/api/v1/gemini/generate-cards', json=test_payload_2)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    print()
    
    # Test 3: Solo campos requeridos del modelo
    print("📍 Test 3: Campos requeridos según modelo")
    test_payload_3 = {
        'topic': 'Test Topic Required',
        'deck_id': -1,
        'deck_name': 'Required Deck'
    }
    
    print(f"   Payload: {test_payload_3}")
    response = client.post('/api/v1/gemini/generate-cards', json=test_payload_3)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    print()

if __name__ == "__main__":
    test_gemini_422() 