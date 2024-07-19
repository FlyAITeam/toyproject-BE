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

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

# Update User
def update_user(db: Session, user_id: int, update_data: dict):
    db.query(User).filter(User.userId == user_id).update(update_data)
    db.commit()
    return db.query(User).filter(User.userId == user_id).first()

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
        contentType=image.contentType,
        path=image.path
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

# Update Image
def update_image(db: Session, image_id: int, update_data: dict):
    db.query(Image).filter(Image.imageId == image_id).update(update_data)
    db.commit()
    return db.query(Image).filter(Image.imageId == image_id).first()

# Delete Image
def delete_image(db: Session, image_id: int):
    db.query(Image).filter(Image.imageId == image_id).delete()
    db.commit()
    return {"message": "Image deleted successfully"}

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

# Update Disability
def update_disability(db: Session, disability_id: int, update_data: dict):
    db.query(Disability).filter(Disability.disabilityId == disability_id).update(update_data)
    db.commit()
    return db.query(Disability).filter(Disability.disabilityId == disability_id).first()

# Delete Disability
def delete_disability(db: Session, disability_id: int):
    db.query(Disability).filter(Disability.disabilityId == disability_id).delete()
    db.commit()
    return {"message": "Disability deleted successfully"}

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

# Read Log
def get_log(db: Session, log_id: int):
    return db.query(Log).filter(Log.logId == log_id).first()

def get_logs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Log).offset(skip).limit(limit).all()

# Update Log
def update_log(db: Session, log_id: int, update_data: dict):
    db.query(Log).filter(Log.logId == log_id).update(update_data)
    db.commit()
    return db.query(Log).filter(Log.logId == log_id).first()

# Delete Log
def delete_log(db: Session, log_id: int):
    db.query(Log).filter(Log.logId == log_id).delete()
    db.commit()
    return {"message": "Log deleted successfully"}

# Create Reform
def create_reform(db: Session, reform: ReformCreate):
    db_reform = Reform(
        reformType=reform.reformType,
        cloth=reform.cloth,
        target=reform.target,
        trim=reform.trim,
        description=reform.description,
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

# Update Reform
def update_reform(db: Session, guide_id: int, update_data: dict):
    db.query(Reform).filter(Reform.guideId == guide_id).update(update_data)
    db.commit()
    return db.query(Reform).filter(Reform.guideId == guide_id).first()

# Delete Reform
def delete_reform(db: Session, guide_id: int):
    db.query(Reform).filter(Reform.guideId == guide_id).delete()
    db.commit()
    return {"message": "Reform deleted successfully"}
