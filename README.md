# pyrest-octoprint

*Pythonic Rest Api Wrapper for OctoPrint*

---

Pythonic wrapper for OctoPrint's REST API. Currently covers the majority
of the current API's functionality, minus these features that are yet
to be implemented:

1. [ ] `copy` and `move` endpoints for File object
2. [ ] Websocket push updates
3. [ ] Access control endpoints
4. [ ] User-login based authentication
5. [ ] Timelapse endpoints
6. [ ] Wizard endpoints

This list is ordered by what I would like to implement first while I continue
working on this. If you use OctoPrint a lot and would like to help, please do!

You might notice that there is no slicing functionality implemented and it is
not on the above checklist. I don't plan on adding this functionality since I
was told recently it will be removed from OctoPrint in future versions.

---

## Usage

Here's a basic example, using mostly default configurations within OctoPrint.
For more tweaking, see documentation (currently only in code).

```python
from pyrest-octoprint import Client

# set up a client
client = Client(base_url="https://your.octoprint.domain.com:5000", api_key="OCTOPRINT_API_KEY")

# connect and retrieve a Printer object
printer = client.connect_to_printer("/dev/serial_port")

# retrieve a File object 
# this is a path to a file within OctoPrint's storage, not locally
file = client.get_files("/path/to/file.gcode")

# start print
printer.start_print(file)

# get job info and print its status
job = printer.job_info()
print(job.status)
```

## Acknowledgements

Obviously, [octoprint]("https://github.com/OctoPrint/OctoPrint").

Acknowledgements to the [octorest repo]("https://github.com/dougbrion/OctoRest"), which
covers the API for version `1.3.11`. I decided to rewrite this API for the current version
as of 2026-02-05: `1.11.6`.

## License

MIT License can be found [here](LICENSE).
