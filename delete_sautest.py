import requests
 
# Các thông tin cần thiết
API_KEY = 'dataset-oB18KobCvufR8Gf0YjlKW9Ms'
DATASET_ID = '18cb9306-32e8-487a-993c-586b2c563cc3'
DOCUMENT_ID = '59abce73-608a-459c-a47d-0d9276ea6b83'
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
    url = f'{BASE_URL}/datasets/{dataset_id}/documents/{document_id}/segments'
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response = response.json()['data']
        for segment in response:
            segment_id = segment['id']
            print(segment_id)
    else:
        print(f"Error fetching segments: {response.status_code} - {response.text}")
        return []
get_segments2(DATASET_ID, DOCUMENT_ID)