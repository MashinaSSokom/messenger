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
        def __init__(self, user_id, login_time, ip_address, port):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

    def __init__(self):
        self.engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
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
            Column('port', String(8)),
            Column('login_time', DateTime)
        )

        login_history_table = Table(
            'Login_history', self.metadata,
            Column('user', ForeignKey('User.id'), unique=True),
            Column('ip_address', String(16)),
            Column('port', String(8)),
            Column('login_time', DateTime)
        )

        self.metadata.create_all(self.engine)

        mapper(self.Users, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, login_history_table)

        session = sessionmaker(bind=self.engine)
        self.session = session()

        # Cleat Active_users table after reload server
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    # Database methods
    def login_user(self):
        pass

    def logout_user(self):
        pass

    def get_all_users(self):
        pass

    def get_all_active_users(self):
        pass

    def get_login_history(self):
        pass


if __name__ == '__main__':
    pass
