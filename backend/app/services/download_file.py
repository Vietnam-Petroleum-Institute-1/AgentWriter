import logging
import random
import httpx


import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class DownloadFileService:
    def __init__(self, chatbot_url: str):
        self.chatbot_url = chatbot_url
    async def download(self,download_segment_id : str):
        url = f"{settings.CHATBOT_URL}/datasets/6f2c01c5-9773-4bf0-b058-6b2e42787c1c/documents/9372129a-8f6f-46c2-bdd1-bed9ff5adfa6/segments"
        logger.debug(f"Received download_segment_id: {download_segment_id}")

        if not download_segment_id or download_segment_id == "undefined":
            return None,"segment_id or updated_file_id missing"

        headers = {
            "Authorization": "Bearer dataset-oB18KobCvufR8Gf0YjlKW9Ms",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
            except httpx.RequestError as e:
                logger.error(f"Request to {url} failed: {e}")
                return None,"Failed to connect to API"
            
            if response.status_code == 200:
                try:
                    response_data = response.json().get("data", [])
                    logger.debug(f"Received response data: {response_data}")

                    if not response_data:
                        logger.warning("Empty data received from API")
                        return None,"No segments available"

                    for segment in response_data:
                        segment_id = segment["id"]
                        content = segment["content"]
                        if download_segment_id in segment_id:
                            return {"message": content},None
                    logger.info(f"No segment with ID matching {download_segment_id} found.")
                    return None,"Segment ID not found"

                except ValueError as e:
                    logger.error(f"Error decoding JSON response: {e}")
                    return None,"Failed to decode response"
            
            elif response.status_code == 404:
                return None,"Segments not found"
            else:
                logger.error(
                    f"Unexpected status code {response.status_code}. Response: {response.text}"
                )
                return None, "Failed to download file"

