"""Carga 10 restaurantes de prueba en el emulador de Firestore.

Uso:  python -m scripts.seed

Es idempotente: cada restaurante tiene un ID fijo y se escribe con set(),
así que ejecutarlo varias veces no genera duplicados.
"""

import sys

from app.core.config import settings
from app.core.firebase import get_db
from app.domain.models import COLLECTION_NAME

RESTAURANTS = {
    "la-abuela": {
        "name": "La Abuela", "category": "Mexicana", "city": "Puebla", "price": 2,
        "photoUrl": "https://images.unsplash.com/photo-1552566626-52f8b828add9",
        "avgRating": 4.5, "numRatings": 20,
    },
    "pizza-central": {
        "name": "Pizza Central", "category": "Pizza", "city": "Puebla", "price": 1,
        "photoUrl": "https://images.unsplash.com/photo-1513104890138-7c749659a591",
        "avgRating": 4.0, "numRatings": 12,
    },
    "mole-y-mezcal": {
        "name": "Mole y Mezcal", "category": "Mexicana", "city": "Puebla", "price": 3,
        "photoUrl": None, "avgRating": 4.7, "numRatings": 48,
    },
    "tacos-el-guero": {
        "name": "Tacos El Güero", "category": "Tacos", "city": "Puebla", "price": 1,
        "photoUrl": None, "avgRating": 4.6, "numRatings": 87,
    },
    "cafe-las-flores": {
        "name": "Café Las Flores", "category": "Cafetería", "city": "Cholula", "price": 1,
        "photoUrl": None, "avgRating": 4.2, "numRatings": 15,
    },
    "sushi-zen": {
        "name": "Sushi Zen", "category": "Japonesa", "city": "Ciudad de México", "price": 3,
        "photoUrl": None, "avgRating": 4.3, "numRatings": 31,
    },
    "la-trattoria": {
        "name": "La Trattoria", "category": "Italiana", "city": "Ciudad de México", "price": 2,
        "photoUrl": None, "avgRating": 4.1, "numRatings": 26,
    },
    "mariscos-la-playita": {
        "name": "Mariscos La Playita", "category": "Mariscos", "city": "Veracruz", "price": 2,
        "photoUrl": None, "avgRating": 4.4, "numRatings": 39,
    },
    "verde-vivo": {
        "name": "Verde Vivo", "category": "Vegetariana", "city": "Guadalajara", "price": 2,
        "photoUrl": None, "avgRating": 4.0, "numRatings": 9,
    },
    "parrilla-del-sur": {
        "name": "Parrilla del Sur", "category": "Carnes", "city": "Monterrey", "price": 3,
        "photoUrl": None, "avgRating": 4.5, "numRatings": 53,
    },
}


def main() -> int:
    if not settings.FIRESTORE_EMULATOR_HOST:
        print(
            "FIRESTORE_EMULATOR_HOST no está definido: el script solo carga datos "
            "en el emulador, para no escribir por error en Firestore real.\n"
            "Copia .env.example a .env o exporta la variable y vuelve a intentarlo.",
            file=sys.stderr,
        )
        return 1

    collection = get_db().collection(COLLECTION_NAME)
    for doc_id, data in RESTAURANTS.items():
        collection.document(doc_id).set(data)

    print(
        f"Datos semilla creados: {len(RESTAURANTS)} restaurantes "
        f"en {settings.FIRESTORE_EMULATOR_HOST}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
