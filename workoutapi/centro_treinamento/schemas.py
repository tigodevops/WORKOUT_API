from typing import Annotated

from pydantic import UUID4, Field
from workoutapi.contrib.schemas import BaseSchema

class CentroTreinamentoIN(BaseSchema):
    nome: Annotated[str, Field(description="Centro de treinamento", example="CT King", max_length=20)]
    endereco: Annotated[str, Field(description="Endereço do treinamento", example="Rua X, Q02", max_length=30)]
    proprietario: Annotated[str, Field(description="Proprietário do treinamento", example="Marcos", max_length=20)]

class CentroTreinamentoAtleta(BaseSchema):
    nome: Annotated[str, Field(description="Nome do centro de treinamento", example="CT King", max_length=20)]

class CentroTreinamentoOut(CentroTreinamentoIN):
    id: Annotated[UUID4, Field(description="Identificador do centro de treinamento")]

