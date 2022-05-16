from __future__ import annotations

import datetime

from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import or_
from common.variables import SERVER_DATABASE


class ClientStorage:
    class KnownUsers:
        def __init__(self, username):
            self.id = None
            self.username = username

    class MessageHistory:
        def __init__(self, sender, recipient, message):
            self.id = None
            self.sender = sender
            self.recipient = recipient
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts:
        def __init__(self, contact_name):
            self.id = None
            self.contact_name = contact_name

    def __init__(self, username):
        self.db_engine = create_engine(f'sqlite:///client_{username}.db3', echo=False, pool_recycle=7200,
                                       connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        known_users_table = Table(
            'known_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String)
        )

        message_history_table = Table(
            'message_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('sender', String),
            Column('recipient', String),
            Column('message', Text),
            Column('date', DateTime)
        )

        contacts_table = Table(
            'contacts', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('contact_name', String, unique=True)
        )

        self.metadata.create_all(self.db_engine)

        mapper(self.KnownUsers, known_users_table)
        mapper(self.MessageHistory, message_history_table)
        mapper(self.Contacts, contacts_table)

        session = sessionmaker(bind=self.db_engine)
        self.session = session()

        # Cleat Active_users table after reload server
        self.session.query(self.KnownUsers).delete()
        self.session.commit()

    def add_contact(self, contact_name: str) -> None:
        # TODO: Проверить что пользователь не добавляет сам себя
        if not self.session.query(self.Contacts).filter_by(contact_name=contact_name).first():
            contact = self.Contacts(contact_name)
            self.session.add(contact)
            self.session.commit()

    def del_contact(self, contact_name: str) -> None:
        self.session.query(self.Contacts).filter_by(contact_name=contact_name).delete()
        self.session.commit()

    def add_users_to_known(self, users_list: list[str]) -> None:
        self.session.query(self.KnownUsers).delete()
        for user_name in users_list:
            known_user = self.KnownUsers(user_name)
            self.session.add(known_user)
        self.session.commit()

    def save_message(self, sender: str, recipient: str, message: str) -> None:
        message_history_record = self.MessageHistory(sender, recipient, message)
        self.session.add(message_history_record)
        self.session.commit()

    def get_known_users(self) -> list:
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def get_contacts(self) -> list:
        return [contact[0] for contact in self.session.query(self.Contacts.contact_name).all()]

    def check_is_known_user(self, username: str) -> bool:
        if self.session.query(self.KnownUsers).filter_by(username=username).first():
            return True
        return False

    def check_is_contact(self, contact_name: str) -> bool:
        if self.session.query(self.Contacts).filter_by(contact_name=contact_name).first():
            return True
        return False

    def get_message_history(self, sender=None, recipient=None) -> list | bool:
        if sender and recipient:
            return False
        print(sender, recipient)
        query = self.session.query(self.MessageHistory)

        if sender or recipient:
            print(self.session.query(self.MessageHistory).filter(or_(self.MessageHistory.recipient == recipient, self.MessageHistory.sender == recipient)).all())
            query = self.session.query(self.MessageHistory).filter(or_(self.MessageHistory.recipient == recipient, self.MessageHistory.sender == recipient))
        print('Запрос', query)
        # elif recipient:
        #     query = self.session.query(self.MessageHistory).filter_by(recipient=recipient)

        return [(history_record.sender, history_record.recipient, history_record.message, history_record.date) for
                history_record in query.all()]


if __name__ == '__main__':
    test_db = ClientStorage('client_1')
    # test_db.add_contact('test4')
    # test_db.add_users_to_known(['test1', 'test2', 'test3', 'test4', 'test5'])
    # test_db.save_message('test1', 'test2', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    # test_db.save_message('test2', 'test1', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    # print(test_db.get_contacts())
    # print(test_db.get_known_users())
    # print(test_db.check_is_known_user('test1'))
    # print(test_db.check_is_known_user('test10'))
    # print(test_db.get_message_history('test2'))
    # print(test_db.get_message_history(recipient='test2'))
    # print(test_db.get_message_history('test3'))
    # test_db.del_contact('test4')
    # print(test_db.get_contacts())
    # print(test_db.get_contacts())
    # print(test_db.check_is_contact('client_2'))
