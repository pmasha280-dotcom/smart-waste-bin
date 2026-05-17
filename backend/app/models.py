from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    WORKER = "worker"
    GUEST = "guest"

class WasteType(str, enum.Enum):
    GENERAL = "general"
    PLASTIC = "plastic"
    PAPER = "paper"
    GLASS = "glass"
    ORGANIC = "organic"

class BinStatus(str, enum.Enum):
    EMPTY = "empty"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    FULL = "full"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Nullable for demo user
    role = Column(Enum(UserRole), default=UserRole.WORKER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    cleanings = relationship("CleaningLog", back_populates="worker")

class Floor(Base):
    __tablename__ = "floors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    level = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bins = relationship("Bin", back_populates="floor", cascade="all, delete-orphan")

class Bin(Base):
    __tablename__ = "bins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    identifier = Column(String(50), unique=True, index=True, nullable=False)
    floor_id = Column(Integer, ForeignKey("floors.id", ondelete="CASCADE"), nullable=False)
    position_x = Column(Float, nullable=False)  # X coordinate on map
    position_y = Column(Float, nullable=False)  # Y coordinate on map
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    floor = relationship("Floor", back_populates="bins")
    compartments = relationship("Compartment", back_populates="bin", cascade="all, delete-orphan")
    fill_history = relationship("FillHistory", back_populates="bin", cascade="all, delete-orphan")

class Compartment(Base):
    __tablename__ = "compartments"
    
    id = Column(Integer, primary_key=True, index=True)
    bin_id = Column(Integer, ForeignKey("bins.id", ondelete="CASCADE"), nullable=False)
    waste_type = Column(Enum(WasteType), nullable=False)
    fill_level = Column(Integer, default=0)  # 0-100 percent
    max_capacity = Column(Integer, default=100)  # In liters
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    bin = relationship("Bin", back_populates="compartments")
    fill_history = relationship("FillHistory", back_populates="compartment", cascade="all, delete-orphan")

class FillHistory(Base):
    __tablename__ = "fill_history"
    
    id = Column(Integer, primary_key=True, index=True)
    bin_id = Column(Integer, ForeignKey("bins.id", ondelete="CASCADE"), nullable=False)
    compartment_id = Column(Integer, ForeignKey("compartments.id", ondelete="CASCADE"), nullable=False)
    fill_level = Column(Integer, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    bin = relationship("Bin", back_populates="fill_history")
    compartment = relationship("Compartment", back_populates="fill_history")

class CleaningLog(Base):
    __tablename__ = "cleaning_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    bin_id = Column(Integer, ForeignKey("bins.id", ondelete="CASCADE"), nullable=False)
    worker_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    cleaned_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    
    # Relationships
    bin = relationship("Bin")
    worker = relationship("User", back_populates="cleanings")


class InviteKey(Base):
    __tablename__ = "invite_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False)  # admin или worker
    used_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[used_by])