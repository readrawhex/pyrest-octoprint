class LoginResponse:
    def __init__(self, session: str, _is_external_client: bool):
        self.session = session
        self._is_external_client = _is_external_client


class CurrentUser:
    def __init__(self, name: str, permissions: list = None, groups: list = None):
        self.name = name
        self.permissions = permissions
        self.groups = groups
