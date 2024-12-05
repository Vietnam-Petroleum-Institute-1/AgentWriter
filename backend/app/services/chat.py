import json
import json
import logging
import random
import re
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.models.bot import Bot
from app.models.file import File
from app.models.message_log import MessageLog
from app.models.notebook import Notebook
from app.schemas.chat import MessageLogCreate
from app.schemas.file import FileData
from app.services.upload_file import UploadFileService

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: AsyncSession, chatbot_url: str, dify_api_key: str):
        self.db = db
        self.chatbot_url = chatbot_url
        self.dify_api_key = dify_api_key
        self.upload_file_service = UploadFileService(chatbot_url, db)

    async def process_file_upload(
        self, file_data: FileData, file_content: bytes, mime_type: str
    ) -> Tuple[str, Optional[str]]:
        """Process and upload a file"""
        if not file_content:
            return None, "File content is empty"

        # Extract content based on mime type
        content = ""
        if mime_type == "csv":
            content = await self._extract_csv_content(file_content)
        elif mime_type == "docx":
            content = await self._extract_docx_content(file_content)
        else:
            return None, f"Unsupported MIME type: {mime_type}"

        # Call upload API
        file_id, error = await self.upload_file_service.call_upload_api(
            mime_type, content
        )
        if error:
            return None, error

        # Save file record
        file_data.file_id = file_id
        await self.upload_file_service.create_file(file_data)

        return file_id, None

    async def create_first_conversation_id(self, file_id: str):
        # Save first conversation id
        file = await self.get_file_by_id(file_id)
        first_chat_response = await self.process_chat_message(
            user_message="Hello",
            user_id=file.user_id,
            file_id=file_id,
        )
        print(first_chat_response)
        if first_chat_response:
            conversation_id = first_chat_response.get("conversation_id")

        # Save conversation to notebook table
        notebook = await self.get_notebook_by_id(file.notebook_id)
        if notebook:
            notebook.conversation_dify_id = conversation_id
            await self.db.commit()

    async def update_segment(
        self, segment_id: str, content: str
    ) -> Tuple[bool, Optional[str]]:
        """Update a segment's content"""
        if not segment_id or not content:
            return False, "Missing segment_id or content"

        try:
            words = re.findall(r"\b\w+\b", content)
            random_keywords = random.sample(words, min(len(words), 10))

            url = f"{self.chatbot_url}/datasets/270f6651-fb96-461d-a489-6658d1d2624b/documents/ad1e6bed-6c8d-42c2-a6f6-d0aecedcf1ff/segments/{segment_id}"

            payload = {
                "segment": {
                    "content": content,
                    "keywords": random_keywords,
                    "enabled": "true",
                }
            }

            headers = {
                "Authorization": "Bearer dataset-oB18KobCvufR8Gf0YjlKW9Ms",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    return True, None
                return False, f"API error: {response.status_code}"

        except Exception as e:
            logger.error(f"Error updating segment: {str(e)}")
            return False, f"Error updating segment: {str(e)}"

    async def process_chat_message(
        self, user_message: str, user_id: str, file_id: str
    ) -> Optional[Dict[str, Any]]:
        """Process a chat message and get response"""
        file = await self.get_file_by_id(file_id)
        notebook = await self.get_notebook_by_id(file.notebook_id)
        try:
            headers = {
                "Authorization": f"Bearer {self.dify_api_key}",
                "Content-Type": "application/json",
            }

            body = {
                "inputs": {"chunk_id": file_id},
                "query": user_message,
                "response_mode": "streaming",
                "conversation_id": (
                    notebook.conversation_dify_id
                    if notebook.conversation_dify_id
                    else ""
                ),
                "user": user_id,
            }

            url = f"{self.chatbot_url}/chat-messages"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=body)
                return await self._process_stream_response(response)

        except httpx.RequestError as e:
            logger.error(f"Error calling chat API: {e}")
            return None

    async def create_message_log(
        self, message_data: MessageLogCreate
    ) -> Optional[MessageLog]:
        """Create a message log entry"""
        try:
            message = MessageLog(
                notebook_id=message_data.notebook_id,
                bot_id=message_data.bot_id,
                content=message_data.content,
                from_user=message_data.from_user,
            )
            self.db.add(message)
            await self.db.commit()
            await self.db.refresh(message)
            return message
        except Exception as e:
            logger.error(f"Error creating message log: {e}")
            await self.db.rollback()
            return None

    async def get_chat_history(
        self, notebook_id: str, skip: int = 0, limit: int = 50
    ) -> List[MessageLog]:
        """Get chat history for a notebook"""
        result = await self.db.execute(
            select(MessageLog)
            .filter(MessageLog.notebook_id == notebook_id)
            .order_by(MessageLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_bot_by_type(self, bot_type: str) -> Optional[Bot]:
        """Get bot by type"""
        result = await self.db.execute(select(Bot).filter(Bot.type == bot_type))
        return result.scalar_one_or_none()

    async def _extract_csv_content(self, file_content: bytes) -> str:
        """Extract content from CSV file"""
        try:
            # Add CSV content extraction logic here
            return file_content.decode("utf-8")
        except Exception as e:
            logger.error(f"Error extracting CSV content: {e}")
            raise

    async def _extract_docx_content(self, file_content: bytes) -> str:
        """Extract content from DOCX file"""
        try:
            # Add DOCX content extraction logic here
            from io import BytesIO

            from docx import Document

            doc = Document(BytesIO(file_content))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error extracting DOCX content: {e}")
            raise

    async def get_notebook_by_id(self, notebook_id: str) -> Optional[Notebook]:
        """Get notebook by id"""
        result = await self.db.execute(
            select(Notebook).filter(Notebook.notebook_id == notebook_id)
        )
        return result.scalar_one_or_none()

    async def get_file_by_id(self, file_id: str) -> Optional[File]:
        """Get file by id"""
        result = await self.db.execute(select(File).filter(File.file_id == file_id))
        return result.scalar_one_or_none()

    async def get_files_in_notebook(self, notebook_id: str) -> List[File]:
        """Get files in notebook"""
        result = await self.db.execute(
            select(File).filter(File.notebook_id == notebook_id)
        )
        return result.scalars().all()
    
    async def _process_stream_response(
        self, response: httpx.Response
    ) -> Dict[str, Any]:
        """Process streaming response from chat API"""
        final_result = ""
        buffer = ""
        conversation_id = None
        message_id = None

        async for chunk in response.aiter_lines():
            if not chunk:
                continue

            buffer += chunk
            json_blocks = re.split(r"(?<=\})\s*(?=data: {)", buffer)
            buffer = json_blocks.pop() if json_blocks else ""

            for json_block in json_blocks:
                if json_block.startswith("data:"):
                    try:
                        json_data = json.loads(json_block.replace("data: ", ""))
                        logger.debug(f"Received JSON data: {json_data}")

                        if json_data.get("event") in ["tts_message_end", "message_end"]:
                            return {
                                "final_result": final_result,
                                "conversation_id": conversation_id,
                                "message_id": message_id,
                            }

                        if "answer" in json_data:
                            final_result += json_data["answer"]
                        if "conversation_id" in json_data:
                            conversation_id = json_data["conversation_id"]
                        if "message_id" in json_data:
                            message_id = json_data["message_id"]
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON: {e}")

        # Process any remaining data in buffer
        if buffer.startswith("data:"):
            try:
                json_data = json.loads(buffer.replace("data: ", ""))
                if "answer" in json_data:
                    final_result += json_data["answer"]
                if "conversation_id" in json_data:
                    conversation_id = json_data["conversation_id"]
                if "message_id" in json_data:
                    message_id = json_data["message_id"]
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing remaining JSON: {e}")

        return {
            "final_result": final_result,
            "conversation_id": conversation_id,
            "message_id": message_id,
        }