# активировать VENV: venv\Scripts\activate либо .\venv\Scripts\Activate.ps1
# КОМПИЛИЦИЯ:
# 1. cd "F:\Doki\СВОЙ ЗАПРЕТ\CODE PY\zapret-discord-youtube" 2. pyinstaller --noconsole --name="ZapretCustom" main.py
# # Если будет ошибка выполнения скриптов: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
"""
Zapret-Custom GUI - PyQt6 + QFluentWidgets версия
Современный интерфейс в стиле Hiddify с системой логирования
Установка: pip install PyQt6 PyQt6-Fluent-Widgets psutil
"""
import sys
import os
import subprocess
import platform
import urllib.request
import urllib.error
import ssl
import json
import socket
import signal
import webbrowser
import threading
import winreg
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize, QObject
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import (
    NavigationInterface, NavigationItemPosition,
    PushButton, PrimaryPushButton, TransparentToolButton,
    FluentIcon as FIF, setTheme, Theme, InfoBar, InfoBarPosition,
    ComboBox, CheckBox, TextEdit, ListWidget, ScrollArea,
    MessageBox, Dialog, BodyLabel, SubtitleLabel, TitleLabel,
    StrongBodyLabel, CaptionLabel, ProgressRing, StateToolTip, isDarkTheme
)
import psutil

class Logger(QObject):
    """Централизованная система логирования"""
    log_updated = pyqtSignal(str)
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self.logs = []
        self.max_logs = 1000
    
    def log(self, level, message):
        """Добавление записи в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        
        # Ограничение количества логов
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
        
        self.log_updated.emit(log_entry)
        print(log_entry)  # Также выводим в консоль
    
    def info(self, message):
        """Информационное сообщение"""
        self.log("INFO", message)
    
    def success(self, message):
        """Успешное действие"""
        self.log("SUCCESS", message)
    
    def warning(self, message):
        """Предупреждение"""
        self.log("WARNING", message)
    
    def error(self, message):
        """Ошибка"""
        self.log("ERROR", message)
    
    def get_all_logs(self):
        """Получить все логи"""
        return "\n".join(self.logs)
    
    def clear_logs(self):
        """Очистить логи"""
        self.logs.clear()
        self.info("Логи очищены")

class TestConnectionThread(QThread):
    """Поток для тестирования соединения"""
    finished = pyqtSignal(str)

    def run(self):
        logger = Logger()
        logger.info("Начато тестирование соединения")
        
        try:
            result = "═══════════════════════════════════════════════\n"
            result += "        ТЕСТИРОВАНИЕ СОЕДИНЕНИЯ\n"
            result += "═══════════════════════════════════════════════\n\n"
            websites = [
                ('Discord (Домен)', 'https://discord.com'),
                ('YouTube', 'https://www.youtube.com'),
                ('Google', 'https://www.google.com'),
                ('Cloudflare', 'https://www.cloudflare.com'),
                ('Yahoo', 'https://www.yahoo.com'),
                ('Amazon', 'https://www.amazon.com')
            ]
            result += "ПРОВЕРКА ДОСТУПНОСТИ САЙТОВ:\n"
            result += "─────────────────────────────────────────────\n"

            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            for name, url in websites:
                try:
                    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    response = urllib.request.urlopen(request, timeout=5, context=ssl_context)
                    result += f"✓ {name:20} | Доступен (Код: {response.status})\n"
                    logger.info(f"Сайт {name} доступен (код {response.status})")
                except urllib.error.URLError as e:
                    result += f"✗ {name:20} | Недоступен ({str(e.reason)[:30]})\n"
                    logger.warning(f"Сайт {name} недоступен: {str(e.reason)[:30]}")
                except Exception as e:
                    result += f"✗ {name:20} | Ошибка ({str(e)[:30]})\n"
                    logger.error(f"Ошибка проверки {name}: {str(e)[:30]}")
            
            result += "\nПРОВЕРКА IP И DNS:\n"
            result += "─────────────────────────────────────────────\n"

            try:
                request = urllib.request.Request('https://api.ipify.org', headers={'User-Agent': 'Mozilla/5.0'})
                ip_response = urllib.request.urlopen(request, timeout=5, context=ssl_context)
                external_ip = ip_response.read().decode('utf-8')
                result += f"✓ Внешний IP: {external_ip}\n"
                logger.info(f"Внешний IP: {external_ip}")
            except Exception as e:
                result += f"✗ Не удалось получить внешний IP: {str(e)[:40]}\n"
                logger.error(f"Не удалось получить внешний IP: {str(e)[:40]}")
            
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
                    logger.info(f"DNS {name} ({dns_ip}) доступен")
                except Exception as e:
                    result += f"✗ {name:20} | {dns_ip} - Недоступен\n"
                    logger.warning(f"DNS {name} ({dns_ip}) недоступен")
            
            result += "\nПРОВЕРКА DNS РЕЗОЛВИНГА:\n"
            result += "─────────────────────────────────────────────\n"

            test_domains = ['discord.com', 'google.com', 'cloudflare.com']

            for domain in test_domains:
                try:
                    ip = socket.gethostbyname(domain)
                    result += f"✓ {domain:20} → {ip}\n"
                    logger.info(f"DNS резолвинг {domain} → {ip}")
                except Exception as e:
                    result += f"✗ {domain:20} → Не удалось разрешить\n"
                    logger.error(f"Не удалось разрешить {domain}")
            
            result += "\n═══════════════════════════════════════════════\n"
            result += "           ТЕСТИРОВАНИЕ ЗАВЕРШЕНО\n"
            result += "═══════════════════════════════════════════════\n"

            logger.success("Тестирование соединения завершено успешно")
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Критическая ошибка при тестировании: {str(e)}")
            self.finished.emit(f"Критическая ошибка при тестировании:\n{str(e)}")

class HomeInterface(QWidget):
    """Главная страница с кнопкой подключения"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.zapret_process = None
        self.zapret_pid = None
        self.selected_config = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.is_connected = False
        self.logger = Logger()

        self.setObjectName("homeInterface")
        self.init_ui()
        self.load_settings()
        
        self.logger.info("Интерфейс HomeInterface инициализирован")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = TitleLabel("Zapret Custom", self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        version_label = CaptionLabel("version 0.3", self)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        layout.addStretch(1)

        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setSpacing(30)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.connection_icon = QLabel()
        self.connection_icon.setFixedSize(180, 180)
        self.connection_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_icon_theme()

        icon_path = os.path.join(self.script_dir, 'iconhome.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            self.connection_icon.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.connection_icon.setText("⚡")

        center_layout.addWidget(self.connection_icon, 0, Qt.AlignmentFlag.AlignCenter)

        self.connect_button = PrimaryPushButton("Нажмите для подключения", self)
        self.connect_button.setFixedSize(280, 50)
        self.connect_button.clicked.connect(self.toggle_connection)
        center_layout.addWidget(self.connect_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.status_label = StrongBodyLabel("Отключено", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #f44336; font-size: 14px;")
        center_layout.addWidget(self.status_label, 0, Qt.AlignmentFlag.AlignCenter)

        self.config_label = BodyLabel("Конфигурация: Не выбрана", self)
        self.config_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.config_label, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(center_widget)
        layout.addStretch(2)

    def update_icon_theme(self):
        if self.is_connected:
            if isDarkTheme():
                self.connection_icon.setStyleSheet("""
                    QLabel {
                        background-color: #1a1a2e;
                        border-radius: 90px;
                        border: 2px solid #64B5F6;
                    }
                """)
            else:
                self.connection_icon.setStyleSheet("""
                    QLabel {
                        background-color: #e3f2fd;
                        border-radius: 90px;
                        border: 2px solid #2196F3;
                    }
                """)
        else:
            if isDarkTheme():
                self.connection_icon.setStyleSheet("""
                    QLabel {
                        background-color: #2d2d2d;
                        border-radius: 90px;
                        border: 2px solid #444;
                    }
                """)
            else:
                self.connection_icon.setStyleSheet("""
                    QLabel {
                        background-color: #f5f5f5;
                        border-radius: 90px;
                        border: 2px solid #ccc;
                    }
                """)

    def toggle_connection(self):
        if self.is_connected:
            self.stop_zapret()
        else:
            self.start_zapret()

    def start_zapret(self):
        if not self.selected_config:
            self.logger.warning("Попытка запуска без выбранной конфигурации")
            InfoBar.warning(
                title="Ошибка",
                content="Сначала выберите конфигурацию в Config Options!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        if self.selected_config.startswith("version 1.8.3/"):
            bat_path = os.path.join(self.script_dir, self.selected_config)
        else:
            bat_path = os.path.join(self.script_dir, self.selected_config)

        if not os.path.exists(bat_path):
            self.logger.error(f"Файл конфигурации не найден: {self.selected_config}")
            InfoBar.error(
                title="Ошибка",
                content=f"Файл {self.selected_config} не найден!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        
        try:
            bat_dir = os.path.dirname(bat_path)
            os.chdir(bat_dir)

            if platform.system() == "Windows":
                self.zapret_process = subprocess.Popen(
                    [bat_path],
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                self.zapret_process = subprocess.Popen(
                    ['bash', bat_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

            self.zapret_pid = self.zapret_process.pid
            self.is_connected = True

            self.animate_connection_start()
            
            display_name = self.selected_config.replace("version 1.8.3/", "")
            self.logger.success(f"Zapret запущен: {display_name} (PID: {self.zapret_pid})")

            InfoBar.success(
                title="Успех",
                content=f"Zapret запущен: {display_name}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
        except Exception as e:
            self.logger.error(f"Ошибка запуска Zapret: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Не удалось запустить: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def stop_zapret(self):
        if not self.zapret_process:
            return
        
        try:
            if self.zapret_process.poll() is None:
                if platform.system() == "Windows":
                    if self.zapret_pid:
                        subprocess.run(
                            ['taskkill', '/PID', str(self.zapret_pid), '/F'],
                            capture_output=True,
                            timeout=5
                        )
                    self.zapret_process.terminate()
                else:
                    os.kill(self.zapret_process.pid, signal.SIGTERM)

            self.zapret_process = None
            self.zapret_pid = None
            self.is_connected = False

            self.animate_connection_stop()
            
            self.logger.success("Zapret остановлен")

            InfoBar.success(
                title="Успех",
                content="Zapret остановлен!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

        except Exception as e:
            self.logger.error(f"Ошибка остановки Zapret: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Не удалось остановить: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def animate_connection_start(self):
        self.update_icon_theme()
        self.update_connection_ui()

    def animate_connection_stop(self):
        self.update_icon_theme()
        self.update_connection_ui()

    def update_connection_ui(self):
        if self.is_connected:
            self.connect_button.setText("Отключиться")
            self.status_label.setText("Подключено")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 14px;")
        else:
            self.connect_button.setText("Нажмите для подключения")
            self.status_label.setText("Отключено")
            self.status_label.setStyleSheet("color: #f44336; font-size: 14px;")

    def set_config(self, config_name):
        self.selected_config = config_name
        display_name = config_name.replace("version 1.8.3/", "")
        self.config_label.setText(f"Конфигурация: {display_name}")
        self.config_label.setStyleSheet("color: #2196F3; font-size: 12px;")
        self._save_selected_config()
        self.logger.info(f"Выбрана конфигурация: {display_name}")

    def _save_selected_config(self):
        try:
            settings_path = os.path.join(self.script_dir, 'settings.json')
            settings = {}
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            settings['selected_config'] = self.selected_config
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Ошибка сохранения конфигурации: {e}")

    def load_settings(self):
        try:
            settings_path = os.path.join(self.script_dir, 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'selected_config' in settings:
                        self.selected_config = settings['selected_config']
                        display_name = self.selected_config.replace("version 1.8.3/", "")
                        self.config_label.setText(f"Конфигурация: {display_name}")
                        self.config_label.setStyleSheet("color: #2196F3; font-size: 12px;")
                        self.logger.info(f"Загружена конфигурация из настроек: {display_name}")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки настроек: {e}")

class ConfigInterface(QWidget):
    config_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.bat_directory = self.script_dir
        self.logger = Logger()
        self.setObjectName("configInterface")
        self.init_ui()
        self.load_bat_files()
        self.logger.info("Интерфейс ConfigInterface инициализирован")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = SubtitleLabel("Выбор конфигурации", self)
        layout.addWidget(title)

        dir_layout = QHBoxLayout()
        self.dir_label = BodyLabel(f"Директория: {self.bat_directory}", self)
        dir_layout.addWidget(self.dir_label)

        dir_button = PushButton("Выбрать папку", self)
        dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(dir_button)
        layout.addLayout(dir_layout)

        self.config_list = ListWidget(self)
        self.update_list_theme()
        self.config_list.itemClicked.connect(self.on_config_clicked)
        layout.addWidget(self.config_list)

        buttons_layout = QHBoxLayout()

        self.select_button = PrimaryPushButton("Выбрать", self)
        self.select_button.clicked.connect(self.select_config)
        self.select_button.setEnabled(False)
        buttons_layout.addWidget(self.select_button)

        refresh_button = PushButton("Обновить", self)
        refresh_button.clicked.connect(self.load_bat_files)
        buttons_layout.addWidget(refresh_button)

        layout.addLayout(buttons_layout)

    def update_list_theme(self):
        if isDarkTheme():
            self.config_list.setStyleSheet("""
                QListWidget {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    border-radius: 5px;
                    color: white;
                    outline: none;
                }
                QListWidget::item {
                    background-color: #2d2d2d;
                    color: white;
                    padding: 8px;
                    border-bottom: 1px solid #444;
                }
                QListWidget::item:selected {
                    background-color: #2196F3;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #3d3d3d;
                }
            """)
        else:
            self.config_list.setStyleSheet("""
                QListWidget {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    color: black;
                    outline: none;
                }
                QListWidget::item {
                    background-color: white;
                    color: black;
                    padding: 8px;
                    border-bottom: 1px solid #eee;
                }
                QListWidget::item:selected {
                    background-color: #2196F3;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #f5f5f5;
                }
            """)

    def select_directory(self):
        from PyQt6.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(
            self,
            "Выберите директорию с BAT файлами",
            self.bat_directory
        )
        if directory:
            self.bat_directory = directory
            self.dir_label.setText(f"Директория: {directory}")
            self.load_bat_files()
            self.logger.info(f"Изменена директория конфигураций: {directory}")

    def load_bat_files(self):
        try:
            self.config_list.clear()

            bat_files = [
                f for f in os.listdir(self.bat_directory)
                if f.endswith('.bat') and f.lower() != 'service.bat'
                and os.path.isfile(os.path.join(self.bat_directory, f))
            ]
            
            version_dir = os.path.join(self.bat_directory, 'version 1.8.3')
            version_bat_files = []
            if os.path.exists(version_dir) and os.path.isdir(version_dir):
                version_bat_files = [
                    f"version 1.8.3/{f}" for f in os.listdir(version_dir)
                    if f.endswith('.bat') and f.lower() != 'service.bat'
                    and os.path.isfile(os.path.join(version_dir, f))
                ]
            
            all_files = bat_files + version_bat_files
            
            if all_files:
                for bat_file in sorted(all_files):
                    self.config_list.addItem(bat_file)
                self.select_button.setEnabled(False)
                self.logger.info(f"Загружено конфигураций: {len(all_files)}")
            else:
                self.config_list.addItem("Нет доступных BAT файлов")
                self.select_button.setEnabled(False)
                self.logger.warning("BAT файлы не найдены")
        except Exception as e:
            self.logger.error(f"Ошибка загрузки BAT файлов: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Ошибка загрузки файлов: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def on_config_clicked(self, item):
        if item.text() != "Нет доступных BAT файлов":
            self.select_button.setEnabled(True)

    def select_config(self):
        current_item = self.config_list.currentItem()
        if current_item and current_item.text() != "Нет доступных BAT файлов":
            config_name = current_item.text()
            self.config_selected.emit(config_name)
            display_name = config_name.replace("version 1.8.3/", "")
            InfoBar.success(
                title="Успех",
                content=f"Выбрана конфигурация: {display_name}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

class TestConnectionInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_thread = None
        self.logger = Logger()
        self.setObjectName("testInterface")
        self.init_ui()
        self.logger.info("Интерфейс TestConnectionInterface инициализирован")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = SubtitleLabel("Тестирование соединения", self)
        layout.addWidget(title)

        self.result_text = TextEdit(self)
        self.result_text.setReadOnly(True)
        self.update_text_theme()
        self.result_text.setPlainText("Нажмите 'Запустить тест' для проверки соединения")
        layout.addWidget(self.result_text)

        buttons_layout = QHBoxLayout()

        self.start_button = PrimaryPushButton("Запустить тест", self)
        self.start_button.clicked.connect(self.start_test)
        buttons_layout.addWidget(self.start_button)

        clear_button = PushButton("Очистить", self)
        clear_button.clicked.connect(self.clear_results)
        buttons_layout.addWidget(clear_button)

        layout.addLayout(buttons_layout)

    def update_text_theme(self):
        if isDarkTheme():
            self.result_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    border-radius: 5px;
                    color: #ccc;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 11px;
                    padding: 10px;
                }
            """)
        else:
            self.result_text.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    color: #333;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 11px;
                    padding: 10px;
                }
            """)

    def start_test(self):
        self.result_text.setPlainText("Выполняется тестирование...\nПожалуйста, подождите...\n")
        self.start_button.setEnabled(False)
        self.start_button.setText("Тестирование...")

        self.test_thread = TestConnectionThread()
        self.test_thread.finished.connect(self.test_finished)
        self.test_thread.start()

    def test_finished(self, result):
        self.result_text.setPlainText(result)
        self.start_button.setEnabled(True)
        self.start_button.setText("Запустить тест")

    def clear_results(self):
        self.result_text.setPlainText("Нажмите 'Запустить тест' для проверки соединения")

class SettingsInterface(QWidget):
    theme_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.logger = Logger()
        self.setObjectName("settingsInterface")
        self.init_ui()
        self.load_settings()
        self.logger.info("Интерфейс SettingsInterface инициализирован")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = SubtitleLabel("Настройки", self)
        layout.addWidget(title)

        theme_label = StrongBodyLabel("Тема оформления:", self)
        layout.addWidget(theme_label)

        self.theme_combo = ComboBox(self)
        self.theme_combo.addItems(["Темная", "Светлая"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        layout.addWidget(self.theme_combo)

        self.autostart_checkbox = CheckBox("Автозапуск Zapret при старте программы", self)
        layout.addWidget(self.autostart_checkbox)
        
        self.app_autostart_checkbox = CheckBox("Автозапуск приложения при входе в Windows", self)
        layout.addWidget(self.app_autostart_checkbox)
        
        self.bat_autostart_checkbox = CheckBox("Автозапуск BAT при старте приложения", self)
        layout.addWidget(self.bat_autostart_checkbox)
        
        self.update_combo_theme()
        self.update_checkbox_theme()

        buttons_label = StrongBodyLabel("Дополнительные функции:", self)
        layout.addWidget(buttons_label)

        self.service_button = PushButton("Настроить service.bat", self)
        self.service_button.clicked.connect(self.configure_service)
        layout.addWidget(self.service_button)
        
        self.service_183_button = PushButton("Настроить service.bat 1.8.3", self)
        self.service_183_button.clicked.connect(self.configure_service_183)
        layout.addWidget(self.service_183_button)

        self.list_button = PushButton("Настроить списки", self)
        self.list_button.clicked.connect(self.configure_lists)
        layout.addWidget(self.list_button)

        self.warp_button = PushButton("Cloudflare WARP", self)
        self.warp_button.clicked.connect(self.open_warp)
        layout.addWidget(self.warp_button)

        layout.addStretch()

        self.save_button = PrimaryPushButton("Сохранить настройки", self)
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

    def update_combo_theme(self):
        if isDarkTheme():
            self.theme_combo.setStyleSheet("""
                QComboBox {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    border-radius: 5px;
                    color: white;
                    padding: 5px;
                    min-width: 120px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 1px solid #444;
                    padding: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    color: white;
                    selection-background-color: #2196F3;
                }
            """)
        else:
            self.theme_combo.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    color: black;
                    padding: 5px;
                    min-width: 120px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 1px solid #ddd;
                    padding: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    border: 1px solid #ddd;
                    color: black;
                    selection-background-color: #2196F3;
                }
            """)

    def update_checkbox_theme(self):
        if isDarkTheme():
            style = """
                QCheckBox {
                    color: #ccc;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #444;
                    border-radius: 3px;
                    background-color: #2d2d2d;
                }
                QCheckBox::indicator:checked {
                    background-color: #2196F3;
                    border: 1px solid #2196F3;
                }
            """
        else:
            style = """
                QCheckBox {
                    color: #333;
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #2196F3;
                    border: 1px solid #2196F3;
                }
            """
        self.autostart_checkbox.setStyleSheet(style)
        self.app_autostart_checkbox.setStyleSheet(style)
        self.bat_autostart_checkbox.setStyleSheet(style)

    def change_theme(self, theme_name):
        if theme_name == "Темная":
            setTheme(Theme.DARK)
            self.logger.info("Тема изменена на темную")
        else:
            setTheme(Theme.LIGHT)
            self.logger.info("Тема изменена на светлую")
        self.theme_changed.emit()

    def configure_service(self):
        bat_path = os.path.join(self.script_dir, "service.bat")
        if not os.path.exists(bat_path):
            self.logger.error("Файл service.bat не найден")
            InfoBar.error(
                title="Ошибка",
                content=f"Файл service.bat не найден!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        try:
            if platform.system() == "Windows":
                os.startfile(bat_path)
            else:
                subprocess.Popen(['open' if platform.system() == "Darwin" else 'xdg-open', bat_path])
            self.logger.info("Открыт файл service.bat")
        except Exception as e:
            self.logger.error(f"Ошибка открытия service.bat: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Не удалось открыть файл: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def configure_service_183(self):
        bat_path = os.path.join(self.script_dir, "version 1.8.3", "service.bat")
        if not os.path.exists(bat_path):
            self.logger.error("Файл service.bat 1.8.3 не найден")
            InfoBar.error(
                title="Ошибка",
                content=f"Файл service.bat в папке version 1.8.3 не найден!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        try:
            if platform.system() == "Windows":
                os.startfile(bat_path)
            else:
                subprocess.Popen(['open' if platform.system() == "Darwin" else 'xdg-open', bat_path])
            self.logger.info("Открыт файл service.bat 1.8.3")
        except Exception as e:
            self.logger.error(f"Ошибка открытия service.bat 1.8.3: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Не удалось открыть файл: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def configure_lists(self):
        lists_dir = os.path.join(self.script_dir, 'lists')
        if os.path.exists(lists_dir):
            try:
                if platform.system() == "Windows":
                    os.startfile(lists_dir)
                else:
                    subprocess.Popen(['open' if platform.system() == "Darwin" else 'xdg-open', lists_dir])
                self.logger.info("Открыта папка lists")
            except Exception as e:
                self.logger.error(f"Ошибка открытия папки lists: {str(e)}")
                InfoBar.error(
                    title="Ошибка",
                    content=f"Не удалось открыть папку: {str(e)}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
        else:
            self.logger.warning("Папка lists не найдена")
            InfoBar.warning(
                title="Предупреждение",
                content="Папка lists не найдена!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def open_warp(self):
        webbrowser.open("https://1.1.1.1")
        self.logger.info("Открыта страница Cloudflare WARP")

    def load_settings(self):
        bat_path = os.path.join(self.script_dir, "service.bat")
        if not os.path.exists(bat_path):
            self.logger.error("Файл service.bat не найден")
            InfoBar.error(
                title="Ошибка",
                content=f"Файл service.bat не найден!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        try:
            if platform.system() == "Windows":
                os.startfile(bat_path)
            else:
                subprocess.Popen(['open' if platform.system() == "Darwin" else 'xdg-open', bat_path])
            self.logger.info("Открыт файл service.bat")
        except Exception as e:
            self.logger.error(f"Ошибка открытия service.bat: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Не удалось открыть файл: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def configure_service_183(self):
        bat_path = os.path.join(self.script_dir, "version 1.8.3", "service.bat")
        if not os.path.exists(bat_path):
            self.logger.error("Файл service.bat 1.8.3 не найден")
            InfoBar.error(
                title="Ошибка",
                content=f"Файл service.bat в папке version 1.8.3 не найден!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
            return
        try:
            if platform.system() == "Windows":
                os.startfile(bat_path)
            else:
                subprocess.Popen(['open' if platform.system() == "Darwin" else 'xdg-open', bat_path])
            self.logger.info("Открыт файл service.bat 1.8.3")
        except Exception as e:
            self.logger.error(f"Ошибка открытия service.bat 1.8.3: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Не удалось открыть файл: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def configure_lists(self):
        lists_dir = os.path.join(self.script_dir, 'lists')
        if os.path.exists(lists_dir):
            try:
                if platform.system() == "Windows":
                    os.startfile(lists_dir)
                else:
                    subprocess.Popen(['open' if platform.system() == "Darwin" else 'xdg-open', lists_dir])
                self.logger.info("Открыта папка lists")
            except Exception as e:
                self.logger.error(f"Ошибка открытия папки lists: {str(e)}")
                InfoBar.error(
                    title="Ошибка",
                    content=f"Не удалось открыть папку: {str(e)}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
        else:
            self.logger.warning("Папка lists не найдена")
            InfoBar.warning(
                title="Предупреждение",
                content="Папка lists не найдена!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

    def open_warp(self):
        webbrowser.open("https://1.1.1.1")
        self.logger.info("Открыта страница Cloudflare WARP")

    def add_to_startup(self):
        if platform.system() != "Windows":
            return False
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            exe_path = sys.executable
            if exe_path.endswith('python.exe') or exe_path.endswith('pythonw.exe'):
                script_path = os.path.abspath(__file__)
                startup_command = f'"{exe_path}" "{script_path}"'
            else:
                startup_command = f'"{exe_path}"'
            
            winreg.SetValueEx(key, "ZapretCustom", 0, winreg.REG_SZ, startup_command)
            winreg.CloseKey(key)
            self.logger.success("Приложение добавлено в автозагрузку Windows")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка добавления в автозагрузку: {e}")
            return False

    def remove_from_startup(self):
        if platform.system() != "Windows":
            return False
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.DeleteValue(key, "ZapretCustom")
            winreg.CloseKey(key)
            self.logger.success("Приложение удалено из автозагрузки Windows")
            return True
        except FileNotFoundError:
            return True
        except Exception as e:
            self.logger.error(f"Ошибка удаления из автозагрузки: {e}")
            return False

    def is_in_startup(self):
        if platform.system() != "Windows":
            return False
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            
            try:
                winreg.QueryValueEx(key, "ZapretCustom")
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception as e:
            return False

    def load_settings(self):
        try:
            settings_path = os.path.join(self.script_dir, 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'theme' in settings:
                        theme_map = {"Dark": "Темная", "Light": "Светлая"}
                        self.theme_combo.setCurrentText(theme_map.get(settings['theme'], "Темная"))
                    if 'autostart' in settings:
                        self.autostart_checkbox.setChecked(settings['autostart'])
                    
                    if 'bat_autostart' in settings:
                        self.bat_autostart_checkbox.setChecked(settings['bat_autostart'])
            
            self.app_autostart_checkbox.setChecked(self.is_in_startup())
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки настроек: {e}")

    def save_settings(self):
        theme_map = {"Темная": "Dark", "Светлая": "Light"}

        settings = {
            'autostart': self.autostart_checkbox.isChecked(),
            'theme': theme_map.get(self.theme_combo.currentText(), "Dark"),
            'bat_autostart': self.bat_autostart_checkbox.isChecked()
        }
        
        # Логирование изменения автозапуска BAT
        if self.bat_autostart_checkbox.isChecked():
            self.logger.success("Автозапуск BAT включен")
        else:
            self.logger.info("Автозапуск BAT выключен")
        
        if self.app_autostart_checkbox.isChecked():
            if self.add_to_startup():
                InfoBar.success(
                    title="Успех",
                    content="Приложение добавлено в автозагрузку!",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            else:
                InfoBar.error(
                    title="Ошибка",
                    content="Не удалось добавить в автозагрузку!",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
        else:
            if self.remove_from_startup():
                InfoBar.success(
                    title="Успех",
                    content="Приложение удалено из автозагрузки!",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
        
        try:
            settings_path = os.path.join(self.script_dir, 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
                    if 'selected_config' in existing_settings:
                        settings['selected_config'] = existing_settings['selected_config']
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
            
            self.logger.success("Настройки сохранены")
            
            InfoBar.success(
                title="Успех",
                content="Настройки сохранены!",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        except Exception as e:
            self.logger.error(f"Ошибка сохранения настроек: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Не удалось сохранить настройки: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

class LogsInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()
        self.setObjectName("logsInterface")
        self.init_ui()
        
        # Подключаемся к сигналу обновления логов
        self.logger.log_updated.connect(self.append_log)
        
        # Загружаем существующие логи
        self.refresh_logs()
        
        self.logger.info("Интерфейс LogsInterface инициализирован")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = SubtitleLabel("Логи приложения", self)
        layout.addWidget(title)

        self.log_text = TextEdit(self)
        self.log_text.setReadOnly(True)
        self.update_text_theme()
        layout.addWidget(self.log_text)

        buttons_layout = QHBoxLayout()

        refresh_button = PrimaryPushButton("Обновить", self)
        refresh_button.clicked.connect(self.refresh_logs)
        buttons_layout.addWidget(refresh_button)

        clear_button = PushButton("Очистить", self)
        clear_button.clicked.connect(self.clear_logs)
        buttons_layout.addWidget(clear_button)
        
        export_button = PushButton("Экспортировать", self)
        export_button.clicked.connect(self.export_logs)
        buttons_layout.addWidget(export_button)

        layout.addLayout(buttons_layout)

    def update_text_theme(self):
        if isDarkTheme():
            self.log_text.setStyleSheet("""
                QTextEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    border-radius: 5px;
                    color: #ccc;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 11px;
                    padding: 10px;
                }
            """)
        else:
            self.log_text.setStyleSheet("""
                QTextEdit {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    color: #333;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 11px;
                    padding: 10px;
                }
            """)

    def append_log(self, log_entry):
        """Добавление новой записи в лог"""
        self.log_text.append(log_entry)
        # Автопрокрутка вниз
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def refresh_logs(self):
        """Обновление всех логов"""
        all_logs = self.logger.get_all_logs()
        if all_logs:
            self.log_text.setPlainText(all_logs)
        else:
            self.log_text.setPlainText("Логи пусты. Действия будут отображаться здесь...")
        
        # Прокрутка вниз
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        """Очистка логов"""
        self.logger.clear_logs()
        self.log_text.setPlainText("Логи очищены")

    def export_logs(self):
        """Экспорт логов в файл"""
        try:
            from PyQt6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить логи",
                f"zapret_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logger.get_all_logs())
                
                self.logger.success(f"Логи экспортированы в: {file_path}")
                InfoBar.success(
                    title="Успех",
                    content=f"Логи сохранены в {os.path.basename(file_path)}",
                    orient=Qt.Orientation.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
        except Exception as e:
            self.logger.error(f"Ошибка экспорта логов: {str(e)}")
            InfoBar.error(
                title="Ошибка",
                content=f"Не удалось экспортировать логи: {str(e)}",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )

class AboutInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = Logger()
        self.setObjectName("aboutInterface")
        self.init_ui()
        self.logger.info("Интерфейс AboutInterface инициализирован")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon_label.setFixedSize(120, 120)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if isDarkTheme():
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #1a1a2e;
                    border-radius: 60px;
                    border: 2px solid #64B5F6;
                }
            """)
        else:
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    border-radius: 60px;
                    border: 2px solid #2196F3;
                }
            """)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'iconhome.png')
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText("⚡")

        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)

        title = TitleLabel("Zapret Custom", self)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        version = SubtitleLabel("Version 0.3", self)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        description = BodyLabel(
            "Графический интерфейс для zapret-discord-youtube\n"
            "Программа для обхода блокировок Discord и YouTube\n\n"
            "Создано с использованием PyQt6 и QFluentWidgets",
            self
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)

        author = CaptionLabel("by Savvy08", self)
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author)

        layout.addStretch()

        github_button = PushButton("GitHub Repository", self)
        github_button.clicked.connect(lambda: webbrowser.open("https://github.com/Savvy08/Zapret-Custom"))
        layout.addWidget(github_button, 0, Qt.AlignmentFlag.AlignCenter)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zapret Custom 0.3")
        self.resize(900, 650)
        
        self.logger = Logger()

        setTheme(Theme.DARK)
        self.update_palette()
        self.set_icon()
        self.init_ui()
        self.center_window()
        
        self.logger.info("="*50)
        self.logger.info("Приложение Zapret Custom запущено")
        self.logger.info(f"Версия: 0.3")
        self.logger.info(f"Платформа: {platform.system()} {platform.release()}")
        self.logger.info("="*50)
        
        self.check_bat_autostart()

    def update_palette(self):
        if isDarkTheme():
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
            dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 30))
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            QApplication.setPalette(dark_palette)
            self.setPalette(dark_palette)
        else:
            light_palette = QPalette()
            light_palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
            light_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            light_palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
            light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
            light_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
            light_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            light_palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            light_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            light_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            light_palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
            light_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            light_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
            QApplication.setPalette(light_palette)
            self.setPalette(light_palette)

    def set_icon(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(script_dir, 'icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            self.logger.error(f"Не удалось установить иконку: {e}")

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.navigation = NavigationInterface(self, showMenuButton=True)

        self.home_interface = HomeInterface(self)
        self.config_interface = ConfigInterface(self)
        self.test_interface = TestConnectionInterface(self)
        self.settings_interface = SettingsInterface(self)
        self.logs_interface = LogsInterface(self)
        self.about_interface = AboutInterface(self)

        self.add_navigation_items()

        from PyQt6.QtWidgets import QStackedWidget
        self.stack_widget = QStackedWidget(self)
        self.stack_widget.addWidget(self.home_interface)
        self.stack_widget.addWidget(self.config_interface)
        self.stack_widget.addWidget(self.test_interface)
        self.stack_widget.addWidget(self.settings_interface)
        self.stack_widget.addWidget(self.logs_interface)
        self.stack_widget.addWidget(self.about_interface)

        main_layout.addWidget(self.navigation)
        main_layout.addWidget(self.stack_widget)

        self.navigation.displayModeChanged.connect(self.on_display_mode_changed)
        self.config_interface.config_selected.connect(self.on_config_selected)
        self.settings_interface.theme_changed.connect(self.on_theme_changed)

        self.stack_widget.setCurrentWidget(self.home_interface)

    def add_navigation_items(self):
        self.navigation.addItem(
            routeKey='home',
            icon=FIF.HOME,
            text='Главная',
            onClick=lambda: self.switch_interface(self.home_interface),
            position=NavigationItemPosition.TOP
        )

        self.navigation.addItem(
            routeKey='config',
            icon=FIF.SETTING,
            text='Конфигурация',
            onClick=lambda: self.switch_interface(self.config_interface),
            position=NavigationItemPosition.TOP
        )

        self.navigation.addItem(
            routeKey='test',
            icon=FIF.SYNC,
            text='Тест сети',
            onClick=lambda: self.switch_interface(self.test_interface),
            position=NavigationItemPosition.TOP
        )

        self.navigation.addItem(
            routeKey='logs',
            icon=FIF.DOCUMENT,
            text='Логи',
            onClick=lambda: self.switch_interface(self.logs_interface),
            position=NavigationItemPosition.TOP
        )

        self.navigation.addItem(
            routeKey='settings',
            icon=FIF.SETTING,
            text='Настройки',
            onClick=lambda: self.switch_interface(self.settings_interface),
            position=NavigationItemPosition.BOTTOM
        )

        self.navigation.addItem(
            routeKey='about',
            icon=FIF.INFO,
            text='О программе',
            onClick=lambda: self.switch_interface(self.about_interface),
            position=NavigationItemPosition.BOTTOM
        )

    def switch_interface(self, interface):
        self.stack_widget.setCurrentWidget(interface)
        interface_name = interface.objectName()
        self.logger.info(f"Переключено на интерфейс: {interface_name}")

    def on_display_mode_changed(self):
        pass

    def on_config_selected(self, config_name):
        self.home_interface.set_config(config_name)
        self.switch_interface(self.home_interface)

    def on_theme_changed(self):
        self.update_palette()
        self.home_interface.update_icon_theme()
        self.config_interface.update_list_theme()
        self.test_interface.update_text_theme()
        self.settings_interface.update_combo_theme()
        self.settings_interface.update_checkbox_theme()
        self.logs_interface.update_text_theme()

    def check_bat_autostart(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            settings_path = os.path.join(script_dir, 'settings.json')
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                    if settings.get('bat_autostart', False) and settings.get('selected_config'):
                        self.logger.info(f"Автозапуск BAT активирован для: {settings.get('selected_config')}")
                        QTimer.singleShot(1000, self.home_interface.start_zapret)
                    else:
                        self.logger.info("Автозапуск BAT не активирован")
        except Exception as e:
            self.logger.error(f"Ошибка проверки автозапуска BAT: {e}")

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def closeEvent(self, event):
        if self.home_interface.is_connected:
            self.logger.warning("Попытка закрытия приложения с активным Zapret процессом")
            reply = MessageBox(
                "Подтверждение",
                "Процесс Zapret запущен. Остановить его перед выходом?",
                self
            ).exec()

            if reply:
                self.home_interface.stop_zapret()

        self.logger.info("Приложение закрывается")
        self.logger.info("="*50)
        event.accept()

def main():
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    app.setApplicationName("Zapret Custom")
    app.setApplicationVersion("0.3")
    app.setOrganizationName("Savvy08")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()