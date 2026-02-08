import pytest 

class FakeDBConnection:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        print("[SETUP] Connecting to the database...")

    def close(self):
        self.connected = False
        print("[TEARDOWN] Closing the database connection...")
        
    def fetch_user(self):
        if not self.connected:
            raise RuntimeError("Database is not connected.")
        return {"name": "John", "age": 30}

@pytest.fixture
def db_connection():
    db = FakeDBConnection()
    db.connect()
    yield db
    db.close()
    
def test_fetch_user(db_connection):
    user = db_connection.fetch_user()
    assert user == {"name": "John", "age": 30}

# pytest fixtures\fake_db_onnection.py -v