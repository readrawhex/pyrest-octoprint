from __future__ import annotations
import requests
import urllib
from requests_toolbelt.utils import dump


class BaseClient:
    """
    Defines an abstract client-like object used for making requests to
    the octoprint server.
    """

    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        parent_client: BaseClient | None = None,
    ):
        if parent_client:
            api_key = parent_client._api_key
            base_url = parent_client._base_url
        elif api_key is None or base_url is None:
            raise TypeError("Missing `base_url`/`api_key` pair or `parent_client` argument")
        self._api_key = api_key
        self._base_url = base_url

    def _make_request(self, endpoint: str, method: str = "GET", **kwargs):
        """
        make request to Octoprint with `self._api_key` included
        in `X-Api-Key` header.
        """
        if "headers" in kwargs.keys():
            headers = dict(kwargs.pop("headers"))
            headers["X-Api-Key"] = self._api_key
        else:
            headers = {
                "X-Api-Key": self._api_key,
            }
        url = urllib.parse.urljoin(self._base_url, endpoint)
        resp = requests.request(method, url, headers=headers, **kwargs)
        resp.raise_for_status()
        return resp

    def _connection_settings(self):
        """
        Retrieve Octoprint connection settings.

        Note: this is underscored (private) by default, but
        a non-underscored (public) function is provided for `Client`
        subclass.

        - endpoint: `/api/connection`
        - method: `GET`
        """
        resp = self._make_request("/api/connection")
        return resp.json()
