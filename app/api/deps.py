from functools import lru_cache

from app.services.restaurant_service import RestaurantService


@lru_cache
def get_restaurant_service() -> RestaurantService:
    """Una sola instancia del servicio; las pruebas la reemplazan con dependency_overrides."""
    return RestaurantService()
