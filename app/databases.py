import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging

load_dotenv()

HOST = os.getenv("DB_HOST")


def connect_db():
    return psycopg2.connect(
        dbname="agent_writer",
        user="phuongpd",
        password="vdkvn22.05",
        host="localhost",
        port="5432",
    )


def user_exists(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    exists = cur.fetchone() is not None
    cur.close()
    logging.debug(f"Check user_exists for create new: {exists}")
    return exists

    # return exists, None


def insert_user(conn, user_id, name):
    logging.debug(f"Attempting to insert user in database: {user_id}")
    if user_exists(conn, user_id):
        logging.debug(f"User {user_id} already exists.")
        return
    cur = conn.cursor()
    insert_user_query = """
    INSERT INTO users (user_id, name)
    VALUES (%s, %s)
    """
    cur.execute(insert_user_query, (user_id, name))
    conn.commit()
    cur.close()
    logging.debug(f"User {user_id} inserted successfully.")


def session(conn, user_id, session_id, start_time, end_time):
    if not user_exists(conn, user_id):
        print(f"User {user_id} does not exist.")
        return
    cur = conn.cursor()
    created_at = updated_at = datetime.now()
    insert_session_query = """
    INSERT INTO sessions (user_id, session_id, start_time, end_time, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(
        insert_session_query,
        (user_id, session_id, start_time, end_time, created_at, updated_at),
    )
    conn.commit()
    cur.close()
    print(f"Session {session_id} inserted successfully.")


def session_exists(conn, user_id, session_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM sessions WHERE user_id = %s AND session_id = %s",
        (user_id, session_id),
    )
    exists = cur.fetchone() is not None
    cur.close()
    return exists


def session_valid(conn, user_id, session_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM sessions WHERE user_id = %s AND session_id = %s AND end_time > NOW()",
        (user_id, session_id),
    )
    exists = cur.fetchone() is not None
    cur.close()
    return exists


def session_continue(conn, user_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT session_id FROM sessions WHERE user_id = %s AND end_time > NOW() ORDER BY end_time DESC LIMIT 1",
        (user_id,)
    )
    session = cur.fetchone()
    cur.close()
    return session


def conversation(
    conn,
    message_id,
    session_id,
    user_id,
    inputs,
    token_input,
    outputs,
    token_output,
    total_token,
    timestamp,
    conversation_id,
):
    if not session_exists(conn, user_id, session_id):
        print(f"Session {session_id} does not exist.")
        return
    cur = conn.cursor()
    print(
        "all variables:",
        message_id,
        session_id,
        user_id,
        inputs,
        token_input,
        outputs,
        token_output,
        total_token,
        timestamp,
        conversation_id,
    )
    insert_conversation_query = """
    INSERT INTO conversation_logs (message_id, session_id, user_id, inputs, token_input, outputs, token_output, total_token, timestamp, conversation_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(
        insert_conversation_query,
        (
            message_id,
            session_id,
            user_id,
            inputs,
            token_input,
            outputs,
            token_output,
            total_token,
            timestamp,
            conversation_id,
        ),
    )
    print("Pass!")
    conn.commit()
    cur.close()
    print(f"Message {message_id} inserted successfully.")


def get_conversation(conn, user_id, session_id):
    if not session_exists(conn, user_id, session_id):
        print(f"Session {session_id} does not exist.")
        return
    cur = conn.cursor()
    cur.execute(
        "SELECT message_id FROM conversation_logs WHERE session_id = %s", (session_id,)
    )
    message_id = cur.fetchall()
    cur.close()
    return message_id


# update end_time in sessions table = NOW() + 30 minutes
def end_session(conn, user_id, session_id):
    if not session_exists(conn, user_id, session_id):
        print(f"Session {session_id} does not exist.")
        return
    cur = conn.cursor()
    cur.execute(
        "UPDATE sessions SET end_time = NOW() + INTERVAL '30 minutes' WHERE user_id = %s AND session_id = %s",
        (user_id, session_id),
    )
    conn.commit()
    cur.close()
    print(f"Session {session_id} ended successfully.")


def get_message_lastest_timestamp(conn, user_id, session_id):
    if not session_exists(conn, user_id, session_id):
        print(f"Session {session_id} does not exist.")
        return
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp FROM conversation_logs WHERE session_id = %s ORDER BY timestamp DESC LIMIT 1",
        (session_id,),
    )
    timestamp = cur.fetchone()
    cur.close()
    return timestamp


def get_transcripts(conn, user_id, session_id):
    if not session_exists(conn, user_id, session_id):
        print(f"Session {session_id} does not exist.")
        return
    cur = conn.cursor()
    cur.execute(
        "SELECT transcripts FROM transcripts WHERE session_id = %s and user_id = %s",
        (session_id, user_id),
    )
    transcripts = cur.fetchall()
    cur.close()
    return transcripts


def add_conversation(conn, conversation_id, session_id, user_id):
    if not session_exists(conn, user_id, session_id):
        print(f"Session {session_id} does not exist.")
        return
    cur = conn.cursor()
    insert_conversation_query = """
    INSERT INTO conversations (conversation_id, session_id, user_id)
    VALUES (%s, %s, %s)
    """
    cur.execute(insert_conversation_query, (conversation_id, session_id, user_id))
    conn.commit()
    cur.close()
    print(f"Conversation {conversation_id} inserted successfully.")


def get_conversation_id(conn, user_id, session_id):
    if not session_exists(conn, user_id, session_id):
        print(f"Session {session_id} does not exist.")
        return
    cur = conn.cursor()
    cur.execute(
        "SELECT conversation_id FROM conversations WHERE session_id = %s and user_id = %s",
        (session_id, user_id),
    )
    conversation_id = cur.fetchone()
    cur.close()
    return conversation_id


def write_feedback(conn, user_id, session_id, message_id, feedback_type, feedback_text):
    if not session_exists(conn, user_id, session_id):
        print(f"Session {session_id} does not exist.")
        return
    cur = conn.cursor()
    insert_feedback_query = """
    INSERT INTO feedback (user_id, session_id, message_id, feedback_type, feedback_text)
    VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(
        insert_feedback_query,
        (user_id, session_id, message_id, feedback_type, feedback_text),
    )
    conn.commit()
    cur.close()
    print(f"Feedback {message_id} inserted successfully.")


def error_logs(
    conn, user_id, session_id, conversation_id, input_message, error_message, error_code
):
    cur = conn.cursor()
    insert_error_logs = """
    INSERT INTO error_logs (user_id, session_id, conversation_id, input_message, error_message, error_code)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cur.execute(
        insert_error_logs,
        (
            user_id,
            session_id,
            conversation_id,
            input_message,
            error_message,
            error_code,
        ),
    )
    conn.commit()
    cur.close()
    print(f"Error log inserted successfully.")


def insert_file(
    conn,
    file_id,
    user_id,
    session_id,
    conversation_id,
    file_name,
    file_path,
    file_size,
    mime_type,
    created_by,
):
    cur = conn.cursor()
    created_at = updated_at = datetime.now()  # Sử dụng thời gian hiện tại
    insert_file_query = """
    INSERT INTO upload_files (file_id, user_id, session_id, conversation_id, file_name, file_path, file_size, mime_type, created_at, created_by, updated_at, updated_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(
        insert_file_query,
        (
            file_id,
            user_id,
            session_id,
            conversation_id,
            file_name,
            file_path,
            file_size,
            mime_type,
            created_at,
            created_by,
            updated_at,
            created_by,
        ),
    )
    conn.commit()
    cur.close()
    print(f"File {file_name} inserted successfully.")


def get_file(conn, file_id):
    cur = conn.cursor()
    get_file_query = """
    SELECT * FROM upload_files WHERE file_id = %s
    """
    cur.execute(get_file_query, (file_id,))
    file_info = cur.fetchone()
    cur.close()

    if file_info:
        print(f"File {file_info[4]} retrieved successfully.")
    else:
        print(f"File with ID {file_id} does not exist.")

    return (
        file_info  # Trả về thông tin file (có thể điều chỉnh cấu trúc dữ liệu trả về)
    )


def delete_file(conn, file_id):
    cur = conn.cursor()
    delete_file_query = """
    DELETE FROM upload_files WHERE file_id = %s
    """
    cur.execute(delete_file_query, (file_id,))
    conn.commit()
    cur.close()
    print(f"File {file_id} deleted successfully.")
