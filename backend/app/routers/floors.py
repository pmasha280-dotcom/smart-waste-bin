from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import FloorResponse, FloorCreate
from app.models import Floor, Bin
from app.dependencies import get_current_user

router = APIRouter(prefix="/floors", tags=["Floors"])

@router.get("", response_model=List[FloorResponse])
async def get_floors(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    floors = db.query(Floor).order_by(Floor.level).all()
    return floors

@router.get("/{floor_id}/bins")
async def get_bins_by_floor(
    floor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    bins = db.query(Bin).filter(Bin.floor_id == floor_id).all()
    return bins

@router.post("", response_model=FloorResponse)
async def create_floor(
    floor_data: FloorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # Add admin check
):
    floor = Floor(**floor_data.model_dump())
    db.add(floor)
    db.commit()
    db.refresh(floor)
    return floor