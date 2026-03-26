import unittest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui import NotesApp

class TestGuiLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tk_patcher = patch('gui.tk')
        cls.tk_mock = cls.tk_patcher.start()
        cls.tk_mock.Tk.return_value = MagicMock()
        cls.tk_mock.Frame.return_value = MagicMock()
        cls.tk_mock.Label.return_value = MagicMock()
        cls.tk_mock.Entry.return_value = MagicMock()
        cls.tk_mock.Text.return_value = MagicMock()
        cls.tk_mock.Button.return_value = MagicMock()
        cls.tk_mock.Scrollbar.return_value = MagicMock()
        cls.tk_mock.Listbox.return_value = MagicMock()
        cls.tk_mock.END = 'end'

    @classmethod
    def tearDownClass(cls):
        cls.tk_patcher.stop()

    def setUp(self):
        self.root = MagicMock()
        self.db_patch = patch('gui.database')
        self.mock_db = self.db_patch.start()
        self.mock_db.get_all_notes.return_value = [(1, "Note1"), (2, "Note2")]
        self.mock_db.get_note_by_id.return_value = ("Note1", "Content1")
        self.mock_db.title_exists.return_value = False

        self.app = NotesApp(self.root)

        # Заменяем реальные виджеты на моки (для контроля вызовов)
        self.app.title_entry = MagicMock()
        self.app.text_area = MagicMock()
        self.app.notes_listbox = MagicMock()
        self.app.save_btn = MagicMock()
        self.app.delete_btn = MagicMock()

        # Подменяем show_success_message, чтобы не открывать реальные окна
        self.app.show_success_message = MagicMock()

        # Очищаем note_ids для контроля
        self.app.note_ids = []

        # Для тестов, где нужно проверить вызов refresh_notes_list и new_note,
        # мы будем использовать локальные моки через patch.object
        # В остальных тестах они будут реальными методами.

    def tearDown(self):
        self.db_patch.stop()

    # --- Тесты ---
    def test_refresh_notes_list(self):
        # Вызываем реальный метод refresh_notes_list
        self.app.refresh_notes_list()
        # Проверяем, что он очистил список и вставил заголовки
        self.app.notes_listbox.delete.assert_called_with(0, 'end')
        self.assertEqual(self.app.notes_listbox.insert.call_count, 2)
        self.assertEqual(self.app.note_ids, [1, 2])

    def test_get_selected_note_ids(self):
        self.app.notes_listbox.curselection.return_value = (0, 1)
        self.app.note_ids = [1, 2]
        selected = self.app.get_selected_note_ids()
        self.assertEqual(selected, [1, 2])

    def test_get_selected_titles(self):
        self.app.notes_listbox.curselection.return_value = (0, 1)
        self.app.notes_listbox.get.side_effect = lambda idx: ["Note1", "Note2"][idx]
        titles = self.app.get_selected_titles()
        self.assertEqual(titles, ["Note1", "Note2"])

    def test_on_note_select_single(self):
        self.app.get_selected_note_ids = MagicMock(return_value=[1])
        self.app.on_note_select(None)
        self.assertEqual(self.app.current_note_id, 1)
        self.mock_db.get_note_by_id.assert_called_with(1)
        self.app.title_entry.delete.assert_called_with(0, 'end')
        self.app.title_entry.insert.assert_called_with(0, "Note1")
        self.app.text_area.delete.assert_called_with(1.0, 'end')
        self.app.text_area.insert.assert_called_with(1.0, "Content1")

    def test_on_note_select_multiple(self):
        self.app.get_selected_note_ids = MagicMock(return_value=[1, 2])
        self.app.on_note_select(None)
        self.assertIsNone(self.app.current_note_id)
        self.app.title_entry.delete.assert_called_with(0, 'end')
        self.app.text_area.delete.assert_called_with(1.0, 'end')

    def test_on_note_select_zero(self):
        self.app.get_selected_note_ids = MagicMock(return_value=[])
        self.app.on_note_select(None)
        self.assertIsNone(self.app.current_note_id)
        self.app.title_entry.delete.assert_called_with(0, 'end')
        self.app.text_area.delete.assert_called_with(1.0, 'end')

    def test_update_ui_state_single_selection(self):
        self.app.get_selected_note_ids = MagicMock(return_value=[1])
        self.app.current_note_id = None
        self.app.update_ui_state()
        self.app.save_btn.config.assert_called_with(state="normal")

    def test_update_ui_state_no_selection_new_note(self):
        self.app.get_selected_note_ids = MagicMock(return_value=[])
        self.app.current_note_id = None
        self.app.update_ui_state()
        self.app.save_btn.config.assert_called_with(state="normal")

    def test_update_ui_state_no_selection_edit_mode(self):
        self.app.get_selected_note_ids = MagicMock(return_value=[])
        self.app.current_note_id = 1
        self.app.update_ui_state()
        self.app.save_btn.config.assert_called_with(state="disabled")

    def test_update_ui_state_multiple_selection(self):
        self.app.get_selected_note_ids = MagicMock(return_value=[1, 2])
        self.app.update_ui_state()
        self.app.save_btn.config.assert_called_with(state="disabled")

    def test_new_note(self):
        # Вызываем реальный метод new_note
        self.app.new_note()
        self.app.title_entry.delete.assert_called_with(0, 'end')
        self.app.text_area.delete.assert_called_with(1.0, 'end')
        self.app.notes_listbox.selection_clear.assert_called_with(0, 'end')
        self.assertIsNone(self.app.current_note_id)

    @patch('gui.messagebox')
    def test_save_note_new_success(self, mock_messagebox):
        self.app.current_note_id = None
        self.app.title_entry.get.return_value = "New Title"
        self.app.text_area.get.return_value = "Content"

        # Временно подменяем refresh_notes_list и new_note на моки, чтобы проверить их вызов
        with patch.object(self.app, 'refresh_notes_list') as mock_refresh, \
             patch.object(self.app, 'new_note') as mock_new:
            self.app.save_note()

        self.mock_db.add_note.assert_called_with("New Title", "Content")
        self.mock_db.update_note.assert_not_called()
        mock_refresh.assert_called()
        mock_new.assert_called()
        self.app.show_success_message.assert_called_with("Note added successfully")
        mock_messagebox.showwarning.assert_not_called()

    @patch('gui.messagebox')
    def test_save_note_update_success(self, mock_messagebox):
        self.app.current_note_id = 1
        self.app.title_entry.get.return_value = "Updated"
        self.app.text_area.get.return_value = "New content"

        with patch.object(self.app, 'refresh_notes_list') as mock_refresh, \
             patch.object(self.app, 'new_note') as mock_new:
            self.app.save_note()

        self.mock_db.update_note.assert_called_with(1, "Updated", "New content")
        self.mock_db.add_note.assert_not_called()
        mock_refresh.assert_called()
        mock_new.assert_called()
        self.app.show_success_message.assert_called_with("Note updated successfully")

    @patch('gui.messagebox')
    def test_save_note_empty_title(self, mock_messagebox):
        self.app.title_entry.get.return_value = "   "
        self.app.save_note()
        self.mock_db.add_note.assert_not_called()
        self.mock_db.update_note.assert_not_called()
        mock_messagebox.showwarning.assert_called_with("Warning", "Title cannot be empty")

    @patch('gui.messagebox')
    def test_save_note_duplicate_title(self, mock_messagebox):
        self.app.current_note_id = None
        self.app.title_entry.get.return_value = "Existing Title"
        self.mock_db.title_exists.return_value = True
        self.app.save_note()
        self.mock_db.add_note.assert_not_called()
        mock_messagebox.showwarning.assert_called_with(
            "Warning", "A note with title 'Existing Title' already exists. Please use a different title."
        )

    @patch('gui.messagebox')
    def test_delete_multiple_notes(self, mock_messagebox):
        mock_messagebox.askyesno.return_value = True
        self.app.get_selected_note_ids = MagicMock(return_value=[1, 2])
        self.app.get_selected_titles = MagicMock(return_value=["Note1", "Note2"])

        with patch.object(self.app, 'refresh_notes_list') as mock_refresh, \
             patch.object(self.app, 'new_note') as mock_new:
            self.app.delete_note()

        expected_msg = "Delete 2 notes:\n• Note1\n• Note2"
        mock_messagebox.askyesno.assert_called_with("Confirm", expected_msg)

        self.assertEqual(self.mock_db.delete_note.call_count, 2)
        self.mock_db.delete_note.assert_any_call(1)
        self.mock_db.delete_note.assert_any_call(2)

        mock_refresh.assert_called()
        mock_new.assert_called()
        self.app.show_success_message.assert_called_with("2 note(s) deleted successfully")

    @patch('gui.messagebox')
    def test_delete_single_note(self, mock_messagebox):
        mock_messagebox.askyesno.return_value = True
        self.app.get_selected_note_ids = MagicMock(return_value=[1])
        self.app.get_selected_titles = MagicMock(return_value=["Note1"])

        with patch.object(self.app, 'refresh_notes_list') as mock_refresh, \
             patch.object(self.app, 'new_note') as mock_new:
            self.app.delete_note()

        mock_messagebox.askyesno.assert_called_with("Confirm", "Delete note 'Note1'?")
        self.mock_db.delete_note.assert_called_once_with(1)
        mock_refresh.assert_called()
        mock_new.assert_called()
        self.app.show_success_message.assert_called_with("1 note(s) deleted successfully")

    @patch('gui.messagebox')
    def test_delete_no_selection(self, mock_messagebox):
        self.app.get_selected_note_ids = MagicMock(return_value=[])
        self.app.delete_note()
        mock_messagebox.showwarning.assert_called_with("Warning", "No notes selected")
        self.mock_db.delete_note.assert_not_called()

    @patch('gui.messagebox')
    def test_delete_cancelled(self, mock_messagebox):
        mock_messagebox.askyesno.return_value = False
        self.app.get_selected_note_ids = MagicMock(return_value=[1])
        self.app.get_selected_titles = MagicMock(return_value=["Note1"])
        self.app.delete_note()
        self.mock_db.delete_note.assert_not_called()

if __name__ == '__main__':
    unittest.main()