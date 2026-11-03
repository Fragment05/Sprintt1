import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_restaurant_service
from app.main import app
from app.services.restaurant_service import RestaurantService


class FakeRestaurantRepository:
    """Repositorio en memoria con la misma interfaz que RestaurantRepository.

    Permite probar la API y las vistas sin necesitar el emulador de Firestore.
    """

    def __init__(self):
        self.docs: dict[str, dict] = {}
        self._counter = 0

    def create(self, data: dict) -> dict:
        self._counter += 1
        doc_id = f"fake-{self._counter}"
        document = {**data, "avgRating": 0, "numRatings": 0}
        self.docs[doc_id] = document
        return {**document, "id": doc_id}

    def get(self, restaurant_id: str):
        doc = self.docs.get(restaurant_id)
        return None if doc is None else {**doc, "id": restaurant_id}

    def list(self, category=None, city=None, price=None, order_by="name",
             limit=20, start_after=None):
        items = [{**d, "id": i} for i, d in self.docs.items()]
        if category:
            items = [r for r in items if r["category"] == category]
        if city:
            items = [r for r in items if r["city"] == city]
        if price:
            items = [r for r in items if r["price"] == price]
        items.sort(key=lambda r: r[order_by], reverse=(order_by == "avgRating"))
        if start_after:
            ids = [r["id"] for r in items]
            if start_after in ids:
                items = items[ids.index(start_after) + 1:]
        return items[:limit]

    def distinct_values(self, field: str):
        return sorted({d[field] for d in self.docs.values() if d.get(field)})

    def update(self, restaurant_id: str, data: dict):
        if restaurant_id not in self.docs:
            return None
        self.docs[restaurant_id].update(data)
        return self.get(restaurant_id)

    def delete(self, restaurant_id: str) -> bool:
        return self.docs.pop(restaurant_id, None) is not None


@pytest.fixture
def repo():
    return FakeRestaurantRepository()


@pytest.fixture
def client(repo):
    service = RestaurantService(repository=repo)
    app.dependency_overrides[get_restaurant_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_restaurant(repo):
    """Crea un restaurante directamente en el repositorio falso y devuelve el documento."""

    def _make(name="La Abuela", category="Mexicana", city="Puebla", price=2,
              photoUrl=None, avgRating=0, numRatings=0):
        created = repo.create(
            {"name": name, "category": category, "city": city,
             "price": price, "photoUrl": photoUrl}
        )
        repo.docs[created["id"]].update(avgRating=avgRating, numRatings=numRatings)
        return repo.get(created["id"])

    return _make
