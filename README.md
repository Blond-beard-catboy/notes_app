# Notes App

A simple cross-platform note-taking application with a graphical user interface (Tkinter) and SQLite database.  
Allows you to create, edit, and delete notes. Notes are stored locally and persist between sessions.

## Features
- Create new notes with a title and content.
- Edit existing notes.
- Delete notes (with confirmation).
- Notes are saved automatically to a SQLite database.
- Clean and intuitive interface.

## Requirements
- Python 3.6 or higher (with `tkinter` and `sqlite3` modules – they are included in the standard Python distribution).
- No external libraries needed.

## Installation and Running

1. **Clone or download** the project:
   ```bash
   git clone https://github.com/yourusername/notes-app.git
   cd notes-app
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Linux/macOS
   venv\Scripts\activate         # On Windows
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

   The first run will automatically create the `notes.db` file in the project folder.

## Project Structure
```
notes_app/
├── main.py          # Entry point – initialises database and launches GUI
├── database.py      # Database operations (SQLite)
├── gui.py           # GUI logic (Tkinter)
├── requirements.txt # Dependencies list (empty, only standard library)
└── README.md        # This file
```

## How to Use
- **Save** a note: enter a title and content, then click "Save". A new note will be added or the current note will be updated.
- **Delete** a note: select a note from the list on the right and click "Delete". Confirm the deletion.
- **New** note: click "New" to clear the fields and start a fresh note.

## Possible Improvements
Here are some ideas to extend the project:
- Add search/filter functionality.
- Display creation date/time for each note.
- Support for categories or tags.
- Export/import notes to JSON or TXT files.
- Add keyboard shortcuts (Ctrl+S to save, Ctrl+N for new note).
- Replace the listbox with a more advanced Treeview for better layout.

## License
This project is open‑source and available under the MIT License.
```