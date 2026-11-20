"""Unit tests for utility_llm_check.list_models."""

from unittest.mock import patch

import requests

from modules.shared.src.utility_llm_check import list_models


class FakeResponse:
    def __init__(self, status_code=200, payload=None, raise_on_status=False):
        self.status_code = status_code
        self._payload = payload or {"data": []}
        self._raise = raise_on_status

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self._raise:
            raise requests.HTTPError("boom")


def test_list_models_success():
    with patch(
        "modules.shared.src.utility_llm_check.requests.get",
        return_value=FakeResponse(payload={"data": [{"id": "model-a"}]}),
    ):
        models = list_models("http://localhost:1234/v1")
        assert models == [{"id": "model-a"}]


def test_list_models_empty_data():
    with patch(
        "modules.shared.src.utility_llm_check.requests.get",
        return_value=FakeResponse(payload={"data": []}),
    ):
        models = list_models("http://localhost:1234/v1")
        assert models == []


def test_list_models_http_error():
    with patch(
        "modules.shared.src.utility_llm_check.requests.get",
        return_value=FakeResponse(raise_on_status=True),
    ):
        models = list_models("http://localhost:1234/v1")
        assert models == []


def test_list_models_connection_error():
    with patch(
        "modules.shared.src.utility_llm_check.requests.get",
        side_effect=requests.ConnectionError("refused"),
    ):
        models = list_models("http://localhost:1234/v1")
        assert models == []
