from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from models import User
from schemas import (
    TranslationHistoryListResponse,
    TranslationRequest,
    TranslationResponse,
)
from services.translation_service import TranslationService

router = APIRouter(prefix="/api/v1", tags=["Transliteration & History"])


@router.post(
    "/translate",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Transliterate Uzbek Latin text and record translation history",
    description="Translates old Uzbek Latin to reformed alphabet (Sh->Ş, Ch->Ç, O'->Ō, G'->Ğ) and logs history for authenticated user.",
)
async def translate_text(
    payload: TranslationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TranslationResponse:
    service = TranslationService(db)
    history_record = await service.translate_and_record(
        user_id=current_user.telegram_id,
        original_text=payload.text,
    )
    return TranslationResponse.model_validate(history_record)


@router.get(
    "/history",
    response_model=TranslationHistoryListResponse,
    summary="Get translation history for authenticated user",
    description="Returns a paginated list of previous translations sorted newest first.",
)
async def get_translation_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TranslationHistoryListResponse:
    service = TranslationService(db)
    items, total = await service.get_user_history(
        user_id=current_user.telegram_id,
        page=page,
        per_page=per_page,
    )
    return TranslationHistoryListResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=items,
    )


@router.delete(
    "/history/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a translation history item",
    description="Deletes a specific translation record belonging to the authenticated user.",
)
async def delete_translation_history_item(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TranslationService(db)
    deleted = await service.delete_user_history_item(
        user_id=current_user.telegram_id,
        history_id=history_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found",
        )
    return None
