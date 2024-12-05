import logging
import os
from typing import List, Optional

import httpx
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    WebSocket,
    status,
)
from fastapi.param_functions import Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette import EventSourceResponse

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import verify_token
from app.schemas.chat import (
    ChatMessage,
    ChatResponse,
    FileUploadResponse,
    MessageLogCreate,
    MessageLogResponse,
    UpdateSegmentRequest,
    UpdateSegmentResponse,
)
from app.schemas.file import FileData
from app.services.chat import ChatService

router = APIRouter(prefix="/chat", tags=["Dify chatbot"])
logger = logging.getLogger(__name__)

# Setup upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def get_file_type(filename: str) -> str:
    _, file_extension = os.path.splitext(filename)
    return file_extension[1:] if file_extension else None


@router.post("/upload_file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    notebook_id: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(verify_token),
):
    """
    Upload a file for chat processing.

    - **file**: The file to upload (supported types: csv, docx)
    - **session_id**: Optional session ID
    - **notebook_id**: Optional notebook ID
    """

    mime_type = get_file_type(file.filename)
    file_content = await file.read()

    chat_service = ChatService(db, settings.CHATBOT_URL, settings.DIFY_API_KEY)

    file_data = FileData(
        file_id="",  # Will be set after upload
        user_id=user_id,
        session_id=session_id,
        notebook_id=notebook_id,
        file_name=file.filename,
        file_path=os.path.join(UPLOAD_FOLDER, file.filename),
        file_size=file.size,
        mime_type=mime_type,
        created_by=user_id,
    )

    file_id, error = await chat_service.process_file_upload(
        file_data, file_content, mime_type
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    # Only create conversation ID if this is first file in notebook
    if notebook_id:
        existing_files = await chat_service.get_files_in_notebook(notebook_id)
        if len(existing_files) == 1:
            await chat_service.create_first_conversation_id(file_id)
    else:
        # If no notebook_id, always create conversation ID
        await chat_service.create_first_conversation_id(file_id)

    return FileUploadResponse(
        message=f"File {file.filename} uploaded successfully", file_id=file_id
    )


@router.post("/update_segment", response_model=UpdateSegmentResponse)
async def update_segment(
    request: UpdateSegmentRequest = Body(
        ..., example={"segment_id": "segment-123", "content": "Updated content here"}
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a segment's content.

    - **segment_id**: ID of the segment to update
    - **content**: New content for the segment
    """
    chat_service = ChatService(db, settings.CHATBOT_URL, settings.DIFY_API_KEY)
    success, error = await chat_service.update_segment(
        request.segment_id, request.content
    )

    if success:
        return UpdateSegmentResponse(
            message="Segment updated successfully", success=True
        )
    raise HTTPException(status_code=400, detail=error or "Failed to update segment")


@router.post("/chat_messages", response_model=ChatResponse)
async def chat_messages(
    chat_message: ChatMessage = Body(...),
    db: AsyncSession = Depends(get_db),
):
    chat_service = ChatService(db, settings.CHATBOT_URL, settings.DIFY_API_KEY)

    # Get bot for logging
    bot = await chat_service.get_bot_by_type("dify")
    if not bot:
        raise HTTPException(status_code=404, detail="Chat bot not found")

    # Get file and notebook info
    file = await chat_service.get_file_by_id(chat_message.file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Log user message
    user_message_log = MessageLogCreate(
        notebook_id=file.notebook_id,
        bot_id=bot.bot_id,
        content=chat_message.user_message,
        from_user=True,
    )


    try:
        full_bot_response = await chat_service.process_chat_message(
            chat_message.user_message,
            chat_message.user_id,
            chat_message.file_id,
        )

        # Log bot response after complete
        bot_message_log = MessageLogCreate(
            notebook_id=file.notebook_id,
            bot_id=bot.bot_id,
            content=full_bot_response,
            from_user=False,
        )
        await chat_service.create_message_log(user_message_log)
        await chat_service.create_message_log(bot_message_log)

        return {"message": full_bot_response}

    except Exception as e:
        logger.error(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail="Error processing chat message")


@router.post("/chat_history")
async def get_chat_history(
    notebook_id: str,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """
    Get chat history for a specific notebook.

    - **notebook_id**: ID of the notebook to get history for
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    chat_service = ChatService(db, settings.CHATBOT_URL, settings.DIFY_API_KEY)
    messages = await chat_service.get_chat_history(notebook_id, skip, limit)
    return messages


@router.post("/download_file", response_model=ChatResponse)
async def download_file(download_segment_id: str):
    """
    Push a segment_id to the server and get a paper's content.

    - **user_message**: The message from the user
    - **file_id**: ID of the file being discussed
    """

    url = f"{settings.CHATBOT_URL}/datasets/6f2c01c5-9773-4bf0-b058-6b2e42787c1c/documents/9372129a-8f6f-46c2-bdd1-bed9ff5adfa6/segments"
    logger.debug(f"Received download_segment_id: {download_segment_id}")

    if not download_segment_id or download_segment_id == "undefined":
        raise HTTPException(
            status_code=400, detail="segment_id or updated_file_id missing"
        )

    headers = {
        "Authorization": "Bearer dataset-oB18KobCvufR8Gf0YjlKW9Ms",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
        except httpx.RequestError as e:
            logger.error(f"Request to {url} failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to connect to API")

        if response.status_code == 200:
            try:
                response_data = response.json().get("data", [])
                logger.debug(f"Received response data: {response_data}")

                if not response_data:
                    logger.warning("Empty data received from API")
                    raise HTTPException(status_code=404, detail="No segments available")

                for segment in response_data:
                    segment_id = segment["id"]
                    content = segment["content"]
                    if download_segment_id in segment_id:
                        return {"message": content}

                logger.info(f"No segment with ID matching {download_segment_id} found.")
                raise HTTPException(status_code=404, detail="Segment ID not found")

            except ValueError as e:
                logger.error(f"Error decoding JSON response: {e}")
                raise HTTPException(status_code=500, detail="Failed to decode response")

        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Segments not found")
        else:
            logger.error(
                f"Unexpected status code {response.status_code}. Response: {response.text}"
            )
            raise HTTPException(status_code=500, detail="Failed to download file")
