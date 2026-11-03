"""Pruebas del CRUD, filtros y validaciones de la API (sin emulador)."""

API = "/api/v1/restaurants"

VALID = {"name": "Restaurante Test", "category": "Mexicana", "city": "Puebla", "price": 2}


# --- Salud ---------------------------------------------------------------

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --- Crear ---------------------------------------------------------------

def test_create_restaurant(client, repo):
    response = client.post(API, json=VALID)
    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["name"] == "Restaurante Test"
    assert body["avgRating"] == 0
    assert body["numRatings"] == 0
    assert body["photoUrl"] is None
    assert body["id"] in repo.docs


def test_create_trims_whitespace_and_blank_photo(client):
    payload = {**VALID, "name": "  La Abuela  ", "photoUrl": "   "}
    body = client.post(API, json=payload).json()
    assert body["name"] == "La Abuela"
    assert body["photoUrl"] is None


def test_create_with_valid_photo_url(client):
    payload = {**VALID, "photoUrl": "https://images.unsplash.com/photo-1"}
    response = client.post(API, json=payload)
    assert response.status_code == 201
    assert response.json()["photoUrl"] == "https://images.unsplash.com/photo-1"


def test_create_ignores_client_supplied_ratings(client):
    payload = {**VALID, "avgRating": 5, "numRatings": 999}
    body = client.post(API, json=payload).json()
    assert body["avgRating"] == 0
    assert body["numRatings"] == 0


def test_invalid_price(client):
    assert client.post(API, json={**VALID, "price": 10}).status_code == 422
    assert client.post(API, json={**VALID, "price": 0}).status_code == 422


def test_missing_and_empty_required_fields(client):
    assert client.post(API, json={**VALID, "name": ""}).status_code == 422
    assert client.post(API, json={**VALID, "name": "   "}).status_code == 422
    payload = dict(VALID)
    del payload["city"]
    assert client.post(API, json=payload).status_code == 422


def test_field_length_limits(client):
    assert client.post(API, json={**VALID, "name": "x" * 101}).status_code == 422
    assert client.post(API, json={**VALID, "category": "x" * 51}).status_code == 422


def test_invalid_photo_url(client):
    for bad in ("javascript:alert(1)", "ftp://x.com/a.png", "no-es-url"):
        assert client.post(API, json={**VALID, "photoUrl": bad}).status_code == 422


# --- Obtener -------------------------------------------------------------

def test_get_restaurant(client, make_restaurant):
    created = make_restaurant(name="Pizza Central")
    response = client.get(f"{API}/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Pizza Central"


def test_get_restaurant_not_found(client):
    response = client.get(f"{API}/no-existe")
    assert response.status_code == 404
    assert response.json()["detail"] == "Restaurante no encontrado"


# --- Listar, ordenar, filtrar, paginar -----------------------------------

def test_list_empty(client):
    response = client.get(API)
    assert response.status_code == 200
    assert response.json() == []


def test_list_ordered_by_name_by_default(client, make_restaurant):
    make_restaurant(name="Zeta")
    make_restaurant(name="Alfa")
    names = [r["name"] for r in client.get(API).json()]
    assert names == ["Alfa", "Zeta"]


def test_list_order_by_rating_descending(client, make_restaurant):
    make_restaurant(name="A", avgRating=3.0, numRatings=1)
    make_restaurant(name="B", avgRating=4.8, numRatings=1)
    make_restaurant(name="C", avgRating=4.1, numRatings=1)
    names = [r["name"] for r in client.get(f"{API}?order_by=avgRating").json()]
    assert names == ["B", "C", "A"]


def test_list_invalid_order_by(client):
    assert client.get(f"{API}?order_by=password").status_code == 422


def test_list_filters(client, make_restaurant):
    make_restaurant(name="A", category="Mexicana", city="Puebla", price=2)
    make_restaurant(name="B", category="Pizza", city="Puebla", price=1)
    make_restaurant(name="C", category="Pizza", city="Cholula", price=1)

    assert {r["name"] for r in client.get(f"{API}?city=Puebla").json()} == {"A", "B"}
    assert {r["name"] for r in client.get(f"{API}?category=Pizza").json()} == {"B", "C"}
    assert {r["name"] for r in client.get(f"{API}?price=1").json()} == {"B", "C"}
    combined = client.get(f"{API}?category=Pizza&city=Puebla&price=1").json()
    assert [r["name"] for r in combined] == ["B"]
    assert client.get(f"{API}?city=Oaxaca").json() == []


def test_list_invalid_price_filter(client):
    assert client.get(f"{API}?price=7").status_code == 422


def test_list_pagination(client, make_restaurant):
    for name in ("A", "B", "C", "D", "E"):
        make_restaurant(name=name)

    page1 = client.get(f"{API}?limit=2").json()
    assert [r["name"] for r in page1] == ["A", "B"]

    page2 = client.get(f"{API}?limit=2&start_after={page1[-1]['id']}").json()
    assert [r["name"] for r in page2] == ["C", "D"]

    page3 = client.get(f"{API}?limit=2&start_after={page2[-1]['id']}").json()
    assert [r["name"] for r in page3] == ["E"]


def test_list_limit_bounds(client):
    assert client.get(f"{API}?limit=0").status_code == 422
    assert client.get(f"{API}?limit=101").status_code == 422


def test_list_default_limit_is_20(client, make_restaurant):
    for i in range(25):
        make_restaurant(name=f"R{i:02d}")
    assert len(client.get(API).json()) == 20


# --- Actualizar ----------------------------------------------------------

def test_update_only_sent_fields(client, make_restaurant):
    created = make_restaurant(name="Vieja", city="Puebla", price=2)
    response = client.patch(f"{API}/{created['id']}", json={"name": "Nueva"})
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Nueva"
    assert body["city"] == "Puebla"
    assert body["price"] == 2


def test_update_persists(client, make_restaurant):
    created = make_restaurant()
    client.patch(f"{API}/{created['id']}", json={"price": 3})
    assert client.get(f"{API}/{created['id']}").json()["price"] == 3


def test_update_cannot_change_ratings(client, make_restaurant):
    created = make_restaurant(avgRating=4.5, numRatings=20)
    response = client.patch(f"{API}/{created['id']}", json={"avgRating": 1, "numRatings": 0})
    assert response.status_code == 400  # ningún campo editable enviado
    stored = client.get(f"{API}/{created['id']}").json()
    assert stored["avgRating"] == 4.5
    assert stored["numRatings"] == 20


def test_update_can_clear_photo(client, make_restaurant):
    created = make_restaurant(photoUrl="https://example.com/a.png")
    response = client.patch(f"{API}/{created['id']}", json={"photoUrl": ""})
    assert response.status_code == 200
    assert response.json()["photoUrl"] is None


def test_update_empty_body(client, make_restaurant):
    created = make_restaurant()
    assert client.patch(f"{API}/{created['id']}", json={}).status_code == 400


def test_update_validations(client, make_restaurant):
    created = make_restaurant()
    url = f"{API}/{created['id']}"
    assert client.patch(url, json={"price": 9}).status_code == 422
    assert client.patch(url, json={"name": ""}).status_code == 422
    assert client.patch(url, json={"name": None}).status_code == 422
    assert client.patch(url, json={"photoUrl": "javascript:alert(1)"}).status_code == 422


def test_update_not_found(client):
    assert client.patch(f"{API}/no-existe", json={"name": "X"}).status_code == 404


# --- Eliminar ------------------------------------------------------------

def test_delete_restaurant(client, make_restaurant):
    created = make_restaurant()
    response = client.delete(f"{API}/{created['id']}")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"{API}/{created['id']}").status_code == 404


def test_delete_not_found(client):
    assert client.delete(f"{API}/no-existe").status_code == 404


# --- Flujo completo ------------------------------------------------------

def test_full_crud_flow(client):
    created = client.post(API, json=VALID).json()
    rid = created["id"]

    assert client.get(f"{API}/{rid}").json()["name"] == "Restaurante Test"
    assert client.patch(f"{API}/{rid}", json={"city": "Cholula"}).json()["city"] == "Cholula"
    assert [r["id"] for r in client.get(f"{API}?city=Cholula").json()] == [rid]
    assert client.delete(f"{API}/{rid}").status_code == 204
    assert client.get(API).json() == []
