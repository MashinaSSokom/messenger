import sys
import json
import logging

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView, QDialog, QLabel, QComboBox, \
    QPushButton, QLineEdit
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt

from client.transport import ClientTransport
from .client_gui_conv import Ui_MainClientWindow
from .client_database import ClientStorage
from common.errors import ServerError

logger = logging.getLogger('client_logger')


class AddContactDialog(QDialog):
    def __init__(self, transport: ClientTransport, database: ClientStorage):
        super().__init__()
        self.transport = transport
        self.database = database

        self.setFixedSize(350, 120)
        self.setWindowTitle('Выберите контакт для добавления:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для добавления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_refresh = QPushButton('Обновить список', self)
        self.btn_refresh.setFixedSize(100, 30)
        self.btn_refresh.move(60, 60)

        self.btn_ok = QPushButton('Добавить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self._update_possible_contacts()
        self.btn_refresh.clicked.connect(self._update_users_and_contacts_from_server)

    def _update_possible_contacts(self):
        self.selector.clear()
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_known_users())
        users_list.remove(self.transport._client_name)
        self.selector.addItems(users_list - contacts_list)

    def _update_users_and_contacts_from_server(self):
        try:
            self.transport.user_list_update()
        except OSError:
            pass
        else:
            logger.debug('Обновление списка пользователей с сервера выполнено')
            self._update_possible_contacts()


class DeleteContactDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database

        self.setFixedSize(350, 120)
        self.setWindowTitle('Выберите контакт для удаления:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для удаления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.selector.addItems(sorted(self.database.get_contacts()))


class ClientNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle('Привет!')
        self.setFixedSize(175, 93)

        self.label = QLabel('Введите имя пользователя:', self)
        self.label.move(10, 10)
        self.label.setFixedSize(150, 10)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(154, 20)
        self.client_name.move(10, 30)

        self.btn_ok = QPushButton('Начать', self)
        self.btn_ok.move(10, 60)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(90, 60)
        self.btn_cancel.clicked.connect(qApp.exit)

        self.show()

    # Обработчик кнопки ОК, если поле вводе не пустое, ставим флаг и завершаем приложение.
    def click(self):
        if self.client_name.text():
            self.ok_pressed = True
            qApp.exit()


class ClientMainWindow(QMainWindow):

    def __init__(self, db: ClientStorage, transport: ClientTransport):
        super(ClientMainWindow, self).__init__()

        self.db = db
        self.transport = transport

        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        self.ui.menu_exit.triggered.connect(qApp.exit)
        self.ui.btn_send.clicked.connect(self._send_message)
        self.ui.btn_add_contact.clicked.connect(self._add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self._add_contact_window)
        self.ui.btn_remove_contact.clicked.connect(self._delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self._delete_contact_window)
        self.ui.list_contacts.doubleClicked.connect(self._select_active_user)

        self.ui.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.list_messages.setWordWrap(True)

        self._contacts_model = None
        self._message_history_model = None
        self._messages = QMessageBox()
        self._current_chat = None

        self._reset_inputs()
        self._contacts_list_update()

        self.show()

    def _reset_inputs(self):
        self.ui.label_new_message.setText('Для выбора получателя используйте двойной левый клик')
        self.ui.text_message.clear()
        if self._message_history_model:
            self._message_history_model.clear()

        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)

    def _contacts_list_update(self):
        contacts_list = self.db.get_contacts()
        self._contacts_model = QStandardItemModel()
        for contact in sorted(contacts_list):
            contact_item = QStandardItem(contact)
            contact_item.setEditable(False)
            self._contacts_model.appendRow(contact_item)
        self.ui.list_contacts.setModel(self._contacts_model)

    def _select_active_user(self):
        self._current_chat = self.ui.list_contacts.currentIndex().data()
        self._set_active_user()

    def _set_active_user(self):
        # вызываем основную функцию
        self.ui.label_new_message.setText(f'Введите сообщенние для {self._current_chat}:')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)
        # Заполняем окно историю сообщений по требуемому пользователю.
        self._message_history_list_update()

    def _add_contact_window(self):
        global add_contact_dialog
        add_contact_dialog = AddContactDialog(self.transport, self.db)
        add_contact_dialog.btn_ok.clicked.connect(lambda: self._add_contact_process(add_contact_dialog))
        add_contact_dialog.show()

    def _add_contact_process(self, ui_item):
        new_contact = ui_item.selector.currentText()
        self._add_contact(new_contact)
        ui_item.close()

    def _add_contact(self, new_contact):
        try:
            self.transport.add_contact(new_contact)
        except ServerError as e:
            self._messages.critical(self, 'Ошибка сервера!', e.text)
        except OSError as e:
            if e.errno:
                self._messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self._messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.db.add_contact(new_contact)
            new_contact_item = QStandardItem(new_contact)
            new_contact_item.setEditable(False)
            self._contacts_model.appendRow(new_contact_item)
            logger.debug(f'Успшно добавлен контакт {new_contact_item}')
            self._messages.information(self, 'Успешно!', 'Контакт добавлен ')

    def _delete_contact_window(self):
        global delete_contact_dialog
        delete_contact_dialog = DeleteContactDialog(self.db)
        delete_contact_dialog.btn_ok.clicked.connect(lambda: self._delete_contact(delete_contact_dialog))
        delete_contact_dialog.show()

    def _delete_contact(self, ui_item):
        contact_to_delete = ui_item.selector.currentText()
        try:
            self.transport.del_contact(contact_to_delete)
        except ServerError as e:
            self._messages.critical(self, 'Ошибка сервера!', e.text)
        except OSError as e:
            if e.errno:
                self._messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self._messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.db.del_contact(contact_to_delete)
            self._contacts_list_update()
            logger.debug(f'Успшно удален контакт {contact_to_delete}')
            self._messages.information(self, 'Успешно!', 'Контакт удален ')
            ui_item.close()
            if contact_to_delete == self._current_chat:
                self._current_chat = None
                self._reset_inputs()

    def _send_message(self):
        message_text = self.ui.text_message.toPlainText()
        if not message_text:
            return
        self.ui.text_message.clear()
        try:
            self.transport.send_message(self._current_chat, message_text)
        except ServerError as err:
            self._messages.critical(self, 'Ошибка', err.text)
        except OSError as err:
            if err.errno:
                self._messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self._messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self._messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
            self.close()
        else:
            self.db.save_message(sender=self.transport._client_name, recipient=self._current_chat, message=message_text)
            logger.debug(f'Отправлено сообщение для {self._current_chat}: {message_text}')
            self._message_history_list_update()

    def _message_history_list_update(self):
        history = sorted(self.db.get_message_history(recipient=self._current_chat), key=lambda item: item[3])
        if not self._message_history_model:
            self._message_history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self._message_history_model)
        self._message_history_model.clear()
        start_index = 0
        if len(history) > 20:
            start_index = len(history) - 20

        for i in range(start_index, len(history)):
            record = history[i]
            if record[0] == self._current_chat:
                message = QStandardItem(f'Входящее сообщение от {record[3].replace(microsecond=0)}:\n{record[2]}')
                message.setEditable(False)
                message.setBackground(QBrush(QColor(255, 213, 213)))
                message.setTextAlignment(Qt.AlignLeft)
                self._message_history_model.appendRow(message)
            else:
                message = QStandardItem(f'Исходящее сообщение от {record[3].replace(microsecond=0)}:\n{record[2]}')
                message.setEditable(False)
                message.setBackground(QBrush(QColor(204, 255, 204)))
                message.setTextAlignment(Qt.AlignRight)
                self._message_history_model.appendRow(message)
        self.ui.list_messages.scrollToBottom()

    @pyqtSlot(str)
    def new_message(self, sender):
        if sender == self._current_chat:
            self._message_history_list_update()
        else:
            if self.db.check_is_contact(sender):
                if self._messages.question(self, 'Новое сообщение', f'Получено сообщение от {sender}, открыть чат?',
                                           QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
                    self._current_chat = sender
                    self._set_active_user()

            else:
                if self._messages.question(self, 'Новое сообщение',
                                           f'Получено сообщение от {sender}, \n Данного пользователя нет в вашем '
                                           f'контакт-листе.\n Добавить в контакты и открыть чат?',
                                           QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
                    self._add_contact(sender)
                    self._current_chat = sender
                    self._set_active_user()

    @pyqtSlot()
    def lost_connection(self):
        self._messages.warning(self, 'Сбой', 'Потеряно соедние с сервером')
        self.close()

    def make_connection(self, transport):
        transport.new_message.connect(self.new_message)
        transport.lost_connection.connect(self.lost_connection)
