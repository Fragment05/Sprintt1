from __future__ import annotations  # el método `list` de la clase tapa al `list` nativo en las anotaciones

from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.firebase import get_db
from app.domain.models import COLLECTION_NAME


class RestaurantRepository:
    """Único lugar de la app que habla con Firestore."""

    def __init__(self, db=None, collection_name: str = COLLECTION_NAME):
        self.collection = (db or get_db()).collection(collection_name)

    def create(self, data: dict) -> dict:
        ref = self.collection.document()  # Firestore genera el ID
        document = {**data, "avgRating": 0, "numRatings": 0}
        ref.set(document)
        return {**document, "id": ref.id}

    def get(self, restaurant_id: str) -> dict | None:
        doc = self.collection.document(restaurant_id).get()
        if not doc.exists:
            return None
        return {**doc.to_dict(), "id": doc.id}

    def list(
        self,
        category: str | None = None,
        city: str | None = None,
        price: int | None = None,
        order_by: str = "name",
        limit: int = 20,
        start_after: str | None = None,
    ) -> list[dict]:
        query = self.collection
        if category:
            query = query.where(filter=FieldFilter("category", "==", category))
        if city:
            query = query.where(filter=FieldFilter("city", "==", city))
        if price:
            query = query.where(filter=FieldFilter("price", "==", price))

        # La calificación se ordena de mayor a menor; el nombre, A-Z.
        direction = (
            firestore.Query.DESCENDING
            if order_by == "avgRating"
            else firestore.Query.ASCENDING
        )
        query = query.order_by(order_by, direction=direction).limit(limit)

        if start_after:
            last_doc = self.collection.document(start_after).get()
            if last_doc.exists:
                query = query.start_after(last_doc)

        return [{**doc.to_dict(), "id": doc.id} for doc in query.stream()]

    def distinct_values(self, field: str) -> list[str]:
        """Valores distintos de un campo (para llenar los filtros de la interfaz)."""
        values = {
            doc.to_dict().get(field)
            for doc in self.collection.select([field]).stream()
        }
        return sorted(v for v in values if v)

    def update(self, restaurant_id: str, data: dict) -> dict | None:
        ref = self.collection.document(restaurant_id)
        if not ref.get().exists:
            return None
        ref.update(data)
        return self.get(restaurant_id)

    def delete(self, restaurant_id: str) -> bool:
        ref = self.collection.document(restaurant_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True
