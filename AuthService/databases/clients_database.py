from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import dirname, abspath, sep, exists

from databases.tables.authorized_client import AuthorizedClient
from databases.tables import Base
from hashlib import md5
import databases


class ClientsDatabase:
    def __init__(self, db_filepath=None):
        if not db_filepath:
           db_filepath = dirname(abspath(databases.__file__)) + sep + "clients_db.sqlite"
        self.db_filepath = db_filepath
        self.db_engine = create_engine("sqlite:///{}".format(self.db_filepath))
        self.session = self._create_session()

        if not exists(self.db_filepath):
            self._create_db()

    def _create_session(self):
        return sessionmaker(bind=self.db_engine)()

    def _create_db(self):
        Base.metadata.create_all(self.db_engine)

    def _get_client(self, client_id):
        return self.session.query(AuthorizedClient).filter(AuthorizedClient.client_id == client_id).one_or_none()

    def client_exists(self, client_id):
        return self._get_client(client_id) is not None

    def verify_client_secret(self, client_id, client_secret):
        auth_client = self._get_client(client_id)
        if not auth_client:
            return False
        return md5(client_secret.encode("utf-8")).hexdigest() == auth_client.client_secret_hash
