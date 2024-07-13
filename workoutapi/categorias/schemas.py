from typing import Annotated

from pydantic import UUID4, Field
from workoutapi.contrib.schemas import BaseSchema

class CategoriaIn(BaseSchema):
    nome: Annotated[str, Field(description="Nome da Categoria", examples="Scale", max_length=10)]

class CategoriaOut(CategoriaIn):
    id: Annotated[UUID4, Field(description="Identificador da categoria")]

    
