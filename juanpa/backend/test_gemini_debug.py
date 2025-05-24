#!/usr/bin/env python3
"""
Test de debug para ver exactamente qué está generando Gemini
"""

import sys
import os
sys.path.append('.')
import logging
from app.gemini_service import GeminiCardGenerator, CardGenerationRequest

# Configurar logging para ver detalles
logging.basicConfig(level=logging.DEBUG)

def test_gemini_raw_response():
    """Test para ver la respuesta cruda de Gemini"""
    
    print("🔍 DEBUG: RESPUESTA CRUDA DE GEMINI")
    print("=" * 60)
    print()
    
    # Crear generador
    generator = GeminiCardGenerator()
    
    # Request simple
    request = CardGenerationRequest(
        topic="Suma y resta básica",
        num_cards=3,
        difficulty="easy",
        card_type="mixed",
        language="es",
        context="Para niños de primaria"
    )
    
    print(f"📍 Request: {request}")
    print()
    
    try:
        # Simular solo la parte de llamada a Gemini
        system_prompt = generator._create_system_prompt(request)
        user_prompt = generator._create_user_prompt(request)
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        print("📤 PROMPT ENVIADO A GEMINI:")
        print("-" * 40)
        print(full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
        print()
        
        # Llamar a Gemini
        response = generator.client.models.generate_content(
            model=generator.model_name,
            contents=full_prompt
        )
        
        raw_text = response.text
        if not raw_text:
            print("❌ Gemini no retornó texto")
            return
            
        print("📥 RESPUESTA CRUDA DE GEMINI:")
        print("-" * 40)
        print(raw_text)
        print()
        print(f"Longitud: {len(raw_text)} caracteres")
        print()
        
        # Probar parsing robusto
        print("🔧 PROBANDO PARSING ROBUSTO:")
        print("-" * 40)
        try:
            cards_data = generator._robust_json_parse(raw_text)
            print(f"✅ Parsing exitoso: {len(cards_data)} elementos")
            
            for i, card in enumerate(cards_data, 1):
                print(f"   Elemento {i}: {type(card).__name__}")
                if isinstance(card, dict):
                    print(f"      Keys: {list(card.keys())}")
                    print(f"      Type: {card.get('type', 'N/A')}")
                    if card.get('type') == 'cloze':
                        print(f"      Cloze: {card.get('cloze_text', 'N/A')[:100]}...")
                    else:
                        front = card.get('front_content', 'N/A')
                        if isinstance(front, list) and len(front) > 0:
                            print(f"      Front: {front[0].get('content', 'N/A')[:100]}...")
                        else:
                            print(f"      Front: {front}")
                print()
                
        except Exception as e:
            print(f"❌ Error en parsing: {e}")
            print()
            
        # Generar usando el método completo
        print("🎯 GENERACIÓN COMPLETA:")
        print("-" * 40)
        try:
            import asyncio
            result = asyncio.run(generator.generate_cards(request))
            print(f"✅ Generación exitosa: {len(result.cards)} tarjetas")
            
            for i, card in enumerate(result.cards, 1):
                print(f"   Tarjeta {i}:")
                print(f"      Type: {type(card).__name__}")
                print(f"      Cloze text: {card.cloze_text}")
                print(f"      Front: {card.front_content}")
                print(f"      Tags: {card.tags}")
                print()
                
        except Exception as e:
            print(f"❌ Error en generación: {e}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_gemini_raw_response() 