import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QLabel, QLineEdit, QFileDialog, QMessageBox, QTableView,\
    QDialog, QPushButton, QApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QTimer

from server_database import Storage


def create_active_clients_model(db: Storage) -> QStandardItemModel:
    active_users = db.get_all_active_users()
    active_users_model = QStandardItemModel()
    active_users_model.setHorizontalHeaderLabels(['Имя клиента', 'IP', 'Порт', 'Время входа'])
    for user in active_users:
        username, ip, port, time = user
        username = QStandardItem(username)
        username.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        active_users_model.appendRow([username, ip, port, time])
    return active_users_model


def create_messages_stats_model(db: Storage) -> QStandardItemModel:
    messages_stats = db.get_messages_stats()

    messages_stats_model = QStandardItemModel()
    messages_stats_model.setHorizontalHeaderLabels(
        ['Имя клиента', 'Время последнего входа', 'Сообщений отправлено', 'Сообщений принято']
    )

    for stat_record in messages_stats:
        username, last_login, sent, received = stat_record
        username = QStandardItem(username)
        username.setEditable(False)
        last_login = QStandardItem(str(last_login.replace(microsecond=0)))
        last_login.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        received = QStandardItem(str(received))
        received.setEditable(False)
        messages_stats_model.appendRow([username, last_login, sent, received])

    return messages_stats_model


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Обновить', self)
        self.config_button = QAction('Настройки сервера', self)
        self.messages_stats_button = QAction('История сообщений клиентов', self)

        self.statusBar()

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(exit_action)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.config_button)
        self.toolbar.addAction(self.messages_stats_button)

        self.setFixedSize(800, 600)
        self.setWindowTitle('Messager Server')

        self.label = QLabel('Список подключенных клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 40)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.setFixedSize(780, 400)
        self.active_clients_table.move(10, 60)

        self.show()


class MessagesStats(QDialog):
    def __init__(self):
        super(MessagesStats, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Статистика сообщений клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.messages_stats_table = QTableView(self)
        self.messages_stats_table.setFixedSize(580, 620)
        self.move(10, 10)

        self.show()


class ConfigWindow(QDialog):
    def __init__(self):
        super(ConfigWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 260)
        self.setWindowTitle('Настройки сервера')

        self.db_path_label = QLabel('Путь до файла базы данных: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        # Строка с путём базы
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        # Кнопка выбора пути.
        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(265, 25)

        # Функция обработчик открытия окна выбора папки
        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        # Метка с именем поля файла базы данных
        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        # Поле для ввода имени файла
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        # Метка с адресом для соединений
        self.ip_label = QLabel('IP-адрес:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        # # Метка с напоминанием о пустом поле.
        # self.ip_label_note = QLabel(' оставьте это поле пустым, чтобы\n принимать соединения с любых адресов.', self)
        # self.ip_label_note.move(10, 168)
        # self.ip_label_note.setFixedSize(500, 30)

        # Поле для ввода ip
        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        # Метка с номером порта
        self.port_label = QLabel('Номер порта:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        # Поле для ввода номера порта
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        # Кнопка сохранения настроек
        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(160, 220)

        # Кнапка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.statusBar().showMessage('Тестовое сообщение')
    timer = QTimer()
    timer.timeout.connect(ex.statusBar().clearMessage)
    timer.start(1000)

    app.exec_()
