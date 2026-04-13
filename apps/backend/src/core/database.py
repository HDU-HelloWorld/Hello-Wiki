from typing import Annotated

from fastapi import Depends
from sqlmodel import Session


def get_session() -> Session:
    raise NotImplementedError("Database session wiring is intentionally not implemented in MVP scaffold.")


DBSession = Annotated[Session, Depends(get_session)]
