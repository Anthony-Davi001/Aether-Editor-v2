"""
Syntax Highlighting Engine - Markdown & Theme Management.

This module provides real-time Markdown syntax highlighting and visual theme 
configuration for a Tkinter text widget. It parses standard Markdown formatting 
(headers, bold, italics, code blocks, lists, and links) using regular expressions 
and applies dynamic color schemes through custom Tkinter text tags.

Author: Anthony Davi <anthonyvieira789@gmail.com>
"""

import re
import tkinter as tk

class SyntaxHighlighter:
    """Handles Markdown syntax highlighting and theme colors for the text editor.

    This class encapsulates the logic for parsing Markdown syntax using regular
    expressions and applying Tkinter text tags to format the text dynamically.

    Attributes:
        text_widget (tk.Text): The Tkinter text widget being styled.
        colors (dict): A dictionary mapping syntax elements to their hex color codes.
    """

    def __init__(self, text_widget: tk.Text):
        """Initializes the highlighter with a reference to the text widget.

        Args:
            text_widget (tk.Text): The editor widget where highlighting will be applied.
        """
        self.text_widget = text_widget
        self.colors = {}
        self.set_theme("light")

    def set_theme(self, theme_name: str):
        """Updates the color palette based on the selected theme (light/dark).

        This method changes the background and foreground of the text widget itself,
        updates the internal color dictionary, and forces a refresh of the text tags.

        Args:
            theme_name (str): The name of the theme to apply (e.g., "dark" or "light").
        """
        if theme_name == "dark":
            self.text_widget.config(bg="#1e1e1e", fg="#ffffff", insertbackground="white")
            self.colors = {
                "header": "#79c0ff",
                "bold": "#ff7b72",
                "italic": "#d2a8ff",
                "code": "#7ee787",
                "code_bg": "#2a2a2a",
                "list": "#ffa657",
                "link": "#58a6ff"
            }
        else:
            self.text_widget.config(bg="#ffffff", fg="#000000", insertbackground="black")
            self.colors = {
                "header": "#005cc5",
                "bold": "#d73a49",
                "italic": "#6f42c1",
                "code": "#22863a",
                "code_bg": "#f0f0f0",
                "list": "#e36209",
                "link": "#0366d6"
            }
        
        self._apply_tag_styles()
        self.apply_highlighting()

    def _apply_tag_styles(self):
        """Configures Tkinter text tags with the current color palette.
        
        Maps tag names (like 'header', 'bold') to their visual representations 
        (fonts, colors, and backgrounds) inside the text widget.
        """
        self.text_widget.tag_configure("header", foreground=self.colors["header"], font=("Consolas", 12, "bold"))
        self.text_widget.tag_configure("bold", foreground=self.colors["bold"], font=("Consolas", 11, "bold"))
        self.text_widget.tag_configure("italic", foreground=self.colors["italic"], font=("Consolas", 11, "italic"))
        self.text_widget.tag_configure("code", foreground=self.colors["code"], background=self.colors["code_bg"])
        self.text_widget.tag_configure("list", foreground=self.colors["list"], font=("Consolas", 11, "bold"))
        self.text_widget.tag_configure("link", foreground=self.colors["link"], underline=True)

    def apply_highlighting(self):
        """Parses the text and applies the appropriate Markdown tags.

        Removes all existing syntax tags, evaluates the entire text content against
        predefined Regex patterns, and reapplies the tags to style the document.
        """
        content = self.text_widget.get("1.0", tk.END)

        for tag in ["header", "bold", "italic", "code", "list", "link"]:
            self.text_widget.tag_remove(tag, "1.0", tk.END)

        patterns = [
            ("header", r"^#+ .*$"),                     
            ("bold", r"\*\*.*?\*\*|__.*?__"),           
            ("italic", r"\*.*?\*|_.*?_"),            
            ("code", r"```[\s\S]*?```|`.*?`"),           
            ("list", r"^\s*([*+-]|\d+\.)\s"),           
            ("link", r"\[.*?\]\(.*?\)")                 
        ]

        # Apply tags based on regex matches
        for tag_name, pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.text_widget.tag_add(tag_name, start, end)