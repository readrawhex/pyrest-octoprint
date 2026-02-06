from . import datamodel


class FileOrFolderDeleted(BaseException):
    pass


class FileInformation:
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
        parent: FileInformation = None,
    ):
        self.name = name
        self.display = display
        self.path = path
        self.type = type
        self.typePath = typePath
        self.user = str(user) if user else None
        self.parent = parent
        self._deleted = False

    def full_path(self) -> str:
        """
        Return the full path for FileInformation object based on
        parent attribute.
        """
        if self.parent:
            return str(os.path.join(self.parent.full_path(), self.path))
        else:
            return str(self.path)


class Folders(FileInformation):
    """
    Represents a folder within OctoPrint server storage.
    """

    def __init__(self, children: list = None, size: float = None, **kwargs):
        self.children = children
        self.size = size
        super().__init__(**kwargs)


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
        self.prints = PrintHistory(**prints) if prints else None
        self.statistics = PrintStatistics(**statistics) if statistics else None
        super().__init__(**kwargs)

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
        path = os.path.join(self.origin, self.full_path())
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
        path = os.path.join(self.origin, self.full_path())
        resp = self._make_request("/api/files/" + path, "DELETE")
        self._deleted = True


class RetrieveResponse:
    """
    Represents a RetrieveResponse for file info from OctoPrint.
    """

    def __init__(self, files=None, free: str = None):
        if type(files) == dict:
            self.files = [File(**files)]
        elif type(files) == list:
            self.files = []
            for x in files:
                if x.get("type", None) == "folder":
                    self.files.append(Folder(**x))
                else:
                    self.files.append(File(**x))
        elif files is not None:
            raise TypeError(f"invalid type for files: {type(files)}")
        self.free = str(free) if free else None


class AbridgedFileOrFolder:
    """
    Represents an AbridgedFileOrFolderInformation object retrieved from uploading /
    creating a file typically.
    """

    def __init__(
        self, name: str, display: str, path: str, origin: str, refs: dict = None
    ):
        self.name = str(name)
        self.display = str(display)
        self.path = str(path)
        self.origin = str(origin)
        if refs:
            self.resource = refs.get("resource")
            self.download = refs.get("download", None)
        else:
            self.resource = None
            self.download = None


class UploadResponse:
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
            self.local_file = datamodel.AbridgedFileOrFolder(**(files.get("local")))
            self.sdcard_file = (
                datamodel.AbridgedFileOrFolder(**(files.get("sdcard")))
                if "sdcard" in files.keys()
                else None
            )
        else:
            self.type = "folder"
            self.folder = datamodel.AbridgedFileOrFolder(**folder)
        self.effectiveSelect = bool(effectiveSelect) if effectiveSelect else None
        self.effectivePrint = bool(effectivePrint) if effectivePrint else None
