import sqlite3
from config import DB_PATH

def get_db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            thumbnail TEXT,
            duration INTEGER,
            link TEXT,
            actions TEXT,
            method TEXT,
            instructions TEXT,
            status TEXT DEFAULT 'pending',
            assigned_to INTEGER DEFAULT NULL,
            proof TEXT DEFAULT NULL,
            verified_by_owner INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            reported_by INTEGER,
            reason TEXT,
            proof_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# User functions
def add_user(user_id, username):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?,?)", (user_id, username))
    conn.commit()
    conn.close()

def user_video_count(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM videos WHERE user_id = ?", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def insert_video(user_id, title, thumbnail, duration, link, actions, method, instructions):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO videos (user_id, title, thumbnail, duration, link, actions, method, instructions)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (user_id, title, thumbnail, duration, link, actions, method, instructions))
    conn.commit()
    conn.close()

def get_user_videos(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE user_id = ?", (user_id,))
    videos = c.fetchall()
    conn.close()
    return videos

def delete_video(video_id, user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM videos WHERE id = ? AND user_id = ?", (video_id, user_id))
    conn.commit()
    conn.close()

def assign_video_to_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM videos
        WHERE user_id != ? AND status = 'pending' AND assigned_to IS NULL
        ORDER BY RANDOM() LIMIT 1
    ''', (user_id,))
    video = c.fetchone()
    if video:
        c.execute("UPDATE videos SET assigned_to = ? WHERE id = ?", (user_id, video[0]))
        conn.commit()
    conn.close()
    return video

def get_task_for_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE assigned_to = ? AND status IN ('pending','assigned')", (user_id,))
    video = c.fetchone()
    conn.close()
    return video

def submit_proof(video_id, file_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE videos SET proof = ?, status = 'proof_uploaded' WHERE id = ?", (file_id, video_id))
    conn.commit()
    conn.close()

def get_proofs_for_owner(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE user_id = ? AND status = 'proof_uploaded'", (user_id,))
    proofs = c.fetchall()
    conn.close()
    return proofs

def verify_proof(video_id, accept):
    conn = get_db()
    c = conn.cursor()
    new_status = 'verified' if accept else 'pending'
    c.execute("UPDATE videos SET verified_by_owner = ?, status = ? WHERE id = ?", (1 if accept else 0, new_status, video_id))
    conn.commit()
    conn.close()

def unassign_task(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE videos SET assigned_to = NULL WHERE assigned_to = ? AND status = 'pending'", (user_id,))
    conn.commit()
    conn.close()

def report_proof(video_id, reported_by, reason, proof_link):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO reports (video_id, reported_by, reason, proof_link) VALUES (?,?,?,?)", (video_id, reported_by, reason, proof_link))
    conn.commit()
    conn.close()

def get_reports_for_admin():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM reports")
    reports = c.fetchall()
    conn.close()
    return reports