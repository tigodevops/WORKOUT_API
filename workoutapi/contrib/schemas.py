from typing import Annotated
from pydantic import UUID4, BaseModel, Field
from datetime import dateTime

class BaseSchema(BaseModel):
    class config:
        extra = "forbid"
        from_attributes = True

        class OutMixin(BaseModel):
            id: Annotated[UUID4, Field(description="Identificador")]
            created_at: Annotated[dateTime, Field(descripition="Data de criação")]
        