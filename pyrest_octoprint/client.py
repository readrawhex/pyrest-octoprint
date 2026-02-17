import requests
import os

from . import printerprofiles, printer, files, system
from .printer import Printer
from .base import BaseClient

from requests_toolbelt.utils import dump


class Client(BaseClient):
    """
    Defines the client used for making requests to
    the octoprint server.
    """

    def server_version(self):
        """
        Retrieve Octoprint version information.

        - endpoint: `/api/version`
        - method: `GET`
        """
        resp = self._make_request("/api/version")
        return resp.json()

    def connection_info(self):
        """
        Retrieve Octoprint connection information.

        - endpoint: `/api/server`
        - method: `GET`
        """
        resp = self._make_request("/api/server")
        return resp.json()

    def connection_settings(self):
        """
        Retrieve Octoprint connection settings.

        - endpoint: `/api/connection`
        - method: `GET`
        """
        return self._connection_settings()

    def connect_to_printer(
        self,
        serial_port: str,
        baudrate: int = None,
        printer_profile: printerprofiles.Profile = None,
        save_default: bool = False,
        autoconnect: bool = None,
    ) -> printer.Printer:
        """
        Instructs OctoPrint to connect to a printer, either by passing
        a Printer object or serial_port & baudrate.

        - endpoint: `/api/connection`
        - method: `POST`

        params:
            serial_port (str): Specific serial port to connect to.
            baudrate (int): Specific baudrate to connect with. Defaults to default
                `baudratePreference` value set in OctoPrint.
            printer_profile (Profile): Specific printer profile to use for connection. Defaults
                to default profile is none is provided.
            save_default (bool): Whether to save the request’s port and baudrate settings as
                new preferences. Defaults to false if not set.
            autoconnect (bool): Whether to automatically connect to the printer on
                OctoPrint’s startup in the future. If not set no changes will be made
                to the current configuration.
        """
        data = {"command": "connect"}
        data["port"] = str(serial_port)
        if baudrate:
            data["baudrate"] = int(baudrate)
        if printer_profile:
            data["printerProfile"] = printer_profile.name
        if save_default:
            data["save"] = save_default
        if autoconnect:
            data["autoconnect"] = autoconnect
        resp = self._make_request("/api/connection", "POST", json=data)
        printer = Printer(parent_client=self, serial_port=data["port"])
        return printer

    def disconnect_current_printer(self):
        """
        Instructs OctoPrint to disconnect from the printer.

        - endpoint: `/api/connection`
        - method: POST
        """
        data = {"command": "disconnect"}
        resp = self._make_request("/api/connection", "POST", json=data)

    def get_files(
        self,
        path: str = None,
        override_cache: bool = False,
        recursive: bool = True,
        location: str = "local",
    ):
        """
        Retrieve information regarding files currently available and
        regarding the disk space still available locally in either the
        `local` or `sdcard` storage. The results are cached for performance
        reasons.

        params:
            override_cache (bool): override cache on request
            recursive (bool): return files within folders in root directory
            location (str): either `local` (uploads folder) or `sdcard`

        Returns a RetrieveResponse object.
        """
        params = {
            "force": override_cache,
            "recursive": recursive,
        }
        url = "/api/files"
        if location not in ["local", "sdcard"]:
            raise ValueError("`location` argument must be one of ['local', 'sdcard']")
        url += f"/{location}"
        if path is not None:
            url = os.path.join(url, path)
        resp = self._make_request(url, params=params)
        return files.RetrieveResponse(**(resp.json()), parent_client=self)

    def get_file(
        self,
        filename: str,
        path: str = None,
        override_cache: bool = False,
        recursive: bool = False,
        location: str = "local",
    ):
        """
        Similar to `self.get_files`, but returns the specified `File` object
        with a name of `filename`.

        params:
            override_cache (bool): override cache on request
            recursive (bool): return files within folders in root directory
            location (str): either `local` (uploads folder) or `sdcard`

        Returns a File object if it exists, else None.
        """
        retrieve_response = self.get_files(path, override_cache, recursive, location)
        for f in retrieve_response.files:
            if f.name == filename:
                return f
        return None

    def upload_file(
        self, file, path: str = "/", location: str = "local"
    ):
        """
        Upload a file to the selected `location`.

        - endpoint: `/api/files`
        - method: `POST`

        params:
            file (file-like): actual file object to upload (bytes object)
            path (str): path to parent folder within `location` for upload.
            location (str): full path location to upload file to
        """
        if location not in ["local", "sdcard"]:
            raise ValueError("`location` path must be either 'local' or 'sdcard'")
        url = "/api/files/" + location + (path if path not in ["/", None] else "")
        files_data = {"file": file}
        resp = self._make_request(url, "POST", files=files_data)
        return self.get_file(os.path.basename(file.name), path=(path if path not in ["/", None] else None), override_cache=True, location=location)

    def new_folder(self, foldername: str, path: str = None):
        """
        Create a subfolder within the local uploads folder. Folder
        creation is only supported in `local` storage.

        - endpoint: `/api/files/local`
        - method: `POST`

        params:
            foldername (str): name of folder to create
            path (str): Optional, path to parent folder within uploads folder.
        """
        if foldername in [None, ""]:
            raise ValueError(f"invalid foldername")
        resp = self._make_request(
            "/api/files/local" + (path if path not in [None, "/"] else ""),
            "POST",
            data={"foldername": foldername},
            files={},
        )
        return self.get_file(foldername, path=(path if path not in ["/", None] else None), override_cache=True)

    def unselect_file(self):
        """
        Unselects the currently selected file for printing.

        - endpoint: `/api/files/<path>`
        - method: `POST`
        """
        resp = self._make_request(
            "/api/files/" + path,
            "POST",
            params={
                "command": "unselect",
            },
        )
        return resp.json

    def retrieve_profile(self, profile: str = None) -> printerprofiles.Profile:
        """
        Retrieves an object representing all configured printer profiles or a single
        profilec. If no `profile` argument is specified, defaults to all profiles.

        - endpoint: `/api/printerprofiles`
        - method: `GET`
        """
        url = "/api/printerprofiles"
        if profile:
            url += f"/{profile}"
        resp = self._make_request(url)
        return printerprofiles.Profile(**(resp.json()), parent_client=self)

    def add_profile(self, profile, based_on=None) -> printerprofiles.Profile:
        """
        Adds a new printer profile based on either the current default profile or
        the profile identified in basedOn. The provided profile data will be merged
        with the profile data from the base profile.

        - endpoint: `/api/printerprofiles`
        - method: `POST`
        """
        if based_on:
            if type(based_on) == printerprofiles.Profile:
                based_on = based_on.id
            else:
                based_on = str(based_on)
        if type(profile) == printerprofiles.Profile:
            profile = profile.to_dict()
        else:
            profile = dict(profile)
        data = {"profile": profile}
        if based_on:
            data["basedOn"] = based_on
        resp = self._make_request("/api/printerprofiles", "POST", json=data)
        return printerprofiles.Profile(**(resp.json().get("profile")), parent_client=self)

    def list_system_commands(self, source: str = None) -> list:
        """
        Return a list of the available system commands.

        - endpoint: `/api/system/commands`
        - method: `GET`

        params:
            source (str): either 'core', 'custom', or None for both.
        """
        url = "/api/system/commands"
        if source:
            if source not in ["core", "custom"]:
                raise ValueError("`source` must be one of 'core', 'custom', or None")
            url += "/" + source
        resp = self._make_request(url)
        resp_data = resp.json()
        if source:
            return [system.CommandDefinition(**x) for x in resp_data]
        else:
            return {
                "core": [
                    system.CommandDefinition(**x) for x in resp_data.get("core", [])
                ],
                "custom": [
                    system.CommandDefinition(**x) for x in resp_data.get("custom", [])
                ],
            }

    def system_command(self, action: str, custom_command: bool = False):
        """
        Execute a system command `action`, with `custom_command` specifying if the
        command is a custom user command (True) or a core command (False)

        - endpoint: `/api/system/<core or custom>/<action>`
        - method: `POST`

        params:
            action (str): command name
            custom_command (bool): is `action` a custom command?
        """
        url = "/api/system/commands/" + ("custom/" if custom_command else "core/")
        url += str(action)
        self._make_request(url, "POST")

    def settings(self):
        """
        Retrieve a dictionary of settings defined in OctoPrint's `config.yml` file.

        - endpoint: `/api/settings`
        - method: `GET`
        """
        resp = self._make_request("/api/settings")
        return resp.json()

    def set_settings(self, values: dict):
        """
        Saves the provided settings in OctoPrint. Expects a dict object with the settings
        to change as request body. This can be either a full settings tree, or only a
        partial tree containing only those fields that should be updated.

        - endpoint: `/api/settings`
        - method: `POST`

        params:
            values (dict): a dictionary of settings value following the [partial] structure
                of OctoPrint's `config.yml` file.
        """
        self._make_request("/api/settings", "POST", json=values)

    def regenerate_api_key(self) -> str:
        """
        Generates a new system wide API key.

        - endpoint: `/api/settings/apikey`
        - method: `POST`

        Returns the newly generated systemwide api key. This does not currently update
        any of the api keys within python client-like objects.
        """
        resp = self._make_request("/api/settings/apikey", "POST")
        return resp.json().get("apikey")

    def language_packs(self) -> list:
        """
        Retrieves a list of installed language packs.

        - endpoint: `/api/languages`
        - method: `GET`

        Returns a list of `languages.ComponentList` objects.
        """
        resp = self._make_request("/api/languages")
        return [
            languages.ComponentList(**x) for x in resp.json().get("language_packs", [])
        ]

    def upload_language_pack(self, filename: str, file) -> list:
        """
        Uploads a new language pack to OctoPrint. Only files with one of the extensions
        zip, tar.gz, tgz or tar will be processed, for other file extensions a 400 Bad
        Request will be returned.

        - endpoint: `/api/languages`
        - method: `POST`

        params:
            filename (str): name of language pack file.
            file (file-like): file data to upload.

        Returns a list of `languages.ComponentList` objects.
        """
        resp = self._make_request(
            url,
            "POST",
            files={
                "files": (filename, file),
                "path": (None, path),
            },
        )
        return [
            languages.ComponentList(**x) for x in resp.json().get("language_packs", [])
        ]

    def delete_language_pack(self, locale: str, pack: str = "_core") -> list:
        """
        Deletes the language pack pack for locale `locale`. `pack` can be either the
        `_core` pack (default value) or the language pack for a plugin specified by
        the plugin identifier.

        - endpoint: `/api/languages`
        - method: `DELETE`

        params:
            locale (str): locale of language pack
            pack (str): plugin containing the language pack, or `_core` for core packs.

        Returns a list of `languages.ComponentList` objects.
        """
        resp = self._make_request(f"/api/languages/{locale}/{pack}", "DELETE")
        return [
            languages.ComponentList(**x) for x in resp.json().get("language_packs", [])
        ]
