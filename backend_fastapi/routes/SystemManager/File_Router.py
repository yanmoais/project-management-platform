from fastapi import APIRouter, UploadFile, File
import os
import uuid
import shutil
from backend_fastapi.core.config import settings

router = APIRouter(tags=["文件管理"])

# Configuration
# This file is in backend_fastapi/routes/SystemManager/File_Router.py
# 1. SystemManager
# 2. routes
# 3. backend_fastapi
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'static', 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@router.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    if not file:
        return {'code': 400, 'msg': 'No file part', 'data': None}
    if not file.filename:
        return {'code': 400, 'msg': 'No selected file', 'data': None}
        
    try:
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Construct URL
        # Assuming static files are mounted at /static
        file_url = f"/static/uploads/{filename}"
        
        return {
            'code': 200, 
            'msg': 'success', 
            'data': {
                'name': file.filename,
                'url': file_url
            }
        }
    except Exception as e:
        return {'code': 500, 'msg': str(e), 'data': None}
