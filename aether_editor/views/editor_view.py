"""
Aether Editor - Editor View.

This module contains the Graphical User Interface (GUI) components of the application.
It uses tkinter for the main window, layout, and event handling, while delegating 
specific rendering tasks to specialized sub-components (Highlighting and PDF Preview).

Author: Anthony Davi <anthonyvieira789@gmail.com>
"""

import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox

import sv_ttk

from .pdf_previwer import PDFPreviewer
from .syntax_highlighter import SyntaxHighlighter

class EditorView:
    """Main Graphical User Interface for the Aether Editor.

    This class handles the creation of the application window, layout construction,
    menus, and event bindings. It acts as the View in an MVC/Mediator architecture,
    sending user interactions to the Controller and displaying updates.

    Attributes:
        root (tk.Tk): The root window of the application.
        controller: A reference to the EditorController.
        timer (str): Tkinter after ID used to debounce keystrokes.
        open_files (dict): Maps file paths to their Treeview item IDs.
        highlighter (SyntaxHighlighter): Handles Markdown syntax styling.
        previewer (PDFPreviewer): Handles rendering the PDF preview.
    """

    def __init__(self, root):
        """Initializes the view, sets up the main layout, and binds events.

        Args:
            root (tk.Tk): The main Tkinter application window.
        """
        
        self.root = root
        self.root.title("Aether Editor - Untitled.md")
        self.root.geometry("1300x750")

        self.controller = None
        self.timer = None
        self.open_files = {}

        self._setup_ui()
        
        self.highlighter = SyntaxHighlighter(self.text_editor)
        self.previewer = PDFPreviewer(self.canvas)

        self._bind_shortcuts()

    def set_controller(self, controller):
        """Injects the controller dependency into the view.

        Args:
            controller: The EditorController instance managing application logic.
        """

        self.controller = controller

    def update_window_title(self, file_name: str):
        """Updates the title bar of the main window.

        Args:
            file_name (str): The name of the currently active file.
        """

        self.root.title(f"Aether Editor - {file_name}")

    def _setup_ui(self):
        """Builds the main window layout, menus, and widgets.

        Constructs a PanedWindow containing three main areas: a sidebar notebook
        with Outline and File tree tabs, an editor pane utilizing a Text widget
        for Markdown, and a preview pane using a Canvas widget for PDF rendering.
        """

        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open MD...", accelerator="Ctrl+O", command=self.on_open_md_click)
        file_menu.add_command(label="Save MD...", accelerator="Ctrl+S", command=self.on_save_md_click)
        file_menu.add_command(label="New MD", accelerator="Ctrl+N", command=self.on_new_md_click)
        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF...", accelerator="Ctrl+E", command=self.on_export_click)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme (Light/Dark)", accelerator="Ctrl+T", command=self.toggle_theme)

        self.paned = ttk.PanedWindow(self.root, orient="horizontal")
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        sidebar_frame = ttk.Frame(self.paned)
        self.paned.add(sidebar_frame, weight=0)

        sidebar_notebook = ttk.Notebook(sidebar_frame)
        sidebar_notebook.pack(fill="both", expand=True)

        outline_tab = ttk.Frame(sidebar_notebook)
        sidebar_notebook.add(outline_tab, text="Outline")

        self.outline_tree = ttk.Treeview(outline_tab, show="tree", selectmode="browse")
        outline_scroll = ttk.Scrollbar(outline_tab, orient="vertical", command=self.outline_tree.yview)
        self.outline_tree.configure(yscrollcommand=outline_scroll.set)

        outline_scroll.pack(side="right", fill="y")
        self.outline_tree.pack(side="left", fill="both", expand=True)
        self.outline_tree.bind("<<TreeviewSelect>>", self.on_outline_select)

        files_tab = ttk.Frame(sidebar_notebook)
        sidebar_notebook.add(files_tab, text="Files")

        self.files_tree = ttk.Treeview(files_tab, show="tree", selectmode="browse")
        files_scroll = ttk.Scrollbar(files_tab, orient="vertical", command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scroll.set)

        files_scroll.pack(side="right", fill="y")
        self.files_tree.pack(side="left", fill="both", expand=True)
        self.files_tree.bind("<<TreeviewSelect>>", self.on_file_select)

        editor_frame = ttk.Frame(self.paned)
        self.paned.add(editor_frame, weight=1)

        lbl_editor = ttk.Label(editor_frame, text="Markdown", font=("Helvetica", 10, "bold"))
        lbl_editor.pack(anchor="w", pady=(0, 2))

        self.text_editor = tk.Text(
            editor_frame, 
            wrap="word", 
            undo=True, 
            font=("Consolas", 11), 
            padx=10, 
            pady=10,
            relief="flat"
        )
        self.text_editor.pack(fill="both", expand=True)
        self.text_editor.bind("<KeyRelease>", self.on_key_release)

        preview_frame = ttk.Frame(self.paned)
        self.paned.add(preview_frame, weight=1)

        lbl_preview = ttk.Label(preview_frame, text="Preview (PDF)", font=("Helvetica", 10, "bold"))
        lbl_preview.pack(anchor="w", pady=(0, 2))

        self.canvas = tk.Canvas(preview_frame, bg="#e0e0e0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def adjust_sidebar_width(self):
        """Calculates content length in Treeviews to adjust the sidebar size dynamically.

        Prevents the sidebar from hiding long file names or deep document outlines
        while ensuring it doesn't grow too large and squash the editor.
        """

        default_font = tkfont.nametofont("TkTextFont")
        max_text_width = 100  

        def get_max_width(tree):
            max_w = 0
            for item in tree.get_children(""):
                _measure_item(tree, item, 0, max_w)
            return max_w

        def _measure_item(tree, item_id, depth, current_max):
            nonlocal max_text_width
            text = tree.item(item_id, "text")
            indent = depth * 20
            text_w = default_font.measure(text)
            total = indent + text_w + 65
            if total > max_text_width:
                max_text_width = total

            for child in tree.get_children(item_id):
                _measure_item(tree, child, depth + 1, current_max)

        get_max_width(self.outline_tree)
        get_max_width(self.files_tree)

        # Keep limits sane (between 180px and 450px)
        ideal_width = max(180, min(max_text_width, 450))
        
        self.root.update_idletasks()
        try:
            self.paned.sashpos(0, ideal_width)
        except tk.TclError:
            pass

    def update_outline(self, text_content: str):
        """Parses Markdown headers to build the outline tree dynamically.

        Reads the provided text line by line, identifies Markdown headers (#, ##, etc.),
        and constructs a hierarchical Treeview representing the document structure.

        Args:
            text_content (str): The raw Markdown text to parse.
        """

        for item in self.outline_tree.get_children():
            self.outline_tree.delete(item)

        lines = text_content.split("\n")
        level_parents = {0: ""}

        for index, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped.startswith("#"):
                match = re.match(r"^(#+)\s*(.*)", line_stripped)
                if match:
                    hashes, title_text = match.groups()
                    level = len(hashes)

                    parent = ""
                    for lvl in range(level - 1, 0, -1):
                        if lvl in level_parents:
                            parent = level_parents[lvl]
                            break

                    item_id = self.outline_tree.insert(
                        parent, "end", text=title_text, values=(index,), open=True
                    )
                    level_parents[level] = item_id

        self.adjust_sidebar_width()

    def add_file_to_tree(self, file_path: str):
        """Adds an opened file to the sidebar's Files tab.

        Extracts the base file name and adds it to the Treeview to allow easy
        navigation between multiple opened files.

        Args:
            file_path (str): The absolute path of the file to add.
        """

        if file_path not in self.open_files:
            # Extract just the file name
            file_name = file_path.split("/")[-1].split("\\")[-1]
            item_id = self.files_tree.insert("", "end", text=file_name, values=(file_path,))
            self.open_files[file_path] = item_id
        
        self.files_tree.selection_set(self.open_files[file_path])
        self.adjust_sidebar_width()

    def on_outline_select(self, event: tk.Event):
        """Handles click events on the Outline Treeview.

        When a user clicks a header in the outline, this function scrolls the text
        editor directly to the corresponding line number.

        Args:
            event (tk.Event): The Tkinter event object triggered by the selection.
        """

        selected_item = self.outline_tree.selection()
        if not selected_item:
            return
        
        item_values = self.outline_tree.item(selected_item[0], "values")
        if item_values:
            line_index = int(item_values[0]) + 1
            self.text_editor.see(f"{line_index}.0")
            self.text_editor.mark_set("insert", f"{line_index}.0")
            self.text_editor.focus()

    def on_file_select(self, event: tk.Event):
        """Handles click events on the Files Treeview.

        Delegates to the controller to switch the editor context to the selected file.

        Args:
            event (tk.Event): The Tkinter event object triggered by the selection.
        """

        selected_item = self.files_tree.selection()
        if not selected_item:
            return
        
        file_path = self.files_tree.item(selected_item[0], "values")[0]
        if self.controller:
            self.controller.handle_select_file(file_path)

    def toggle_theme(self):
        """Toggles between Light and Dark mode for the UI and sub-components.

        Leverages the sv_ttk library for overall OS-level UI styling, and propagates
        the theme change to the SyntaxHighlighter and PDFPreviewer.
        """

        sv_ttk.toggle_theme()
        current_theme = sv_ttk.get_theme()
        
        self.highlighter.set_theme(current_theme)
        self.previewer.set_theme(current_theme)

    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling on the PDF canvas.

        Args:
            event (tk.Event): The event object containing scroll delta data.
        """

        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_shortcuts(self):
        """Binds keyboard shortcuts (Ctrl+S, Ctrl+O, etc.) to view methods."""
        self.root.bind("<Control-o>", lambda event: [self.on_open_md_click(), "break"][1])
        self.root.bind("<Control-O>", lambda event: [self.on_open_md_click(), "break"][1])
        self.root.bind("<Control-s>", lambda event: [self.on_save_md_click(), "break"][1])
        self.root.bind("<Control-S>", lambda event: [self.on_save_md_click(), "break"][1])
        self.root.bind("<Control-e>", lambda event: [self.on_export_click(), "break"][1])
        self.root.bind("<Control-E>", lambda event: [self.on_export_click(), "break"][1])
        self.root.bind("<Control-t>", lambda event: [self.toggle_theme(), "break"][1])
        self.root.bind("<Control-T>", lambda event: [self.toggle_theme(), "break"][1])
        self.root.bind("<Control-n>", lambda event: [self.on_new_md_click(), "break"][1])
        self.root.bind("<Control-N>", lambda event: [self.on_new_md_click(), "break"][1])

    def on_key_release(self, event):
        """Applies highlighting and debounces auto-save / PDF rendering on keypress.

        Uses a 500ms timer to wait for the user to pause typing before triggering
        heavy operations like PDF generation, ensuring the editor remains responsive.

        Args:
            event (tk.Event): The Tkinter keyboard event.
        """
        self.highlighter.apply_highlighting()

        if event.state & 4: 
            return

        if self.timer:
            self.root.after_cancel(self.timer)
        self.timer = self.root.after(500, self._notify_text_changed)

    def _notify_text_changed(self):
        """Alerts the Controller that the user has stopped typing."""
        if self.controller:
            self.controller.handle_text_changed()

    def on_open_md_click(self):
        """Triggers the file open sequence in the controller."""
        if self.controller:
            self.controller.handle_open_md()

    def on_save_md_click(self):
        """Triggers the file save sequence in the controller."""
        if self.controller:
            self.controller.handle_save_md()

    def on_new_md_click(self):
        """Triggers the new document sequence in the controller."""
        if self.controller:
            self.controller.handle_new_md()

    def on_export_click(self):
        """Triggers the PDF export sequence in the controller."""
        if self.controller:
            self.controller.handle_export()

    def get_text(self) -> str:
        """Retrieves all current text from the editor widget.

        Returns:
            str: The raw Markdown string content.
        """
        return self.text_editor.get("1.0", tk.END).strip()

    def set_text(self, text: str):
        """Replaces text in the editor and updates dependent UI features.

        Clears the current text widget, inserts the new content, forces a syntax
        highlighting pass, and rebuilds the document outline.

        Args:
            text (str): The new Markdown text to populate the editor.
        """

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", text)
        self.highlighter.apply_highlighting()
        self.update_outline(text)

    def update_preview(self, pdf_bytes: bytes):
        """Passes PDF bytes to the previewer on the main UI thread.

        Uses `root.after(0, ...)` to ensure that rendering, which manipulates Tkinter 
        widgets, is safely executed on the main thread rather than a background thread.

        Args:
            pdf_bytes (bytes): The compiled PDF data to render.
        """
        self.root.after(0, self.previewer.render_pdf, pdf_bytes)

    def ask_open_md_file(self) -> str:
        """Opens a file dialog for the user to select an existing Markdown file.

        Returns:
            str: The selected file path, or an empty string if cancelled.
        """

        return filedialog.askopenfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
            title="Open Markdown File"
        )

    def ask_save_md_file(self, initial_file: str = None) -> str:
        """Opens a 'Save As' dialog for saving Markdown files.

        Args:
            initial_file (str, optional): The default name for the file.

        Returns:
            str: The chosen destination path, or an empty string if cancelled.
        """

        return filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
            title="Save Markdown As"
        )
    
    def ask_save_pdf_file(self, initial_file: str = None) -> str:
        """Opens a 'Save As' dialog specifically for exporting PDFs.

        Args:
            initial_file (str, optional): The default name for the PDF file.

        Returns:
            str: The chosen destination path, or an empty string if cancelled.
        """

        return filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
            title="Export PDF As"
        )

    def show_message(self, title: str, msg: str, msg_type: str = "info"):
        """Displays a standard Tkinter popup message box.

        Args:
            title (str): The title of the popup window.
            msg (str): The body text of the message.
            msg_type (str, optional): The type of message ("info", "warning", or "error"). 
                Defaults to "info".
        """
        if msg_type == "info":
            messagebox.showinfo(title, msg)
        elif msg_type == "warning":
            messagebox.showwarning(title, msg)
        elif msg_type == "error":
            messagebox.showerror(title, msg)