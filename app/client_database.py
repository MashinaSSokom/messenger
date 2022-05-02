from __future__ import annotations

import datetime

from sqlalchemy import create_engine, Table, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.orm import mapper, sessionmaker
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

    def __init__(self, name):
        self.db_engine = create_engine(f'sqlite:///client_{name}.db3', echo=False, pool_recycle=7200,
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
        self.session.query(self.Contacts).delete()
        self.session.commit()


