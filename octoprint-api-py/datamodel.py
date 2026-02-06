class TemperatureData:
    def __init__(self, name: str, actual: float, target: float, offset: float = None):
        self.actual = actual
        self.target = target
        self.offset = offset


class TemperatureOffset:
    def __init__(self, tool: list = None, bed: float = None):
        self.tool = tool
        self.bed = bed


class ResendStats:
    def __init__(self, count: int, transmitted: int, ratio: int):
        self.count = count
        self.transmitted = transmitted
        self.ratio = ratio


class ProgressInformation:
    def __init__(
        self,
        completion: float,
        filepos: int,
        printTime: int,
        printTimeLeft: int,
        printTimeLeftOrigin: str,
    ):
        self.completion = completion
        self.filepos = filepos
        self.printTime = printTime
        self.printTimeLeft = printTimeLeft
        self.printTimeLeftOrigin = printTimeLeftOrigin


class GcodeAnalysisInformation:
    """
    Represents analysis information for a specific gcode file.
    """

    def __init__(
        self,
        estimatedPrintTime: float = None,
        filament: dict = None,
        dimensions: dict = None,
        printingArea: dict = None,
        travelArea: dict = None,
        travelDimensions: dict = None,
    ):
        self.estimatedPrintTime = (
            float(estimatedPrintTime) if estimatedPrintTime else None
        )
        self.filament = dict(filament) if filament else None
        self.dimensions = dict(dimensions) if dimensions else None
        self.printingArea = dict(printingArea) if printingArea else None
        self.travelArea = dict(travelArea) if travelArea else None
        self.travelDimensions = dict(travelDimensions) if travelDimensions else None


class PrintHistory:
    def __init__(self, success: float, failure: float, last: dict):
        self.success = success
        self.failure = failure
        self.last = last


class PrintStatistics:
    def __init__(self, averagePrintTime: dict, lastPrintTime: dict):
        self.averagePrintTime = averagePrintTime
        self.lastPrintTime = lastPrintTime


class Needs:
    def __init__(self, role: list = None, group: list = None):
        self.role = role
        self.group = group


class UserRecord:
    def __init__(
        self,
        name: str,
        active: bool,
        user: bool,
        admin: bool,
        settings: dict,
        groups: list,
        needs: Needs,
        apikey: str = None,
        permissions: list = None,
    ):
        self.name = name
        self.active = active
        self.user = user
        self.admin = admin
        self.settings = settings
        self.groups = groups
        self.needs = needs
        self.apikey = apikey
        self.permissions = permissions


class PermissionRecord:
    def __init__(
        self,
        key: str,
        name: str,
        dangerous: bool,
        default_groups: list,
        description: str,
        needs: Needs,
    ):
        self.key = key
        self.name = name
        self.dangerous = dangerous
        self.default_groups = default_groups
        self.description = description
        self.needs = needs


class GroupRecord:
    def __init__(
        self,
        key: str,
        name: str,
        description: str,
        needs: Needs,
        default: bool,
        removable: bool,
        changeable: bool,
        toggleable: bool,
        permissions: list = None,
        subgroups: list = None,
    ):
        self.key = key
        self.name = name
        self.description = description
        self.needs = needs
        self.default = default
        self.removable = removable
        self.changeable = changeable
        self.toggleable = toggleable
        self.permissions = permissions
        self.subgroups = subgroups
