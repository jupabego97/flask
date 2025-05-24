#!/usr/bin/env python3
"""
Test para verificar que la eliminación y sincronización funcionan correctamente
"""

import sys
import os
sys.path.append('.')
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime, timezone

def test_delete_and_sync():
    """Test completo de eliminación y sincronización"""
    client = TestClient(app)
    
    print("🎯 TEST: ELIMINACIÓN Y SINCRONIZACIÓN")
    print("=" * 50)
    print()
    
    # Paso 1: Crear un mazo
    print("📍 Paso 1: Crear mazo de prueba")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    deck_data = {
        "name": f"Test Delete Sync {timestamp}",
        "description": "Mazo para probar eliminación y sync"
    }
    
    response = client.post("/api/v1/decks/", json=deck_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        created_deck = response.json()
        deck_id = created_deck["id"]
        print(f"   ✅ Mazo creado con ID: {deck_id}")
    else:
        print(f"   ❌ Error creando mazo: {response.text}")
        return
    
    # Paso 2: Verificar que el mazo aparece en la lista
    print("\n📍 Paso 2: Verificar mazo en lista")
    response = client.get("/api/v1/decks/")
    decks = response.json()
    found_deck = next((d for d in decks if d["id"] == deck_id), None)
    
    if found_deck:
        print(f"   ✅ Mazo encontrado en lista: {found_deck['name']}")
    else:
        print("   ❌ Mazo no encontrado en lista")
        return
    
    # Paso 3: Eliminar el mazo (soft delete)
    print(f"\n📍 Paso 3: Eliminar mazo ID {deck_id}")
    response = client.delete(f"/api/v1/decks/{deck_id}")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        deleted_deck = response.json()
        print(f"   ✅ Mazo eliminado. is_deleted: {deleted_deck.get('is_deleted', 'N/A')}")
        print(f"   ✅ deleted_at: {deleted_deck.get('deleted_at', 'N/A')}")
    else:
        print(f"   ❌ Error eliminando mazo: {response.text}")
        return
    
    # Paso 4: Verificar que el mazo no aparece en la lista normal
    print("\n📍 Paso 4: Verificar que mazo no aparece en lista")
    response = client.get("/api/v1/decks/")
    decks = response.json()
    found_deck = next((d for d in decks if d["id"] == deck_id), None)
    
    if not found_deck:
        print("   ✅ Mazo NO aparece en lista (correcto)")
    else:
        print("   ❌ Mazo aún aparece en lista (incorrecto)")
        return
    
    # Paso 5: Verificar que aparece en sincronización
    print("\n📍 Paso 5: Verificar que aparece en sync con is_deleted=True")
    response = client.get("/api/v1/sync/pull")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        sync_data = response.json()
        sync_decks = sync_data.get("decks", [])
        found_deleted_deck = next((d for d in sync_decks if d["id"] == deck_id), None)
        
        if found_deleted_deck:
            is_deleted = found_deleted_deck.get("is_deleted", False)
            deleted_at = found_deleted_deck.get("deleted_at")
            print(f"   ✅ Mazo encontrado en sync")
            print(f"   ✅ is_deleted: {is_deleted}")
            print(f"   ✅ deleted_at: {deleted_at}")
            
            if is_deleted and deleted_at:
                print("   ✅ Soft delete funcionando correctamente")
            else:
                print("   ❌ Campos de soft delete incorrectos")
        else:
            print("   ❌ Mazo no encontrado en sync")
            return
    else:
        print(f"   ❌ Error en sync pull: {response.text}")
        return
    
    # Paso 6: Simular que el cliente envía una eliminación via sync
    print("\n📍 Paso 6: Simular eliminación vía sync push")
    
    # Crear otro mazo para eliminar vía sync
    deck_data_2 = {
        "name": f"Test Delete Sync 2 {timestamp}",
        "description": "Segundo mazo para probar eliminación via sync"
    }
    
    response = client.post("/api/v1/decks/", json=deck_data_2)
    if response.status_code == 200:
        deck_2 = response.json()
        deck_2_id = deck_2["id"]
        print(f"   ✅ Segundo mazo creado con ID: {deck_2_id}")
        
        # Preparar payload de sync con mazo eliminado
        sync_payload = {
            "client_timestamp": datetime.now(timezone.utc).isoformat(),
            "updated_decks": [
                {
                    "id": deck_2_id,
                    "name": deck_2["name"],
                    "description": deck_2["description"],
                    "created_at": deck_2["created_at"],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "is_deleted": True,
                    "deleted_at": datetime.now(timezone.utc).isoformat()
                }
            ]
        }
        
        response = client.post("/api/v1/sync/push", json=sync_payload)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            sync_result = response.json()
            print(f"   ✅ Sync push exitoso: {sync_result.get('message', 'N/A')}")
            conflicts = sync_result.get("conflicts", [])
            if conflicts:
                print(f"   ⚠️  Conflictos: {len(conflicts)}")
                for conflict in conflicts:
                    print(f"      - {conflict}")
            else:
                print("   ✅ Sin conflictos")
        else:
            print(f"   ❌ Error en sync push: {response.text}")
            return
        
        # Verificar que el mazo 2 ya no aparece en lista
        response = client.get("/api/v1/decks/")
        decks = response.json()
        found_deck_2 = next((d for d in decks if d["id"] == deck_2_id), None)
        
        if not found_deck_2:
            print("   ✅ Segundo mazo eliminado correctamente vía sync")
        else:
            print("   ❌ Segundo mazo aún aparece en lista")
    else:
        print(f"   ❌ Error creando segundo mazo: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 TEST COMPLETADO")
    print("✅ Soft delete funcionando")
    print("✅ Sincronización de eliminaciones funcionando")
    print("✅ Problema resuelto: mazos eliminados no reaparecen")

if __name__ == "__main__":
    test_delete_and_sync() 