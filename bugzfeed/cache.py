# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import json

from sqlalchemy import create_engine, Column, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bugzfeed import config

Base = declarative_base()
engine = create_engine(config.database_url)
Session = sessionmaker(bind=engine)


class BaseMessage(object):

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    bug = Column(Integer)
    when = Column(DateTime)

    @classmethod
    def update(cls, message):
        session = Session()
        m = cls(message=json.dumps(message), bug=message['bug'],
                when=message['when'])
        session.add(m)
        last_id = session.query(cls.id).order_by(
            cls.id.desc()).first().id
        session.query(cls).filter(
            cls.id <= (last_id - config.max_messages)).delete()
        session.commit()
        session.close()

    @classmethod
    def query(cls, bug_ids, since):
        '''Generator that yields messages, in JSON format.'''
        session = Session()
        for m in session.query(cls.message).filter(
                cls.bug.in_(bug_ids), cls.when >= since):
            yield m.message
        session.close()


class Message(Base, BaseMessage):
    __tablename__ = 'messages'


class DevMessage(Base, BaseMessage):
    __tablename__ = 'devmessages'

Base.metadata.create_all(engine)
