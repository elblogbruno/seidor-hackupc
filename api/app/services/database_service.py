from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.item import Base, Item

class DatabaseService:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def execute_sql(self, sql):
        session = self.Session()
        try:
            result = session.execute(sql)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_items(self):
        session = self.Session()
        try:
            items = session.query(Item).all()
            return items
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()