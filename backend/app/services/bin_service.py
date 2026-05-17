from sqlalchemy.orm import Session
from app.models import Bin, BinStatus

class BinService:
    @staticmethod
    def calculate_bin_status(bin_obj: Bin) -> BinStatus:
        if not bin_obj.compartments:
            return BinStatus.EMPTY
        
        # Calculate average fill level across compartments
        avg_fill = sum(c.fill_level for c in bin_obj.compartments) / len(bin_obj.compartments)
        
        if avg_fill <= 10:
            return BinStatus.EMPTY
        elif avg_fill <= 30:
            return BinStatus.LOW
        elif avg_fill <= 70:
            return BinStatus.MEDIUM
        elif avg_fill <= 90:
            return BinStatus.HIGH
        else:
            return BinStatus.FULL
    
    @staticmethod
    def enrich_bin_with_status(bin_obj: Bin, db: Session):
        """Add status field to bin object"""
        bin_obj.status = BinService.calculate_bin_status(bin_obj)
        return bin_obj