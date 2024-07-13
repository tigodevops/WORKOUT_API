from typing import Annotated, Optional

from centro_treinamento.schemas import CentroTreinamentoAtleta
from workoutapi.contrib.schemas import BaseSchema, OutMixin
from pydantic import BaseModel, Field, PositiveFloat
from workoutapi.categorias.schemas import CategoriaIn


class Atleta(BaseSchema):
    nome: Annotated[str, Field(description="Nome do atleta", examples="Joao", max_length=50)]    
    cpf: Annotated[str, Field(description="CPF do atleta", examples="12345678900", max_length=11)]
    idade: Annotated[int, Field(description="Idade do atleta", examples=25)]
    peso: Annotated[PositiveFloat, Field(description="Peso do atleta", examples=75.5)]
    altura: Annotated[PositiveFloat, Field(description="Altura do atleta", examples=1.70)]
    sexo: Annotated[int, Field(description="Sexo do atleta", examples="M", max_length=1)]
    categoria: Annotated[CategoriaIn, Field(description='Categoria do Atleta')]
    centro_treinamento: Annotated[CentroTreinamentoAtleta, Field(description='Categoria do Atleta')]


class AtletaIn(Atleta):
    pass

class AtletaOut(Atleta, OutMixin):
    pass

class AtletaUpdate(BaseSchema):
    nome: Annotated[Optional[str], Field(description="Nome do atleta", examples="Joao", max_length=50)]
    idade: Annotated[Optional[int], Field(description="Idade do atleta", examples=25)]


