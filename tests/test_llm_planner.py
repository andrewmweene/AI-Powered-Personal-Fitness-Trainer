import recommendation.llm_planner as llm_planner


def test_get_gemini_client_uses_google_genai_when_available(monkeypatch):
    created = {}

    class FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key

    class FakeGenAI:
        @staticmethod
        def Client(api_key):
            created["api_key"] = api_key
            return FakeClient(api_key)

    monkeypatch.setattr(llm_planner, "_load_genai_module", lambda: FakeGenAI)
    client = llm_planner.get_gemini_client("abc123")

    assert isinstance(client, FakeClient)
    assert client.api_key == "abc123"
