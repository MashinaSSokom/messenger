import sys
import json
import logging

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt

from client_gui_conv import Ui_MainClientWindow
from client_database import ClientStorage



logger = logging.getLogger('client_logger')


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
