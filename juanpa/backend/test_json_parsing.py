#!/usr/bin/env python3
"""
Test para diagnosticar problemas de parsing JSON de respuestas de Gemini
"""

import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app
import json

def test_gemini_json_parsing_issue():
    """Test para reproducir el error de parsing JSON de Gemini"""
    client = TestClient(app)
    
    print("🔍 DIAGNÓSTICO: ERROR DE PARSING JSON DE GEMINI")
    print("=" * 60)
    print()
    
    # Test 1: Intentar reproducir el error
    print("📍 Test 1: Generar tarjetas para reproducir error JSON")
    payload_error = {
        'topic': 'Matemáticas básicas',
        'num_cards': 5,
        'difficulty': 'medium',
        'card_type': 'mixed',
        'language': 'es',
        'context': 'Conceptos fundamentales',
        'deck_id': -1,
        'deck_name': 'Matemáticas - Test JSON',
        'deck_description': 'Mazo para probar parsing JSON'
    }
    
    print(f"   Payload: {payload_error}")
    print()
    
    response = client.post('/api/v1/gemini/generate-cards', json=payload_error)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success: {result.get('success', False)}")
        cards_created = result.get('cards_created', [])
        print(f"   ✅ Tarjetas creadas: {len(cards_created)}")
        print("   ✅ JSON parseado correctamente en este intento")
    else:
        print(f"   ❌ Error: {response.text}")
        
        # Buscar errores específicos de parsing
        error_text = response.text
        if "parseando respuesta de Gemini" in error_text:
            print("   🎯 ERROR DE PARSING REPRODUCIDO!")
        if "Expecting" in error_text and "delimiter" in error_text:
            print("   🎯 Error de delimitador JSON confirmado")
    
    print()
    print("=" * 60)
    print("💡 ANÁLISIS DEL PROBLEMA")
    print("=" * 60)
    print()
    print("🔍 CAUSAS PROBABLES:")
    print("   1. Gemini genera JSON con sintaxis incorrecta")
    print("   2. Respuesta contiene caracteres especiales sin escape")
    print("   3. JSON tiene comas extra o faltantes")
    print("   4. Prompt no especifica formato JSON suficientemente claro")
    print("   5. Respuesta mezclada con texto + JSON")
    print()
    print("🛠️  SOLUCIONES NECESARIAS:")
    print("   1. Mejorar parsing robusto con regex")
    print("   2. Limpiar respuesta antes de parsear")
    print("   3. Validar JSON parcialmente")
    print("   4. Mejorar prompts para JSON más consistente")
    print("   5. Agregar fallbacks para parsing")

if __name__ == "__main__":
    test_gemini_json_parsing_issue() 