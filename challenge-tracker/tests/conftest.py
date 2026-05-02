import pytest

from pftracker import JsonFileStorage, PersonalFinanceTracker


@pytest.fixture
def json_storage_path(tmp_path):
    storage_path = tmp_path / "finance.json"
    return storage_path


@pytest.fixture
def storage(json_storage_path):
    s = JsonFileStorage(json_storage_path)
    yield s
    s.close()


@pytest.fixture
def tracker(storage):
    with PersonalFinanceTracker(storage=storage) as t:
        yield t
