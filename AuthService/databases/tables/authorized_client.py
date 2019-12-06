from databases.tables import Base
from sqlalchemy import Column, Integer, String


class AuthorizedClient(Base):
    __tablename__ = 'authorized_client'
    id = Column('id', Integer, primary_key=True)
    client_id = Column('client_id', String)
    client_secret_hash = Column('client_secret_hash', String)
