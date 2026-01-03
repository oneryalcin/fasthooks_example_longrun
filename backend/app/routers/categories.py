from fastapi import APIRouter
from app.schemas import CategoryEnum

router = APIRouter()

@router.get("")
async def get_categories():
    """Get all available expense categories"""
    categories = [
        {"name": cat.value, "value": cat.value}
        for cat in CategoryEnum
    ]
    return {"categories": categories}
