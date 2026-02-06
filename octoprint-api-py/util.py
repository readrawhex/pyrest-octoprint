class PathTestResult:
    def __init__(
        self, path: str, exists: bool, typeok: bool, access: bool, result: bool
    ):
        self.path = path
        self.exists = exists
        self.typeok = typeok
        self.access = access
        self.result = result


class UrlTestResult:
    def __init__(
        self,
        url: str,
        status: int,
        result: bool,
        response: dict = None,
        headers: dict = None,
    ):
        self.url = url
        self.status = status
        self.result = result
        self.response = response
        self.headers = headers


class ServerTestResult:
    def __init__(self, host: str, port: int, protocol: str, result: bool):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.result = result


class ResolutionTestResult:
    def __init__(self, name: str, result: bool):
        self.name = name
        self.result = result


class AddressTestResult:
    def __init__(self, address: str, is_lan_address: bool, subnet: str = None):
        self.address = address
        self.is_lan_address = is_lan_address
        self.subnet = subnet
