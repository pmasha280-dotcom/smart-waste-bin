import random
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Compartment, FillHistory
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimulationService:
    def __init__(self):
        self.is_running = False
        self.task = None
    
    async def start_simulation(self):
        """Запуск симуляции заполнения урн"""
        if self.is_running:
            logger.warning("Симуляция уже запущена")
            return
        
        self.is_running = True
        logger.info("Симуляция заполнения урн запущена")
        
        while self.is_running:
            try:
                await self.update_all_compartments()
                await asyncio.sleep(1800)
            except Exception as e:
                logger.error(f"Ошибка в симуляции: {e}")
                await asyncio.sleep(60)
    
    async def update_all_compartments(self):
        """Обновление уровня заполнения всех отсеков"""
        db = SessionLocal()
        try:
            compartments = db.query(Compartment).all()
            
            if not compartments:
                logger.warning("Нет отсеков для обновления")
                return
            
            for compartment in compartments:
                new_level = self.calculate_new_fill_level(compartment)
                
                if new_level != compartment.fill_level:
                    old_level = compartment.fill_level
                    compartment.fill_level = new_level
                    
                    if abs(new_level - old_level) >= 1:
                        history = FillHistory(
                            bin_id=compartment.bin_id,
                            compartment_id=compartment.id,
                            fill_level=new_level,
                            recorded_at=datetime.now()
                        )
                        db.add(history)
                        logger.info(f"Отсек {compartment.id} обновлен: {old_level}% -> {new_level}%")
            
            db.commit()
            logger.info(f"Обновлено {len(compartments)} отсеков")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении: {e}")
            db.rollback()
        finally:
            db.close()
    
    def calculate_new_fill_level(self, compartment):
        """Расчет нового уровня заполнения"""
        current_level = compartment.fill_level
        
        if current_level <= 5:
            increment = random.uniform(4, 8)
        else:
            base_increment = 6.0
            variation = random.uniform(0.7, 1.3)
            increment = base_increment * variation
            
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 12 or 14 <= current_hour <= 18:
                increment *= random.uniform(1.2, 1.5)
            elif 22 <= current_hour or current_hour <= 6:
                increment *= random.uniform(0.3, 0.7)
        
        new_level = current_level + increment
        
        if new_level >= 100:
            new_level = 100
            
        if new_level < 0:
            new_level = 0
            
        return round(new_level, 1)
    
    async def stop_simulation(self):
        """Остановка симуляции"""
        self.is_running = False
        if self.task:
            self.task.cancel()
        logger.info("Симуляция остановлена")

simulation_service = SimulationService()
