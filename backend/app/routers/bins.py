from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from app.database import get_db
from app.schemas import BinResponse, BinCreate, BinUpdate, CleanRequest
from app.models import Bin, Compartment, CleaningLog, FillHistory, BinStatus
from app.dependencies import get_current_user, get_current_admin, get_current_worker_or_admin
from app.services.bin_service import BinService

router = APIRouter(prefix="/bins", tags=["Bins"])

# Публичные эндпоинты (без авторизации)
@router.get("", response_model=List[BinResponse])
async def get_bins(
    floor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Публичный эндпоинт - доступен без авторизации"""
    query = db.query(Bin)
    if floor_id:
        query = query.filter(Bin.floor_id == floor_id)
    bins = query.all()
    return [BinService.enrich_bin_with_status(bin, db) for bin in bins]

@router.get("/{bin_id}", response_model=BinResponse)
async def get_bin(
    bin_id: int,
    db: Session = Depends(get_db)
):
    """Публичный эндпоинт - доступен без авторизации"""
    bin_obj = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin_obj:
        raise HTTPException(status_code=404, detail="Bin not found")
    return BinService.enrich_bin_with_status(bin_obj, db)

@router.get("/{bin_id}/history")
async def get_bin_history(
    bin_id: int,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Публичный эндпоинт - доступен без авторизации"""
    start_date = datetime.now() - timedelta(days=days)
    history = db.query(FillHistory).filter(
        FillHistory.bin_id == bin_id,
        FillHistory.recorded_at >= start_date
    ).order_by(FillHistory.recorded_at).all()
    return history

# Защищённые эндпоинты (требуют авторизацию)
@router.post("", response_model=BinResponse)
async def create_bin(
    bin_data: BinCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Только для администраторов"""
    # ... код создания урны

@router.put("/{bin_id}", response_model=BinResponse)
async def update_bin(
    bin_id: int,
    bin_data: BinUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Только для администраторов"""
    # ... код обновления

@router.delete("/{bin_id}")
async def delete_bin(
    bin_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Только для администраторов"""
    # ... код удаления

@router.post("/{bin_id}/clean")
async def clean_bin(
    bin_id: int,
    clean_request: CleanRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_worker_or_admin)
):
    """Для работников и администраторов"""
    bin_obj = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin_obj:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    for compartment in bin_obj.compartments:
        compartment.fill_level = 0
    
    cleaning_log = CleaningLog(
        bin_id=bin_id,
        worker_id=current_user.id,
        notes=clean_request.notes
    )
    db.add(cleaning_log)
    db.commit()
    
    return {"message": "Bin cleaned successfully", "bin": BinService.enrich_bin_with_status(bin_obj, db)}
