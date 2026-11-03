from fastapi import APIRouter, Depends, Query, Response

from app.api.deps import get_restaurant_service
from app.domain.models import OrderBy
from app.domain.schemas import RestaurantCreate, RestaurantResponse, RestaurantUpdate
from app.services.restaurant_service import RestaurantService

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

# Las rutas son `def` (no `async def`) porque el cliente de Firestore es
# bloqueante: así FastAPI las ejecuta en un hilo y no frena el servidor.


@router.get("", response_model=list[RestaurantResponse])
def list_restaurants(
    category: str | None = None,
    city: str | None = None,
    price: int | None = Query(default=None, ge=1, le=3),
    order_by: OrderBy = "name",
    limit: int = Query(default=20, ge=1, le=100),
    start_after: str | None = Query(
        default=None, description="ID del último restaurante de la página anterior"
    ),
    service: RestaurantService = Depends(get_restaurant_service),
):
    return service.list(
        category=category,
        city=city,
        price=price,
        order_by=order_by,
        limit=limit,
        start_after=start_after,
    )


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(
    restaurant_id: str, service: RestaurantService = Depends(get_restaurant_service)
):
    return service.get(restaurant_id)


@router.post("", status_code=201, response_model=RestaurantResponse)
def create_restaurant(
    payload: RestaurantCreate,
    service: RestaurantService = Depends(get_restaurant_service),
):
    return service.create(payload)


@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: str,
    payload: RestaurantUpdate,
    service: RestaurantService = Depends(get_restaurant_service),
):
    return service.update(restaurant_id, payload)


@router.delete("/{restaurant_id}", status_code=204)
def delete_restaurant(
    restaurant_id: str, service: RestaurantService = Depends(get_restaurant_service)
):
    service.delete(restaurant_id)
    return Response(status_code=204)
