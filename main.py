## при смене темы лагает и невозможно закрыть, 
# в настройки добавь кнопку "настроить list" - чтобы открывалось окно с выбором докуметов:
## ipset-all.txt
## ipset-exclude.txt
## list-exclude.txt
## list-general.txt
## list-google.txt
## и при нажатии нажитие на них они выделиляслись, а на кнопку "открыть" они открывались и их можно было редактировать
# активировать VENV: venv\Scripts\activate либо .\venv\Scripts\Activate.ps1
# КОМПИЛИЦИЯ:
# 1. cd "F:\Doki\СВОЙ ЗАПРЕТ\CODE PY\zapret-discord-youtube" 2. pyinstaller --noconsole --name="ZapretCustom" testi.py
# # Если будет ошибка выполнения скриптов: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

import sys
import os
import subprocess
import platform
import urllib.request
import json
import webbrowser
import threading
import socket
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk

# Настройка внешнего вида
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class TestConnectionThread:
    """Поток для тестирования соединения"""
    def __init__(self, callback):
        self.callback = callback
        
    def start(self):
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
        
    def run(self):
        try:
            result = "═══════════════════════════════════════════════\n"
            result += "        ТЕСТИРОВАНИЕ СОЕДИНЕНИЯ\n"
            result += "═══════════════════════════════════════════════\n\n"

            # Список сайтов для проверки
            websites = [
                ('Discord', 'https://discord.com'),
                ('YouTube', 'https://www.youtube.com'),
                ('Google', 'https://www.google.com'),
                ('Cloudflare', 'https://www.cloudflare.com'),
                ('Yahoo', 'https://www.yahoo.com'),
                ('Amazon', 'https://www.amazon.com')
            ]

            result += "ПРОВЕРКА ДОСТУПНОСТИ САЙТОВ:\n"
            result += "─────────────────────────────────────────────\n"
            
            for name, url in websites:
                try:
                    response = urllib.request.urlopen(url, timeout=5)
                    result += f"✓ {name:15} | Доступен (Код: {response.status})\n"
                except urllib.error.URLError as e:
                    result += f"✗ {name:15} | Недоступен ({str(e.reason)[:30]})\n"
                except Exception as e:
                    result += f"✗ {name:15} | Ошибка ({str(e)[:30]})\n"

            result += "\nПРОВЕРКА IP И DNS:\n"
            result += "─────────────────────────────────────────────\n"
            
            # Проверка внешнего IP
            try:
                ip_response = urllib.request.urlopen('https://api.ipify.org', timeout=5)
                external_ip = ip_response.read().decode('utf-8')
                result += f"✓ Внешний IP: {external_ip}\n"
            except Exception as e:
                result += f"✗ Не удалось получить внешний IP: {str(e)[:40]}\n"

            # Проверка DNS
            dns_servers = [
                ('Google DNS', '8.8.8.8'),
                ('Cloudflare DNS', '1.1.1.1'),
                ('Yandex DNS', '77.88.8.8')
            ]

            result += "\nПРОВЕРКА DNS СЕРВЕРОВ:\n"
            result += "─────────────────────────────────────────────\n"
            
            for name, dns_ip in dns_servers:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    sock.connect((dns_ip, 53))
                    sock.close()
                    result += f"✓ {name:20} | {dns_ip} - Доступен\n"
                except Exception as e:
                    result += f"✗ {name:20} | {dns_ip} - Недоступен\n"

            # Проверка DNS резолвинга
            result += "\nПРОВЕРКА DNS РЕЗОЛВИНГА:\n"
            result += "─────────────────────────────────────────────\n"
            
            test_domains = [
                'discord.com',
                'google.com',
                'cloudflare.com'
            ]
            
            for domain in test_domains:
                try:
                    ip = socket.gethostbyname(domain)
                    result += f"✓ {domain:20} → {ip}\n"
                except Exception as e:
                    result += f"✗ {domain:20} → Не удалось разрешить\n"

            # Ping тест
            result += "\nPING ТЕСТ (RTT - Round Trip Time):\n"
            result += "─────────────────────────────────────────────\n"
            
            ping_hosts = [
                'discord.com',
                'google.com',
                '1.1.1.1'
            ]
            
            system = platform.system()
            ping_param = '-n' if system == 'Windows' else '-c'
            
            for host in ping_hosts:
                try:
                    cmd = ['ping', ping_param, '1', host]
                    if system != 'Windows':
                        cmd.extend(['-W', '3'])
                    
                    ping_result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    
                    if ping_result.returncode == 0:
                        output = ping_result.stdout
                        if system == 'Windows':
                            if 'ms' in output:
                                time_line = [l for l in output.split('\n') if 'ms' in l.lower()][0]
                                result += f"✓ {host:20} | {time_line.strip()}\n"
                            else:
                                result += f"✓ {host:20} | Доступен\n"
                        else:
                            if 'time=' in output:
                                time_line = [l for l in output.split('\n') if 'time=' in l][0]
                                result += f"✓ {host:20} | {time_line.strip()}\n"
                            else:
                                result += f"✓ {host:20} | Доступен\n"
                    else:
                        result += f"✗ {host:20} | Недоступен для ping\n"
                except Exception as e:
                    result += f"✗ {host:20} | Ошибка ping\n"

            result += "\n═══════════════════════════════════════════════\n"
            result += "           ТЕСТИРОВАНИЕ ЗАВЕРШЕНО\n"
            result += "═══════════════════════════════════════════════\n"
            
            self.callback(result)
        except Exception as e:
            self.callback(f"Критическая ошибка при тестировании:\n{str(e)}")

class TestConnectionDialog(ctk.CTkToplevel):
    """Окно тестирования соединения"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Тест соединения")
        self.geometry("700x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        
        self._center_window()
        self._create_widgets()
        
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Текстовое поле с моноширинным шрифтом
        self.text_box = ctk.CTkTextbox(
            self, 
            wrap="word",
            font=("Consolas", 11) if platform.system() == "Windows" else ("Monaco", 11)
        )
        self.text_box.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        
        # Кнопки
        self.start_button = ctk.CTkButton(
            self, 
            text="Запустить тест", 
            command=self.start_test,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.start_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.close_button = ctk.CTkButton(
            self, 
            text="Закрыть", 
            command=self.destroy,
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.close_button.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
    def start_test(self):
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", "Выполняется тестирование...\nПожалуйста, подождите...\n")
        self.start_button.configure(state="disabled", text="Тестирование...")
        
        self.thread = TestConnectionThread(self.test_finished)
        self.thread.start()
        
    def test_finished(self, result):
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", result)
        self.start_button.configure(state="normal", text="Запустить тест")

class ConfigSelectionDialog(ctk.CTkToplevel):
    """Окно выбора конфигурации"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Настроить конфиг")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.selected_config = None
        self.bat_directory = os.path.dirname(os.path.abspath(__file__))
        self._center_window()
        self._create_widgets()
        self.load_bat_files()
        
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Панель выбора директории
        dir_frame = ctk.CTkFrame(self)
        dir_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        dir_frame.grid_columnconfigure(0, weight=1)
        
        self.dir_label = ctk.CTkLabel(
            dir_frame,
            text=f": {self.bat_directory}",
            font=ctk.CTkFont(size=12),
            wraplength=500
        )
        self.dir_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        dir_button = ctk.CTkButton(
            dir_frame,
            text="Выбрать",
            command=self.select_directory,
            height=35,
            width=200
        )
        dir_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")
        
        label = ctk.CTkLabel(
            self, 
            text="Выберите конфигурацию:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        
        self.config_list = tk.Listbox(
            self,
            bg="#343638",
            fg="white",
            selectbackground="#1f6aa5",
            selectforeground="white",
            font=("Arial", 12),
            relief="flat",
            highlightthickness=0
        )
        self.config_list.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        scrollbar = ctk.CTkScrollbar(self, command=self.config_list.yview)
        scrollbar.grid(row=2, column=1, pady=10, sticky="ns")
        self.config_list.configure(yscrollcommand=scrollbar.set)
        
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        self.select_button = ctk.CTkButton(
            buttons_frame, 
            text="Выбрать", 
            command=self.select_config,
            height=40
        )
        self.select_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.cancel_button = ctk.CTkButton(
            buttons_frame, 
            text="Отмена", 
            command=self.destroy,
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE")
        )
        self.cancel_button.grid(row=0, column=1, padx=5, sticky="ew")
        
    def select_directory(self):
        """Выбор директории с BAT файлами"""
        directory = filedialog.askdirectory(title="Выберите директорию с BAT файлами")
        if directory:
            self.bat_directory = directory
            self.dir_label.configure(text=f"Директория: {directory}")
            self.load_bat_files()
        
    def load_bat_files(self):
        try:
            self.config_list.delete(0, tk.END)
            
            print(f"Ищем BAT файлы в директории: {self.bat_directory}")
            
            bat_files = [f for f in os.listdir(self.bat_directory)
                        if f.endswith('.bat') and f.lower() != 'service.bat' 
                        and os.path.isfile(os.path.join(self.bat_directory, f))]

            print(f"Найдены BAT файлы: {bat_files}")

            if bat_files:
                for bat_file in sorted(bat_files):
                    self.config_list.insert("end", bat_file)
                self.select_button.configure(state="normal")
            else:
                self.config_list.insert("end", "Нет доступных BAT файлов")
                self.select_button.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки файлов: {str(e)}")
            print(f"Ошибка: {e}")

    def select_config(self):
        selection = self.config_list.curselection()
        if selection:
            config_name = self.config_list.get(selection[0])
            if config_name != "Нет доступных BAT файлов":
                self.selected_config = config_name
                self.parent.on_config_selected(config_name)
                self.destroy()
        else:
            messagebox.showwarning("Предупреждение", "Выберите конфигурацию из списка")

class ListEditorDialog(ctk.CTkToplevel):
    """Окно редактирования списков"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Редактор списков - Version 0.1")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.lists_dir = os.path.join(self.script_dir, 'lists')
        self.selected_file = None
        self._center_window()
        self._create_widgets()
        self.load_list_files()
        
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            self, 
            text="Выберите файл списка для редактирования:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Фрейм для списка файлов
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Список файлов
        self.list_listbox = tk.Listbox(
            list_frame,
            bg="#343638",
            fg="white",
            selectbackground="#1f6aa5",
            selectforeground="white",
            font=("Arial", 11),
            relief="flat",
            highlightthickness=0
        )
        self.list_listbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.list_listbox.bind('<<ListboxSelect>>', self.on_list_select)
        self.list_listbox.bind('<Double-Button-1>', lambda e: self.open_file())
        
        # Скроллбар для списка
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.list_listbox.yview)
        scrollbar.grid(row=0, column=1, pady=10, sticky="ns")
        self.list_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Информационная метка
        self.info_label = ctk.CTkLabel(
            self,
            text="Выберите файл из списка и нажмите 'Открыть' для редактирования",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        
        # Фрейм для кнопок
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        self.open_button = ctk.CTkButton(
            buttons_frame, 
            text="Открыть в блокноте", 
            command=self.open_file,
            height=40,
            state="disabled",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.open_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.close_button = ctk.CTkButton(
            buttons_frame, 
            text="Закрыть", 
            command=self.destroy,
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.close_button.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Кнопка обновления списка
        self.refresh_button = ctk.CTkButton(
            buttons_frame, 
            text="Обновить список", 
            command=self.load_list_files,
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE")
        )
        self.refresh_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
    def load_list_files(self):
        """Загрузка списка файлов для редактирования"""
        try:
            # Очищаем список
            self.list_listbox.delete(0, tk.END)
            
            # Основные файлы в папке lists
            main_files = [
                'ipset-all.txt',
                'ipset-exclude.txt', 
                'list-exclude.txt',
                'list-general.txt',
                'list-google.txt'
            ]
            
            # Файлы в папке DLC
            dlc_files = [
                'ipset-cloudflare.txt',
                'ipset-ea.txt',
                'list-general (2).txt',
                'list-general.txt'
            ]
            
            # Добавляем разделитель для основных файлов
            self.list_listbox.insert("end", "=== ОСНОВНЫЕ ФАЙЛЫ ===")
            self.list_listbox.itemconfig(tk.END, {'fg': 'yellow'})
            
            # Добавляем основные файлы
            for file_name in main_files:
                file_path = os.path.join(self.lists_dir, file_name)
                if os.path.exists(file_path):
                    self.list_listbox.insert("end", f"✓ {file_name}")
                    self.list_listbox.itemconfig(tk.END, {'fg': '#4CAF50'})  # Зеленый для существующих
                else:
                    self.list_listbox.insert("end", f"✗ {file_name} (не найден)")
                    self.list_listbox.itemconfig(tk.END, {'fg': '#f44336'})  # Красный для отсутствующих
            
            # Добавляем разделитель для DLC файлов
            self.list_listbox.insert("end", "=== ФАЙЛЫ DLC ===")
            self.list_listbox.itemconfig(tk.END, {'fg': 'yellow'})
            
            # Добавляем файлы DLC
            dlc_dir = os.path.join(self.lists_dir, 'DLC')
            for file_name in dlc_files:
                file_path = os.path.join(dlc_dir, file_name)
                if os.path.exists(file_path):
                    self.list_listbox.insert("end", f"✓ DLC/{file_name}")
                    self.list_listbox.itemconfig(tk.END, {'fg': '#4CAF50'})
                else:
                    self.list_listbox.insert("end", f"✗ DLC/{file_name} (не найден)")
                    self.list_listbox.itemconfig(tk.END, {'fg': '#f44336'})
                    
            print(f"Загружены файлы из папки: {self.lists_dir}")
            
        except Exception as e:
            print(f"Ошибка загрузки файлов списков: {e}")
            self.list_listbox.insert("end", f"Ошибка загрузки: {str(e)}")
    
    def on_list_select(self, event):
        """Обработчик выбора файла в списке"""
        selection = self.list_listbox.curselection()
        if selection:
            item_text = self.list_listbox.get(selection[0])
            
            # Пропускаем разделители
            if "===" in item_text:
                self.selected_file = None
                self.open_button.configure(state="disabled")
                self.info_label.configure(text="Выберите файл из списка (не разделитель)")
                return
            
            # Проверяем существование файла
            if item_text.startswith("✓ "):
                # Убираем "✓ " и получаем путь к файлу
                file_path_part = item_text[2:]
                if file_path_part.startswith("DLC/"):
                    # Файл из папки DLC
                    file_name = file_path_part[4:]  # Убираем "DLC/"
                    self.selected_file = os.path.join(self.lists_dir, 'DLC', file_name)
                else:
                    # Обычный файл
                    self.selected_file = os.path.join(self.lists_dir, file_path_part)
                
                self.open_button.configure(state="normal")
                self.info_label.configure(text=f"Выбран: {file_path_part} - готов к открытию")
                
            else:
                self.selected_file = None
                self.open_button.configure(state="disabled")
                if "(не найден)" in item_text:
                    file_name = item_text[2:].split(" (не найден)")[0]  # Убираем "✗ " и "(не найден)"
                    self.info_label.configure(text=f"Файл {file_name} не найден!", text_color="#f44336")
                else:
                    self.info_label.configure(text="Выберите существующий файл из списка")
    
    def open_file(self):
        """Открытие выбранного файла в текстовом редакторе"""
        if not self.selected_file or not os.path.exists(self.selected_file):
            messagebox.showerror("Ошибка", "Файл не найден или не выбран!")
            return

        try:
            file_name = os.path.basename(self.selected_file)
            
            if platform.system() == "Windows":
                # Открываем в блокноте Windows
                os.system(f'notepad "{self.selected_file}"')
                
            elif platform.system() == "Darwin":
                # Для MacOS
                subprocess.Popen(['open', '-t', self.selected_file])
                
            else:
                # Для Linux
                subprocess.Popen(['xdg-open', self.selected_file])
            
            messagebox.showinfo("Успех", 
                              f"Файл '{file_name}' открыт в текстовом редакторе!\n\n"
                              f"После редактирования сохраните изменения в редакторе.")
            
            print(f"Открыт файл: {self.selected_file}")
            
        except Exception as e:
            error_msg = f"Не удалось открыть файл:\n{str(e)}"
            messagebox.showerror("Ошибка", error_msg)
            print(f"Ошибка открытия файла: {e}")

class WarpDialog(ctk.CTkToplevel):
    """Окно управления Cloudflare WARP"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cloudflare WARP")
        self.geometry("450x300")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._center_window()
        self._create_widgets()
        self.check_warp()
        
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Проверка статуса WARP...",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        self.check_button = ctk.CTkButton(
            self,
            text="Проверить установку WARP",
            command=self.check_warp,
            height=45
        )
        self.check_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.download_button = ctk.CTkButton(
            self,
            text="Скачать WARP",
            command=self.download_warp,
            height=45,
            state="disabled"
        )
        self.download_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.connection_button = ctk.CTkButton(
            self,
            text="Проверить соединение",
            command=self.check_connection,
            height=45
        )
        self.connection_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.close_button = ctk.CTkButton(
            self,
            text="Закрыть",
            command=self.destroy,
            height=45,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE")
        )
        self.close_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

    def check_warp(self):
        system = platform.system()
        warp_installed = False

        if system == "Windows":
            warp_path = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                                    'Cloudflare', 'Cloudflare WARP', 'warp-svc.exe')
            warp_installed = os.path.exists(warp_path)
        elif system == "Darwin":
            warp_path = '/Applications/Cloudflare WARP.app'
            warp_installed = os.path.exists(warp_path)
        elif system == "Linux":
            try:
                subprocess.run(['which', 'warp-cli'], capture_output=True, check=True)
                warp_installed = True
            except:
                warp_installed = False

        if warp_installed:
            self.status_label.configure(
                text="Cloudflare WARP установлен",
                text_color="#4CAF50"
            )
            self.download_button.configure(state="disabled")
        else:
            self.status_label.configure(
                text="Cloudflare WARP не найден",
                text_color="#f44336"
            )
            self.download_button.configure(state="normal")

    def download_warp(self):
        system = platform.system()

        if system == "Windows":
            url = "https://1111-releases.cloudflareclient.com/win/latest"
        elif system == "Darwin":
            url = "https://1111-releases.cloudflareclient.com/mac/latest"
        else:
            url = "https://1111-releases.cloudflareclient.com/linux/latest"

        if messagebox.askyesno('Скачать WARP', f'Открыть страницу загрузки WARP?\n{url}'):
            webbrowser.open(url)

    def check_connection(self):
        try:
            system = platform.system()

            if system == "Windows":
                result = subprocess.run(['warp-cli', 'status'],
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    messagebox.showinfo("Статус WARP", f"Соединение активно\n\n{result.stdout}")
                else:
                    messagebox.showwarning("Статус WARP", "WARP не подключен или не запущен")
            else:
                messagebox.showinfo("Проверка соединения", 
                                  "Проверьте статус WARP в системных настройках")
        except FileNotFoundError:
            messagebox.showwarning("Ошибка", 
                                 "Команда warp-cli не найдена. Убедитесь, что WARP установлен.")
        except Exception as e:
            messagebox.showwarning("Ошибка", f"Не удалось проверить соединение: {str(e)}")

class HelpDialog(ctk.CTkToplevel):
    """Окно справки"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Справка")
        self.geometry("600x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._center_window()
        self._create_widgets()
        
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        help_text = """
Zapret-Custom - Справка по использованию

О программе
Zapret-Custom - это графический интерфейс для форка официального
zapret-discord-youtube. Программа предназначена для обхода блокировок
Discord и YouTube.

Основные функции:

0. Обновить сам "Zapret" 
переходите в "Настройки" и нажимайте: "Настроить service.bat".
- Это обновляет саму программу? Нет, вы обновляете только сам Zapret.

1. Настроить конфиг
Выберите нужный BAT файл конфигурации из списка. После выбора и нажатия
"Выбрать", конфигурация будет готова к запуску.

2. Запустить Zapret
Запускает выбранную конфигурацию. Статус отображается вверху окна.

3. Остановить Zapret
Останавливает процесс Zapret, если он запущен.

4. Тест соединения
Проверяет доступность Discord, YouTube, Google, Cloudflare, Yahoo, Amazon
и общее интернет-соединение. Также проверяет DNS серверы и разрешение имен.

5. WARP
Управление Cloudflare WARP. Проверка установки, скачивание и проверка
соединения с WARP.

Для корректной работы требуются права администратора.

Версия: 0.1
        """

        text_box = ctk.CTkTextbox(self, wrap="word", font=("Arial", 12))
        text_box.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        text_box.insert("1.0", help_text)
        text_box.configure(state="disabled")
        
        close_button = ctk.CTkButton(
            self,
            text="Закрыть",
            command=self.destroy,
            height=40
        )
        close_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

class SettingsDialog(ctk.CTkToplevel):
    """Окно настроек"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Настройки")
        self.geometry("500x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self._center_window()
        self._create_widgets()
        self.load_settings()
        
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)
        
        theme_label = ctk.CTkLabel(
            self,
            text="Тема оформления:",
            font=ctk.CTkFont(weight="bold")
        )
        theme_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.theme_combo = ctk.CTkComboBox(
            self,
            values=["Темная", "Светлая", "Системная"],
            command=self.change_theme
        )
        self.theme_combo.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.autostart_checkbox = ctk.CTkCheckBox(
            self,
            text="Автозапуск Zapret при старте программы"
        )
        self.autostart_checkbox.grid(row=2, column=0, padx=20, pady=15, sticky="w")
        
        service_label = ctk.CTkLabel(
            self,
            text="Настройка службы:",
            font=ctk.CTkFont(weight="bold")
        )
        service_label.grid(row=3, column=0, padx=20, pady=(15, 5), sticky="w")
        
        self.service_button = ctk.CTkButton(
            self,
            text="Настроить service.bat",
            command=self.configure_service,
            height=45
        )
        self.service_button.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        # Новая кнопка для редактирования списков
        self.list_button = ctk.CTkButton(
            self,
            text="Настроить списки",
            command=self.configure_lists,
            height=45
        )
        self.list_button.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        
        self.help_button = ctk.CTkButton(
            self,
            text="Справка",
            command=self.show_help,
            height=45
        )
        self.help_button.grid(row=6, column=0, padx=20, pady=15, sticky="ew")
        
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=7, column=0, padx=20, pady=20, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        self.save_button = ctk.CTkButton(
            buttons_frame,
            text="Сохранить",
            command=self.save_settings,
            height=40
        )
        self.save_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            command=self.destroy,
            height=40,
            fg_color="transparent",
            border_width=2,
            text_color=("gray10", "#DCE4EE")
        )
        self.cancel_button.grid(row=0, column=1, padx=5, sticky="ew")
        
    def change_theme(self, theme_name):
        """Безопасное изменение темы"""
        try:
            theme_map = {
                "Темная": "Dark",
                "Светлая": "Light", 
                "Системная": "System"
            }
            new_theme = theme_map.get(theme_name, "Dark")
            ctk.set_appearance_mode(new_theme)
        except Exception as e:
            print(f"Ошибка при смене темы: {e}")
        
    def configure_service(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bat_path = os.path.join(script_dir, "service.bat")

        if not os.path.exists(bat_path):
            messagebox.showerror("Ошибка", f"Файл service.bat не найден в директории:\n{script_dir}")
            return

        try:
            if platform.system() == "Windows":
                os.startfile(bat_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(['open', bat_path])
            else:
                subprocess.Popen(['xdg-open', bat_path])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить service.bat:\n{str(e)}")

    def configure_lists(self):
        """Открытие редактора списков"""
        list_dialog = ListEditorDialog(self)
        
    def show_help(self):
        help_dialog = HelpDialog(self)
        
    def load_settings(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(script_dir, 'settings.json')
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'theme' in settings:
                        theme_map_reverse = {"Dark": "Темная", "Light": "Светлая", "System": "Системная"}
                        self.theme_combo.set(theme_map_reverse.get(settings['theme'], "Темная"))
                    if 'autostart' in settings:
                        self.autostart_checkbox.select() if settings['autostart'] else self.autostart_checkbox.deselect()
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
        
    def save_settings(self):
        theme_map = {
            "Темная": "Dark",
            "Светлая": "Light",
            "Системная": "System"
        }
        
        settings = {
            'autostart': bool(self.autostart_checkbox.get()),
            'theme': theme_map.get(self.theme_combo.get(), "Dark")
        }

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(script_dir, 'settings.json')
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f)
            messagebox.showinfo("Успех", "Настройки сохранены!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки:\n{str(e)}")

class ZapretGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.zapret_process = None
        self.selected_config = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self._is_closing = False
        
        self.title("Zapret-Custom")
        self.geometry("480x700")
        self.resizable(False, False)
        
        # Установка иконки программы
        self._set_icon()
        
        self._center_window()
        self._create_widgets()
        self.load_settings()
        
        # Правильная привязка обработчика закрытия
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def _set_icon(self):
        """Установка иконки программы"""
        try:
            icon_path = os.path.join(self.script_dir, 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
            else:
                print(f"Иконка не найдена: {icon_path}")
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")
        
    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        
        title_label = ctk.CTkLabel(
            self,
            text="Zapret Custom",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Статус программы: ВЫКЛЮЧЕН",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ff4444"
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=5)
        
        self.strategy_label = ctk.CTkLabel(
            self,
            text="Текущая стратегия:",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.strategy_label.grid(row=2, column=0, padx=20, pady=2)
        
        self.config_name_label = ctk.CTkLabel(
            self,
            text="Не выбрана",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2196F3"
        )
        self.config_name_label.grid(row=3, column=0, padx=20, pady=(2, 15))
        
        button_options = {
            "height": 50,
            "font": ctk.CTkFont(size=13, weight="bold"),
            "corner_radius": 8
        }
        
        self.config_button = ctk.CTkButton(
            self,
            text="⚙ НАСТРОИТЬ КОНФИГ",
            command=self.open_config_selection,
            **button_options
        )
        self.config_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.start_button = ctk.CTkButton(
            self,
            text="✓ ЗАПУСТИТЬ ZAPRET",
            command=self.start_zapret,
            fg_color="#388E3C",
            hover_color="#4CAF50",
            state="disabled",
            **button_options
        )
        self.start_button.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        
        self.stop_button = ctk.CTkButton(
            self,
            text="✗ ОСТАНОВИТЬ ZAPRET",
            command=self.stop_zapret,
            fg_color="#C2185B", 
            hover_color="#E91E63",
            state="disabled",
            **button_options
        )
        self.stop_button.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        
        self.test_button = ctk.CTkButton(
            self,
            text="📡 ТЕСТ СОЕДИНЕНИЯ",
            command=self.test_connection,
            **button_options
        )
        self.test_button.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        
        self.warp_button = ctk.CTkButton(
            self,
            text="☁ WARP",
            command=self.open_warp,
            **button_options
        )
        self.warp_button.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        
        self.settings_button = ctk.CTkButton(
            self,
            text="⚙ НАСТРОЙКИ",
            command=self.open_settings,
            **button_options
        )
        self.settings_button.grid(row=9, column=0, padx=20, pady=10, sticky="ew")
        
        theme_footer = ctk.CTkLabel(
            self,
            text="by Savvy08 - version 0.1",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        theme_footer.grid(row=10, column=0, padx=20, pady=(20, 2))
        
        self.theme_display = ctk.CTkLabel(
            self,
            text="Темная",
            font=ctk.CTkFont(size=12),
            text_color="#2196F3"
        )
        self.theme_display.grid(row=11, column=0, padx=20, pady=(2, 20))
        
    def update_theme_display(self, theme_name):
        """Обновляет отображение текущей темы"""
        self.theme_display.configure(text=theme_name)
        
    def on_config_selected(self, config_name):
        self.selected_config = config_name
        self.config_name_label.configure(text=config_name)
        self.start_button.configure(state="normal")
        messagebox.showinfo("Конфигурация выбрана", 
                          f"Конфигурация '{config_name}' готова к запуску.\nНажмите 'Запустить Zapret' для активации.")
        
    def open_config_selection(self):
        dialog = ConfigSelectionDialog(self)
        
    def start_zapret(self):
        if not self.selected_config:
            messagebox.showwarning("Ошибка", "Сначала выберите конфигурацию!")
            return

        bat_path = os.path.join(self.script_dir, self.selected_config)
        
        if not os.path.exists(bat_path):
            messagebox.showerror("Ошибка", f"Файл {self.selected_config} не найден!\nИскали по пути: {bat_path}")
            return

        try:
            os.chdir(self.script_dir)
            
            if platform.system() == "Windows":
                self.zapret_process = subprocess.Popen([bat_path],
                                                       shell=True,
                                                       creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                self.zapret_process = subprocess.Popen(['bash', bat_path])

            self.status_label.configure(
                text="Статус программы: ВКЛЮЧЕН",
                text_color="#4CAF50"
            )
            self.stop_button.configure(state="normal")
            self.start_button.configure(state="disabled")
            messagebox.showinfo("Успех", f"Zapret запущен с конфигурацией:\n{self.selected_config}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить конфигурацию:\n{str(e)}")

    def stop_zapret(self):
        if self.zapret_process:
            try:
                self.zapret_process.terminate()
                self.zapret_process.wait(timeout=5)
                self.zapret_process = None
                self.status_label.configure(
                    text="Статус программы: ВЫКЛЮЧЕН", 
                    text_color="#ff4444"
                )
                self.stop_button.configure(state="disabled")
                self.start_button.configure(state="normal")
                messagebox.showinfo("Успех", "Zapret остановлен!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось остановить процесс:\n{str(e)}")
        else:
            messagebox.showwarning("Предупреждение", "Процесс не запущен.")

    def test_connection(self):
        dialog = TestConnectionDialog(self)
        
    def open_warp(self):
        dialog = WarpDialog(self)
        
    def open_settings(self):
        dialog = SettingsDialog(self)
        
    def load_settings(self):
        try:
            settings_path = os.path.join(self.script_dir, 'settings.json')
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'theme' in settings:
                        theme_map = {"Dark": "Темная", "Light": "Светлая", "System": "Системная"}
                        theme_name = theme_map.get(settings['theme'], "Темная")
                        self.theme_display.configure(text=theme_name)
                        ctk.set_appearance_mode(settings['theme'])
        except Exception as e:
            print(f"Не удалось загрузить настройки: {e}")

    def on_closing(self):
        """Безопасное закрытие приложения"""
        if self._is_closing:
            return
            
        self._is_closing = True
        
        # Проверяем, запущен ли процесс Zapret
        if self.zapret_process and self.zapret_process.poll() is None:
            if messagebox.askyesno('Подтверждение', 
                                 "Процесс Zapret запущен. Остановить его перед выходом?"):
                try:
                    self.zapret_process.terminate()
                    self.zapret_process.wait(timeout=3)
                except:
                    try:
                        self.zapret_process.kill()
                    except:
                        pass
        
        # Безопасное уничтожение окна
        self.safe_destroy()

    def safe_destroy(self):
        """Безопасное уничтожение окна"""
        try:
            self.quit()
        except:
            pass
        try:
            self.destroy()
        except:
            pass

if __name__ == "__main__":
    print(f"Python исполняется из: {sys.executable}")
    print(f"Текущая рабочая директория: {os.getcwd()}")
    print(f"Директория скрипта: {os.path.dirname(os.path.abspath(__file__))}")
    
    try:
        app = ZapretGUI()
        app.mainloop()
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")
        input("Нажмите Enter для выхода...")