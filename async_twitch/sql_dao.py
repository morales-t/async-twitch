from models import Twitch_Messages


def upload_data(engine, data):
    with engine.begin() as conn:
        conn.execute(
            Twitch_Messages.insert(), data
        )
