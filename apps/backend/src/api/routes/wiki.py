from fastapi import APIRouter, status

router = APIRouter(prefix="/wiki", tags=["wiki"])


@router.get("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_wiki_pages() -> dict[str, str]:
    return {"detail": "MVP scaffold only, wiki listing is not implemented."}
