from src.core import MongoLoader


class FakeBulkResult:
    def __init__(self, upserted_count=0, modified_count=0, matched_count=0) -> None:
        self.upserted_count = upserted_count
        self.modified_count = modified_count
        self.matched_count = matched_count


class FakeCollection:
    def __init__(self) -> None:
        self.indexes = []
        self.operations = []

    def create_index(self, field, unique=False, name=None):
        self.indexes.append((field, unique, name))
        return name

    def bulk_write(self, operations, ordered=False):
        self.operations.extend(operations)
        return FakeBulkResult(
            upserted_count=len(operations),
            modified_count=0,
            matched_count=0,
        )


class FakeDatabase:
    def __init__(self, collection):
        self.collection = collection

    def __getitem__(self, name):
        return self.collection


class FakeAdmin:
    def command(self, name):
        if name == "ping":
            return {"ok": 1}
        raise ValueError("Comando inesperado")


class FakeClient:
    def __init__(self, database):
        self.database = database
        self.admin = FakeAdmin()
        self.closed = False

    def __getitem__(self, name):
        return self.database

    def close(self):
        self.closed = True


def test_loader_connect_and_load_contracts() -> None:
    """Deve conectar e realizar carga em lote com upsert."""
    collection = FakeCollection()
    database = FakeDatabase(collection)
    client = FakeClient(database)

    loader = MongoLoader(client=client)
    loader.connect()

    summary = loader.load_contracts(
        [
            {"id": "1", "objeto": "Contrato 1"},
            {"id": "2", "objeto": "Contrato 2"},
        ]
    )

    assert summary["received"] == 2
    assert summary["operations"] == 2
    assert summary["inserted"] == 2
    assert collection.indexes[0][0] == "id"