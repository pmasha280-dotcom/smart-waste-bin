from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import BinResponse, BinCreate, BinUpdate, CleanRequest
from app.models import Bin, Compartment, CleaningLog, UserRole, BinStatus
from app.dependencies import get_current_user, get_current_admin, get_current_worker_or_admin, get_demo_user
from app.services.bin_service import BinService

router = APIRouter(prefix="/bins", tags=["Bins"])

@router.get("", response_model=List[BinResponse])
async def get_bins(
    floor_id: int = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Bin)
    if floor_id:
        query = query.filter(Bin.floor_id == floor_id)
    
    bins = query.all()
    return [BinService.enrich_bin_with_status(bin, db) for bin in bins]

@router.get("/{bin_id}", response_model=BinResponse)
async def get_bin(
    bin_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    bin = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    return BinService.enrich_bin_with_status(bin, db)

@router.post("", response_model=BinResponse)
async def create_bin(
    bin_data: BinCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    # Check if bin with same identifier exists
    existing = db.query(Bin).filter(Bin.identifier == bin_data.identifier).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bin identifier already exists")
    
    # Create bin
    bin = Bin(
        name=bin_data.name,
        identifier=bin_data.identifier,
        floor_id=bin_data.floor_id,
        position_x=bin_data.position_x,
        position_y=bin_data.position_y
    )
    db.add(bin)
    db.commit()
    db.refresh(bin)
    
    # Create compartments
    for comp_data in bin_data.compartments:
        compartment = Compartment(
            bin_id=bin.id,
            waste_type=comp_data.get("waste_type"),
            max_capacity=comp_data.get("max_capacity", 100)
        )
        db.add(compartment)
    
    db.commit()
    db.refresh(bin)
    
    return BinService.enrich_bin_with_status(bin, db)

@router.put("/{bin_id}", response_model=BinResponse)
async def update_bin(
    bin_id: int,
    bin_data: BinUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    bin = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    for field, value in bin_data.model_dump(exclude_unset=True).items():
        setattr(bin, field, value)
    
    db.commit()
    db.refresh(bin)
    
    return BinService.enrich_bin_with_status(bin, db)

@router.delete("/{bin_id}")
async def delete_bin(
    bin_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    bin = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    db.delete(bin)
    db.commit()
    
    return {"message": "Bin deleted successfully"}

@router.post("/{bin_id}/clean")
async def clean_bin(
    bin_id: int,
    clean_request: CleanRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_worker_or_admin)
):
    bin = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    # Reset all compartments fill levels to 0
    for compartment in bin.compartments:
        compartment.fill_level = 0
    
    # Log cleaning
    cleaning_log = CleaningLog(
        bin_id=bin_id,
        worker_id=current_user.id if current_user.role != UserRole.GUEST else None,
        notes=clean_request.notes
    )
    db.add(cleaning_log)
    db.commit()
    
    return {"message": "Bin cleaned successfully", "bin": BinService.enrich_bin_with_status(bin, db)}



@router.get("/{bin_id}/history")
async def get_bin_history(
    bin_id: int,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Получить историю заполнения урны за указанное количество дней"""
    bin_obj = db.query(Bin).filter(Bin.id == bin_id).first()
    if not bin_obj:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    start_date = datetime.now() - timedelta(days=days)
    
    history = db.query(FillHistory).filter(
        FillHistory.bin_id == bin_id,
        FillHistory.recorded_at >= start_date
    ).order_by(FillHistory.recorded_at).all()
    
    # Группируем по отсекам
    result = {}
    for record in history:
        if record.compartment_id not in result:
            result[record.compartment_id] = {
                "compartment_id": record.compartment_id,
                "waste_type": record.compartment.waste_type.value,
                "data": []
            }
        result[record.compartment_id]["data"].append({
            "date": record.recorded_at.isoformat(),
            "fill_level": record.fill_level
        })
    
    return list(result.values())