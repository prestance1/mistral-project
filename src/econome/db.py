from pymongo import MongoClient
from contextlib import contextmanager
from econome.settings import settings
from typing import Generator


@contextmanager
def get_client() -> Generator[MongoClient, None, None]:
    client = MongoClient(settings.MONGO_URL)
    try:
        yield client
    finally:
        client.close()


def get_econome_db():
    with get_client() as client:
        db = client["econome"]
        yield db
