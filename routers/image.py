import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from datetime import timedelta
from schemas import ReformCreate, ImageCreate, LogCreate
from crud import create_image, create_reform, create_log, get_user_by_loginId
from database import get_db
from core.security import decode_access_token
import torch
from ultralytics import YOLO
from PIL import Image
import io

router = APIRouter()

device = 'cuda' if torch.cuda.is_available() else 'cpu'
# 모델 로드
model = YOLO("./routers/best.pt").to(device)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/reform-guide", status_code=status.HTTP_201_CREATED)
async def create_reform_guide(
    image: UploadFile = File(None), 
    access: str = Header(None),
    db: Session = Depends(get_db)
):
    if not access:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"errorMessage": "Access token is null."}
        )
    try:
        try:
            # Access token 검증
            payload = decode_access_token(access)
            if payload is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"errorMessage": "Invalid access token"}
                )
        except Exception as e:
            logger.error(f"Error occurred during token verification: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"errorMessage": "Error during token verification."}
            )

        try:
            user_id = get_user_by_loginId(db, payload["sub"]).userId
        except Exception as e:
            logger.error(f"Error occurred while fetching user by loginId: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"errorMessage": "Error while fetching user information."}
            )
        
        try:
            # 이미지 데이터 읽기
            image_bytes = await image.read()

            # 이미지 저장 경로 설정
            file_location = f"images/{image.filename}"
            with open(file_location, "wb") as file:
                file.write(image_bytes)
        except Exception as e:
            logger.error(f"Error occurred while saving the image: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"errorMessage": "Error while saving the image."}
            )

        try:
            # 이미지 정보 DB에 저장
            image_data = ImageCreate(
                fileName=image.filename,
                contentType=image.content_type,
                path=file_location
            )
            new_image = create_image(db, image_data, user_id)
        except Exception as e:
            logger.error(f"Error occurred while saving image information to the DB: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"errorMessage": "Error while saving image information to the DB."}
            )
        
        try:
            # yolo 모델 사용 코드 --------------------------------
            image_pil = Image.open(io.BytesIO(image_bytes))
            results = model.predict(image_pil)
            for result in results:
                boxes = result.boxes.data.cpu().numpy()
                for box in boxes:
                    x1, y1, x2, y2, score, class_id = box
                    class_name = model.names[int(class_id)]
                    print(f"Detected {class_name} with confidence {score:.2f}. filename: {image.filename}")
                    logger.debug(f"Detected {class_name} with confidence {score:.2f}")
                    cloth_type = class_name
            # ----------------------------------------------------
        except Exception as e:
            logger.error(f"Error occurred while running YOLO model: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"errorMessage": "Error while running YOLO model."}
            )
        
        try:
            # 리폼 가이드 생성
            reform_data = ReformCreate(
                reformType="example_reform_type",
                cloth=cloth_type,
                fileName=image.filename,
                contentType=image.content_type,
                path=file_location
            )
            new_reform = create_reform(db, reform_data)
        except Exception as e:
            logger.error(f"Error occurred while creating reform guide: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"errorMessage": "Error while creating reform guide."}
            )
        
        try:
            # 로그 정보 DB에 저장
            log_data = LogCreate(
                userId=user_id,
                imageId=new_image.imageId,
                guideId=new_reform.guideId
            )
            new_log = create_log(db, log_data, user_id, new_image.imageId, new_reform.guideId)
        except Exception as e:
            logger.error(f"Error occurred while saving log information to the DB: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"errorMessage": "Error while saving log information to the DB."}
            )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "리폼 가이드가 성공적으로 생성되었습니다.",
                "cloth": new_reform.cloth
            }
        )
    
    except Exception as e:
        logger.error(f"Error occurred while creating reform guide: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"errorMessage": "Server error."}
        )