"""
Aether Editor - Editor Controller.

This module acts as the mediator between the Editor Model and View components,
handling user interactions, auto-saving, and asynchronous rendering.

Author: Anthony Davi <anthonyvieira789@gmail.com>
"""

import threading
from .constants import EXAMPLE_MD

class EditorController:
    """Controller class that connects the Editor Model and View.

    This class follows the Mediator pattern, isolating the graphical interface (View)
    from the business logic and file management (Model). It listens for user actions
    triggered in the View, updates the Model accordingly, and pushes the new state
    back to the View.

    Attributes:
        model (EditorModel): The model instance handling business logic, state management,
            and file operations.
        view (EditorView): The view instance managing the graphical user interface components
            and user event bindings.
    """

    def __init__(self, model, view):
        """"Initializes the EditorController with model and view instances.

        Binds the controller to the view so the view can delegate events back to
        this controller. It also triggers the initial setup of the editor interface.

        Args:
            model (EditorModel): The application model instance.
            view (EditorView): The application view instance.
        """
        self.model = model
        self.view = view
        
        self.view.set_controller(self)
        self._init_editor()

    def _init_editor(self):
        """Initializes the editor view with default settings and content.

        This method populates the text area with a default example markdown,
        syncs the window title with the model's current state, and triggers
        the first render pass for the outline and PDF preview.
        """

        self.view.set_text(EXAMPLE_MD)
        self.view.update_window_title(self.model.get_title_file_name())
        self.handle_text_changed()

    def handle_text_changed(self):
        """Handles real-time text change events originating from the View.

        This core utility method runs whenever the user types, simultaneously 
        refreshing the document outline based on the new text and attempting 
        to auto-save the document if it is already linked to a file path. 
        Additionally, it spawns a background thread to generate the PDF preview 
        without freezing the main UI thread.

        Raises:
            IOError: If the auto-save operation fails due to disk or permission issues.
                Note: This exception is caught internally and printed to stdout to 
                prevent interrupting the user's typing experience.
        """

        md_text = self.view.get_text()
        self.view.update_outline(md_text)

        if self.model.current_file_path:
            try:
                self.model.save_md(self.model.current_file_path, md_text)
            except Exception as e:
                print(f"Auto-save error: {e}")

        if not md_text:
            self.view.update_preview(None)
            return

        threading.Thread(target=self._async_generate_pdf, args=(md_text,), daemon=True).start()

    def handle_new_md(self):
        """Handles the creation of a new, blank Markdown document.

        Utility used when the user requests a new tab or file. It resets the underlying
        model to an empty state, clears the View's text area, and resets the window title
        to an 'Untitled' state.
        """

        self.model.create_new_md()
        self.view.set_text("")
        self.view.update_window_title(self.model.get_title_file_name())
        self.handle_text_changed()

    def _async_generate_pdf(self, md_text: str):
        """Generates a PDF asynchronously and updates the view preview.

        This method is designed to be run in a separate thread. It delegates the heavy
        lifting of PDF compilation to the model and passes the resulting binary data
        back to the view for rendering.

        Args:
            md_text (str): The raw Markdown text to be converted into a PDF.

        Raises:
            ValueError: If the markdown parsing fails or contains invalid syntax.
            Exception: Any unexpected error from the PDF generation engine.
                Note: Caught internally and printed to stdout.
        """

        try:
            pdf_bytes = self.model.generate_pdf_bytes(md_text)
            self.view.update_preview(pdf_bytes)
        except Exception as e:
            print(f"PDF generation error: {e}")

    def handle_open_md(self):
        """Handles the routine for opening an existing Markdown file.

        Prompts the user with a file dialog. If a file is selected, it delegates
        reading to the model, injects the content into the UI, updates the file explorer
        tree, and refreshes the preview.

        Raises:
            FileNotFoundError: If the selected file is moved or deleted before reading.
            PermissionError: If the user lacks read permissions for the file.
                Note: Caught internally and displayed to the user via an error dialog.
        """

        file_path = self.view.ask_open_md_file()
        if file_path:
            try:
                content = self.model.open_md(file_path)
                self.view.set_text(content)
                self.view.add_file_to_tree(file_path)
                self.view.update_window_title(self.model.get_title_file_name())
                self.handle_text_changed()
            except Exception as e:
                self.view.show_message("Error", f"Failed to open file:\n{e}", "error")

    def handle_select_file(self, file_path: str):
        """Handles context switching when a user selects a different file in the UI.

        This utility ensures that before switching to a new file, the current file's
        unsaved content is preserved in the model's memory. It then loads the requested
        file's content into the active View.

        Args:
            file_path (str): The absolute or relative path of the file being selected.
        """

        if file_path == self.model.current_file_path:
            return

        if self.model.current_file_path:
            self.model.set_document_content(self.model.current_file_path, self.view.get_text())

        if file_path in self.model.open_documents:
            content = self.model.get_document_content(file_path)
            self.model.current_file_path = file_path
            self.view.set_text(content)
            self.view.update_window_title(self.model.get_title_file_name())
            self.handle_text_changed()

    def handle_save_md(self):
        """Saves the active Markdown document persistently to disk.

        If the document is new (has no linked file path), it prompts the user with
        a 'Save As' dialog. Otherwise, it overwrites the existing file. It also
        provides visual feedback (success/error messages) based on the operation's result.

        Raises:
            PermissionError: If the application lacks write access to the destination.
            OSError: For general disk errors (e.g., disk full).
                Note: Caught internally and displayed via an error dialog.
        """

        md_text = self.view.get_text()
        file_path = self.model.current_file_path or self.view.ask_save_md_file(self.model.get_title_file_name())
        
        if file_path:
            try:
                self.model.save_md(file_path, md_text)
                self.view.add_file_to_tree(file_path)
                self.view.update_window_title(self.model.get_title_file_name())
                self.view.show_message("Success", f"File saved successfully at:\n{file_path}", "info")
            except Exception as e:
                self.view.show_message("Error", f"Failed to save file:\n{e}", "error")

    def handle_export(self):
        """Compiles and exports the active Markdown document as a PDF file.

        This utility validates that the document is not empty, prompts the user
        for a destination directory, generates the raw PDF bytes, and handles the
        I/O operation to write those bytes to the disk.

        Raises:
            IOError: If there's an issue writing the binary PDF data to the disk.
            Exception: If the PDF generation engine fails to compile the document.
                Note: Caught internally and displayed via an error dialog.
        """
        md_text = self.view.get_text()
        
        if not md_text:
            self.view.show_message("Warning", "The document is empty!", "warning")
            return

        default_pdf_name = self.model.get_title_file_name().replace(".md", ".pdf")
        file_path = self.view.ask_save_pdf_file(default_pdf_name)
        
        if file_path:
            try:
                pdf_bytes = self.model.generate_pdf_bytes(md_text)
                with open(file_path, "wb") as f:
                    f.write(pdf_bytes)
                self.view.show_message("Success", f"PDF exported successfully at:\n{file_path}", "info")
            except Exception as e:
                self.view.show_message("Error", f"Failed to export PDF:\n{e}", "error")