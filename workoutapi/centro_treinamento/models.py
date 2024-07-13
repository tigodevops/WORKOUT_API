from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship 
from workoutapi.contrib.models import BaseModel


class CentroTreinamentoModel(BaseModel):
    __tablename__ = "centros_treinamento"

    pk_id: Mapped[int] = mapped_column (Integer, primary_key=True)
    nome: Mapped[str] = mapped_column (String(50), unique=True, nullable=False)
    endereco: Mapped[str] = mapped_column (String(60), nullable=False)
    proprietario: Mapped[str] = mapped_column (String(30), nullable=False)
    atleta: Mapped["atletaModel"] = relationship(back_populates="centros_treinamento")
    