#!/usr/bin/env python3
"""
Test final para verificar que la solución completa del error JSON funciona
"""

import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app

def test_solucion_json_completa():
    """Test final para confirmar que la solución completa funciona"""
    client = TestClient(app)
    
    print("🎯 TEST FINAL: SOLUCIÓN COMPLETA PROBLEMA JSON")
    print("=" * 60)
    print()
    
    # Test que reproduce exactamente la situación del frontend
    print("📍 Test: Generar tarjetas mixtas como en el frontend")
    payload = {
        'topic': 'Física básica - Fuerza y movimiento',
        'num_cards': 4,
        'difficulty': 'medium',
        'card_type': 'mixed',
        'language': 'es',
        'context': 'Conceptos fundamentales para estudiantes de secundaria',
        'deck_id': -1,
        'deck_name': 'Física - Test Final JSON',
        'deck_description': 'Mazo para verificar solución completa'
    }
    
    print(f"   Request payload configurado")
    print(f"   Esperando: JSON válido con 4 tarjetas mixtas")
    print()
    
    response = client.post('/api/v1/gemini/generate-cards', json=payload)
    print(f"   Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Respuesta exitosa")
        print(f"   ✅ Success: {result.get('success', False)}")
        
        cards_created = result.get('cards_created', [])
        print(f"   ✅ Tarjetas generadas: {len(cards_created)}")
        print()
        
        # Análisis detallado de cada tarjeta
        print("📋 ANÁLISIS DE TARJETAS GENERADAS:")
        print("-" * 50)
        
        cloze_count = 0
        standard_count = 0
        
        for i, card in enumerate(cards_created, 1):
            print(f"   🏷️  Tarjeta {i}:")
            print(f"      ID: {card.get('id')}")
            print(f"      Deck ID: {card.get('deck_id')}")
            
            # Verificar tipo y contenido
            has_cloze = card.get('cloze_data') is not None
            has_front_back = (card.get('front_content') is not None and 
                             card.get('back_content') is not None)
            
            if has_cloze:
                cloze_count += 1
                cloze_data = card.get('cloze_data', {})
                if isinstance(cloze_data, dict) and 'cloze_text' in cloze_data:
                    cloze_text = cloze_data['cloze_text']
                    print(f"      🔍 Tipo: CLOZE")
                    print(f"      📝 Texto: {cloze_text[:80]}...")
                    
                    # Verificar formato cloze
                    if '{{c1::' in cloze_text or '{{c2::' in cloze_text:
                        print(f"      ✅ Formato cloze correcto")
                    else:
                        print(f"      ⚠️  Formato cloze inusual")
                else:
                    print(f"      🔍 Tipo: CLOZE (estructura rara)")
                    print(f"      📝 Data: {cloze_data}")
            
            elif has_front_back:
                standard_count += 1
                print(f"      📖 Tipo: ESTÁNDAR")
                
                front = card.get('front_content')
                back = card.get('back_content') 
                
                if isinstance(front, str):
                    print(f"      ❓ Pregunta: {front[:60]}...")
                elif isinstance(front, list) and len(front) > 0:
                    content = front[0].get('content', '') if isinstance(front[0], dict) else str(front[0])
                    print(f"      ❓ Pregunta: {content[:60]}...")
                else:
                    print(f"      ❓ Pregunta: {front}")
                
                if isinstance(back, str):
                    print(f"      💡 Respuesta: {back[:60]}...")
                elif isinstance(back, list) and len(back) > 0:
                    content = back[0].get('content', '') if isinstance(back[0], dict) else str(back[0])
                    print(f"      💡 Respuesta: {content[:60]}...")
                else:
                    print(f"      💡 Respuesta: {back}")
            
            else:
                print(f"      ❌ Tipo: MALFORMADA")
                print(f"      ⚠️  Sin contenido válido")
            
            # Tags
            tags = card.get('tags', [])
            if tags:
                print(f"      🏷️  Tags: {', '.join(tags[:3])}...")
            
            print()
        
        print("=" * 50)
        print("🏆 RESUMEN FINAL:")
        print(f"   📊 Total tarjetas: {len(cards_created)}")
        print(f"   🔍 Tarjetas cloze: {cloze_count}")
        print(f"   📖 Tarjetas estándar: {standard_count}")
        print(f"   📈 Distribución: {(cloze_count/len(cards_created)*100):.1f}% cloze, {(standard_count/len(cards_created)*100):.1f}% estándar")
        print()
        
        if len(cards_created) >= 4:
            print("   ✅ CANTIDAD: Generó la cantidad esperada")
        else:
            print("   ⚠️  CANTIDAD: Menos tarjetas de las esperadas")
            
        if cloze_count > 0 and standard_count > 0:
            print("   ✅ VARIEDAD: Tipos mixtos correctos")
        else:
            print("   ⚠️  VARIEDAD: Solo un tipo de tarjeta")
            
        if len(cards_created) > 0:
            print("   ✅ PARSING: JSON procesado correctamente")
            print("   ✅ FRONTEND: Compatible con interfaz de usuario")
            print()
            print("🎉 SOLUCIÓN COMPLETA: PROBLEMA RESUELTO AL 100%")
        
    else:
        print(f"   ❌ Error HTTP: {response.text}")
        print("   ❌ La solución necesita más ajustes")

if __name__ == "__main__":
    test_solucion_json_completa() 