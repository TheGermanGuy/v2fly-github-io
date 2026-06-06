"""
m3uScan v21.5 Kivy - App Constants
"""

import os
from kivy.metrics import dp

# App Metadata
APP_NAME = "m3uScan v21.5"
APP_VERSION = "21.5-kivy"
APP_AUTHOR = "TheGermanGuy™"

# Data Directories
DATA_DIR = os.path.expanduser("~/.m3uscan")
LEDGER_FILE = os.path.join(DATA_DIR, "link_ledger.json")
BACKUPS_DIR = os.path.join(DATA_DIR, "backups")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUPS_DIR, exist_ok=True)

# UI Dimensions
BUTTON_HEIGHT_DP = 48  # Android minimum touch target
DIALOG_WIDTH = 0.9
DIALOG_HEIGHT = 0.7

# Timeouts
NETWORK_TIMEOUT = 5  # seconds
CACHE_TTL = 3600    # 1 hour

# Colors (Dark Mode Default)
THEME_DARK = {
    'primary': '#1976D2',
    'primary_dark': '#1565C0',
    'accent': '#FF5722',
    'background': '#121212',
    'surface': '#1E1E1E',
    'text': '#FFFFFF',
    'text_secondary': '#B0BEC5',
    'error': '#CF6679',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'info': '#29B6F6',
}

THEME_LIGHT = {
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'accent': '#FF5722',
    'background': '#FAFAFA',
    'surface': '#FFFFFF',
    'text': '#212121',
    'text_secondary': '#757575',
    'error': '#B71C1C',
    'success': '#388E3C',
    'warning': '#F57C00',
    'info': '#0277BD',
}

# Status Icons & Emojis
STATUS_ICONS = {
    'ok': '✓',
    'error': '✗',
    'warning': '⚠',
    'pending': '⧖',
}

STATUS_EMOJIS = {
    'ok': '🟢',
    'error': '🔴',
    'warning': '🟡',
    'pending': '⏳',
    'offline': '⛔',
}

# Feature Flags
ENABLE_DARK_MODE_DEFAULT = True
ENABLE_OFFLINE_MODE = True
ENABLE_NOTIFICATIONS = True

# Batch Check Settings
BATCH_CHECK_TIMEOUT = 30  # seconds
BATCH_CHECK_WORKERS = 4

# Cache Settings
MAX_CACHE_SIZE = 100  # MB
CACHE_CLEANUP_INTERVAL = 3600  # seconds
