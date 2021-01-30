from app import APP
from app.model import DB, Rink, People
import json


def init_database():
    """Initialize the database"""
    with APP.app_context():
        DB.drop_all()
        print("Dropped all tables")
        DB.create_all()
        my_rink = None
        with open("data/rinks.json", "r") as f:
            rinks = json.load(f)
            # add a few entities
            for data in rinks:
                rink = Rink(data['name'], link=data["link"])
                if data['name'] == 'Glendale Park':
                    my_rink = rink
                DB.session.add(rink)
            DB.session.commit()
        me = People('dallas.fraser.waterloo@gmail.com',
                    my_rink, is_administrator=True, is_coordinator=True)
        DB.session.add(me)
        DB.session.commit()


if __name__ == "__main__":
    init_database()
