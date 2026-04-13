from fastapi import APIRouter, status

router = APIRouter(prefix="/qa", tags=["qa"])


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def ask_question() -> dict[str, str]:
    return {"detail": "MVP scaffold only, QA workflow is not implemented."}
