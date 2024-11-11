import csv
import requests
from docx import Document
from app.schemas.file import FileData
from app.models.file import File
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime

class UploadFileService:
    def __init__(self, CHATBOT_URL:str,db: AsyncSession):
        self.db = db
        self.CHATBOT_URL = CHATBOT_URL

    async def create_file(self,file_data: FileData):
        created_at = updated_at = datetime.now()
        # Create an instance of UploadFile ORM model
        file = File(
            file_id=file_data.file_id,
            user_id=file_data.user_id,
            session_id=file_data.session_id,
            notebook_id=file_data.conversation_id,
            file_name=file_data.file_name,
            file_path=file_data.file_path,
            file_size=file_data.file_size,
            extension=file_data.mime_type,
            created_at=created_at,
            updated_at=updated_at,
            updated_by=file_data.created_by,
        )

        # Add the file record to the session and commit it
        self.db.add(file)
        self.db.commit()
        self.db.refresh(file)

        print("added file to db")
        return file
    
    # Hàm để gọi API upload
    async def call_upload_api(self,mime_type, content):
        url = ""
        if mime_type == "csv":
            url = f"{self.CHATBOT_URL}/datasets/18cb9306-32e8-487a-993c-586b2c563cc3/documents/59abce73-608a-459c-a47d-0d9276ea6b83/segments"
        elif mime_type == "docx":
            url = f"{self.CHATBOT_URL}/datasets/0770fc48-186c-45a8-8a85-2f80abeb593a/documents/8a81cf1f-8dc1-42dc-88ac-5fe641604392/segments"
        
        if not url:
            return None, "Unsupported MIME type"
        
        payload = {
            "segments": [{"content": content}]
        }
        
        headers = {
            "Authorization": "Bearer dataset-oB18KobCvufR8Gf0YjlKW9Ms",
            "Content-Type": "application/json",
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            response_json = response.json()
            if "data" in response_json and len(response_json["data"]) > 0:
                file_id = response_json["data"][0].get("id", "")
                return file_id, None
            return None, "No data returned from API"
        else:
            return None, f"Failed to upload. Status code: {response.status_code}"

    # Hàm trích xuất nội dung CSV
    def extract_csv_content(self,file_path):
        content = []
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                content.append(",".join(row))
        return "\n".join(content)

    # Hàm trích xuất nội dung DOCX
    def extract_docx_content(self,file_path):
        doc = Document(file_path)
        content = [paragraph.text for paragraph in doc.paragraphs]
        return "\n".join(content)
    
    def set_content(self, content):
        self.content = content
