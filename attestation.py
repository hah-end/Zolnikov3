import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime
import os

class WeatherDiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        self.entries = []
        self.load_data()

        # === Поля ввода ===
        input_frame = ttk.LabelFrame(root, text="Добавить запись", padding=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", pady=2)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky="w", pady=2)
        self.temp_entry = ttk.Entry(input_frame, width=20)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Описание погоды:").grid(row=2, column=0, sticky="w", pady=2)
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Осадки:").grid(row=3, column=0, sticky="w", pady=2)
        self.precipitation_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Да", variable=self.precipitation_var).grid(row=3, column=1, sticky="w")

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить запись", command=self.add_entry).grid(row=4, column=1, sticky="e", pady=5)

        # === Фильтры ===
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Температура > (°C):").grid(row=0, column=2, sticky="w", padx=10)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)

        ttk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters).grid(row=0, column=4, padx=10)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).grid(row=0, column=5)

        # === Таблица записей ===
        table_frame = ttk.LabelFrame(root, text="Записи", padding=10)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("date", "temp", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("date", width=100, anchor="center")
        self.tree.column("temp", width=100, anchor="center")
        self.tree.column("description", width=250, anchor="w")
        self.tree.column("precipitation", width=80, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        # === Кнопки сохранения/загрузки ===
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_data_file).pack(side="left", padx=5)

        self.update_table()

    def validate_input(self):
        date_str = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()

        # Проверка даты
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД.")
            return False

        # Проверка температуры
        try:
            float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом.")
            return False

        # Проверка описания
        if not desc:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым.")
            return False

        return True

    def add_entry(self):
        if not self.validate_input():
            return

        entry = {
            "date": self.date_entry.get().strip(),
            "temperature": float(self.temp_entry.get().strip()),
            "description": self.desc_entry.get().strip(),
            "precipitation": self.precipitation_var.get()
        }

        self.entries.append(entry)
        self.update_table()

        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precipitation_var.set(False)

        messagebox.showinfo("Успех", "Запись добавлена!")

    def update_table(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        display_data = data if data is not None else self.entries

        for entry in display_data:
            self.tree.insert("", "end", values=(
                entry["date"],
                f"{entry['temperature']:.1f}",
                entry["description"],
                "Да" if entry["precipitation"] else "Нет"
            ))

    def apply_filters(self):
        date_filter = self.filter_date_entry.get().strip()
        temp_filter = self.filter_temp_entry.get().strip()

        filtered = self.entries

        if date_filter:
            try:
                datetime.strptime(date_filter, "%Y-%m-%d")
                filtered = [e for e in filtered if e["date"] == date_filter]
            except ValueError:
                messagebox.showwarning("Предупреждение", "Неверный формат даты для фильтра.")
                return

        if temp_filter:
            try:
                temp_val = float(temp_filter)
                filtered = [e for e in filtered if e["temperature"] > temp_val]
            except ValueError:
                messagebox.showwarning("Предупреждение", "Температура фильтра должна быть числом.")
                return

        self.update_table(filtered)

    def reset_filters(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()

    def save_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.entries, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Сохранение", f"Данные сохранены в {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def load_data_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
                self.update_table()
                messagebox.showinfo("Загрузка", f"Данные загружены из {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def load_data(self):
        if os.path.exists("weather_data.json"):
            try:
                with open("weather_data.json", "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception:
                self.entries = []
        else:
            self.entries = []

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiaryApp(root)
    root.mainloop()