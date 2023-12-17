from pydantic import BaseModel

PROJECTION = {
    "_id": 0,
    "id_utilisateur": 1,
    "date_naissance": 1,
    "id_genre": 1,
    "age": 1,
    "size": 1,
    "is_pratiquant": 1,
    "salat_pratique": 1,
    "veil": 1,
    "eat_halal": 1,
    "want_children": 1,
    "has_children": 1,
    "family_situation": 1,
    "study_level": 1,
    "fume": 1,
    "figure": 1,
    "pays_code": 1,
    "dept_code": 1,
    "region_code": 1,
    "geoname_id": 1,
    "date_mise_avant": 1,
    "last_live_time": 1,
    "date_create": 1,
    "taux_remplissage": 1,
    "origin": 1,
    "latitude": 1,
    "longitude": 1,
    "photos": {
        "id_photo": 1,
        "hash": 1,
    },
    "location": 1,
    "pseudo": 1,
    "email": 1,
    "actif": 1,
    "app_origin": 1,
    "accroche": 1,
}
ELASTIC_PROJECTION = [
    "id_utilisateur",
    "id_genre",
    "age",
    "size",
    "is_pratiquant",
    "salat_pratique",
    "veil",
    "eat_halal",
    "want_children",
    "has_children",
    "family_situation",
    "study_level",
    "fume",
    "figure",
    "pays_code",
    "dept_code",
    "region_code",
    "geoname_id",
    "date_mise_avant",
    "last_live_time",
    "date_create",
    "taux_remplissage",
    "origin",
    "latitude",
    "longitude",
    "photos",
    "location",
    "interacted_users_number",
    "actif",
]


class RangeInput(BaseModel):
    min_tall: int
    max_tall: int
    min_age: int
    max_age: int


class FeatureInput(BaseModel):
    age: int
    size: int


class CommonInput(BaseModel):
    eat_halal: int
    is_pratiquant: int
    salat_pratique: int
    veil: int
    want_children: int
    has_children: int
    family_situation: int
    study_level: int
    figure: int
    fume: int
    origin: int


class LocationInput(BaseModel):
    latitude: float
    longitude: float
