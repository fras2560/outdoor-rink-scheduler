from app import APP
from app.model import DB, Rink

MOCK_DATA = ["Glendale Park"]


def init_database():
    """Initialize the database"""
    with APP.app_context():
        DB.drop_all()
        DB.create_all()
        # add a few entities
        for name in MOCK_DATA:
            rink = Rink(name)
            DB.session.add(rink)
        DB.session.commit()


if __name__ == "__main__":
    init_database()
