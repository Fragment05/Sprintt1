"""Prueba de integración contra el emulador real de Firestore.

Se omite automáticamente si el emulador no está corriendo
(firebase emulators:start --only firestore). Usa la colección
"restaurants_test" para no tocar los datos de la app.
"""

import os
import socket

import pytest

EMULATOR_HOST = os.getenv("FIRESTORE_EMULATOR_HOST", "127.0.0.1:8080")


def _emulator_is_up() -> bool:
    host, _, port = EMULATOR_HOST.rpartition(":")
    try:
        socket.create_connection((host, int(port)), timeout=0.5).close()
        return True
    except (OSError, ValueError):
        return False


pytestmark = pytest.mark.skipif(
    not _emulator_is_up(), reason="El emulador de Firestore no está corriendo"
)


@pytest.fixture
def real_repo(monkeypatch):
    from app.core.config import settings
    from app.core.firebase import get_db
    from app.repositories.restaurant_repository import RestaurantRepository

    # Garantiza que NUNCA se use Firestore real en esta prueba.
    monkeypatch.setattr(settings, "FIRESTORE_EMULATOR_HOST", EMULATOR_HOST)
    get_db.cache_clear()
    repo = RestaurantRepository(collection_name="restaurants_test")
    yield repo
    for doc in repo.collection.stream():
        doc.reference.delete()
    get_db.cache_clear()


def test_repository_crud_against_emulator(real_repo):
    created = real_repo.create(
        {"name": "Emulador", "category": "Pizza", "city": "Puebla", "price": 1, "photoUrl": None}
    )
    rid = created["id"]
    assert rid
    assert real_repo.get(rid)["name"] == "Emulador"
    assert real_repo.get(rid)["numRatings"] == 0

    assert [r["id"] for r in real_repo.list(city="Puebla", category="Pizza", price=1)] == [rid]
    assert real_repo.list(city="Oaxaca") == []
    assert "Puebla" in real_repo.distinct_values("city")

    assert real_repo.update(rid, {"price": 3})["price"] == 3
    assert real_repo.update("no-existe", {"price": 3}) is None

    assert real_repo.delete(rid) is True
    assert real_repo.delete(rid) is False
    assert real_repo.get(rid) is None
