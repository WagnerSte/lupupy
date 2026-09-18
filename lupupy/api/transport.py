"""Sending requests to the panel and reading its answers.

Shared by the facades in lupupy.api.current.vendor_api and lupupy.api.legacy.undocumented_legacy_api.
It knows nothing about any particular action; a facade decides whether its
requests carry a token and how its answers are read.
"""

import json

import requests

from lupupy.exceptions import LupusecException

REQUEST_TIMEOUT = 15


class Transport:
    """A session against the panel's /action/ endpoints."""

    def __init__(self, username: str, password: str, ip_address: str):
        """Open a session against the panel's web API."""
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.base_url = f"http://{ip_address}"
        self.api_url = f"{self.base_url}/action/"
        self._token: str | None = None
        self._token_time = 0.0

    def _get(self, action: str, params: dict | None = None) -> dict:
        """Send a GET for an action and return what it answered."""
        return self._send("GET", action, params)

    def _post(self, action: str, data: dict | None = None) -> dict:
        """Send a POST for an action and return what it answered."""
        return self._send("POST", action, data)

    def _send(self, method: str, action: str, payload: dict | None) -> dict:
        """Send a request, once more with a fresh token after a 401."""
        response = self._request(method, action, payload)
        if response.status_code == 401 and self._uses_token():
            self._token = None
            response = self._request(method, action, payload)

        if response.status_code != 200:
            raise LupusecException(
                f"{action} was answered with status {response.status_code}",
                details=response.status_code,
            )
        return self._decode(action, response.text)

    def _request(
        self, method: str, action: str, payload: dict | None
    ) -> requests.Response:
        self._ensure_token()
        headers = {"X-Token": self._token} if self._token else None
        if method == "GET":
            return self.session.get(
                self.api_url + action,
                params=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
        return self.session.post(
            self.api_url + action,
            data=payload or {},
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

    def _decode(self, action: str, text: str) -> dict:
        """Parse an answer. The panel pads its JSON with raw tabs."""
        try:
            return json.loads(text.replace("\t", ""))
        except ValueError as error:
            raise LupusecException(f"{action} was not answered with JSON") from error

    def _uses_token(self) -> bool:
        """Whether requests carry a token."""
        return False

    def _ensure_token(self) -> None:
        """Make sure a request that needs a token has one."""
