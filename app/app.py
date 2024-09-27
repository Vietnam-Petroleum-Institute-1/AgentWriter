import csv
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    make_response,
)
import requests
import logging
from databases import (
    insert_file,
    get_file,
    delete_file,
    session_continue,
    connect_db,
    user_exists,
    end_session,
    session,
    session_exists,
    conversation,
    insert_user,
    get_message_lastest_timestamp,
    get_transcripts,
    add_conversation,
    get_conversation_id,
    write_feedback,
    session_valid,
    error_logs,
)
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import re
from flask_cors import CORS
from dotenv import load_dotenv
import os
import uuid
import jwt  # For token handling
from werkzeug.utils import secure_filename
from docx import Document  # Thư viện để đọc file DOCX


app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

CHATBOT_APIKEY = os.getenv("CHATBOT_APIKEY")
CHATBOT_URL = os.getenv("CHATBOT_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
API_KEY = os.getenv("API_KEY")

app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Giới hạn kích thước file 16MB


def decode_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")
        exp = decoded.get("exp")
        if user_id and exp:
            # Verify token has not expired
            if datetime.utcnow().timestamp() < exp:
                return user_id
            else:
                # Token has expired
                return None
        else:
            # Invalid token payload
            return None
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None


@app.route("/api/check_token", methods=["POST"])
def api_check_token():
    data = request.json  # Thay đổi để lấy toàn bộ dữ liệu JSON
    token = data.get("token")
    logging.debug(f"Token receive: {token}")
    user_id = decode_token(token)
    if user_id:
        conn = connect_db()
        session_id = session_continue(conn, user_id)
        if not session_id:
            session_id = f"{uuid.uuid4()}"
        if isinstance(session_id, tuple):
            session_id = session_id[0]
        logging.debug(f"Redirecting to home with session_id: {session_id}")

        # Set cookie for session_id and user_id
        response = make_response(redirect(url_for("chatbot")))
        # Đặt thời gian hết hạn cụ thể, ví dụ 10 phút kể từ bây giờ
        expires = datetime.now(timezone.utc) + timedelta(minutes=60)

        # Đặt cookie với thời gian hết hạn cụ thể
        response.set_cookie("session_id", session_id, expires=expires)
        response.set_cookie("user_id", user_id, expires=expires)

        return response
    else:
        logging.warning(f"Authentication failed: Token not valid")
        return render_template("chatbot.html")


@app.after_request
def add_security_headers(response):
    # Bỏ X-Frame-Options để không hạn chế việc nhúng iframe
    # Nếu bạn không muốn hạn chế bất cứ domain nào thì không cần thêm X-Frame-Options
    response.headers.pop("X-Frame-Options", None)

    # Cho phép tất cả các domain nhúng iframe
    response.headers["Content-Security-Policy"] = "frame-ancestors *"

    return response


@app.route("/")
def home():
    session_id = request.cookies.get("session_id")
    user_id = request.cookies.get("user_id")

    if not session_id:
        logging.debug("No session_id found, redirecting to signin.")
        return redirect(url_for("signin"))

    logging.debug(
        f"Rendering home page for user_id: {user_id}, session_id: {session_id}"
    )
    return render_template("index.html")


@app.route("/chatbot")
def chatbot():
    session_id = request.cookies.get("session_id")
    user_id = request.cookies.get("user_id")

    if not session_id:
        logging.debug("No session_id found, redirecting to signin.")
        return redirect(url_for("signin"))

    logging.debug(
        f"Rendering home page for user_id: {user_id}, session_id: {session_id}"
    )
    return render_template("chatbot.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        logging.debug(f"Received POST request for signin with username: {username}")

        if not username or not password:
            logging.warning("Username or password missing.")
            return render_template(
                "signin.html", error="Username or password is missing."
            )

        success = True
        message = "Thành Công!"

        if success:
            conn = connect_db()
            session_id = session_continue(conn, username)
            if not session_id:
                session_id = f"{uuid.uuid4()}"
            if isinstance(session_id, tuple):
                session_id = session_id[0]
            logging.debug(f"Redirecting to home with session_id: {session_id}")

            # Set cookie for session_id and user_id
            response = make_response(redirect(url_for("home")))
            # Đặt thời gian hết hạn cụ thể, ví dụ 10 phút kể từ bây giờ
            expires = datetime.now(timezone.utc) + timedelta(minutes=60)

            # Đặt cookie với thời gian hết hạn cụ thể
            response.set_cookie("session_id", session_id, expires=expires)
            response.set_cookie("user_id", username, expires=expires)

            return response
        else:
            logging.warning(f"Authentication failed: {message}")
            return render_template("signin.html", error=message)

    logging.debug("Rendering signin page.")
    return render_template("signin.html")


import re


def call_chat_messages_api_and_process_stream(
    user_message, user_id, file_id, conversation_id
):
    headers = {
        "Authorization": f"Bearer {CHATBOT_APIKEY}",
        "Content-Type": "application/json",
    }

    body = {
        "inputs": {"chunk_id":file_id},
        "query": user_message,
        "response_mode": "streaming",
        "conversation_id": conversation_id if conversation_id else "",
        "user": user_id,
    }
    app.logger.debug(f'Body: {body}')
    try:
        url = f"{CHATBOT_URL}/chat-messages"
        with requests.post(url, headers=headers, json=body, stream=True) as response:
            final_result = ""
            buffer = ""
            conversation_id = None
            message_id = None

            for chunk in response.iter_lines():
                # Bỏ qua các chunk rỗng
                if not chunk:
                    continue

                # Giải mã chunk từ bytes thành string
                chunk_str = chunk.decode("utf-8")
                buffer += chunk_str

                # Sử dụng regex để tách từng JSON object
                json_blocks = re.split(r"(?<=\})\s*(?=data: {)", buffer)

                # Gán phần còn lại của buffer chưa hoàn chỉnh
                buffer = json_blocks.pop() if json_blocks else ""

                for json_block in json_blocks:
                    json_block = json_block.strip()
                    if json_block.startswith("data:"):
                        json_string = json_block.replace("data: ", "")
                        try:
                            json_data = json.loads(json_string)
                            app.logger.debug(f"json_data: {json_data}")

                            # Kiểm tra tín hiệu kết thúc stream
                            if json_data.get("event") in [
                                "tts_message_end",
                                "message_end",
                            ]:
                                return (
                                    final_result,
                                    conversation_id,
                                    message_id,
                                )  # Kết thúc stream

                            if "answer" in json_data:
                                final_result += json_data["answer"]
                            if "conversation_id" in json_data:
                                conversation_id = json_data["conversation_id"]
                            if "message_id" in json_data:
                                message_id = json_data["message_id"]
                        except json.JSONDecodeError as e:
                            app.logger.error(f"Error parsing JSON: {e}")

            # Xử lý phần còn lại trong buffer khi kết thúc stream
            if buffer.startswith("data:"):
                json_string = buffer.replace("data: ", "")
                try:
                    json_data = json.loads(json_string)
                    app.logger.debug(f"json_data (remaining buffer): {json_data}")
                    if "answer" in json_data:
                        final_result += json_data["answer"]
                    if "conversation_id" in json_data:
                        conversation_id = json_data["conversation_id"]
                    if "message_id" in json_data:
                        message_id = json_data["message_id"]
                except json.JSONDecodeError as e:
                    app.logger.error(f"Error parsing JSON (remaining buffer): {e}")

            return final_result, conversation_id, message_id

    except requests.RequestException as e:
        app.logger.error(f"Error calling the API: {e}")
        return None, None, None


@app.route("/api/message", methods=["GET"])
def api_message():
    conn = connect_db()
    user_id = request.args.get("user_id")
    user_message = request.args.get("text")
    session_id = request.args.get("session_id")
    conversation_id = request.args.get("conversation_id")
    file_id = request.args.get("file_id")

    # Parse file_id as a JSON object
    # file_id = json.loads(file_id)

    end_session(conn, user_id, session_id)

    if not user_message:
        error_logs(
            user_id,
            session_id,
            conversation_id,
            user_message,
            "No message provided",
            "400",
        )
        return jsonify({"result": "No message provided"}), 400

    transcripts = get_transcripts(conn, user_id, session_id)
    transcripts = json.dumps(transcripts)
    print(conversation_id, transcripts, user_message, user_id, session_id)

    try:
        # Gọi API và xử lý streaming response
        result_answer, conversation_id, message_id = (
            call_chat_messages_api_and_process_stream(
                user_message, user_id, file_id, conversation_id
            )
        )

        if not result_answer:
            return jsonify({"result": "Không nhận được phản hồi từ chatbot"}), 500

        # Lưu lại conversation_id và message_id
        print("Conversation ID:", conversation_id)
        print("Message ID:", message_id)

        input_token = len(user_message) // 4 + 1
        output_token = len(result_answer) // 4 + 1
        total_token = input_token + output_token
        timestamp = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime(
            "%Y-%m-%d %H:%M:%S %z"
        )

        conversation(
            conn,
            message_id,
            session_id,
            user_id,
            user_message,
            input_token,
            result_answer,
            output_token,
            total_token,
            timestamp,
            conversation_id,
        )

        conn.close()
        return jsonify(
            {
                "result": result_answer,
                "conversation_id": conversation_id,
                "message_id": message_id,
            }
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"RequestException: {e}")
        error_logs(
            conn, user_id, session_id, conversation_id, user_message, str(e), "500"
        )
        return (
            jsonify(
                {"result": f"Xin lỗi, tôi không đủ thông tin để trả lời câu hỏi này"}
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Exception: {e}")
        error_logs(
            conn, user_id, session_id, conversation_id, user_message, str(e), "500"
        )
        return (
            jsonify(
                {"result": f"Xin lỗi, tôi không đủ thông tin để trả lời câu hỏi này"}
            ),
            500,
        )


@app.route("/api/start_conversation", methods=["POST"])
def start_conversation():
    conn = connect_db()
    try:
        # Lấy dữ liệu từ request JSON
        user_id = request.json.get("user_id")
        session_id = request.json.get("session_id")

        if not user_id or not session_id:
            return jsonify({"error": "Thiếu user_id hoặc session_id"}), 400

        conversation_id = ""  # Khi bắt đầu, chưa có conversation_id
        # Kiểm tra mime type và đặt URL tương ứng

        url = f"{CHATBOT_URL}/datasets/270f6651-fb96-461d-a489-6658d1d2624b/documents/ad1e6bed-6c8d-42c2-a6f6-d0aecedcf1ff/segments"

            # Dữ liệu gửi qua API
        payload = {
            "segments": [
                {
                    "content": "None",  # Nội dung được lấy từ file
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer dataset-oB18KobCvufR8Gf0YjlKW9Ms",
            "Content-Type": "application/json",
        }

        # Gửi request POST đến API
        response = requests.post(url, headers=headers, json=payload)

        # Kiểm tra nếu request thành công
        if response.status_code == 200:
            response_json = response.json()
            if "data" in response_json and len(response_json["data"]) > 0:
                segment_id = response_json["data"][0].get("id", "")

        # Gọi hàm xử lý streaming
        result_answer, conversation_id, message_id = (
            call_chat_messages_api_and_process_stream(
                "Xin chào", user_id, segment_id, conversation_id
            )
        )

        app.logger.debug(f"conversation_id: {conversation_id}")

        if not result_answer:
            app.logger.error("Không nhận được phản hồi từ API chatbot.")
            return jsonify({"error": "Không nhận được phản hồi từ chatbot"}), 500

        # Tính toán token
        input_token = 0  # Tin nhắn đầu tiên "Xin chào" không tính token đầu vào
        output_token = len(result_answer) // 4 + 1
        total_token = input_token + output_token
        timestamp = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime(
            "%Y-%m-%d %H:%M:%S %z"
        )

        # Lưu thông tin cuộc hội thoại vào cơ sở dữ liệu
        add_conversation(conn, conversation_id, session_id, user_id)
        conversation(
            conn,
            message_id,
            session_id,
            user_id,
            "",
            input_token,
            result_answer,
            output_token,
            total_token,
            timestamp,
            conversation_id,
        )

        conn.close()

        # Trả về thông tin conversation_id và message_id
        return jsonify(
            {
                "conversation_id": conversation_id,
                "message_id": message_id,
                "result": result_answer,
                "start_segment_id": segment_id
            }
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"RequestException: {e}")
        error_logs(conn, user_id, session_id, "", "Xin chào", str(e), "501")
        conn.close()
        return jsonify({"error": "Lỗi khi gọi API chatbot"}), 501

    except Exception as e:
        app.logger.error(f"Exception: {e}")
        error_logs(conn, user_id, session_id, "", "Xin chào", str(e), "501")
        conn.close()
        return jsonify({"error": "Lỗi không xác định"}), 501


@app.route("/api/user", methods=["POST"])
def api_user():
    conn = connect_db()
    user_id = request.json["user_id"]
    if not user_exists(conn, user_id):
        insert_user(conn, user_id, user_id)
    conn.close()
    return jsonify({"result": "User added successfully"})

@app.route("/api/user_exist", methods=["POST"])
def user_exist():
    conn = connect_db()
    user_id = request.json["user_id"]
    exists = user_exists(conn, user_id)
    if not exists:
        return jsonify({"result": 0}), 404
    conn.close()
    return jsonify({"result": 1})


@app.route("/api/chat_status", methods=["GET"])
def api_chat_status():
    conn = connect_db()
    data = request.get_json()
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    print(f"user_id: {user_id}, session_id: {session_id}")

    if not user_exists(conn, user_id):
        return jsonify({"result": "User does not exist"}), 404
    if not session_exists(conn, user_id, session_id):
        return jsonify({"result": "Session does not exist"}), 404

    timestamp = get_message_lastest_timestamp(conn, user_id, session_id)
    print(f"timestamp: {timestamp}")

    if timestamp is None or len(timestamp) == 0:
        return jsonify({"result": "No message found"}), 404

    timestamp = timestamp[0]
    now = datetime.now()
    diff = now - timestamp

    if diff <= timedelta(minutes=5):
        return jsonify({"result": 1})
    else:
        return jsonify({"result": 0})


@app.route("/api/session", methods=["POST"])
def api_session():
    conn = connect_db()
    user_id = request.json["user_id"]
    session_id = request.json["session_id"]
    start_time = request.json["start_time"]
    end_time = request.json["end_time"]

    session(conn, user_id, session_id, start_time, end_time)
    conn.close()
    return jsonify({"result": "Session added successfully"})


@app.route("/api/session_exist", methods=["POST"])
def api_session_exist():
    conn = connect_db()
    user_id = request.json["user_id"]
    session_id = request.json["session_id"]
    if not session_exists(conn, user_id, session_id):
        return jsonify({"result": 0}), 200
    if not session_valid(conn, user_id, session_id):
        return jsonify({"result": "session expired"}), 404
    conn.close()
    return jsonify({"result": 1})


@app.route("/api/conversation_id", methods=["POST"])
def api_conversation_id():
    conn = connect_db()
    user_id = request.json["user_id"]
    session_id = request.json["session_id"]

    conversation_id = get_conversation_id(conn, user_id, session_id)
    print(conversation_id)
    if conversation_id is None:
        return jsonify({"result": "Conversation ID not found"}), 404
    else:
        return jsonify({"result": conversation_id[0]})


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    conn = connect_db()
    data = request.json  # Thay đổi để lấy toàn bộ dữ liệu JSON
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    message_id = data.get("messageId")  # Đảm bảo sử dụng đúng tên khóa
    feedback_type = data.get("feedbackType")
    feedback_text = data.get("feedbackText", "")

    write_feedback(conn, user_id, session_id, message_id, feedback_type, feedback_text)
    conn.close()
    return jsonify({"result": "Feedback added successfully"})


@app.route("/api/get_transcripts", methods=["POST"])
def api_transcripts():
    conn = connect_db()
    data = request.json
    user_id = data.get("user_id")
    session_id = data.get("session_id")
    transcripts = get_transcripts(conn, user_id, session_id)
    # Thêm logging để kiểm tra dữ liệu trả về
    app.logger.debug(
        f"Transcripts for user_id={user_id}, session_id={session_id}: {transcripts}"
    )
    return jsonify({"transcripts": json.dumps(transcripts)})


def decode_unicode_escapes(string):
    # This function will only decode the Unicode escape sequences, not the emojis
    unicode_escape_pattern = re.compile(r"\\u[0-9a-fA-F]{4}")
    return unicode_escape_pattern.sub(lambda m: chr(int(m.group(0)[2:], 16)), string)


@app.route("/embed")
def embed():
    user_id = request.args.get("user_id")
    session_id = request.args.get("session_id")

    if not user_id or not session_id:
        return redirect(url_for("signin"))

    # Tạo đối tượng response trước
    response = make_response(render_template("chatbot.html"))

    # Đặt cookies mà không chỉ định domain
    response.set_cookie("session_id", session_id, max_age=1, path="/")
    response.set_cookie("user_id", user_id, max_age=1, path="/")

    return response


def call_upload_api(mime_type, content):
    url = ""

    # Kiểm tra mime type và đặt URL tương ứng
    if mime_type == "csv":
        url = f"{CHATBOT_URL}/datasets/18cb9306-32e8-487a-993c-586b2c563cc3/documents/59abce73-608a-459c-a47d-0d9276ea6b83/segments"
    elif mime_type == "docx":
        url = f"{CHATBOT_URL}/datasets/0770fc48-186c-45a8-8a85-2f80abeb593a/documents/8a81cf1f-8dc1-42dc-88ac-5fe641604392/segments"

    if not url:
        return None, "Unsupported MIME type"

        # Dữ liệu gửi qua API
    payload = {
        "segments": [
            {
                "content": content,  # Nội dung được lấy từ file
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer dataset-oB18KobCvufR8Gf0YjlKW9Ms",
        "Content-Type": "application/json",
    }

    # Gửi request POST đến API
    response = requests.post(url, headers=headers, json=payload)

    # Kiểm tra nếu request thành công
    if response.status_code == 200:
        response_json = response.json()
        if "data" in response_json and len(response_json["data"]) > 0:
            file_id = response_json["data"][0].get("id", "")
            return file_id, None
        return None, "No data returned from API"
    else:
        return None, f"Failed to upload. Status code: {response.status_code}"


# Đọc nội dung từ file CSV
def extract_csv_content(file_path):
    content = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            content.append(",".join(row))  # Nối các cột của mỗi dòng thành chuỗi
    return "\n".join(content)  # Nối các dòng lại với nhau để tạo thành một chuỗi lớn


# Đọc nội dung từ file DOCX
def extract_docx_content(file_path):
    doc = Document(file_path)
    content = []
    for paragraph in doc.paragraphs:
        content.append(paragraph.text)  # Lấy mỗi đoạn văn bản từ file
    return "\n".join(content)  # Nối tất cả các đoạn văn bản lại với nhau


@app.route("/api/upload_file", methods=["POST"])
def upload_file():
    user_id = request.form.get("user_id")
    session_id = request.form.get("session_id")
    conversation_id = request.form.get("conversation_id")
    file_size = request.form.get("file_size")
    mime_type = request.form.get("mime_type")
    created_by = request.cookies.get("user_id")

    file = request.files["file"]  # Nhận file từ request

    if file:
        # Sử dụng secure_filename để đảm bảo tên file an toàn
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Trích xuất nội dung từ file dựa trên loại MIME type
        content = ""
        if mime_type == "csv":
            content = extract_csv_content(file_path)
        elif mime_type == "docx":
            content = extract_docx_content(file_path)
        else:
            return jsonify({"error": "Unsupported MIME type"}), 400

        # Gọi API upload với nội dung trích xuất từ file
        file_id, error = call_upload_api(mime_type, content)
        if error:
            return jsonify({"error": error}), 400

        # Insert thông tin file vào cơ sở dữ liệu
        print("Index node hash: ", file_id)
        conn = connect_db()
        insert_file(
            conn,
            file_id,
            user_id,
            session_id,
            conversation_id,
            filename,
            file_path,
            file_size,
            mime_type,
            created_by,
        )
        conn.close()

        return (
            jsonify(
                {
                    "message": f"File {filename} uploaded successfully",
                    "file_id": file_id,
                }
            ),
            200,
        )

    return jsonify({"error": "No file uploaded"}), 400

@app.route("/api/update_upload_file", methods=["POST"])
def update_file():
    segment_id = request.form.get("segment_id")
    content = request.form.get("updated_file_id")
    url = f"{CHATBOT_URL}/datasets/270f6651-fb96-461d-a489-6658d1d2624b/documents/ad1e6bed-6c8d-42c2-a6f6-d0aecedcf1ff/segments/{segment_id}"

        # Dữ liệu gửi qua API
    payload = {
        "segments": [
            {
                "content": content,  # Nội dung được lấy từ file
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer dataset-oB18KobCvufR8Gf0YjlKW9Ms",
        "Content-Type": "application/json",
    }

    # Gửi request POST đến API
    response = requests.post(url, headers=headers, json=payload)

    # Kiểm tra nếu request thành công
    if response.status_code == 200:
        return (
        jsonify(
            {
                "message": f"Chunk updated successfully",
            }
        ),
        200,
    )
    else:
        return jsonify({"error": "No file uploaded"}), 400

if __name__ == "__main__":
    app.run(debug=True)
