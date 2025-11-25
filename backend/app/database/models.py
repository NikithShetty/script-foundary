"""Database models for SQLAlchemy."""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.database.connection import Base


class Script(Base):
    """Model for generated scripts."""
    
    __tablename__ = "scripts"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), nullable=False)
    year_level = Column(String(50), nullable=False)
    learning_objective = Column(Text, nullable=False)
    subject = Column(String(100))
    generated_script = Column(Text)
    script_data = Column(JSON)  # Full pipeline output
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CurriculumOutcome(Base):
    """Model for cached curriculum outcomes."""
    
    __tablename__ = "curriculum_outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)
    description = Column(Text)
    year_level = Column(String(50))
    subject = Column(String(100))
    outcome_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Misconception(Base):
    """Model for misconceptions database."""
    
    __tablename__ = "misconceptions"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255), index=True)
    misconception = Column(Text, nullable=False)
    correction = Column(Text, nullable=False)
    subject = Column(String(100))
    year_level_range = Column(String(20))  # e.g., "5-8"
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FactCheck(Base):
    """Model for fact-checking results."""
    
    __tablename__ = "fact_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    claim = Column(Text, nullable=False)
    verified = Column(Integer, default=0)  # 0 = false, 1 = true
    confidence = Column(Float)
    sources = Column(JSON)
    script_id = Column(Integer)  # Foreign key to scripts
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PipelineRun(Base):
    """Model for pipeline execution audit trail."""
    
    __tablename__ = "pipeline_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(255))
    year_level = Column(String(50))
    modules_executed = Column(JSON)
    success = Column(Integer, default=1)  # 0 = false, 1 = true
    errors = Column(JSON)
    execution_time = Column(Float)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())



