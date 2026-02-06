class CommandDefinition:
    """
    Defines a definition of a system command in OctoPrint.
    """

    def __init__(
        self,
        name: str,
        command: str,
        action: str,
        source: str,
        resource: str,
        confirm: str = None,
        async: bool = None,
        ignore: bool = None,
    ):
        self.name = name
        self.command = command
        self.action = action
        self.source = source
        self.resource = resource
        self.confirm = confirm
        self.async = async
        self.ignore = ignore
