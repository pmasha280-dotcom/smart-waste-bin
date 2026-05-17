from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Compartment, FillHistory, Bin
from app.dependencies import get_current_admin
from app.services.simulation_service import simulation_service
import random

router = APIRouter(prefix="/simulation", tags=["Simulation"])

@router.post("/start")
async def start_simulation(
    current_user = Depends(get_current_admin)
):
    """Запуск автоматической симуляции заполнения"""
    if simulation_service.is_running:
        return {"message": "Симуляция уже запущена"}
    
    # Запускаем в фоне
    import asyncio
    asyncio.create_task(simulation_service.start_simulation())
    
    return {"message": "Симуляция запущена"}

@router.post("/stop")
async def stop_simulation(
    current_user = Depends(get_current_admin)
):
    """Остановка симуляции"""
    await simulation_service.stop_simulation()
    return {"message": "Симуляция остановлена"}

@router.post("/initialize-data")
async def initialize_demo_data(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """Инициализация демонстрационных данных"""
    
    # Проверяем, есть ли уже данные
    bins_count = db.query(Bin).count()
    if bins_count > 0:
        return {"message": f"Данные уже существуют (урн: {bins_count})"}
    
    # Создаем этажи
    from app.models import Floor
    floors = [
        Floor(name="Первый этаж", level=1),
        Floor(name="Второй этаж", level=2),
        Floor(name="Третий этаж", level=3)
    ]
    for floor in floors:
        db.add(floor)
    db.commit()
    
    # Создаем урны
    bins_data = [
        {"name": "Урна А1", "identifier": "B001", "floor_id": 1, "position_x": 15, "position_y": 20},
        {"name": "Урна А2", "identifier": "B002", "floor_id": 1, "position_x": 45, "position_y": 35},
        {"name": "Урна B1", "identifier": "B003", "floor_id": 1, "position_x": 75, "position_y": 60},
        {"name": "Урна С1", "identifier": "B004", "floor_id": 2, "position_x": 25, "position_y": 30},
        {"name": "Урна С2", "identifier": "B005", "floor_id": 2, "position_x": 60, "position_y": 25},
        {"name": "Урна D1", "identifier": "B006", "floor_id": 3, "position_x": 35, "position_y": 40},
    ]
    
    from app.models import Bin, Compartment
    from app.schemas import WasteType
    
    bins = []
    for bin_data in bins_data:
        bin_obj = Bin(**bin_data)
        db.add(bin_obj)
        db.flush()
        bins.append(bin_obj)
    
    # Создаем отсеки для каждой урны с начальным уровнем 10-30%
    compartments_config = [
        # Урна 1
        [(WasteType.GENERAL, 100), (WasteType.PLASTIC, 80)],
        # Урна 2
        [(WasteType.GENERAL, 100), (WasteType.PAPER, 70)],
        # Урна 3
        [(WasteType.GENERAL, 100), (WasteType.ORGANIC, 60)],
        # Урна 4
        [(WasteType.GENERAL, 100), (WasteType.PLASTIC, 80)],
        # Урна 5
        [(WasteType.GENERAL, 100), (WasteType.GLASS, 50)],
        # Урна 6
        [(WasteType.GENERAL, 100), (WasteType.PAPER, 70)],
    ]
    
    for i, bin_obj in enumerate(bins):
        for waste_type, max_capacity in compartments_config[i]:
            # Случайный начальный уровень 10-30%
            initial_level = random.uniform(10, 30)
            compartment = Compartment(
                bin_id=bin_obj.id,
                waste_type=waste_type,
                fill_level=initial_level,
                max_capacity=max_capacity
            )
            db.add(compartment)
            
            # Добавляем историю за последние 7 дней
            for days_ago in range(7, 0, -1):
                recorded_at = datetime.now() - timedelta(days=days_ago)
                # Симулируем изменение уровня
                simulated_level = max(0, min(100, initial_level + random.uniform(-20, 20)))
                history = FillHistory(
                    bin_id=bin_obj.id,
                    compartment_id=compartment.id,
                    fill_level=simulated_level,
                    recorded_at=recorded_at
                )
                db.add(history)
    
    db.commit()
    
    return {
        "message": "Демо-данные успешно созданы",
        "floors": len(floors),
        "bins": len(bins),
        "compartments": sum(len(config) for config in compartments_config)
    }

@router.get("/status")
async def get_simulation_status(
    current_user = Depends(get_current_admin)
):
    """Получить статус симуляции"""
    return {
        "is_running": simulation_service.is_running,
        "message": "Симуляция активна" if simulation_service.is_running else "Симуляция остановлена"
    }