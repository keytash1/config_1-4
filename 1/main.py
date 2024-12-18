import os
import zipfile
import tkinter as tk
from tkinter import scrolledtext, filedialog
import csv


class ShellEmulator:
    def __init__(self):
        # Загружаем конфигурацию
        self.load_config()

        # Инициализация истории команд
        self.history = []  # Хранение истории команд

        # GUI
        self.root = tk.Tk()
        self.root.title(f"{self.username}@{self.hostname} Shell Emulator")

        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')

        self.entry = tk.Entry(self.root)
        self.entry.pack(fill='x')
        self.entry.bind('<Return>', self.execute_command)

        # Монтируем файловую систему
        self.mount_filesystem()

        # Выполняем стартовый скрипт
        self.execute_startup_script()

        self.root.mainloop()

    def load_config(self):
        """Чтение конфигурационного файла"""
        config_path = filedialog.askopenfilename(title="Выберите конфигурационный файл", filetypes=[("CSV файлы", "*.csv")])
        with open(config_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.username = row[0]      # Имя пользователя
                self.fs_path = row[1]       # Путь к виртуальной файловой системе (архив zip)
                self.script_path = row[2]   # Путь к стартовому скрипту

        # Назначаем стандартное имя хоста
        self.hostname = "localhost"

    def mount_filesystem(self):
        """Распаковать файловую систему из ZIP-архива."""
        with zipfile.ZipFile(self.fs_path, 'r') as zip_file:
            zip_file.extractall(path="virtual_fs")
            self.cwd = os.path.join(os.getcwd(), "virtual_fs")  # Текущая рабочая директория

    def execute_startup_script(self):
        """Выполнить стартовый скрипт"""
        if os.path.exists(self.script_path):
            with open(self.script_path, 'r') as script_file:
                for line in script_file:
                    self.execute_command_from_script(line.strip())
        else:
            self.text_area.insert(tk.END, f"Startup script not found: {self.script_path}\n")

    def execute_command_from_script(self, command):
        """Выполнение команды из скрипта без GUI-событий."""
        self.history.append(command)
        self.text_area.insert(tk.END, f"{self.username}@{self.hostname}: {command}\n")

        if command == "exit":
            self.root.quit()
        elif command == "clear":
            self.text_area.delete(1.0, tk.END)
        elif command == "history":
            self.show_history()
        elif command.startswith("cd"):
            self.change_directory(command.split()[1])
        elif command == "ls":
            self.list_directory()
        elif command.startswith("tail"):
            self.tail_command(command.split()[1])
        elif command.startswith("find"):
            self.find_command(command.split()[1])
        else:
            self.text_area.insert(tk.END, f"Command not found: {command}\n")

    def execute_command(self, event):
        """Обработка введенной команды."""
        command = self.entry.get().strip()
        self.history.append(command)
        self.text_area.insert(tk.END, f"{self.username}@{self.hostname}: {command}\n")

        if command == "exit":
            self.root.quit()
        elif command == "clear":
            self.text_area.delete(1.0, tk.END)
        elif command == "history":
            self.show_history()
        elif command.startswith("cd"):
            self.change_directory(command.split()[1])
        elif command == "ls":
            self.list_directory()
        elif command.startswith("tail"):
            self.tail_command(command.split()[1])
        elif command.startswith("find"):
            self.find_command(command.split()[1])
        else:
            self.text_area.insert(tk.END, f"Command not found: {command}\n")

        self.entry.delete(0, tk.END)

    def show_history(self):
        """Показать историю команд."""
        history_str = "\n".join(self.history)
        self.text_area.insert(tk.END, history_str + "\n")

    def change_directory(self, path):
        """Изменить текущую директорию."""
        try:
            new_dir = os.path.join(self.cwd, path)
            if os.path.isdir(new_dir):
                self.cwd = new_dir
                self.text_area.insert(tk.END, f"Changed directory to {path}\n")
            else:
                raise FileNotFoundError
        except FileNotFoundError:
            self.text_area.insert(tk.END, f"No such directory: {path}\n")

    def list_directory(self):
        """Вывести содержимое текущей директории."""
        try:
            files = os.listdir(self.cwd)
            self.text_area.insert(tk.END, "\n".join(files) + "\n")
        except Exception as e:
            self.text_area.insert(tk.END, str(e) + "\n")

    def tail_command(self, file_name):
        """Вывести последние 10 строк файла."""
        try:
            file_path = os.path.join(self.cwd, file_name)
            with open(file_path, 'r') as f:
                lines = f.readlines()
                self.text_area.insert(tk.END, "".join(lines[-10:]) + "\n")
        except FileNotFoundError:
            self.text_area.insert(tk.END, f"No such file: {file_name}\n")

    def find_command(self, file_name):
        """Найти файл с указанным именем."""
        results = []
        for root, dirs, files in os.walk(self.cwd):
            for file in files:
                if file_name in file:
                    results.append(os.path.join(root, file))

        if results:
            self.text_area.insert(tk.END, "\n".join(results) + "\n")
        else:
            self.text_area.insert(tk.END, f"No files found with name: {file_name}\n")


if __name__ == "__main__":
    ShellEmulator()
