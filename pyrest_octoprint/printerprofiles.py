from .base import BaseClient

class Profile(BaseClient):
    def __init__(
        self,
        id: str = None,
        name: str = None,
        color: str = None,
        model: str = None,
        default: bool = None,
        current: bool = None,
        resource: str = None,
        volume: dict = None,
        heatedBed: bool = None,
        heatedChamber: bool = None,
        axes: dict = None,
        extruder: dict = None,
        **kwargs,
    ):
        self.id = str(id) if id else None
        self.name = str(name) if name else None
        self.color = str(color) if color else None
        self.model = str(model) if model else None
        self.default = bool(default) if default else None
        self.current = bool(current) if current else None
        self.resource = str(resource) if resource else None
        self.volume = dict(volume) if volume else None
        self.heatedBed = bool(heatedBed) if heatedBed else None
        self.heatedChamber = bool(heatedChamber) if heatedChamber else None
        self.axes = dict(axes) if axes else None
        self.extruder = dict(extruder) if extruder else None
        self._deleted = False
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return str(self.to_dict())

    def to_dict(self) -> dict:
        """
        Return a dictionary of all of the profile data, excluding non-mutable
        data. This is used for serialization in api requests primarily.
        """
        data = {}
        if self.id is not None:
            data["id"] = self.id
        if self.name is not None:
            data["name"] = self.name
        if self.color is not None:
            data["color"] = self.color
        if self.model is not None:
            data["model"] = self.model
        if self.default is not None:
            data["default"] = self.default
        if self.resource is not None:
            data["resource"] = self.resource
        if self.volume is not None:
            data["volume"] = self.volume
        if self.heatedBed is not None:
            data["heatedBed"] = self.heatedBed
        if self.heatedChamber is not None:
            data["heatedChamber"] = self.heatedChamber
        if self.axes is not None:
            data["axes"] = self.axes
        if self.extruder is not None:
            data["extruder"] = self.extruder
        return data

    def update(self):
        """
        Update any changes made to the Profile object within OctoPrint.

        - endpoint: `/api/printerprofiles/<self.id>`
        - method: `PATCH`
        """
        resp = self._make_request(
            f"/api/printerprofiles/{self.id}", "PATCH", json={"profile": self.to_dict()}
        )
        for k, v in resp.json().get("profile").items():
            setattr(self, k, v)

    def delete(self):
        """
        Deletes the Profile within OctoPrint.

        - endpoint: `/api/printerprofiles/<self.id>`
        - method: `DELETE`
        """
        self._make_request(f"/api/printerprofiles/{self.id}", "DELETE")
        self._deleted = True


class AddOrUpdateRequest:
    def __init__(self, profiles: Profile, basedOn: str = None):
        self.profiles = profiles
        self.basedOn = basedOn
