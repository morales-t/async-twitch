from sqlalchemy import Column, DateTime, String, Integer, MetaData, Table

metadata = MetaData()

Twitch_Messages = Table('twitch_messages', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('author', String),
                        Column('channel', String),
                        Column('message', String),
                        Column('date_processed', DateTime))
