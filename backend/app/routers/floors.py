from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import FloorResponse, FloorCreate
from app.models import Floor, Bin

router = APIRouter(prefix="/floors", tags=["Floors"])

@router.get("", response_model=List[FloorResponse])
async def get_floors(
    db: Session = Depends(get_db)
):
    """Публичный эндпоинт - доступен без авторизации"""
    floors = db.query(Floor).order_by(Floor.level).all()
    return floors

@router.get("/{floor_id}/bins")
async def get_bins_by_floor(
    floor_id: int,
    db: Session = Depends(get_db)
):
    """Публичный эндпоинт - доступен без авторизации"""
    bins = db.query(Bin).filter(Bin.floor_id == floor_id).all()
    return bins
