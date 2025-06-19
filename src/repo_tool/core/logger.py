"""
Logging configuration for RepoTool
"""
import logging
from pathlib import Path
import sys
from typing import Optional
from logging.handlers import RotatingFileHandler

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = Path.home() / ".local" / "share" / "repo_tool" / "logs"
LOG_FILE = LOG_DIR / "repo_tool.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3

def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Set up and return a configured logger"""
    logger = logging.getLogger(name or "repo_tool")
    
    if logger.handlers:  # Logger already configured
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger by name"""
    return logging.getLogger(name)

