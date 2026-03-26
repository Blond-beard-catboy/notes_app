import tkinter as tk
from tkinter import messagebox
import database

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        self.current_note_id = None
        self.note_ids = []  # список id заметок в порядке отображения

        # Поле заголовка
        title_frame = tk.Frame(root)
        title_frame.pack(pady=5, fill="x")
        tk.Label(title_frame, text="Title:").pack(side="left", padx=5)
        self.title_entry = tk.Entry(title_frame, width=60)
        self.title_entry.pack(side="left", fill="x", expand=True, padx=5)

        # Текст заметки
        self.text_area = tk.Text(root, wrap="word", height=15)
        self.text_area.pack(pady=5, padx=10, fill="both", expand=True)

        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        self.save_btn = tk.Button(btn_frame, text="Save", command=self.save_note)
        self.save_btn.pack(side="left", padx=5)
        self.delete_btn = tk.Button(btn_frame, text="Delete", command=self.delete_note)
        self.delete_btn.pack(side="left", padx=5)
        tk.Button(btn_frame, text="New", command=self.new_note).pack(side="left", padx=5)

        # Список заметок с прокруткой (множественный выбор)
        list_frame = tk.Frame(root)
        list_frame.pack(pady=5, padx=10, fill="both", expand=True)
        tk.Label(list_frame, text="Notes list:").pack(anchor="w")

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.notes_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set,
                                        selectmode=tk.EXTENDED)
        self.notes_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.notes_listbox.yview)

        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

        self.refresh_notes_list()

    def refresh_notes_list(self):
        """Обновляет список заметок: очищает Listbox и заполняет заголовками"""
        self.notes_listbox.delete(0, tk.END)
        self.note_ids.clear()
        notes = database.get_all_notes()
        for note_id, title in notes:
            self.notes_listbox.insert(tk.END, title)
            self.note_ids.append(note_id)
        self.update_ui_state()

    def get_selected_note_ids(self):
        """Возвращает список id всех выделенных заметок"""
        selected_indices = self.notes_listbox.curselection()
        selected_ids = []
        for idx in selected_indices:
            if idx < len(self.note_ids):
                selected_ids.append(self.note_ids[idx])
        return selected_ids

    def get_selected_titles(self):
        """Возвращает список заголовков выделенных заметок"""
        selected_indices = self.notes_listbox.curselection()
        titles = []
        for idx in selected_indices:
            titles.append(self.notes_listbox.get(idx))
        return titles

    def on_note_select(self, event):
        """Обработка изменения выделения в списке"""
        selected_ids = self.get_selected_note_ids()
        if len(selected_ids) == 1:
            # Ровно одна заметка выделена – загружаем её
            note_id = selected_ids[0]
            note = database.get_note_by_id(note_id)
            if note:
                self.current_note_id = note_id
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, note[0])
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, note[1])
        else:
            # Ноль или несколько заметок – очищаем поля и сбрасываем current_note_id
            self.current_note_id = None
            self.title_entry.delete(0, tk.END)
            self.text_area.delete(1.0, tk.END)

        self.update_ui_state()

    def update_ui_state(self):
        """Активирует/деактивирует кнопку Save в зависимости от состояния"""
        selected_count = len(self.get_selected_note_ids())
        if selected_count == 1:
            # Редактирование существующей заметки
            self.save_btn.config(state="normal")
        elif selected_count == 0 and self.current_note_id is None:
            # Создание новой заметки
            self.save_btn.config(state="normal")
        else:
            self.save_btn.config(state="disabled")

    def save_note(self):
        """Сохраняет заметку (добавление или обновление)"""
        title = self.title_entry.get().strip()
        content = self.text_area.get(1.0, tk.END).strip()
        if not title:
            messagebox.showwarning("Warning", "Title cannot be empty")
            return

        # Проверка уникальности заголовка
        if database.title_exists(title, exclude_id=self.current_note_id):
            messagebox.showwarning("Warning", f"A note with title '{title}' already exists. Please use a different title.")
            return

        if self.current_note_id is None:
            database.add_note(title, content)
            self.show_success_message("Note added successfully")
        else:
            database.update_note(self.current_note_id, title, content)
            self.show_success_message("Note updated successfully")

        self.refresh_notes_list()
        self.new_note()

    def delete_note(self):
        """Удаляет все выделенные заметки с подтверждением"""
        selected_ids = self.get_selected_note_ids()
        if not selected_ids:
            messagebox.showwarning("Warning", "No notes selected")
            return

        titles = self.get_selected_titles()
        count = len(selected_ids)
        if count == 1:
            msg = f"Delete note '{titles[0]}'?"
        else:
            msg = f"Delete {count} notes:\n" + "\n".join(f"• {t}" for t in titles)

        if messagebox.askyesno("Confirm", msg):
            for note_id in selected_ids:
                database.delete_note(note_id)
            self.refresh_notes_list()
            self.new_note()
            self.show_success_message(f"{count} note(s) deleted successfully")

    def new_note(self):
        """Создаёт новую заметку (очищает поля и сбрасывает выделение)"""
        self.current_note_id = None
        self.title_entry.delete(0, tk.END)
        self.text_area.delete(1.0, tk.END)
        self.notes_listbox.selection_clear(0, tk.END)
        self.update_ui_state()

    def show_success_message(self, message):
        """Кастомное всплывающее окно с увеличенным шрифтом"""
        popup = tk.Toplevel(self.root)
        popup.title("Success")
        popup.geometry("400x150")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        label = tk.Label(popup, text=message, font=("Arial", 14, "bold"), pady=20)
        label.pack(expand=True, fill="both")
        btn = tk.Button(popup, text="OK", width=10, command=popup.destroy)
        btn.pack(pady=10)
        popup.after(2000, popup.destroy)