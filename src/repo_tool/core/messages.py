"""
Message center for RepoTool
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum
import json
from pathlib import Path
import sqlite3
from .logger import get_logger

logger = get_logger(__name__)

class MessageType(Enum):
    """Types of messages"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"

@dataclass
class Message:
    """Message data structure"""
    type: MessageType
    text: str
    timestamp: datetime
    source: str
    details: Optional[dict] = None
    progress: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert message to dictionary"""
        return {
            "type": self.type.value,
            "text": self.text,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "details": json.dumps(self.details) if self.details else None,
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """Create message from dictionary"""
        return cls(
            type=MessageType(data["type"]),
            text=data["text"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data["source"],
            details=json.loads(data["details"]) if data["details"] else None,
            progress=data["progress"]
        )

class MessageCenter:
    """Central message management system"""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize message center
        
        Args:
            db_path: Path to the message database. If None, uses default location.
        """
        if db_path is None:
            db_path = Path.home() / ".local" / "share" / "repo_tool" / "messages.db"
            
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize the message database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    text TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    details TEXT,
                    progress REAL
                )
            """)
            conn.commit()
            
    def add_message(
        self,
        text: str,
        type: MessageType = MessageType.INFO,
        source: str = "system",
        details: Optional[dict] = None,
        progress: Optional[float] = None
    ) -> Message:
        """Add a new message
        
        Args:
            text: Message text
            type: Message type
            source: Message source
            details: Additional details as dictionary
            progress: Progress value (0-100)
            
        Returns:
            Message: The created message
        """
        message = Message(
            type=type,
            text=text,
            timestamp=datetime.now(),
            source=source,
            details=details,
            progress=progress
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO messages
                (type, text, timestamp, source, details, progress)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    message.type.value,
                    message.text,
                    message.timestamp.isoformat(),
                    message.source,
                    json.dumps(message.details) if message.details else None,
                    message.progress
                )
            )
            conn.commit()
            
        logger.info(f"New message: [{message.type.value}] {message.text}")
        return message
        
    def get_messages(
        self,
        limit: Optional[int] = None,
        type: Optional[MessageType] = None,
        source: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Message]:
        """Get messages with optional filtering
        
        Args:
            limit: Maximum number of messages to return
            type: Filter by message type
            source: Filter by message source
            since: Only return messages after this timestamp
            
        Returns:
            List[Message]: List of messages matching criteria
        """
        query = "SELECT * FROM messages WHERE 1=1"
        params = []
        
        if type:
            query += " AND type = ?"
            params.append(type.value)
            
        if source:
            query += " AND source = ?"
            params.append(source)
            
        if since:
            query += " AND timestamp > ?"
            params.append(since.isoformat())
            
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT ?"
            params.append(limit)
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
        messages = []
        for row in rows:
            messages.append(Message(
                type=MessageType(row[1]),
                text=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                source=row[4],
                details=json.loads(row[5]) if row[5] else None,
                progress=row[6]
            ))
            
        return messages
        
    def clear_messages(
        self,
        older_than: Optional[datetime] = None,
        type: Optional[MessageType] = None,
        source: Optional[str] = None
    ) -> int:
        """Clear messages based on criteria
        
        Args:
            older_than: Clear messages older than this timestamp
            type: Clear messages of this type
            source: Clear messages from this source
            
        Returns:
            int: Number of messages cleared
        """
        query = "DELETE FROM messages WHERE 1=1"
        params = []
        
        if older_than:
            query += " AND timestamp < ?"
            params.append(older_than.isoformat())
            
        if type:
            query += " AND type = ?"
            params.append(type.value)
            
        if source:
            query += " AND source = ?"
            params.append(source)
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.rowcount
            
    def update_progress(
        self,
        source: str,
        progress: float,
        text: Optional[str] = None
    ) -> None:
        """Update progress for a source
        
        Args:
            source: Message source
            progress: New progress value (0-100)
            text: Optional new message text
        """
        with sqlite3.connect(self.db_path) as conn:
            if text:
                conn.execute(
                    """
                    UPDATE messages
                    SET progress = ?, text = ?
                    WHERE source = ?
                    AND type = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """,
                    (progress, text, source, MessageType.PROGRESS.value)
                )
            else:
                conn.execute(
                    """
                    UPDATE messages
                    SET progress = ?
                    WHERE source = ?
                    AND type = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """,
                    (progress, source, MessageType.PROGRESS.value)
                )
            conn.commit()
            
    def get_latest_progress(self, source: str) -> Optional[float]:
        """Get latest progress for a source
        
        Args:
            source: Message source
            
        Returns:
            Optional[float]: Latest progress value or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT progress
                FROM messages
                WHERE source = ?
                AND type = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (source, MessageType.PROGRESS.value)
            )
            row = cursor.fetchone()
            return row[0] if row else None

