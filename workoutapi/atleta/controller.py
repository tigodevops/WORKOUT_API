from datetime import datetime
from uuid import uuid4
from fastapi import FastApi, APIRouter, Body, HTTPException, status
from fastapi_pagination import Page, add_pagination, paginate
from pydantic import UUID4
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, ProgrammingError
from psycopg2.errors import UniqueViolation


from workoutapi.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workoutapi.atleta.models import AtletaModel
from categorias.models import CategoriaModel
from workoutapi.centro_treinamento.models import CentroTreinamentoModel

from workoutapi.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
        "/",
        summary="Criar um novo atleta",
        status_code=status.HTTP_201_CREATED,
        response_model=AtletaOut 
)
async def post(
    db_session: DatabaseDependency, 
    atleta_in: AtletaIn=Body(...)
):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome


    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'A categoria {categoria_nome} não foi encontrada'
        )
    
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O centro de treinamento {centro_treinamento_nome} não foi encontrado'
        )
    try:
    
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utc(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()

    except IntegrityError as exc:
        if isinstance(exc.orig, UniqueViolation):
            conflicting_cpf = exc.params.get('cpf')
            return JSONResponse(
                status_code=status.HTTP_303_SEE_OTHER,
                content={"message": f"Já existe um atleta cadastrado com o cpf: {conflicting_cpf}"}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Erro de integridade de dados"}
            )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ocorreu um erro ao inserir os dados no banco'
        )

    return atleta_out

@router.get(
        "/",
        summary="Consultar todos os Atletas",
        status_code=status.HTTP_200_OK,
        response_model=list[AtletaOut],
)
async def query(db_session: DatabaseDependency, page: int = 1, size: int = 10) -> Page[AtletaOut]:
    atletas_query = select(AtletaModel)
    atletas = await db_session.execute(atletas_query)

    return paginate([AtletaOut.model_validate(atleta) for atleta in atletas.scalars().all()], page, size)

add_pagination(router) 

@router.get(
        "/{id}",
        summary="Consultar um atleta pelo id",
        status_code=status.HTTP_200_OK,
        response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(
        select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail=f'Atleta não encontrado no id: {id}'
        )

    return atleta

@router.patch(
        "/{id}",
        summary="Editar um atleta pelo id",
        status_code=status.HTTP_200_OK,
        response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(
        select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail=f'Atleta não encontrado no id: {id}'
        )
    atleta_update = atleta_up.models_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta

@router.get(
        "/{id}",
        summary="Deletar um atleta pelo id",
        status_code=status.HTTP_204_NO_CONTENT,
        
)
async def get(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (await db_session.execute(
        select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    await db_session.delete(atleta)
    await db_session.commit()
