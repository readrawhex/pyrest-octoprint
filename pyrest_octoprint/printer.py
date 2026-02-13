from .datamodel import *
from .base import BaseClient
from . import files, printerprofiles, job


class ErrorInformation:
    """
    Defines error information received from Printer.
    """

    def __init__(
        self,
        error: str = None,
        reason: str = None,
        consequence: str = None,
        faq: str = None,
        logs: list = None,
    ):
        self.error = str(error)
        self.reason = str(reason)
        self.consequence = str(consequence)
        self.faq = str(faq)
        if logs is not None:
            self.logs = list(logs)


class TemperatureState:
    """
    Defines temperature state of Printer for tools and bed. For
    chamber temperature information, see `ChamberState`.
    """

    def __init__(self, tools: list = None, bed: TemperatureData = None):
        self.tools = tools
        self.bed = bed

    def __str__(self):
        return str({"tools": [x.to_dict() for x in self.tools], "bed": self.bed.to_dict()})

    def to_dict(self):
        return {"tools": [x.to_dict() for x in self.tools], "bed": self.bed.to_dict()}


class FullState:
    """
    Defines a FullStateResponse retrieved from OctoPrint.
    """

    def __init__(
        self,
        temperature: TemperatureState,
        sd_ready: bool,
        state_text: str,
        state_flags: dict,
        temperature_history: list = None,
    ):
        self.temperature = temperature
        self.sd_ready = bool(sd_ready)
        self.state_text = str(state_text)
        self.state_flags = dict(state_flags)
        self.temperature_history = (
            list(temperature_history) if temperature_history else []
        )

    def __str__(self):
        return str({
            "temperature": self.temperature.to_dict(),
            "sd.ready": self.sd_ready,
            "state.text": self.state_text,
            "state.flags": self.state_flags,
            "temperature.history": "[" + ", ".join([str(x) for x in self.temperature_history]) + "]" if self.temperature_history else None,
        })

    def to_dict(self):
        return {
            "temperature": self.temperature.to_dict(),
            "sd.ready": self.sd_ready,
            "state.text": self.state_text,
            "state.flags": self.state_flags,
            "temperature.history": [x.to_dict() for x in self.temperature_history],
        }


class ChamberState:
    """
    Defines Chamber temperature data retrieved from OctoPrint.
    """

    def __init__(self, temperature: TemperatureState, temperature_history: list = None):
        self.temperature = temperature
        self.temperature_history = temperature_history


class PrinterConnectionError(BaseException):
    pass


class Printer(BaseClient):
    """
    Represents a printer within Octoprint and its appropriate
    operations for interaction with its components.
    """

    def __init__(self, serial_port: str, **kwargs):
        self.serial_port = str(serial_port)
        self.baudrate = None
        self.printer_profile = None
        super().__init__(**kwargs)

    def _parse_temperature(self, data: dict) -> TemperatureState:
        """
        Parse a json response containing a TemperatureState object
        into a python object.
        """
        tools = []
        for k in [
            x for x in sorted(data.keys(), key=lambda x: x) if x.startswith("tool")
        ]:
            tools.append(TemperatureData(**data[k]))
        bed = TemperatureData(**(data["bed"])) if "bed" in data.keys() else None
        return TemperatureState(tools=tools, bed=bed)

    def connect(
        self,
        baudrate: int = None,
        printer_profile: printerprofiles.Profile = None,
        save_default: bool = False,
        autoconnect: bool = None,
    ) -> dict:
        """
        Connect to printer based on its `serial_port` member.

        params:
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
        data["port"] = self.serial_port
        if baudrate:
            data["baudrate"] = int(baudrate)
        elif self.baudrate:
            data["baudrate"] = self.baudrate
            baudrate = self.baudrate
        if printer_profile:
            data["printerProfile"] = printer_profile.name
        elif self.printer_profile:
            data["printerProfile"] = self.printer_profile.name
            printer_profile = self.printer_profile
        if save_default:
            data["save"] = save_default
        if autoconnect:
            data["autoconnect"] = autoconnect
        resp = self._make_request("/api/connection", "POST", json=data)
        return self._ensure_connection(fail_on_disconnect=True)

    def disconnect(self):
        """
        Disconnect printer if connected, else... nothing.
        """
        try:
            self._ensure_connection(fail_on_disconnect=True)
        except PrinterConnectionError:
            return
        data = {"command": "disconnect"}
        resp = self._make_request("/api/connection", "POST", json=data)

    def _ensure_connection(
        self,
        baudrate: int = None,
        printer_profile: printerprofiles.Profile = None,
        fail_on_disconnect: bool = False,
    ) -> dict:
        """
        Retrieve current connection in OctoPrint, if not connected to matching
        serial port then reconnect.
        """
        connection_data = self._connection_settings()
        if (
            connection_data.get("current", {}).get("state", None) in [None, "Error", "CloseOrError"]
            or connection_data.get("current", {}).get("port", None) != self.serial_port
        ):
            if fail_on_disconnect:
                raise PrinterConnectionError(
                    "Printer is not operationally connected: state: {}, port: {} (should be {})".format(
                        connection_data.get("current", {}).get("state", None),
                        connection_data.get("current", {}).get("port", None),
                        self.serial_port,
                    )
                )
            else:
                baudrate = self.baudrate if baudrate is None else baudrate
                printer_profile = (
                    self.printer_profile if printer_profile is None else printer_profile
                )
                connection_data = self.connect(baudrate, printer_profile)
        return connection_data

    def retrieve_info(self, history: int = 0) -> FullState:
        """
        Retrieve the most updated state of printer, including
        temperature, sdcard, and state information. Update self
        and return FullState object containing updated information.

        - endpoint: `/api/printer`
        - method: `GET`

        params:
            history (int): number of temperature records to include

        Returns a FullState object.
        """
        if history is None or history < 0:
            raise ValueError("`history` must be positive int or zero")

        data = {}
        if history > 0:
            data["history"] = True
            data["limit"] = history

        self._ensure_connection()
        resp = self._make_request("/api/printer", params=data)

        resp_data = resp.json()
        temp_history = resp_data["temperature"].pop("history", [])

        self.temperature = self._parse_temperature(resp_data["temperature"])
        self.temp_history = {}
        for x in temp_history:
            k = x.pop("time")
            v = self._parse_temperature(x)
            self.temp_history[k] = v
        self.sd_ready = resp_data.get("sd", {}).get("ready", None)
        self.state = str(resp_data["state"]["text"])
        for k, v in resp_data["state"]["flags"].items():
            setattr(self, k, v)
        return FullState(
            self.temperature,
            self.sd_ready,
            self.state,
            resp_data["state"]["flags"],
            self.temp_history,
        )

    def printhead_jog(
        self,
        x: int = None,
        y: int = None,
        z: int = None,
        absolute: bool = False,
        speed: int = None,
    ):
        """
        Jogs the print head (relatively) by a defined amount in one or more axes.

        - endpoint: `/api/printer/printhead`
        - method: `POST`

        params:
            x (int): Amount/coordinate to jog print head on x axis,
                must be a valid number corresponding to the distance
                to travel in mm.
            y (int): Amount/coordinate to jog print head on y axis,
                must be a valid number corresponding to the distance
                to travel in mm.
            z (int): Amount/coordinate to jog print head on z axis,
                must be a valid number corresponding to the distance
                to travel in mm.
            absolute (bool): specifies whether to move relative to
                current position (provided axes values are relative
                amounts) or to absolute position (provided axes values
                are coordinates)
            speed (int): Speed at which to move. If not provided, minimum
                speed for all selected axes from printer profile will
                be used.
        """
        if x is None and y is None and z is None:
            raise TypeError("no `x`, `y`, or `z` argument was provided")

        data = {"command": "jog"}
        if x:
            data["x"] = x
        if y:
            data["y"] = y
        if z:
            data["z"] = z
        if absolute:
            data["absolute"] = absolute
        if speed:
            data["speed"] = speed
        self._ensure_connection()
        resp = self._make_request("/api/printer/printhead", "POST", json=data)

    def printhead_home(self, x: bool = True, y: bool = True, z: bool = True):
        """
        Homes the print head in all of the given axes.

        - endpoint: `/api/printer/printhead`
        - method: `POST`

        params:
            x (bool): home the printer along the x-axis
            y (bool): home the printer along the y-axis
            z (bool): home the printer along the z-axis
        """
        if True not in [x, y, z]:
            raise TypeError("one of `x`, `y`, or `z` must be `True`")

        self._ensure_connection()
        data = {"command": "home", "axes": []}
        if x:
            data["axes"].append("x")
        if y:
            data["axes"].append("y")
        if z:
            data["axes"].append("z")
        resp = self._make_request("/api/printer/printhead", "POST", json=data)

    def printhead_feedrate(self, factor: float = 100.0):
        """
        Changes the feedrate factor to apply to the movements of the axes.

        - endpoint: `/api/printer/printhead`
        - method: `POST`

        params:
            factor (float): The new factor, percentage between 50 and 200% as
            integer (50 to 200) or float (0.5 to 2.0).
        """
        if factor > 2.0:
            factor /= round(100.0, 2)
        if factor > 2.0 or factor < 0.5:
            raise ValueError("`factor` must be between [0.5, 2.0] or [50, 200].")

        self._ensure_connection()
        resp = self._make_request(
            "/api/printer/printhead",
            "POST",
            json={
                "command": "feedrate",
                "factor": factor,
            },
        )

    def tool_target(self, temp):
        """
        Sets the given target temperature on the printer’s tools. Can either
        provide a zero or positive int value for `temp`, or a list of ints
        where each index N corresponds to tool{N}.

        - endpoint: `/api/printer/tool`
        - method: `POST`

        params:
            temp (int / list): temperature(s) for tool(s) in celsius.
        """
        if type(temp) not in [int, list]:
            raise ValueError("`temp` must be either an integer or list object")
        elif type(temp) == int:
            data = {"command": "target", "targets": {"tool": temp}}
        else:
            targets = {}
            for i, x in enumerate(temp):
                targets[f"tool{i}"] = x
            data = {"command": "target", "targets": targets}

        self._ensure_connection()
        resp = self._make_request("/api/printer/tool", "POST", json=data)

    def tool_offsets(self, offsets: list):
        """
        Sets the given temperature offset on the printer’s tools.

        - endpoint: `/api/printer/tool`
        - method: `POST`

        params:
            offsets (list): list of temperature offsets, with index N being
                offset for tool N.
        """
        _offsets = {}
        for i, x in enumerate(offsets):
            _offsets[f"tool{i}"] = x
        data = {"command": "offset", "offsets": _offsets}

        self._ensure_connection()
        resp = self._make_request("/api/printer/tool", "POST", json=data)

    def tool_select(self, tool: int):
        """
        Selects the printer’s current tool.

        - endpoint: `/api/printer/tool`
        - method: `POST`

        params:
            tool (int): index of tool to select (zero-indexed)
        """
        if tool < 0:
            raise ValueError("`tool` must be zero or positive")
        data = {"command": "select", "tool": tool}

        self._ensure_connection()
        resp = self._make_request("/api/printer/tool", "POST", json=data)

    def tool_extrude(self, amount: int, speed: int = None, tool: int = None):
        """
        Extrudes the given amount of filament from the currently selected tool.

        - endpoint: `/api/printer/tool`
        - method: `POST`

        params:
            amount (int): The amount of filament to extrude in mm. May
                be negative to retract.
            speed (int): Optional. Speed at which to extrude. If not provided,
                maximum speed for E axis from printer profile will be used.
                Otherwise interpreted as an integer signifying the speed in mm/min,
                to append to the command.
            tool (int): if provided, select tool{tool} for extruding. Else, extrude
                from currently selected tool.
        """
        data = {"command": "extrude", "amount": amount}
        if speed:
            if speed < 0:
                raise ValueError("`speed` must be zero or positive")
            data["speed"] = speed

        self._ensure_connection()
        resp = self._make_request("/api/printer/tool", "POST", json=data)

    def tool_flowrate(self, factor: int):
        """
        Changes the flow rate factor to apply to extrusion of the tool.

        - endpoint: `/api/printer/tool`
        - method: `POST`

        params:
            factor (int): The new factor, percentage between 75 and 125%
                as integer (75 to 125) or float (0.75 to 1.25).
        """
        if factor > 1.25:
            factor /= round(100.0, 2)
        if factor > 1.25 or factor < 0.75:
            raise ValueError("`factor` must be between [0.75, 1.25] or [75, 125].")

        self._ensure_connection()
        resp = self._make_request(
            "/api/printer/tool",
            "POST",
            json={
                "command": "flowrate",
                "factor": factor,
            },
        )

    def bed_target(self, target: int):
        """
        Sets the given target temperature on the printer’s bed.

        - endpoint: `/api/printer/bed`
        - method: `POST`

        params:
            target (int): Target temperature to set. A value of 0 will turn
                the heater off.
        """
        if target < 0:
            raise ValueError("`target` must be zero or positive")
        data = {"command": "target", "target": target}

        self._ensure_connection()
        resp = self._make_request("/api/printer/bed", json=data)

    def bed_offset(self, offset: int):
        """
        Sets the given temperature offset on the printer’s bed.

        - endpoint: `/api/printer/bed`
        - method: `POST`

        params:
            offset (int): Offset to set.
        """
        data = {"command": "offset", "offset": offset}

        self._ensure_connection()
        resp = self._make_request("/api/printer/bed", json=data)

    def chamber_target(self, target: int):
        """
        Sets the given target temperature on the printer’s chamber.

        - endpoint: `/api/printer/chamber`
        - method: `POST`

        params:
            target (int): Target temperature to set. A value of 0 will turn
                the heater off.
        """
        if target < 0:
            raise ValueError("`target` must be zero or positive")
        data = {"command": "target", "target": target}

        self._ensure_connection()
        resp = self._make_request("/api/printer/chamber", json=data)

    def chamber_offset(self, offset: int):
        """
        Sets the given temperature offset on the printer’s chamber.

        - endpoint: `/api/printer/chamber`
        - method: `POST`

        params:
            offset (int): Offset to set.
        """
        data = {"command": "offset", "offset": offset}

        self._ensure_connection()
        resp = self._make_request("/api/printer/chamber", json=data)

    def retrieve_chamber(self, history: int = 0):
        """
        Retrieves the current temperature data (actual, target and offset)
        plus optionally a (limited) history (actual, target, timestamp) for
        the printer’s heated chamber.

        - endpoint: `/api/printer/chamber`
        - method: `GET`

        params:
            history (int): number of temperature records to include
        """
        if history is None or history < 0:
            raise ValueError("`history` must be positive int or zero")
        data = {}
        if history > 0:
            data["history"] = True
            data["limit"] = history

        self._ensure_connection()
        resp = self._make_request("/api/printer/chamber", params=data)

        resp_data = resp.json()
        temp_history = resp_data.pop("history", None)

        self.chamber = TemperatureData(**(resp_data["chamber"]))
        self.chamber_history = {}
        for x in temp_history:
            k = x.pop("time")
            v = TemperatureData(**(x["chamber"]))
            self.temp_history[k] = v
        return ChamberState(self.chamber, self.chamber_history)

    def sd_init(self):
        """
        Initializes the printer’s SD card, making it available for use. This
        also includes an initial retrieval of the list of files currently stored
        on the SD card, so after issuing that command a retrieval of the files
        on SD card will return a successful result.

        - endpoint: `/api/printer/sd`
        - method: `POST`
        """
        self._ensure_connection()
        resp = self._make_request("/api/printer/sd", "POST", json={"command": "init"})

    def sd_refresh(self):
        """
        Refreshes the list of files stored on the printer’s SD card. Will throw a
        409 Conflict if the card has not been initialized yet

        - endpoint: `/api/printer/sd`
        - method: `POST`
        """
        self._ensure_connection()
        resp = self._make_request(
            "/api/printer/sd", "POST", json={"command": "refresh"}
        )

    def sd_release(self):
        """
        Releases the SD card from the printer. The reverse operation to init. After
        issuing this command, the SD card won’t be available anymore, hence and
        operations targeting files stored on it will fail. Will throw a 409 Conflict
        if the card has not been initialized yet.

        - endpoint: `/api/printer/sd`
        - method: `POST`
        """
        self._ensure_connection()
        resp = self._make_request(
            "/api/printer/sd", "POST", json={"command": "release"}
        )

    def is_sd_ready(self):
        """
        Retrieves the current state of the printer’s SD card.

        - endpoint: `/api/printer/sd`
        - method: `GET`
        """
        self._ensure_connection()
        resp = self._make_request("/api/printer/sd")
        self.sd_ready = resp.json().get("ready", None)
        return self.sd_ready

    def printer_error(self):
        """
        Retrieves information about the last error that occurred on the printer.

        - endpoint: `/api/printer/error`
        - method: `GET`
        """
        self._ensure_connection()
        resp = self._make_request("/api/printer/error")
        return ErrorInformation(**(resp.json()))

    def printer_command(
        self,
        command: str = None,
        commands: list = None,
        script: str = None,
        parameters: dict = None,
        context: dict = None,
    ):
        """
        Sends any command to the printer via the serial interface. Should be used
        with some care as some commands can interfere with or even stop a running
        print job.

        - endpoint: `/api/printer/command`
        - method: `POST`

        params:
            command (str): Single command as str.
            commands (list): List of arbitrary commands as str's.
            script (str): Name of the GCODE script template to send to the printer.
            parameters (dict): Key value pairs of parameters to replace in sent
                commands/provide to the script renderer.
            context (dict): (Only if script is set) additional template variables
                to provide to the script renderer.
        """
        if (command and commands) or (command and script) or (commands and script):
            raise TypeError(
                "Only one of `command`, `commands`, `script` should be provided"
            )
        if context and not script:
            raise TypeError("`context` should only be provided when providing `script`")
        commands = [str(c) for c in commands] if commands else None

        data = {}
        if command:
            data["command"]
        elif commands:
            data["commands"] = commands
        elif script:
            data["script"] = script
        else:
            raise TypeError("One of `command`, `commands`, `script` should be provided")

        if parameters:
            data["parameters"] = parameters
        if context:
            data["context"] = context

        self._ensure_connection()
        resp = self._make_request("/api/printer/command", "POST", json=data)

    def printer_controls(self):
        """
        Retrieves the custom controls as configured in config.yaml.

        - endpoint: `/api/printer/command/custom`
        - method: `GET`
        """
        self._ensure_connection()
        resp = self._make_request("/api/printer/command/custom")
        return resp.json()

    def job_info(self) -> job.JobInformationResponse:
        """
        Retrieves the current information about the Printer's job and
        updates its own related attributes appropriately.

        - endpoint: `/api/job`
        - method: `GET`
        """
        self._ensure_connection()
        resp = self._make_request("/api/job")
        resp_data = resp.json()

        self.job = resp_data.get("job")
        self.progress = resp_data.get("progress")
        self.print_status = resp_data.get("state")
        self.print_error = resp_data.get("error", None)
        obj = job.JobInformationResponse(
            self.job, self.progress, self.print_status, self.print_error
        )
        self.job = obj.job
        return obj

    def start_print(self, file: files.File):
        """
        Instruct printer to select `file` for printing and begin print.

        - endpoint: `/api/job`
        - method: `POST`

        params:
            file (File): file for printing
        """
        self._ensure_connection()
        file.select()
        self._make_request("/api/job", "POST", json={"command": "start"})

    def cancel_print(self):
        """
        Cancels the current print job. If no print job is active (either paused
        or printing), a 409 Conflict will be returned.

        - endpoint: `/api/job`
        - method: `POST`
        """
        self._ensure_connection()
        resp = self._make_request("/api/job", "POST", json={"command": "cancel"})

    def restart_print(self):
        """
        Restart the print of the currently selected file from the beginning.
        There must be an active print job for this to work and the print job
        must currently be paused. If either is not the case, a 409 Conflict
        will be returned.

        - endpoint: `/api/job`
        - method: `POST`
        """
        self._ensure_connection()
        resp = self._make_request("/api/job", "POST", json={"command": "restart"})

    def pause_print(self):
        """
        Pauses the current job if it’s printing, does nothing if it’s already
        paused.

        - endpoint: `/api/job`
        - method: `POST`
        """
        self._ensure_connection()
        resp = self._make_request(
            "/api/job", "POST", json={"command": "pause", "action": "pause"}
        )

    def resume_print(self):
        """
        Resumes the current job if it’s paused, does nothing if it’s already
        printing.

        - endpoint: `/api/job`
        - method: `POST`
        """
        self._ensure_connection()
        resp = self._make_request(
            "/api/job", "POST", json={"command": "pause", "action": "resume"}
        )

    def toggle_print(self):
        """
        Toggles the pause state of the job, pausing it if it’s printing and
        resuming it if it’s currently paused.

        - endpoint: `/api/job`
        - method: `POST`
        """
        resp = self._make_request(
            "/api/job", "POST", json={"command": "pause", "action": "toggle"}
        )
