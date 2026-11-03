from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def normalize_photo_url(value: str | None) -> str | None:
    """Acepta None o texto vacío (sin foto) y exige http(s) en cualquier otro caso."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if not value.lower().startswith(("http://", "https://")):
        raise ValueError("photoUrl debe empezar con http:// o https://")
    return value


class RestaurantBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)
    price: int = Field(ge=1, le=3)
    photoUrl: str | None = Field(default=None, max_length=500)

    @field_validator("photoUrl")
    @classmethod
    def _validate_photo_url(cls, value: str | None) -> str | None:
        return normalize_photo_url(value)


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    """Solo los campos editables; todos opcionales (PATCH)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    city: str | None = Field(default=None, min_length=1, max_length=50)
    price: int | None = Field(default=None, ge=1, le=3)
    photoUrl: str | None = Field(default=None, max_length=500)

    @field_validator("photoUrl")
    @classmethod
    def _validate_photo_url(cls, value: str | None) -> str | None:
        return normalize_photo_url(value)

    @model_validator(mode="after")
    def _required_fields_cannot_be_null(self):
        # photoUrl sí puede enviarse como null/"" para quitar la foto,
        # pero los demás campos son obligatorios en el documento.
        for field in ("name", "category", "city", "price"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} no puede ser nulo")
        return self


class RestaurantResponse(BaseModel):
    id: str
    name: str
    category: str
    city: str
    price: int
    photoUrl: str | None = None
    avgRating: float = 0
    numRatings: int = 0
