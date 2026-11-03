# FriendlyEats FastAPI — Sprint 1

Versión local de FriendlyEats: un CRUD de restaurantes con **FastAPI**, vistas HTML con **Jinja2** y
**Firestore** (emulador local) como base de datos.

**Fuera del alcance de este sprint:** autenticación, reseñas, subida de imágenes y despliegue.

## Requisitos

- Python 3.11 o superior
- Node.js 18 o superior (para Firebase CLI)
- Java 11 o superior (lo necesita el emulador de Firestore)
- Firebase CLI: `npm install -g firebase-tools`

## Puesta en marcha

```bash
# 1. Entorno virtual y dependencias
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip freeze > requirements.txt      # opcional: fija las versiones exactas instaladas

# 2. Variables de entorno
cp .env.example .env               # Windows: copy .env.example .env
```

Después, abre **dos terminales** (con el entorno virtual activo en la segunda):

```bash
# Terminal 1: emulador de Firestore (UI del emulador en http://localhost:4000)
firebase emulators:start --only firestore

# Terminal 2: aplicación
uvicorn app.main:app --reload
```

Y en una tercera (o en la segunda, antes de arrancar la app) carga los datos de ejemplo:

```bash
python -m scripts.seed             # 10 restaurantes; se puede ejecutar varias veces sin duplicar
```

| Qué | Dónde |
|---|---|
| Listado de restaurantes | http://localhost:8000 |
| Documentación interactiva de la API | http://localhost:8000/docs |
| Salud | http://localhost:8000/health |
| Datos persistidos en Firestore | http://localhost:4000/firestore |

### Pruebas

```bash
pytest -v
```

Las pruebas del CRUD, filtros, validaciones y vistas usan un repositorio en memoria, así que **no
necesitan el emulador**. `tests/test_firestore_emulator.py` es una prueba de integración que se
ejecuta sola cuando el emulador está corriendo y se omite si no lo está.

## Firebase (S1-06)

Para el desarrollo con el emulador no hace falta una cuenta: el ID `demo-friendlyeats` (cualquier ID que
empiece por `demo-`) funciona sin login. Si prefieres vincular tu propio proyecto:

```bash
firebase login
firebase use --add                 # elige tu proyecto; actualiza .firebaserc
```

y pon el mismo ID en `FIREBASE_PROJECT_ID` dentro de `.env`.

## API

Base: `/api/v1`

| Método | Ruta | Descripción | Respuestas |
|---|---|---|---|
| GET | `/restaurants` | Lista paginada. Query: `city`, `category`, `price` (1-3), `order_by` (`name` \| `avgRating`), `limit` (1-100, por defecto 20), `start_after` (ID del último de la página anterior) | 200 |
| POST | `/restaurants` | Crea un restaurante (`avgRating` y `numRatings` arrancan en 0) | 201, 422 |
| GET | `/restaurants/{id}` | Detalle | 200, 404 |
| PATCH | `/restaurants/{id}` | Actualiza solo los campos enviados (`name`, `category`, `city`, `price`, `photoUrl`) | 200, 400, 404, 422 |
| DELETE | `/restaurants/{id}` | Elimina | 204, 404 |

Ejemplo:

```bash
curl -X POST http://localhost:8000/api/v1/restaurants \
  -H "Content-Type: application/json" \
  -d '{"name":"La Abuela","category":"Mexicana","city":"Puebla","price":2}'
```

Vistas HTML: `/` (listado con filtros), `/restaurants/new`, `/restaurants/{id}`, `/restaurants/{id}/edit`.

## Arquitectura

```
friendlyeats-fastapi/
├── app/
│   ├── main.py                  # App FastAPI, rutas montadas, /health, manejo de errores
│   ├── core/                    # config.py (variables de entorno), firebase.py (cliente), templating.py
│   ├── domain/                  # schemas.py (Pydantic), models.py (constantes y tipos)
│   ├── repositories/            # restaurant_repository.py: ÚNICO acceso a Firestore
│   ├── services/                # restaurant_service.py: reglas de negocio y errores 404/400
│   ├── api/
│   │   ├── deps.py              # inyección del servicio
│   │   ├── views.py             # páginas HTML
│   │   └── v1/restaurants.py    # endpoints REST
│   └── templates/               # base, listado, detalle, formulario, error
├── static/                      # css/styles.css, js/app.js, img/
├── scripts/seed.py              # datos semilla
├── tests/
├── firebase.json · firestore.rules · firestore.indexes.json · .firebaserc
├── .env.example · requirements.txt · pytest.ini
```

Flujo de una petición: **ruta (API o vista) → servicio → repositorio → Firestore**. Las capas
superiores nunca importan el cliente de Firestore.

## Decisiones de diseño

- **`.gitignore` más preciso que `*.json`.** Ignorar todos los `.json` dejaría fuera `firebase.json` y
  `firestore.indexes.json`, que sí deben estar en Git. Se ignoran solo `.env`, `secrets/`,
  `service-account*.json` y los logs de Firebase.
- **Rutas con `def` en vez de `async def`.** El cliente de Firestore es bloqueante; con `def` FastAPI
  ejecuta cada petición en un hilo y no congela el servidor.
- **Inyección de dependencias.** El servicio se obtiene con `Depends(get_restaurant_service)`; las
  pruebas lo sustituyen por un repositorio en memoria. El cliente de Firestore se crea de forma
  perezosa (`get_db()`), no al importar el módulo.
- **ID generado por Firestore** (`document().set()`), no guardado dentro del documento. Los datos
  semilla usan IDs fijos con `set()` para poder repetir el script sin duplicados.
- **`PATCH` solo acepta campos editables.** `avgRating` y `numRatings` los calculará el sistema de
  reseñas (Sprint 2); aunque el cliente los envíe, se ignoran.
- **`photoUrl` solo admite `http://` o `https://`** (evita URLs tipo `javascript:`). Un valor vacío
  significa "sin foto". Las fotos son solo un enlace; la subida de imágenes es de un sprint posterior.
- **Orden:** por `name` de A a Z; por `avgRating` de mayor a menor.
- **Reglas de Firestore (`firestore.rules`) cierran todo el acceso directo de clientes.** La app accede
  con el SDK de servidor, que no pasa por las reglas. Las reglas por propietario llegan con
  autenticación.
- **Índices compuestos.** El emulador no los exige, pero en Firestore real combinar filtros con `order_by`
  requerirá índices en `firestore.indexes.json` (Firestore muestra un enlace para crearlos al primer error).

## Solución de problemas

- **`FIRESTORE_EMULATOR_HOST no está definido` al correr el seed** → copia `.env.example` a `.env`.
- **La app arranca pero el listado da error de conexión** → el emulador no está corriendo (Terminal 1).
- **El emulador no inicia** → comprueba `java -version` y que el puerto 8080 esté libre.
- **Nunca subas** el JSON de cuenta de servicio: guárdalo en `secrets/` (ignorado por Git).

## Siguiente sprint

Firebase Authentication, control de propietario con `ownerId`, Security Rules y reseñas con
transacciones.
