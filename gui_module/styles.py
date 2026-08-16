"""
m3uScan v21.5 GUI - Styling und Farbschema
"""

import tkinter as tk
from tkinter import ttk


# Farbschema
COLORS = {
    'ok': '#2ecc71',           # Grün
    'error': '#e74c3c',        # Rot
    'warning': '#f39c12',      # Orange
    'disabled': '#95a5a6',     # Grau
    'primary': '#3498db',      # Blau
    'background': '#ecf0f1',   # Helles Grau
    'text': '#2c3e50',         # Dunkles Grau
}

# Status-Icons
STATUS_ICONS = {
    'ok': '✓',
    'error': '✗',
    'warning': '⚠',
    'pending': '⧖',
}

# Status-Emojis
STATUS_EMOJIS = {
    'ok': '🟢',
    'error': '🔴',
    'warning': '🟡',
    'expired': '⏱️',
    'warning_soon': '⚠️',
}


def setup_styles():
    """Konfiguriere ttk Styles"""
    style = ttk.Style()

    # Definiere Custom Styles
    style.theme_use('clam')

    # Farben für verschiedene Zustände
    style.configure('Success.TLabel', foreground=COLORS['ok'], font=('Arial', 10, 'bold'))
    style.configure('Error.TLabel', foreground=COLORS['error'], font=('Arial', 10, 'bold'))
    style.configure('Warning.TLabel', foreground=COLORS['warning'], font=('Arial', 10, 'bold'))
    style.configure('Info.TLabel', foreground=COLORS['primary'], font=('Arial', 10))

    # Button Styles
    style.configure('Success.TButton',
        foreground=COLORS['ok'],
        background=COLORS['background'],
        font=('Arial', 10)
    )
    style.configure('Accent.TButton',
        foreground=COLORS['primary'],
        background=COLORS['background'],
        font=('Arial', 10, 'bold')
    )

    # Frame und Label Styles
    style.configure('TFrame', background=COLORS['background'])
    style.configure('TLabel', background=COLORS['background'], foreground=COLORS['text'])
    style.configure('Title.TLabel', font=('Arial', 14, 'bold'), foreground=COLORS['text'])

    # Treeview Style
    style.configure('Treeview',
        rowheight=25,
        font=('Arial', 9),
        foreground=COLORS['text'],
        background='white'
    )
    style.configure('Treeview.Heading',
        font=('Arial', 10, 'bold'),
        foreground=COLORS['primary']
    )

    # Notebook (Tab) Style
    style.configure('TNotebook', background=COLORS['background'])
    style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 10))

    return style


def get_status_color(status: str) -> str:
    """Gebe Farbe basierend auf Status zurück"""
    if status == "ok" or status == "active":
        return COLORS['ok']
    elif status == "error" or status == "expired":
        return COLORS['error']
    elif status == "warning":
        return COLORS['warning']
    else:
        return COLORS['disabled']


def get_status_icon(status: str, emoji: bool = True) -> str:
    """Gebe Icon/Emoji basierend auf Status zurück"""
    if emoji:
        return STATUS_EMOJIS.get(status, '?')
    else:
        return STATUS_ICONS.get(status, '?')


def format_status_text(status: str, emoji: bool = True) -> str:
    """Formatiere Status-Text mit Icon"""
    icon = get_status_icon(status, emoji)
    return f"{icon} {status.upper()}"
