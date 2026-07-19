import sqlite3
from app.core.config import settings
from typing import List, Dict, Any

class TimeMachineEngine:
    def __init__(self):
        # Establish connection to metadata SQLite database
        # Convert Database URL (sqlite:///./iml_metadata.db) to filename
        db_path = settings.DATABASE_URL.replace("sqlite:///", "")
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        """
        Creates the snapshots table if it doesn't exist.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                scroll_depth_percent REAL DEFAULT 0.0,
                trigger_event TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def save_snapshot(self, url: str, title: str, scroll_depth: float, trigger: str, timestamp: str):
        """
        Appends a state snapshot to the database log.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO timeline_snapshots (url, title, scroll_depth_percent, trigger_event, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (url, title, scroll_depth, trigger, timestamp))
        self.conn.commit()

    def get_replay_session(self, date_str: str) -> List[Dict[str, Any]]:
        """
        Retrieves browsing history snapshots matching a specific date (YYYY-MM-DD).
        """
        cursor = self.conn.cursor()
        # Simple date matching string check
        cursor.execute("""
            SELECT url, title, scroll_depth_percent, trigger_event, timestamp 
            FROM timeline_snapshots 
            WHERE timestamp LIKE ? 
            ORDER BY timestamp ASC
        """, (f"{date_str}%",))
        
        rows = cursor.fetchall()
        snapshots = []
        for r in rows:
            snapshots.append({
                "url": r[0],
                "title": r[1],
                "scroll_depth_percent": r[2],
                "trigger_event": r[3],
                "timestamp": r[4]
            })
        return snapshots

time_machine_engine = TimeMachineEngine()
