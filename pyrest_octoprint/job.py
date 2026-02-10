from . import datamodel
from .files import FileInformation


class JobInformation:
    def __init__(
        self, file: dict, lastPrintTime: float = None, averagePrintTime: float = None, estimatedPrintTime: float = None, filament: dict = None, user: str = None,
    ):
        self.file_details = file
        self.lastPrintTime = lastPrintTime
        self.averagePrintTime = averagePrintTime
        self.estimatedPrintTime = estimatedPrintTime
        self.filament = filament
        self.user = user

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            "file": self.file_details,
            "lastPrintTime": self.lastPrintTime,
            "averagePrintTime": self.averagePrintTime,
            "estimatedPrintTime": self.estimatedPrintTime,
            "filament": self.filament,
        }


class JobInformationResponse:
    def __init__(self, job: dict, progress: dict, state: str, error: str = None):
        self.job = JobInformation(**job)
        self.progress = datamodel.ProgressInformation(**progress)
        self.state = state
        self.error = error

    def __str__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            "job": self.job.to_dict(),
            "progress": self.progress.to_dict(),
            "state": self.state,
            "error": self.error,
        }
