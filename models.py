from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = 'user'
    
    userId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    loginId = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    
    disabilities = relationship("Disability", back_populates="disabilityUser")
    images = relationship("Image", back_populates="imageUser")
    logs = relationship("Log", back_populates="logUser")
    
class Reform(Base):
    __tablename__ = 'reformGuide'
    
    guideId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reformType = Column(String(100), nullable=False)
    cloth = Column(String(500), nullable=False)
    target = Column(String(500), nullable=False)
    trim = Column(String(500), nullable=False)
    description = Column(String(500), nullable=False)
    fileName = Column(String(255), nullable=False)
    contentType = Column(String(128), nullable=False)
    path = Column(String(255), nullable=False)
    
    reformLog = relationship("Log", back_populates="logReform")
    
class Log(Base):
    __tablename__ = 'log'
    
    logId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('user.userId'))
    imageId = Column(Integer, ForeignKey('image.imageId'))
    guideId = Column(Integer, ForeignKey('reformGuide.guideId'))
    
    logUser = relationship("User", back_populates="logs")
    logImage = relationship("Image", back_populates="imageLog")
    logReform = relationship("Reform", back_populates="reformLog")
    
class Image(Base):
    __tablename__ = 'image'
    
    imageId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('user.userId'))
    fileName = Column(String(255), nullable=False)
    contentType = Column(String(128), nullable=False)
    path = Column(String(255), nullable=False)
    
    imageUser = relationship("User", back_populates="images")
    imageLog = relationship("Log", back_populates="logImage")
    
class Disability(Base):
    __tablename__ = 'disability'
    
    disabilityId = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('user.userId'))
    obstacle = Column(String(255), nullable=False)
    
    disabilityUser = relationship("User", back_populates="disabilities")