from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.database import get_db
from app.schemas import GeneralStatistics, BinStatistics
from app.models import Bin, Compartment, FillHistory, CleaningLog, UserRole, WasteType
from app.dependencies import get_current_user, get_current_admin, get_current_worker_or_admin

router = APIRouter(prefix="/statistics", tags=["Statistics"])

@router.get("")
async def get_statistics(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_worker_or_admin)
):
    start_date = datetime.now() - timedelta(days=days)
    
    total_bins = db.query(Bin).count()
    total_compartments = db.query(Compartment).count()
    
    # Get bins needing attention (fill level > 80%)
    bins_needing = []
    bins = db.query(Bin).all()
    
    for bin in bins:
        avg_fill = db.query(Compartment).filter(Compartment.bin_id == bin.id).with_entities(
            db.func.avg(Compartment.fill_level)
        ).scalar() or 0
        
        cleaning_count = db.query(CleaningLog).filter(
            CleaningLog.bin_id == bin.id,
            CleaningLog.cleaned_at >= start_date
        ).count()
        
        last_cleaned = db.query(CleaningLog).filter(
            CleaningLog.bin_id == bin.id
        ).order_by(CleaningLog.cleaned_at.desc()).first()
        
        needs_attention = avg_fill > 80
        
        if needs_attention or current_user.role == UserRole.ADMIN:
            bins_needing.append(BinStatistics(
                bin_id=bin.id,
                bin_name=bin.name,
                average_fill_level=avg_fill,
                cleaning_frequency=cleaning_count,
                last_cleaned=last_cleaned.cleaned_at if last_cleaned else None,
                needs_attention=needs_attention
            ))
    
    # Waste type distribution
    waste_dist = {}
    compartments = db.query(Compartment).all()
    for comp in compartments:
        waste_dist[comp.waste_type.value] = waste_dist.get(comp.waste_type.value, 0) + comp.fill_level
    
    # Hourly activity (last 7 days)
    hourly = {}
    for hour in range(24):
        hourly[str(hour)] = 0
    
    cleanings = db.query(CleaningLog).filter(
        CleaningLog.cleaned_at >= start_date
    ).all()
    
    for cleaning in cleanings:
        hour = cleaning.cleaned_at.hour
        hourly[str(hour)] += 1
    
    # Calculate average fill rate
    fill_history = db.query(FillHistory).filter(
        FillHistory.recorded_at >= start_date
    ).all()
    
    avg_fill_rate = 0
    if fill_history:
        avg_fill_rate = sum(f.fill_level for f in fill_history) / len(fill_history)
    
    return GeneralStatistics(
        total_bins=total_bins,
        total_compartments=total_compartments,
        average_fill_rate=avg_fill_rate,
        bins_needing_attention=bins_needing[:10],  # Top 10
        waste_type_distribution=waste_dist,
        hourly_activity=hourly
    )

@router.get("/export")
async def export_statistics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    # Export logic here - would return CSV/Excel
    fill_history = db.query(FillHistory).filter(
        FillHistory.recorded_at.between(start_date, end_date)
    ).all()
    
    return {
        "data": fill_history,
        "count": len(fill_history)
    }