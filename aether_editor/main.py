import tkinter as tk
import sv_ttk
from models.editor_model import EditorModel
from views.editor_view import EditorView
from controllers.editor_controller import EditorController

if __name__ == "__main__":
    root = tk.Tk()
    model = EditorModel()
    view = EditorView(root)
    controller = EditorController(model, view)
    sv_ttk.set_theme("light")
    root.mainloop()