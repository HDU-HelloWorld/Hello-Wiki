from fastapi import APIRouter, status

router = APIRouter(prefix="/compile", tags=["compile"])


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def compile_document() -> dict[str, str]:
    return {"detail": "MVP scaffold only, compile workflow is not implemented."}
