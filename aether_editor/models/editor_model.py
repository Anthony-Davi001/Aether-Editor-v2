"""
Aether Editor - Editor Model.

This module is responsible for the application's data layer. It handles file I/O,
document state management in memory, and the conversion engine (Markdown to PDF).

Author: Anthony Davi <anthonyvieira789@gmail.com>
"""

import io
import os
import markdown
from xhtml2pdf import pisa
from pygments.formatters import HtmlFormatter

class EditorModel:
    """Model class for managing application state, file I/O, and data conversion.

    This class acts as the single source of truth for the document's data. It abstracts
    away file system interactions and heavy processing tasks (like PDF generation) from 
    the controller and the view.

    Attributes:
        current_file_path (str | None): The absolute path of the currently active document.
            Remains None if the document has not been saved yet.
        open_documents (dict): A dictionary acting as an in-memory cache for open files.
            Keys are file paths (str) and values are the Markdown text (str).
    """

    def __init__(self):
        """Initializes the EditorModel.

        Sets up the initial empty state, preparing the memory cache for document content
        and ensuring no file path is actively tracked on startup.
        """

        self.current_file_path = None
        self.open_documents = {}  

    def set_document_content(self, file_path: str, content: str):
        """Caches document content in memory without writing to disk.

        This utility is primarily used when switching between open tabs or files.
        It preserves unsaved work in the `open_documents` cache so the user doesn't
        lose their progress when navigating away from a document.

        Args:
            file_path (str): The path of the file to associate the content with.
            content (str): The raw Markdown text to be stored in memory.
        """
        if file_path:
            self.open_documents[file_path] = content

    def get_document_content(self, file_path: str) -> str:
        """Retrieves the cached content for a specific file path from memory.

        Used to restore a document's state in the editor when the user switches
        back to an already opened file, skipping unnecessary disk reads.

        Args:
            file_path (str): The path of the requested file.

        Returns:
            str: The stored Markdown content, or an empty string if the file
                is not found in the cache.
        """
        return self.open_documents.get(file_path, "")

    def generate_pdf_bytes(self, md_content: str) -> bytes:
        """Converts Markdown content into styled PDF binary data.

        This is a heavy processing utility. It first compiles the Markdown (along with
        extensions like fenced code blocks) into HTML, injects custom CSS styling 
        (including Pygments for syntax highlighting), and then uses xhtml2pdf to 
        render an A4 formatted PDF into an in-memory buffer.

        Args:
            md_content (str): The raw Markdown text to be converted.

        Returns:
            bytes: The binary data of the generated PDF file.

        Raises:
            RuntimeError: If the xhtml2pdf engine encounters a critical error during 
                the HTML-to-PDF conversion process.
        """
        pygments_css = HtmlFormatter(style='default').get_style_defs('.codehilite')

        html_text = markdown.markdown(
            md_content, 
            extensions=['extra', 'fenced_code', 'codehilite']
        )
        
        styled_html = f"""
        <html>
        <head>
            <style>
                @page {{ size: a4 portrait; margin: 2cm; }}
                body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #333333; }}
                h1 {{ color: #1a2a3a; border-bottom: 1px solid #1a2a3a; padding-bottom: 5px; }}
                h2 {{ color: #2c3e50; margin-top: 15px; }}
                {pygments_css}
                .codehilite {{ background-color: #f8f8f8; border: 1px solid #e0e0e0; border-radius: 4px; padding: 10px; margin: 15px 0; width: 100%; display: block; }}
                .codehilite pre {{ font-family: Courier, monospace; font-size: 9.5pt; line-height: 1.4; margin: 0; width: 100%; }}
                :not(pre) > code {{ background-color: #f4f4f4; font-family: Courier, monospace; padding: 2px 4px; border-radius: 3px; color: #d63384; }}
                blockquote {{ background-color: #f9f9f9; border-left: 4px solid #ccc; margin: 10px 0; padding: 8px; }}
            </style>
        </head>
        <body>
            {html_text}
        </body>
        </html>
        """
        
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(io.StringIO(styled_html), dest=pdf_buffer)
        
        if pisa_status.err:
            raise RuntimeError("Error in pdf engine")
            
        return pdf_buffer.getvalue()

    def open_md(self, file_path: str) -> str:
        """Reads a Markdown file from disk into memory and sets it as active.

        This operation handles disk I/O to load external files. Once read, it caches
        the content in `open_documents` and sets the `current_file_path` context.

        Args:
            file_path (str): The absolute or relative path to the Markdown file.

        Returns:
            str: The raw string content extracted from the file.

        Raises:
            FileNotFoundError: If the specified file does not exist on disk.
            PermissionError: If the application lacks read permissions for the file.
            UnicodeDecodeError: If the file is not encoded in valid UTF-8.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.current_file_path = file_path
        self.open_documents[file_path] = content
        return content

    def save_md(self, file_path: str, content: str):
        """Writes Markdown content to a file on disk.

        Handles persistent disk I/O. After a successful write, it updates both the
        active file context (`current_file_path`) and the in-memory cache to ensure
        the application state remains synchronized with the file system.

        Args:
            file_path (str): The destination path where the file will be saved.
            content (str): The text content to write to the file.

        Raises:
            PermissionError: If the application lacks write access to the directory.
            OSError: For general I/O failures, such as disk full or read-only drives.
        """

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        self.current_file_path = file_path
        self.open_documents[file_path] = content

    def get_title_file_name(self) -> str:
        """Extracts the base filename to be used as a display title.

        A UI helper function that determines what should be shown in window borders
        or tabs. It strips away the folder structure, leaving only the file name.

        Returns:
            str: The base name of the current file (e.g., 'document.md'), or 
                'No title.md' if no file is currently active.
        """

        if self.current_file_path:
            return os.path.basename(self.current_file_path)
        return "No title.md"

    def create_new_md(self):
        """Resets the model state for a new, unsaved Markdown document.

        This method detaches the editor from any existing file path, ensuring that
        subsequent save operations prompt the user for a new file location rather
        than overwriting an existing file.
        """
        self.current_file_path = None