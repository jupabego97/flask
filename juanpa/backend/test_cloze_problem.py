#!/usr/bin/env python3
"""
Test específico para diagnosticar el problema de las tarjetas cloze generadas por IA
"""

import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app

def test_cloze_generation_problem():
    """Test para diagnosticar el problema de generación de tarjetas cloze"""
    client = TestClient(app)
    
    print("🔍 DIAGNÓSTICO: PROBLEMA DE TARJETAS CLOZE")
    print("=" * 60)
    print()
    
    # Test 1: Generar tarjetas SOLO cloze
    print("📍 Test 1: Generar SOLO tarjetas cloze")
    payload_cloze = {
        'topic': 'Biología celular básica',
        'num_cards': 3,
        'difficulty': 'easy',
        'card_type': 'cloze',  # SOLO cloze
        'language': 'es',
        'context': 'Conceptos básicos para principiantes',
        'deck_id': -1,
        'deck_name': 'Test Cloze - Diagnóstico',
        'deck_description': 'Mazo para probar tarjetas cloze'
    }
    
    print(f"   Payload: {payload_cloze}")
    print()
    
    response = client.post('/api/v1/gemini/generate-cards', json=payload_cloze)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Success: {result.get('success', False)}")
        
        cards_created = result.get('cards_created', [])
        print(f"   ✅ Tarjetas creadas: {len(cards_created)}")
        print()
        
        print("📋 ANÁLISIS DE TARJETAS CLOZE CREADAS:")
        print("-" * 40)
        
        for i, card in enumerate(cards_created, 1):
            print(f"   Tarjeta {i}:")
            print(f"      ID: {card.get('id')}")
            print(f"      front_content: {card.get('front_content')}")
            print(f"      back_content: {card.get('back_content')}")
            print(f"      cloze_data: {card.get('cloze_data')}")
            print(f"      tags: {card.get('tags', [])}")
            
            # ❌ PROBLEMA IDENTIFICADO
            if not card.get('cloze_data') and not card.get('front_content'):
                print(f"      ❌ PROBLEMA: Tarjeta sin contenido cloze ni front_content")
            elif card.get('cloze_data'):
                print(f"      ✅ Tarjeta cloze correcta")
            else:
                print(f"      ⚠️  Tarjeta convertida a estándar (no cloze)")
            print()
            
        print("🎯 DIAGNÓSTICO:")
        print("-" * 40)
        print("   1. ¿Se generan tarjetas? ✅" if len(cards_created) > 0 else "   1. ❌ No se generan tarjetas")
        
        cloze_cards = [c for c in cards_created if c.get('cloze_data')]
        print(f"   2. Tarjetas cloze reales: {len(cloze_cards)}/{len(cards_created)}")
        
        if len(cloze_cards) == 0:
            print("   ❌ PROBLEMA CRÍTICO: NO se crean tarjetas cloze verdaderas")
        elif len(cloze_cards) < len(cards_created):
            print("   ⚠️  PROBLEMA PARCIAL: Algunas tarjetas no son cloze")
        else:
            print("   ✅ PROBLEMA RESUELTO: Todas son tarjetas cloze")
            
    else:
        print(f"   ❌ Error en generación: {response.text}")
    
    print()
    print("=" * 60)
    print("💡 ANÁLISIS TÉCNICO:")
    print("=" * 60)
    print()
    print("🔄 FLUJO ACTUAL:")
    print("   1. Gemini genera 'cloze_text' → GeneratedCard.cloze_text")
    print("   2. Endpoint procesa → cloze_data = {'cloze_text': generated_card.cloze_text}")
    print("   3. DB guarda en campo cloze_data como JSON")
    print()
    print("⚠️  PROBLEMAS POTENCIALES:")
    print("   - Campo 'raw_cloze_text' de CardCreate no se usa")
    print("   - Conversión incorrecta de cloze_text → cloze_data")
    print("   - Frontend espera formato diferente")
    print("   - Validación de formato {{c1::...}} no funciona")

if __name__ == "__main__":
    test_cloze_generation_problem() 