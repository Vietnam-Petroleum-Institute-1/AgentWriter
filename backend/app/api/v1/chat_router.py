from fastapi import APIRouter, HTTPException, Request, Depends

from app.core.config import settings
from app.services.upload_file import UploadFileService
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.file import FileData

from app.core.database import get_db
from app.core.dependencies import verify_token
from fastapi.responses import StreamingResponse

import os
import re
import random
import httpx
import logging
import json

router = APIRouter(prefix="/chat", tags=["Dify chatbot"])

# Thiết lập thư mục lưu trữ file upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Logger setup for debugging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
CHATBOT_URL = settings.CHATBOT_URL
DIFY_API_KEY = settings.DIFY_API_KEY

@router.post("/upload_file")
async def upload_file(request: Request, db: AsyncSession = Depends(get_db),user_id: str = Depends(verify_token)):
    form_data = await request.form()
    user_id = form_data.get("user_id")
    session_id = form_data.get("session_id")
    conversation_id = form_data.get("conversation_id")
    mime_type = form_data.get("mime_type")
    file = form_data.get("file")

    # Create upload service
    upload_file_service = UploadFileService(CHATBOT_URL=CHATBOT_URL,db=db)

    if not file:
        raise HTTPException(status_code=400, detail="File not found in request")

    # Lưu file tạm thời để xử lý
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Trích xuất nội dung file dựa trên MIME type
    content = ""
    if mime_type == "csv":
        content = upload_file_service.extract_csv_content(file_path)
    elif mime_type == "docx":
        content = upload_file_service.extract_docx_content(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported MIME type")

    # Gọi API upload
    file_id, error = await upload_file_service.call_upload_api(mime_type, content)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # insert_file
    file_data = FileData(
        file_id=file_id,  # Generate unique file ID here (e.g., using UUID)
        user_id=user_id,
        session_id=session_id,
        conversation_id=conversation_id,
        file_name=file.filename,
        file_path=file_path,
        file_size=file.size,
        mime_type=mime_type,
        created_by=user_id
    )
    await upload_file_service.create_file(file_data)

    # Trả về kết quả
    return {"message": f"File {file.filename} uploaded successfully", "file_id": file_id}

@router.post("/update_upload_file")
async def update_file(request: Request):
    form_data = await request.form()
    segment_id = form_data.get("segment_id")
    content = form_data.get("updated_file_id")
    
    # Sử dụng regex để chia đoạn văn thành các từ (loại bỏ dấu câu)
    words = re.findall(r"\b\w+\b", content)

    # Lấy ngẫu nhiên 10 từ trong danh sách
    random_keywords = random.sample(words, min(len(words), 10))
    url = f"{CHATBOT_URL}/datasets/270f6651-fb96-461d-a489-6658d1d2624b/documents/ad1e6bed-6c8d-42c2-a6f6-d0aecedcf1ff/segments/{segment_id}"
    logger.debug(f"segment_id: {segment_id}, content: {content} \n url: {url}")
    if not segment_id or content == "undefined" or not content:
        raise HTTPException(status_code=400, detail="segment_id or updated_file_id missing")
    # Dữ liệu gửi qua API
    payload = {
        "segment": {
            "content": f"{content}",
            "keywords": random_keywords,
            "enabled": "true",
        }
    }
    headers = {
        "Authorization": f"Bearer dataset-oB18KobCvufR8Gf0YjlKW9Ms",
        "Content-Type": "application/json",
    }

    # Gửi request POST đến API
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    logger.debug(f"response: {response.json() if response.status_code == 200 else 'No response'}")

    # Kiểm tra nếu request thành công
    if response.status_code == 200:
        return {"message":"Chunk updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="No file uploaded")

@router.post("/chat_messages")
async def call_chat_messages_api_and_process_stream(
    user_message, user_id, file_id, conversation_id
):
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "inputs": {"chunk_id": file_id},
        "query": user_message,
        "response_mode": "streaming",
        "conversation_id": conversation_id if conversation_id else "",
        "user": user_id,
    }
    logger.debug(f"Body: {body}")
    url = f"{CHATBOT_URL}/chat-messages"

    
    async def stream_response():
        buffer = ""
        final_result = ""
        current_conversation_id = conversation_id
        message_id = None

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=body)

            async for chunk in response.aiter_lines():
                if not chunk:
                    continue

                buffer += chunk
                json_blocks = re.split(r"(?<=\})\s*(?=data: {)", buffer)
                buffer = json_blocks.pop() if json_blocks else ""

                for json_block in json_blocks:
                    json_block = json_block.strip()
                    if json_block.startswith("data:"):
                        json_string = json_block.replace("data: ", "")
                        try:
                            json_data = json.loads(json_string)
                            if json_data.get("event") in ["tts_message_end", "message_end"]:
                                # Trả về kết quả cuối cùng khi kết thúc stream
                                yield json.dumps({
                                    "final_result": final_result,
                                    "conversation_id": current_conversation_id,
                                    "message_id": message_id,
                                }) + "\n"
                                return

                            if "answer" in json_data:
                                final_result += json_data["answer"]
                                # Trả về chunk kèm conversation_id và message_id
                                yield json.dumps({
                                    "answer": json_data["answer"],
                                    "conversation_id": current_conversation_id,
                                    "message_id": message_id,
                                }) + "\n"
                            if "conversation_id" in json_data:
                                current_conversation_id = json_data["conversation_id"]
                            if "message_id" in json_data:
                                message_id = json_data["message_id"]
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing JSON: {e}")

            # Xử lý phần còn lại của buffer khi kết thúc stream
            if buffer.startswith("data:"):
                json_string = buffer.replace("data: ", "")
                try:
                    json_data = json.loads(json_string)
                    if "answer" in json_data:
                        yield json.dumps({
                            "answer": json_data["answer"],
                            "conversation_id": current_conversation_id,
                            "message_id": message_id,
                        }) + "\n"
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON (remaining buffer): {e}")

    return StreamingResponse(stream_response(), media_type="application/json")