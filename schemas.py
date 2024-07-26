from pydantic import BaseModel
from typing import List

# User
class UserBase(BaseModel):
    loginId: str
    username: str

class UserCreate(UserBase):
    password: str
    disabilities: List[str]

class UserCreateRequest(BaseModel):
    loginId: str
    password: str
    name: str
    disabilities: List[str]
    
class UserCreateResponse(BaseModel):
    name: str
    message: str
    userId: int
    
class User(UserBase):
    userId: int
    disabilities: List["Disability"] = []
    images: List["Image"] = []
    logs: List["Log"] = []

    class Config:
        from_attributes = True
        
class NameUpdateRequest(BaseModel):
    name: str
# login
class LoginRequest(BaseModel):
    loginId: str
    password: str
        
# Reform
class ReformBase(BaseModel):
    reformType: str
    cloth: str
    fileName: str
    contentType: str
    path: str

class ReformCreate(ReformBase):
    pass

class Reform(ReformBase):
    guideId: int

    class Config:
        from_attributes = True
        
# Log
class LogBase(BaseModel):
    userId: int
    imageId: int
    guideId: int

class LogCreate(LogBase):
    pass

class Log(LogBase):
    logId: int

    class Config:
        from_attributes = True
        
# Image
class ImageBase(BaseModel):
    fileName: str
    contentType: str
    path: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    imageId: int
    userId: int

    class Config:
        from_attributes = True
        
# Disability
class DisabilityBase(BaseModel):
    obstacle: str

class DisabilityCreate(DisabilityBase):
    pass

class Disability(DisabilityBase):
    disabilityId: int
    userId: int

    class Config:
        from_attributes = True
        
class DisabilityUpdateRequest(BaseModel):
    disabilities: list[str]