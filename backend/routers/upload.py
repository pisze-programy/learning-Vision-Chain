import os
import uuid

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, File
from starlette.responses import StreamingResponse

from routers.agents.router import run_agents_stream

router = APIRouter(tags=["Upload"])

UPLOAD_DIR = "../uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

SUPPORTED_MIME_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif"
]

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...)
):
    if file.content_type not in SUPPORTED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="INVALID_FORMAT")

    if not file.filename:
        raise HTTPException(status_code=400, detail="MISSING_FILENAME")

    file_extension = os.path.splitext(file.filename)[1]

    if not file_extension:
        raise HTTPException(status_code=400, detail="MISSING_FILE_EXTENSION")

    task_id = str(uuid.uuid4())
    stored_filename = f"{task_id}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        while content := await file.read(1024 * 1024):
            await out_file.write(content)

    return StreamingResponse(
        run_agents_stream(task_id=task_id, file_path=file_path),
        media_type="text/event-stream"
    )
