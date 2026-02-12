from requests import Response
from requests.exceptions import HTTPError
from requests_toolbelt.utils import dump

class HTTPException(Exception):
    """
    Basic HTTP Exception with tailored __str__() call
    for providing info from Octoprint's `error` response field
    in 400+ requests, as well as a `dump()` method for reviewing
    the raw HTTP request and response data.
    """
    def __init__(self, response: Response, *args, **kwargs):
        self._response = response
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "{}: {}, error: '{}'".format(
            self._response.status_code,
            self._response.reason,
            (self._response.json().get("error", "no error provided")),
        )

    def dump(self) -> str:
        """
        Return raw HTTP request and response data as
        str.
        """
        return dump.dump_response(self._response).decode('utf-8')


def handle_http_exception(func: callable) -> callable:
    """
    Decorator for throwing custom HTTPException class
    when a requests.
    """
    def newfunc(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            raise HTTPException(e.response)
        except Exception as e:
            raise(e)
    return newfunc
