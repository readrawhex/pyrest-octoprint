from . import datamodel
from .file import FileInformation


class JobInformation:
    def __init__(
        self, file: dict, estimatedPrintTime: float = None, filament: dict = None
    ):
        self.file = FileInformation(**file)
        self.estimatedPrintTime = estimatedPrintTime
        self.filament = filament


class JobInformationResponse:
    def __init__(self, job: dict, progress: dict, state: str, error: str = None):
        self.job = JobInformation(**job)
        self.progress = datamodel.ProgressInformation(**progress)
        self.state = state
        self.error = error
