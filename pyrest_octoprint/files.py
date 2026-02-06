from datetime import datetime
import os

from . import datamodel
from .base import BaseClient


class FileOrFolderDeleted(BaseException):
    pass


class FileInformation(BaseClient):
    """
    Base class defining shared members between `File` and `Folder` object.
    """

    def __init__(
        self,
        name: str,
        display: str,
        path: str,
        type: str,
        typePath: list,
        user: str = None,
        **kwargs,
    ):
        self.name = name
        self.display = display
        self.path = path
        self.type = type
        self.typePath = typePath
        self.user = str(user) if user else None
        self._deleted = False
        super().__init__(**kwargs)


class Folder(FileInformation):
    """
    Represents a folder within OctoPrint server storage.
    """

    def __init__(
        self, 
        children: list = None, 
        size: float = None, 
        date: int = None,
        origin: str = None,
        prints: dict = None,
        refs: dict = None,
        **kwargs
    ):
        self.children = []
        for c in children:
            if c.get("type", None) == "folder":
                self.children.append(Folder(**c, parent_client=kwargs.get("parent_client", None)))
            else:
                self.children.append(File(**c, parent_client=kwargs.get("parent_client", None)))
        self.size = size
        self.date = datetime.fromtimestamp(date) if date else None
        self.origin = str(origin) if origin else None
        self.prints = datamodel.PrintHistory(**prints) if prints else None
        if refs:
            self.resource = refs.get("resource")
            self.download = refs.get("download", None)
        super().__init__(**kwargs)

    def __str__(self):
        return f"Folder(path='{self.path}')"

    def delete(self):
        """
        Delete the selected folder at `self.path`.

        - endpoint: `/api/files/<path>`
        - method: `DELETE`

        params:
            path (str): path to file to delete
        """
        path = os.path.join(self.origin, self.path)
        resp = self._make_request("/api/files/" + path, "DELETE")
        self._deleted = True


class File(FileInformation):
    """
    Represents a File stored on the OctoPrint server.
    """

    def __init__(
        self,
        origin: str,
        hash: str = None,
        size: float = None,
        date: int = None,
        refs: dict = None,
        gcodeAnalysis: dict = None,
        prints: dict = None,
        statistics: dict = None,
        **kwargs,
    ):
        self.origin = str(origin)
        self.hash = str(hash) if hash else None
        self.size = float(size) if size else None
        self.date = datetime.fromtimestamp(date) if date else None
        if refs:
            self.resource = refs.get("resource")
            self.download = refs.get("download", None)
        else:
            self.resource = None
            self.download = None
        self.gcodeAnalysis = (
            datamodel.GcodeAnalysisInformation(**gcodeAnalysis)
            if gcodeAnalysis
            else None
        )
        self.prints = datamodel.PrintHistory(**prints) if prints else None
        self.statistics = PrintStatistics(**statistics) if statistics else None
        super().__init__(**kwargs)

    def __str__(self):
        return f"File(path='{self.path}')"

    def select(self, print_now: bool = False):
        """
        Select `self` for printing.

        - endpoint: `/api/files/<path>`
        - method: `POST`

        params:
            print_now (bool): print file once selected
        """
        if self._deleted:
            raise FileOrFolderDeleted(
                f"File(name='{self.name}') object is marked as deleted."
            )
        path = os.path.join(self.origin, self.path)
        self._make_request(
            "/api/files/" + path,
            "POST",
            params={
                "command": "select",
                "print": print_now,
            },
        )

    def unselect(self):
        """
        Unselects the currently selected file for printing.

        - endpoint: `/api/files/<path>`
        - method: `POST`
        """
        self._make_request(
            "/api/files/" + path,
            "POST",
            params={
                "command": "unselect",
            },
        )

    def delete(self):
        """
        Delete the selected file at `self.path`.

        - endpoint: `/api/files/<path>`
        - method: `DELETE`

        params:
            path (str): path to file to delete
        """
        path = os.path.join(self.origin, self.path)
        resp = self._make_request("/api/files/" + path, "DELETE")
        self._deleted = True

    def move_into(self, folder: Folder):
        """
        Move self's location in OctoPrint storage into `folder.path` for
        Folder object.

        - endpoint: `/api/files/<path>`
        - method: `POST`

        params:
            folder (Folder): Folder to move self into.
        """
        self._make_request(
            "/api/files/" + path,
            "POST",
            params={
                "command": "move",
                "destination": folder.path,
            },
        )
        self.path = os.path.join(folder.path, self.name)


class RetrieveResponse:
    """
    Represents a RetrieveResponse for file info from OctoPrint.
    """

    def __init__(self, files=None, free: str = None, total: str = None, **kwargs):
        if type(files) == dict:
            self.files = [File(**files, **kwargs)] if files.get("type", None) != "folder" else [Folder(**files, **kwargs)]
        elif type(files) == list:
            self.files = []
            for x in files:
                if x.get("type", None) == "folder":
                    self.files.append(Folder(**x, **kwargs))
                else:
                    self.files.append(File(**x, **kwargs))
        elif files is not None:
            raise TypeError(f"invalid type for files: {type(files)}")
        self.free = str(free) if free else None
        self.total = str(total) if total else None

    def __str__(self):
        return str("[" + ", ".join([str(x) for x in self.files]) + "]")


class AbridgedFileOrFolder:
    """
    Represents an AbridgedFileOrFolderInformation object retrieved from uploading /
    creating a file typically.
    """

    def __init__(
        self, name: str, path: str, origin: str, refs: dict = None, display: str = None
    ):
        self.name = str(name)
        self.path = str(path)
        self.origin = str(origin)
        if refs:
            self.resource = refs.get("resource")
            self.download = refs.get("download", None)
        else:
            self.resource = None
            self.download = None
        self.display = str(display) if display else None


class UploadResponse(BaseClient):
    """
    Represents an UploadResponse retrieved from uploading a file / creating
    a folder in OctoPrint.
    """

    def __init__(
        self,
        done: bool,
        files: dict = None,
        folder: dict = None,
        effectiveSelect: bool = None,
        effectivePrint: bool = None,
    ):
        self.done = bool(done)
        if files:
            self.type = "file"
            self.local_file = AbridgedFileOrFolder(**(files.get("local")))
            self.sdcard_file = (
                AbridgedFileOrFolder(**(files.get("sdcard")))
                if "sdcard" in files.keys()
                else None
            )
        else:
            self.type = "folder"
            self.folder = AbridgedFileOrFolder(**folder)
        self.effectiveSelect = bool(effectiveSelect) if effectiveSelect else None
        self.effectivePrint = bool(effectivePrint) if effectivePrint else None
