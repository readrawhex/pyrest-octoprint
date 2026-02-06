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
        ignore: bool = None,
        **kwargs,
    ):
        self.name = name
        self.command = command
        self.action = action
        self.source = source
        self.resource = resource
        self.confirm = str(confirm) if confirm else None
        self.is_async = kwargs.pop("async", None)
        self.ignore = bool(ignore) if ignore is not None else None
        if len(kwargs.keys()) > 0:
            raise TypeError("unrecognized arguments: '{}'".format(list(kwargs.keys())))
