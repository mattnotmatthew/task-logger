# views/utils/helpers.py

import tkinter as tk
from tkinter import ttk
from constants import COLORS

def create_button(parent, text, command, button_type="default", width=None, padx=10, pady=5):
    """
    Create a standardized button with consistent styling based on type
    
    Args:
        parent: Parent widget
        text: Button text
        command: Button command callback
        button_type: One of "default", "primary", "success", "warning", "danger"
        width: Optional width for the button
        padx: Horizontal padding
        pady: Vertical padding
        
    Returns:
        The configured button widget
    """
    button_styles = {
        "default": {
            "bg": COLORS["secondary"],
            "fg": COLORS["text"],
            "font": ("Arial", 10),
            "bold": False
        },
        "primary": {
            "bg": COLORS["primary"],
            "fg": COLORS["background"],
            "font": ("Arial", 10),
            "bold": True
        },
        "success": {
            "bg": COLORS["success"],
            "fg": COLORS["background"],
            "font": ("Arial", 10),
            "bold": True
        },
        "warning": {
            "bg": COLORS["warning"],
            "fg": COLORS["text"],
            "font": ("Arial", 10),
            "bold": True
        },
        "danger": {
            "bg": COLORS["danger"],
            "fg": COLORS["background"],
            "font": ("Arial", 10),
            "bold": True
        }
    }
    
    style = button_styles.get(button_type, button_styles["default"])
    font = (style["font"][0], style["font"][1], "bold" if style["bold"] else "normal")
    
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg=style["bg"],
        fg=style["fg"],
        font=font,
        relief=tk.RAISED,
        borderwidth=2,
        padx=padx,
        pady=pady
    )
    
    if width:
        button.config(width=width)
        
    return button

def create_label(parent, text, style="default", anchor="w", pady=(0, 5)):
    """
    Create a standardized label with consistent styling
    
    Args:
        parent: Parent widget
        text: Label text
        style: One of "default", "header", "subheader", "small"
        anchor: Text anchor position
        pady: Vertical padding
        
    Returns:
        The configured label widget
    """
    label_styles = {
        "default": {
            "font": ("Arial", 10),
            "fg": COLORS["text"],
            "bold": False
        },
        "header": {
            "font": ("Arial", 14),
            "fg": COLORS["primary"],
            "bold": True
        },
        "subheader": {
            "font": ("Arial", 12),
            "fg": COLORS["text"],
            "bold": True
        },
        "small": {
            "font": ("Arial", 8),
            "fg": COLORS["light_text"],
            "bold": False
        }
    }
    
    style_config = label_styles.get(style, label_styles["default"])
    font = (style_config["font"][0], style_config["font"][1], "bold" if style_config["bold"] else "normal")
    
    label = tk.Label(
        parent,
        text=text,
        font=font,
        fg=style_config["fg"],
        bg=COLORS["background"]
    )
    
    label.pack(anchor=anchor, pady=pady)
    return label

def create_entry(parent, textvariable=None, width=45, pady=5):
    """
    Create a standardized entry field
    
    Args:
        parent: Parent widget
        textvariable: Optional StringVar for the entry
        width: Entry width
        pady: Vertical padding
        
    Returns:
        The configured entry widget
    """
    entry = tk.Entry(
        parent,
        textvariable=textvariable,
        width=width,
        font=("Arial", 10),
        bd=2,
        relief=tk.GROOVE
    )
    
    entry.pack(fill="x", pady=pady)
    return entry

def create_combobox(parent, textvariable, values=None, width=45, pady=5):
    """
    Create a standardized combobox
    
    Args:
        parent: Parent widget
        textvariable: StringVar for the combobox
        values: List of values for the dropdown
        width: Combobox width
        pady: Vertical padding
        
    Returns:
        The configured combobox widget
    """
    if values is None:
        values = []
        
    if values:
        textvariable.set(values[0])
    else:
        textvariable.set("")
        
    combobox = ttk.Combobox(
        parent,
        textvariable=textvariable,
        values=values,
        width=width
    )
    
    combobox.pack(fill="x", pady=pady)
    return combobox