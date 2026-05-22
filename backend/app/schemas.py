from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from app.models import UserRole, WasteType, BinStatus

# Auth schemas
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.WORKER

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Floor schemas
class FloorBase(BaseModel):
    name: str
    level: int

class FloorCreate(FloorBase):
    pass

class FloorResponse(FloorBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Bin schemas
class CompartmentResponse(BaseModel):
    id: int
    waste_type: WasteType
    fill_level: int
    max_capacity: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

class BinResponse(BaseModel):
    id: int
    name: str
    identifier: str
    floor_id: int
    position_x: float
    position_y: float
    created_at: datetime
    updated_at: Optional[datetime]
    compartments: List[CompartmentResponse] = []
    status: BinStatus
    
    class Config:
        from_attributes = True

class BinCreate(BaseModel):
    name: str
    identifier: str
    floor_id: int
    position_x: float
    position_y: float
    compartments: List[dict]  # [{waste_type: "general", max_capacity: 100}]

class BinUpdate(BaseModel):
    name: Optional[str] = None
    identifier: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None

# Statistics schemas
class FillHistoryResponse(BaseModel):
    id: int
    bin_id: int
    compartment_id: int
    fill_level: int
    recorded_at: datetime
    
    class Config:
        from_attributes = True

class CleaningLogResponse(BaseModel):
    id: int
    bin_id: int
    worker_id: Optional[int]
    cleaned_at: datetime
    notes: Optional[str]
    
    class Config:
        from_attributes = True

class BinStatistics(BaseModel):
    bin_id: int
    bin_name: str
    average_fill_level: float
    cleaning_frequency: int  # times per week
    last_cleaned: Optional[datetime]
    needs_attention: bool

class GeneralStatistics(BaseModel):
    total_bins: int
    total_compartments: int
    average_fill_rate: float
    bins_needing_attention: List[BinStatistics]
    waste_type_distribution: dict
    hourly_activity: dict

# Clean request
class CleanRequest(BaseModel):
    floorId: int
    timestamp: datetime
    notes: Optional[str] = None


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    invite_key: str 

class InviteKeyCreate(BaseModel):
    role: UserRole
    expires_days: Optional[int] = 7  

class InviteKeyResponse(BaseModel):
    key: str
    role: UserRole
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True
class CompartmentCreate(BaseModel):
    waste_type: WasteType
    max_capacity: int = 100

class CompartmentResponse(BaseModel):
    id: int
    waste_type: WasteType
    fill_level: int
    max_capacity: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

class BinCreate(BaseModel):
    name: str
    identifier: str
    floor_id: int
    position_x: float
    position_y: float
    compartments: List[CompartmentCreate] = []
