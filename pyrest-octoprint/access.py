class PermissionListResponse:
    def __init__(self, permissions: list = None):
        self.permissions = permissions


class GroupListResponse:
    def __init__(self, groups: list = None):
        self.groups = groups


class GroupRegistrationRequest:
    def __init__(
        self,
        key: str,
        name: str,
        permissions: list,
        description: str = None,
        subgroups: list = None,
        default: bool = None,
    ):
        self.key = key
        self.name = name
        self.permissions = permissions
        self.description = description
        self.subgroups = subgroups
        self.default = default


class GroupUpdateRequest:
    def __init__(
        self,
        permissions: list,
        description: str = None,
        subgroups: list = None,
        default: bool = None,
    ):
        self.permissions = permissions
        self.description = description
        self.subgroups = subgroups
        self.default = default


class UserListResponse:
    def __init__(self, users: list = None):
        self.users = users


class UserRegistrationRequest:
    def __init__(
        self,
        name: str,
        password: str,
        active: bool,
        groups: list = None,
        permissions: list = None,
    ):
        self.name = name
        self.password = password
        self.active = active
        self.groups = groups
        self.permissions = permissions


class UserUpdateRequest:
    def __init__(
        self, active: bool = None, groups: list = None, permissions: list = None
    ):
        self.active = active
        self.groups = groups
        self.permissions = permissions
