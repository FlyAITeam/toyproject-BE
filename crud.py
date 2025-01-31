from sqlalchemy.orm import Session
from models import User, Image, Disability, Log, Reform
from schemas import UserCreate, ImageCreate, DisabilityCreate, LogCreate, ReformCreate

# Create User
def create_user(db: Session, user: UserCreate):
    db_user = User(
        loginId=user.loginId,
        password=user.password,
        username=user.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    for obstacle in user.disabilities:
        db_disability = Disability(userId=db_user.userId, obstacle=obstacle)
        db.add(db_disability)
    db.commit()
    
    return db_user

# Read User
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.userId == user_id).first()

def get_user_by_loginId(db: Session, loginId: str):
    return db.query(User).filter(User.loginId == loginId).first()

# Update User
def update_user_name(db: Session, user_id: int, new_name: str):
    user = db.query(User).filter(User.userId == user_id).first()
    if user:
        user.username = new_name
        db.commit()
        return user
    return None

# Delete User
def delete_user(db: Session, user_id: int):
    db.query(User).filter(User.userId == user_id).delete()
    db.commit()
    return {"message": "User deleted successfully"}

# Create Image
def create_image(db: Session, image: ImageCreate, user_id: int):
    db_image = Image(
        userId=user_id,
        fileName=image.fileName,
        path=image.path,
        contentType=image.contentType
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

# Read Image
def get_image(db: Session, image_id: int):
    return db.query(Image).filter(Image.imageId == image_id).first()

def get_images(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Image).offset(skip).limit(limit).all()

# Create Disability
def create_disability(db: Session, disability: DisabilityCreate, user_id: int):
    db_disability = Disability(
        userId=user_id,
        obstacle=disability.obstacle
    )
    db.add(db_disability)
    db.commit()
    db.refresh(db_disability)
    return db_disability

# Read Disability
def get_disability(db: Session, disability_id: int):
    return db.query(Disability).filter(Disability.disabilityId == disability_id).first()

def get_disabilities(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Disability).offset(skip).limit(limit).all()

# Create Log
def create_log(db: Session, log: LogCreate, user_id: int, image_id: int, guide_id: int):
    db_log = Log(
        userId=user_id,
        imageId=image_id,
        guideId=guide_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# Update Disability
def update_user_disabilities(db: Session, user_id: int, disabilities: list[str]):
    # 기존 장애 목록 삭제
    db.query(Disability).filter(Disability.userId == user_id).delete()
    
    # 새로운 장애 목록 추가
    for obstacle in disabilities:
        db_disability = Disability(userId=user_id, obstacle=obstacle)
        db.add(db_disability)
    
    db.commit()
    
# Read Log
def get_log(db: Session, log_id: int):
    return db.query(Log).filter(Log.logId == log_id).first()

def get_logs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Log).offset(skip).limit(limit).all()

def get_user_logs(db: Session, user_id: int):
    return db.query(Log).filter(Log.userId == user_id).all()

# Create Reform
def create_reform(db: Session, reform: ReformCreate):
    db_reform = Reform(
        reformType=reform.reformType,
        cloth=reform.cloth,
        fileName=reform.fileName,
        contentType=reform.contentType,
        path=reform.path
    )
    db.add(db_reform)
    db.commit()
    db.refresh(db_reform)
    return db_reform

# Read Reform
def get_reform(db: Session, guide_id: int):
    return db.query(Reform).filter(Reform.guideId == guide_id).first()

def get_reforms(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Reform).offset(skip).limit(limit).all()
