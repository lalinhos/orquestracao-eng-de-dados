from src.core import PncpExtractor


class FakeResponse:
    def __init__(self, payload, status_code=200, url="https://fake-url") -> None:
        self._payload = payload
        self.status_code = status_code
        self.url = url
        self.text = ""

    def json(self):
        return self._payload


class FakeSession:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return self.responses.pop(0)

    def close(self):
        return None


def test_extract_contracts_returns_data() -> None:
    """Deve extrair registros quando a API retorna payload válido."""
    payload = {
        "data": [
            {"numeroControlePNCP": "1"},
            {"numeroControlePNCP": "2"},
        ],
        "totalPaginas": 1,
    }
    session = FakeSession([FakeResponse(payload)])
    extractor = PncpExtractor(session=session)

    result = extractor.extract_contracts()

    assert len(result) == 2
    assert result[0]["numeroControlePNCP"] == "1"
    assert session.calls[0]["params"]["pagina"] == 1