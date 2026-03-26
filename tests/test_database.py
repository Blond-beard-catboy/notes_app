import unittest
import sys
import os
import tempfile
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Создаём временный файл для БД
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.original_db_name = database.DB_NAME
        database.DB_NAME = self.temp_db.name
        database.init_db()
        # Проверяем, что таблица действительно создалась
        conn = sqlite3.connect(self.temp_db.name)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        if not cur.fetchone():
            raise Exception("Table 'notes' was not created by init_db()")
        conn.close()

    def tearDown(self):
        database.DB_NAME = self.original_db_name
        os.unlink(self.temp_db.name)

    def test_add_and_get_note(self):
        database.add_note("Test Title", "Test Content")
        notes = database.get_all_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0][1], "Test Title")

        note = database.get_note_by_id(notes[0][0])
        self.assertEqual(note[0], "Test Title")
        self.assertEqual(note[1], "Test Content")

    def test_update_note(self):
        database.add_note("Old Title", "Old Content")
        note_id = database.get_all_notes()[0][0]
        database.update_note(note_id, "New Title", "New Content")
        note = database.get_note_by_id(note_id)
        self.assertEqual(note[0], "New Title")
        self.assertEqual(note[1], "New Content")

    def test_delete_note(self):
        database.add_note("To Delete", "Content")
        notes_before = database.get_all_notes()
        note_id = notes_before[0][0]
        database.delete_note(note_id)
        notes_after = database.get_all_notes()
        self.assertEqual(len(notes_after), 0)

    def test_get_nonexistent_note(self):
        self.assertIsNone(database.get_note_by_id(999))

    def test_add_empty_title(self):
        database.add_note("", "Content")
        notes = database.get_all_notes()
        self.assertEqual(notes[0][1], "")

    def test_title_exists(self):
        database.add_note("Unique Title", "Content")
        self.assertTrue(database.title_exists("Unique Title"))
        self.assertFalse(database.title_exists("Nonexistent"))
        database.add_note("Another Title", "Content")
        self.assertTrue(database.title_exists("Another Title"))
        note_id = database.get_all_notes()[0][0]
        self.assertFalse(database.title_exists("Unique Title", exclude_id=note_id))
        other_id = database.get_all_notes()[1][0] if len(database.get_all_notes()) > 1 else None
        if other_id:
            self.assertTrue(database.title_exists("Unique Title", exclude_id=other_id))

if __name__ == '__main__':
    unittest.main()