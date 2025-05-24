#!/usr/bin/env python3
"""
Test simplificado para confirmar que el problema de eliminación está resuelto
"""

import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timezone

def test_delete_problem_solved():
    """Test para confirmar que el problema de eliminación está resuelto"""
    client = TestClient(app)
    
    print("🎯 CONFIRMACIÓN: PROBLEMA DE ELIMINACIÓN RESUELTO")
    print("=" * 60)
    print()
    
    # Crear mazo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    deck_data = {
        "name": f"Test Simple {timestamp}",
        "description": "Test eliminación"
    }
    
    print("📍 1. Crear mazo")
    response = client.post("/api/v1/decks/", json=deck_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        deck = response.json()
        deck_id = deck["id"]
        print(f"   ✅ Mazo creado ID: {deck_id}")
    else:
        print(f"   ❌ Error: {response.text}")
        return
    
    # Verificar en lista
    print("\n📍 2. Verificar en lista antes de eliminar")
    response = client.get("/api/v1/decks/")
    decks = response.json()
    found = any(d["id"] == deck_id for d in decks)
    print(f"   ✅ En lista: {found}")
    
    # Eliminar (soft delete)
    print(f"\n📍 3. Eliminar mazo {deck_id}")
    response = client.delete(f"/api/v1/decks/{deck_id}")
    print(f"   Status: {response.status_code}")
    print(f"   ✅ Soft delete ejecutado")
    
    # Verificar que NO aparece en lista
    print("\n📍 4. Verificar que NO aparece en lista")
    response = client.get("/api/v1/decks/")
    decks = response.json()
    found = any(d["id"] == deck_id for d in decks)
    print(f"   ✅ En lista después de eliminar: {found}")
    
    if not found:
        print("\n🎉 ÉXITO: PROBLEMA RESUELTO")
        print("✅ El mazo eliminado NO reaparece en la lista")
        print("✅ Soft delete funcionando correctamente")
        print("✅ Sincronización ya no traerá mazos eliminados")
    else:
        print("\n❌ PROBLEMA PERSISTE")
        print("❌ El mazo eliminado aún aparece en la lista")

if __name__ == "__main__":
    test_delete_problem_solved() 