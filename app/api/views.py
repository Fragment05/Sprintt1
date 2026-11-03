"""Vistas HTML (Jinja2). Consumen el mismo servicio que la API REST."""

from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_restaurant_service
from app.core.templating import templates
from app.domain.models import OrderBy
from app.services.restaurant_service import RestaurantService

router = APIRouter(include_in_schema=False)

PAGE_SIZE = 20


def _parse_price(value: str | None) -> int | None:
    """El formulario de filtros envía '' cuando no se elige precio."""
    if value in (None, ""):
        return None
    try:
        price = int(value)
    except ValueError:
        return None
    return price if 1 <= price <= 3 else None


@router.get("/")
def home(
    request: Request,
    city: str | None = None,
    category: str | None = None,
    price: str | None = None,
    order_by: OrderBy = "name",
    start_after: str | None = None,
    deleted: str | None = None,
    service: RestaurantService = Depends(get_restaurant_service),
):
    city = city or None
    category = category or None
    price_value = _parse_price(price)

    restaurants = service.list(
        category=category,
        city=city,
        price=price_value,
        order_by=order_by,
        limit=PAGE_SIZE,
        start_after=start_after or None,
    )

    next_url = None
    if len(restaurants) == PAGE_SIZE:
        params = {"order_by": order_by, "start_after": restaurants[-1]["id"]}
        if city:
            params["city"] = city
        if category:
            params["category"] = category
        if price_value:
            params["price"] = price_value
        next_url = "/?" + urlencode(params)

    options = service.filter_options()
    return templates.TemplateResponse(
        request,
        "restaurants.html",
        {
            "restaurants": restaurants,
            "cities": options["cities"],
            "categories": options["categories"],
            "filters": {"city": city, "category": category, "price": price_value},
            "order_by": order_by,
            "next_url": next_url,
            "has_filters": bool(city or category or price_value),
            "flash": "Restaurante eliminado correctamente" if deleted else None,
        },
    )


# /new debe declararse antes que /{restaurant_id}
@router.get("/restaurants/new")
def new_restaurant_form(request: Request):
    return templates.TemplateResponse(
        request, "restaurant_form.html", {"restaurant": None}
    )


@router.get("/restaurants/{restaurant_id}")
def restaurant_detail(
    request: Request,
    restaurant_id: str,
    service: RestaurantService = Depends(get_restaurant_service),
):
    restaurant = service.get(restaurant_id)
    return templates.TemplateResponse(
        request, "restaurant_detail.html", {"restaurant": restaurant}
    )


@router.get("/restaurants/{restaurant_id}/edit")
def edit_restaurant_form(
    request: Request,
    restaurant_id: str,
    service: RestaurantService = Depends(get_restaurant_service),
):
    restaurant = service.get(restaurant_id)
    return templates.TemplateResponse(
        request, "restaurant_form.html", {"restaurant": restaurant}
    )
