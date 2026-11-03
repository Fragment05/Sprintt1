"""Constantes y tipos del dominio de restaurantes."""

from typing import Literal

COLLECTION_NAME = "restaurants"

# Campos por los que se puede ordenar el listado.
OrderBy = Literal["name", "avgRating"]

# Campos que un administrador puede editar (avgRating y numRatings los
# calculará el sistema de reseñas en un sprint posterior).
EDITABLE_FIELDS = ("name", "category", "city", "price", "photoUrl")

PRICE_LABELS = {1: "$", 2: "$$", 3: "$$$"}
