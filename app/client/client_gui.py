import sys
import json
import logging

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView, QDialog, QLabel, QComboBox, \
    QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt

from client_gui_conv import Ui_MainClientWindow
from client_database import ClientStorage
from common.errors import ServerError

logger = logging.getLogger('client_logger')


class AddContactDialog(QDialog):
    def __init__(self, transport, database):
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
        users_list = set(self.database.get_users())
        users_list.remove(self.transport.username)
        self.selector.addItems(users_list - contacts_list)

    def _update_users_and_contacts_from_server(self):
        try:
            self.transport.user_list_update()
        except OSError:
            pass
        else:
            logger.debug('Обновление списка пользователей с сервера выполнено')
            self._update_possible_contacts()


class ClientMainWindow(QMainWindow):

    def __init__(self, db: ClientStorage, transport):
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
        self._history_model = None
        self._messages = QMessageBox()
        self._current_chat = None

        self._reset_inputs()
        self._contacts_list_update()

        self.show()

    def _reset_inputs(self):
        self.ui.label_new_message.setText('Для выбора получателя используйте двойной левый клик')
        self.ui.text_message.clear()
        if self._history_model:
            self._history_model.clear()

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
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        # вызываем основную функцию
        self.ui.label_new_message.setText(f'Введите сообщенние для {self.current_chat}:')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)

        # Заполняем окно историю сообщений по требуемому пользователю.
        self._history_list_update()

