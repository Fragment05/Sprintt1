import os
from functools import lru_cache

from google.cloud import firestore

from app.core.config import settings


@lru_cache
def get_db() -> firestore.Client:
    """Devuelve un único cliente de Firestore (se crea la primera vez que se usa).

    - Con FIRESTORE_EMULATOR_HOST definido, el cliente habla con el emulador
      local y no necesita credenciales.
    - Sin emulador y con FIREBASE_CREDENTIALS_PATH, usa la cuenta de servicio.
    - Sin ninguno de los dos, usa las credenciales por defecto del entorno (ADC).
    """
    if settings.FIRESTORE_EMULATOR_HOST:
        # La librería lee esta variable al crear el cliente.
        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.FIRESTORE_EMULATOR_HOST
        return firestore.Client(project=settings.FIREBASE_PROJECT_ID)

    if settings.FIREBASE_CREDENTIALS_PATH:
        import firebase_admin
        from firebase_admin import credentials
        from firebase_admin import firestore as admin_firestore

        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(
                cred, {"projectId": settings.FIREBASE_PROJECT_ID}
            )
        return admin_firestore.client()

    return firestore.Client(project=settings.FIREBASE_PROJECT_ID)
