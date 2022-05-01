from __future__ import annotations

import datetime

from sqlalchemy import create_engine, Table, Column, String, Integer, ForeignKey, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker

from common.variables import SERVER_DATABASE


class Storage:
    class Users:
        def __init__(self, username):
            self.username = username
            self.last_login = datetime.datetime.now()

    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

    class LoginHistory:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

    class UsersContacts:
        def __init__(self, user_id, contact_id):
            self.user = user_id
            self.contact = contact_id

    class UsersMessagesStats:
        def __init__(self, user_id):
            self.user = user_id
            self.sent = 0
            self.received = 0

    def __init__(self):
        self.engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        self.metadata = MetaData()

        # Tables models
        users_table = Table(
            'Users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('username', String(50), unique=True),
            Column('last_login', DateTime)
        )

        active_users_table = Table(
            'Active_users', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id'), unique=True),
            Column('ip_address', String(16)),
            Column('port', Integer),
            Column('login_time', DateTime)
        )

        login_history_table = Table(
            'Login_history', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id'), unique=False),
            Column('ip_address', String(16)),
            Column('port', Integer),
            Column('login_time', DateTime)
        )

        users_contacts_table = Table(
            'Contacts', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id')),
            Column('contact', ForeignKey('Users.id'))
        )

        users_messages_stats_table = Table(
            'Messages_stats', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('user', ForeignKey('Users.id')),
            Column('sent', Integer, default=0),
            Column('received', Integer, default=0)
        )

        self.metadata.create_all(self.engine)

        mapper(self.Users, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, login_history_table)
        mapper(self.UsersContacts, users_contacts_table)
        mapper(self.UsersMessagesStats, users_messages_stats_table)

        session = sessionmaker(bind=self.engine)
        self.session = session()

        # Cleat Active_users table after reload server
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    # Database methods
    def login_user(self, username: str, ip_address: str, port: int):
        res = self.session.query(self.Users).filter_by(username=username)
        if res.first():
            user = res.first()
            user.last_login = datetime.datetime.now()

        else:
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()
            user_message_history_record = self.UsersMessagesStats(user.id)
            self.session.add(user_message_history_record)

        active_user = self.ActiveUsers(user.id, ip_address, port, login_time=datetime.datetime.now())
        history_record = self.LoginHistory(user_id=user.id, ip_address=ip_address, port=port,
                                           login_time=datetime.datetime.now())
        self.session.add(active_user)
        self.session.add(history_record)
        # self.session.add_all([history_record, active_user])
        self.session.commit()

    def logout_user(self, username: str) -> None:
        user = self.session.query(self.Users).filter_by(username=username).first()

        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def get_all_users(self) -> list:
        return self.session.query(self.Users.username, self.Users.last_login).all()

    def get_all_active_users(self) -> list:
        return self.session.query(self.Users.username, self.ActiveUsers.ip_address, self.ActiveUsers.port,
                                  self.ActiveUsers.login_time).join(self.Users).all()

    def get_login_history(self, username: str = None) -> list:
        try:
            query = self.session.query(self.Users.username, self.LoginHistory.ip_address, self.LoginHistory.port,
                                       self.LoginHistory.login_time).join(self.Users)
            if username:
                return query.filter(self.Users.username == username).limit(10).all()
            return query.limit(10).all()
        except Exception as e:
            print(e)

    def update_users_message_stats(self, sender_name: str, recipient_name: str) -> None:
        sender = self.session.query(self.Users).filter_by(username=sender_name).first()
        recipient = self.session.query(self.Users).filter_by(username=recipient_name).first()
        sender_messages_history = self.session.query(self.UsersMessagesStats).filter_by(user=sender).first()
        recipient_messages_history = self.session.query(self.UsersMessagesStats).filter_by(user=recipient).first()

        sender_messages_history.sent += 1
        recipient_messages_history.received += 1

        self.session.commit()

    def add_contact(self, user_name: str, contact_name: str) -> None | bool:
        user = self.session.query(self.Users).filter_by(username=user_name).first()
        contact = self.session.query(self.Users).filter_by(username=contact_name).first()

        if not contact or self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).count():
            return False

        record = self.UsersContacts(user.id, contact.id)
        self.session.add(record)
        self.session.commit()

    def remove_contact(self, user_name: str, contact_name: str) -> None | bool:
        user = self.session.query(self.Users).filter_by(username=user_name).first()
        contact = self.session.query(self.Users).filter_by(username=contact_name).first()

        if not contact:
            return False

        self.session.query(self.UsersContacts).filter_by(user=user.id, contact=contact.id).delete()

        self.session.commit()

    def get_contacts(self, user_name: str) -> list:
        user = self.session.query(self.Users).filter_by(username=user_name).first()
        contacts = self.session.query(self.Users.username).filter(self.UsersContacts.user == user.id).join(
            self.UsersContacts, self.Users.id == self.UsersContacts.contact).all()
        return [
            contact_name for contact_name in contacts
        ]

    def get_messages_stats(self) -> list:
        return self.session.query(
            self.Users.name,
            self.Users.last_login,
            self.UsersMessagesStatse.sent,
            self.UsersMessagesStatse.received
        ).join(self.UsersMessagesStats).all()


if __name__ == '__main__':
    test_db = Storage()
    # выполняем 'подключение' пользователя
    test_db.login_user('client_1', '192.168.1.4', 7777)
    test_db.login_user('client_2', '192.168.1.5', 7777)
    test_db.login_user('client_3', '192.168.1.6', 7777)
    # выводим список кортежей - активных пользователей
    # print(test_db.get_all_users())
    # print(test_db.get_all_active_users())
    # # выполянем 'отключение' пользователя
    # test_db.logout_user('client_1')
    # # выводим список активных пользователей
    # print(test_db.get_all_active_users())
    # # запрашиваем историю входов по пользователю
    # print(test_db.get_login_history('client_1'))
    test_db.add_contact('client_1', 'client_2')
    test_db.add_contact('client_1', 'client_3')
    print(test_db.get_contacts('client_1'))
    print(test_db.get_contacts('client_2'))
    test_db.remove_contact('client_1', 'client_3')
    print(test_db.get_contacts('client_1'))
