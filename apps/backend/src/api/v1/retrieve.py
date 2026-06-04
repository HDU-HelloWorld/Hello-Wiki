from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.assemblers.retrieve import to_search_knowledge_command, to_search_knowledge_response
from src.api.deps import (
    get_domain_tag_tree_handler,
    get_list_retrieve_domains_handler,
    get_required_workspace_id,
    get_search_knowledge_handler,
)
from src.api.schemas.retrieve import (
    DomainTagTreeResponse,
    RetrieveDomainItem,
    RetrieveDomainsResponse,
    SearchKnowledgeRequest,
    SearchKnowledgeResponse,
)
from src.application.retrieve.catalog_handlers import (
    GetDomainTagTreeHandler,
    ListRetrieveDomainsHandler,
)
from src.application.retrieve.handlers import SearchKnowledgeHandler
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/retrieve", tags=["retrieve"])


@router.get("/domains", response_model=RetrieveDomainsResponse)
async def list_retrieve_domains(
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: ListRetrieveDomainsHandler = Depends(get_list_retrieve_domains_handler),
) -> RetrieveDomainsResponse:
    items, count = await handler.handle(workspace_id)
    logger.info(
        "retrieve.domains workspace=%s domain_count=%s ids=%s",
        workspace_id,
        count,
        [item["id"] for item in items],
    )
    return RetrieveDomainsResponse(
        domains=[RetrieveDomainItem.model_validate(item) for item in items],
        domain_count=count,
    )


@router.get("/domains/{domain}/tag-tree", response_model=DomainTagTreeResponse)
async def get_domain_tag_tree(
    domain: str,
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: GetDomainTagTreeHandler = Depends(get_domain_tag_tree_handler),
) -> DomainTagTreeResponse:
    tag_tree = await handler.handle(workspace_id, domain)
    if tag_tree is None:
        logger.warning(
            "retrieve.tag_tree not_found workspace=%s domain=%s",
            workspace_id,
            domain,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"domain not found: {domain}",
        )
    logger.info(
        "retrieve.tag_tree workspace=%s domain=%s tree_chars=%s",
        workspace_id,
        domain,
        len(tag_tree),
    )
    return DomainTagTreeResponse(domain=domain, tag_tree=tag_tree)


@router.post("/search", response_model=SearchKnowledgeResponse)
async def search_knowledge(
    request: SearchKnowledgeRequest,
    workspace_id: UUID = Depends(get_required_workspace_id),
    handler: SearchKnowledgeHandler = Depends(get_search_knowledge_handler),
) -> SearchKnowledgeResponse:
    hits, degraded = await handler.handle(to_search_knowledge_command(request, workspace_id))
    logger.info(
        "retrieve.search workspace=%s domain=%s top_k=%s hit_count=%s degraded=%s target_tags=%s",
        workspace_id,
        request.domain,
        request.top_k,
        len(hits),
        degraded,
        request.query.target_tags,
    )
    return to_search_knowledge_response(hits, degraded)
