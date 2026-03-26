import tkinter as tk
import database
from gui import NotesApp

if __name__ == "__main__":
    database.init_db()
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()