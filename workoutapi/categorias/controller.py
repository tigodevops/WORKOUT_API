from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError, ProgrammingError
from psycopg2.errors import UniqueViolation

from workoutapi.categorias.schemas import CategoriaIn, CategoriaOut
from workoutapi.categorias.models import CategoriaModel
from workoutapi.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
        "/",
        summary="Criar nova categoria",
        status_code=status.HTTP_201_CREATED,
        response_model=CategoriaOut,
)
async def post(db_session: DatabaseDependency, categoria_in: CategoriaIn = Body(...)):
    categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
    categoria_model = CategoriaModel(**categoria_out.model_dump())

    try:
        db_session.add(categoria_model)
        await db_session.commit()
    except IntegrityError as exc:
        if isinstance(exc.orig, UniqueViolation):
            conflicting_nome = exc.params.get('nome')
            return JSONResponse(
                status_code=status.HTTP_303_SEE_OTHER,
                content={"message": f"Já existe uma categoria cadastrada com o nome: {conflicting_nome}"}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Erro de integridade de dados"}
            )

    except ProgrammingError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ocorreu um erro ao inserir os dados no banco'
        )

    return categoria_out


@router.get(
    "/",
    summary="Consultar todas as categorias",
    status_code=status.HTTP_200_OK,
    response_model=Page[CategoriaOut],
)
async def query(db_session: DatabaseDependency, page: int = 1, size: int = 10) -> Page[CategoriaOut]:
    categorias_query = select(CategoriaModel)
    categorias = await db_session.execute(categorias_query)

    return paginate([CategoriaOut.model_validate(categoria) for categoria in categorias.scalars().all()], page, size)


@router.get(
        "/{id}",
        summary="Consultar uma categoria pelo idd",
        status_code=status.HTTP_200_OK,
        response_model=CategoriaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> list[CategoriaOut]:
    categoria: CategoriaOut = (await db_session.execute(
        select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail=f'Categoria não encontrada no id: {id}'
        )

    return categoria

add_pagination(router)
