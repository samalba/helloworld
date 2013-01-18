
import os
import datetime

from flask import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func


Base = declarative_base()


class HelperBase(object):

    def to_dict(self):
        res = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, (datetime.datetime, datetime.date)):
                value = str(value)
            res[column.name] = value
        return res

    def to_json(self, *args, **kwargs):
        return json.dumps(self.to_dict(), *args, **kwargs)

    def __repr__(self):
        return self.to_json(indent=4)


class Test(Base, HelperBase):

    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    payload = Column(String(512), nullable=False)


def get_session(env):

    def get_engine():
        options = {'echo': True}
        if env == 'dotcloud':
            url = 'mysql+mysqldb://{login}:{password}@{host}:{port}/db'.format(
                    login=os.environ['DOTCLOUD_DB_MYSQL_LOGIN'],
                    password=os.environ['DOTCLOUD_DB_MYSQL_PASSWORD'],
                    host=os.environ['DOTCLOUD_DB_SSH_HOST'],
                    port=os.environ['DOTCLOUD_DB_SSH_PORT']
                    )
            options['pool_recycle'] = 3600
        elif env == 'appfog':
            info = json.loads(os.environ['VCAP_SERVICES'])['mysql-5.1'][0]['credentials']
            url = 'mysql+mysqldb://{user}:{password}@{host}:{port}/{name}'.format(**info)
            options['pool_recycle'] = 3600
        elif env == 'heroku':
            url = 'postgresql+psycopg2://{login}:{password}@{host}:{port}/{db}'.format(
                    login='u16skk7jctqrrd',
                    password='pep99fhu8bt69vcdfhknah0d7u1',
                    host='ec2-107-22-244-17.compute-1.amazonaws.com',
                    port=6542,
                    db='dbo310e8toksit'
                    )
        else:
            url = 'sqlite:///{0}'.format(
                    os.path.join(os.path.dirname(__file__), 'database.db'))
        return create_engine(url, **options)

    engine = get_engine()
    Session = sessionmaker(bind=engine)
    #FIXME: This should be done only for the first call, but it's ok for testing
    Base.metadata.create_all(engine)
    return Session()
