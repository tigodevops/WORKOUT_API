from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.pagination import Page, add_pagination, paginate
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError, ProgrammingError
from psycopg2.errors import UniqueViolation
from workoutapi.centro_treinamento import CentroTreinamentoIn, CentroTreinamentoOut
from workoutapi.centro_treinamento.models import CentroTreinamentoModel
from workoutapi.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
        "/",
        summary="Criar um novo centro de treinamento",
        status_code=status.HTTP_201_CREATED,
        response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency, 
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
    centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())

    try:
        db_session.add(centro_treinamento_model)
        await db_session.commit()
    except IntegrityError as exc:
        if isinstance(exc.orig, UniqueViolation):
            conflicting_nome = exc.params.get('nome')  # Ajuste para o nome do seu campo único
            return JSONResponse(
                status_code=status.HTTP_303_SEE_OTHER,
                content={"message": f"Já existe um centro de treinamento com o nome: {conflicting_nome}"}
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

    return centro_treinamento_out


@router.get(
        "/",
        summary="Consultar todos centros de treinamento0",
        status_code=status.HTTP_200_OK,
        response_model=list[CentroTreinamentoOut],
)
async def query(
    db_session: DatabaseDependency, 
    page: int = 1, 
    size: int = 10
) -> Page[CentroTreinamentoOut]:
    centros_query = select(CentroTreinamentoModel)
    centros = await db_session.execute(centros_query)

    return paginate(
        [CentroTreinamentoOut.model_validate(centro) for centro in centros.scalars().all()], 
        page, 
        size
    )

@router.get(
        "/{id}",
        summary="Consultar um centro de treinamento pelo idd",
        status_code=status.HTTP_200_OK,
        response_model=CentroTreinamentoOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> list[CentroTreinamentoOut]:
    centro_treinamento_out: CentroTreinamentoOut = (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Centro de trinamento não encontrado no id: {id}'
        )

    return centro_treinamento_out

add_pagination(router) 