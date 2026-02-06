class RenderedTimelapse:
    def __init__(
        self, name: str, size: str, bytes: int, date: str, url: str, thumbnail: str
    ):
        self.name = name
        self.size = size
        self.bytes = bytes
        self.date = date
        self.url = url
        self.thumbnail = thumbnail


class UnrenderedTimelapse:
    def __init__(
        self,
        name: str,
        size: str,
        bytes: int,
        date: str,
        recording: bool,
        rendering: bool,
        processing: bool,
    ):
        self.name = name
        self.size = size
        self.bytes = bytes
        self.date = date
        self.recording = recording
        self.rendering = rendering
        self.processing = processing


class TimelapseConfiguration:
    def __init__(self, type: str, save: bool):
        self.type = type
        self.save = save


class TimelapseList:
    def __init__(
        self,
        config: TimelapseConfiguration,
        files: list = None,
        unrendered: list = None,
    ):
        self.config = config
        self.files = files
        self.unrendered = unrendered
