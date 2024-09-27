import requests
 
# Các thông tin cần thiết
API_KEY = 'dataset-oB18KobCvufR8Gf0YjlKW9Ms'
DATASET_ID = '0770fc48-186c-45a8-8a85-2f80abeb593a'
DOCUMENT_ID = '8a81cf1f-8dc1-42dc-88ac-5fe641604392'
BASE_URL = 'http://103.75.180.15/v1'
 
# Hàm lấy danh sách các segments của document
def get_segments(dataset_id, document_id):
    url = f'{BASE_URL}/datasets/{dataset_id}/documents/{document_id}/segments'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Error fetching segments: {response.status_code} - {response.text}")
        return []
 
# Hàm xóa một segment theo segment_id
def delete_segment(dataset_id, document_id, segment_id):
    url = f'{BASE_URL}/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    
    response = requests.delete(url, headers=headers)
    if response.status_code == 200 or response.status_code == 204:
        print(f"Segment {segment_id} deleted successfully.")
    else:
        print(f"Error deleting segment {segment_id}: {response.status_code} - {response.text}")
 
# Xóa tất cả các segment của document
def delete_all_segments(dataset_id, document_id):
    segments = get_segments(dataset_id, document_id)
    for segment in segments:
        segment_id = segment['id']
        delete_segment(dataset_id, document_id, segment_id)
 
# Gọi hàm để xóa tất cả các segment trong document đã biết
# delete_all_segments(DATASET_ID, DOCUMENT_ID)

# Hàm lấy danh sách các segments của document
def get_segments2(dataset_id, document_id):
    url = f'{BASE_URL}/datasets/18cb9306-32e8-487a-993c-586b2c563cc3/documents/59abce73-608a-459c-a47d-0d9276ea6b83/segments'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response = response.json()['data']
        for segment in response:
            segment_id = segment['id']
            content = segment['content']
            # if 'dd5f6caf-8350-4b89-9765-5cb9c0fbbc9d' in segment_id:
            #     print(segment_id, content)
            print(segment_id, content)
    else:
        print(f"Error fetching segments: {response.status_code} - {response.text}")
        return []
get_segments2(DATASET_ID, DOCUMENT_ID)

# 53ba5164-c4a6-434a-aca1-82a6fab4dee6, d67ca0a5-9eca-4e0e-99cf-e7ef0ea11399