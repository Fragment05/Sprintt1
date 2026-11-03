"""Pruebas de las vistas HTML (sin emulador)."""


def test_home_lists_restaurants(client, make_restaurant):
    make_restaurant(name="La Abuela", category="Mexicana", city="Puebla", price=2,
                    avgRating=4.5, numRatings=20)
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "La Abuela" in html
    assert "Mexicana" in html
    assert "Puebla" in html
    assert "$$" in html
    assert "4.5" in html
    assert "Ver detalles" in html


def test_home_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "No hay restaurantes" in response.text


def test_home_filters(client, make_restaurant):
    make_restaurant(name="Taquería Uno", category="Tacos", city="Puebla", price=1)
    make_restaurant(name="Sushi Dos", category="Japonesa", city="Cholula", price=3)

    html = client.get("/?city=Puebla").text
    assert "Taquería Uno" in html and "Sushi Dos" not in html

    html = client.get("/?category=Japonesa").text
    assert "Sushi Dos" in html and "Taquería Uno" not in html

    html = client.get("/?price=3").text
    assert "Sushi Dos" in html and "Taquería Uno" not in html


def test_home_accepts_empty_filter_values(client, make_restaurant):
    """El formulario de filtros envía cadenas vacías cuando no se elige nada."""
    make_restaurant(name="Solo Uno")
    response = client.get("/?city=&category=&price=&order_by=name")
    assert response.status_code == 200
    assert "Solo Uno" in response.text


def test_home_escapes_html(client, make_restaurant):
    make_restaurant(name="<script>alert(1)</script>")
    html = client.get("/").text
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_new_form(client):
    response = client.get("/restaurants/new")
    assert response.status_code == 200
    assert 'data-mode="create"' in response.text
    assert "Nuevo restaurante" in response.text


def test_detail_page(client, make_restaurant):
    created = make_restaurant(name="Pizza Central", category="Pizza")
    response = client.get(f"/restaurants/{created['id']}")
    assert response.status_code == 200
    assert "Pizza Central" in response.text
    assert "Editar" in response.text
    assert "Eliminar" in response.text


def test_detail_page_not_found_renders_html(client):
    response = client.get("/restaurants/no-existe")
    assert response.status_code == 404
    assert "text/html" in response.headers["content-type"]
    assert "Restaurante no encontrado" in response.text


def test_edit_form_is_prefilled(client, make_restaurant):
    created = make_restaurant(name="La Abuela", city="Puebla", price=3)
    response = client.get(f"/restaurants/{created['id']}/edit")
    assert response.status_code == 200
    assert 'data-mode="edit"' in response.text
    assert 'value="La Abuela"' in response.text
    assert '<option value="3" selected>' in response.text


def test_api_errors_stay_json(client):
    response = client.get("/api/v1/restaurants/no-existe")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


def test_static_assets_are_served(client):
    assert client.get("/static/css/styles.css").status_code == 200
    assert client.get("/static/js/app.js").status_code == 200
