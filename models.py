from sqlalchemy import Column, Integer, String, Text, Float, Date, JSON, ForeignKey, DateTime #baru (FK dan DateTime)
from sqlalchemy.orm import relationship #baru
from database import Base
from datetime import datetime #baru
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ModelConfiguration(Base):
    __tablename__ = "model_configuration"  # Nama tabel di database

    # Define columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    modelId = Column(String(255), index=True) 
    namaModel = Column(String(255), index=True)  # namaModel sebagai primary key
    Instruksi = Column(String(255), nullable=False)  # Instruksi kolom teks
    verFine_tuning = Column(String(255), nullable=False)  # versi fine-tuning
    vectorId = Column(String(255), nullable=False)  # versi fine-tuning
    temp = Column(Float, nullable=False)  # Temperature sebagai float
    tanggal = Column(Date, nullable=False)  # Tanggal sebagai tipe Date

class fineTuning(Base):
    __tablename__ = "fine_tuning"  # Nama tabel di database

    # Define columns
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    jobId = Column(String(255), nullable=False)  # Nama Suffix sebagai string
    namaSuffix = Column(String(255), nullable=False)  # Nama Suffix sebagai string
    deskripsi = Column(String(255), nullable=False)  # Deskripsi sebagai string
    dataset = Column(JSON(String), nullable=False)  # Dataset sebagai json of strings
    modelOutput = Column(String(255), nullable=True)  # Model output sebagai string
    epocs = Column(Integer, nullable=False)  # Epocs dengan integer
    date = Column(Date, nullable=False)  # Tanggal sebagai tipe Date


# Tabel vector_stores
class VectorStore(Base):
    __tablename__ = 'vector_stores'

    id = Column(Integer, primary_key=True, index=True)
    vectorId = Column(String(255), unique=True, index=True)
    namaVector = Column(String(255), index=True)
    deskripsi = Column(String(255))
    date = Column(DateTime, default=datetime.utcnow)

    # Relasi ke sub_vector_stores
    sub_vectors = relationship("SubVectorStore", back_populates="vector_store")


# Tabel sub_vector_stores
class SubVectorStore(Base):
    __tablename__ = 'sub_vector_stores'

    id = Column(Integer, primary_key=True, index=True)
    vectorId = Column(String(255), ForeignKey('vector_stores.vectorId'))
    filesId = Column(String(255), index=True)
    deskripsi = Column(String(255))
    topik = Column(String(255))
    path = Column(String(255))
    dataset = Column(JSON(String))  # Dataset sebagai json of strings
    date = Column(DateTime, default=datetime.utcnow)

    # Relasi ke vector_stores
    vector_store = relationship("VectorStore", back_populates="sub_vectors")

    #TIMANNN TIMAN TIMAN

