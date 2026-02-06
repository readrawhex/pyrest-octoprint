from .datamodel import *


class ConnectedPayload:
    def __init__(
        self,
        apikey: str,
        version: str,
        branch: str,
        display_version: str,
        plugin_hash: str,
        config_hash: str,
    ):
        self.apikey = apikey
        self.version = version
        self.branch = branch
        self.display_version = display_version
        self.plugin_hash = plugin_hash
        self.config_hash = config_hash


class EventPayload:
    def __init__(self, type: str, payload: dict):
        self.type = type
        self.payload = payload


class SlicingprogressPayload:
    def __init__(
        self,
        slicer: str,
        source_location: str,
        source_path: str,
        dest_location: str,
        dest_path: str,
        progress: float,
    ):
        self.slicer = slicer
        self.source_location = source_location
        self.source_path = source_path
        self.dest_location = dest_location
        self.dest_path = dest_path
        self.progress = progress


class CurrentAndHistoryPayload:
    def __init__(
        self,
        state: PrinterState,
        job: JobInformation,
        progress: ProgressInformation,
        currentZ: float,
        resends: ResendStats,
        offsets: TemperatureOffset = None,
        temps: list = None,
        logs: list = None,
        messages: list = None,
        plugins: dict = None,
    ):
        self.state = state
        self.job = job
        self.progress = progress
        self.currentZ = currentZ
        self.resends = resends
        self.offsets = offsets
        self.temps = temps
        self.logs = logs
        self.messages = messages
        self.plugins = plugins
