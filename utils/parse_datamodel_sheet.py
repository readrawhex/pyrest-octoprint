"""
This is a quick script to parse the `docs/api` folder of
`github.com/OctoPrint/OctoPrint`. 
"""
import json
import sys
import os
import argparse
import shutil

# Format for a python class
CLASS_FORMAT = """class {}:
    def __init__(self, {}):
        {}


"""

PARSE_KWARGS_FORMAT = """for k, v in kwargs:
            setattr(self, k, v)"""

# Format for parsing **kwargs if necessary



def parse_type(type_str: str) -> str:
    """
    Parse a type string within a '.rst' file into the appropriate
    python3 type.

    params:
        type_str (str): type written in '.rst' file

    Returns python type as string value.
    """
    type_converter = {
        "String": "str",
        "string": "str",
        "url": "str",
        "URL": "str",
        "Object": "dict",
        "object": "dict",
        "boolean": "bool",
        "Boolean": "bool",
        "bool": "bool",
        "Bool": "bool",
        "int": "int",
        "int or null": "int",
        "Integer": "int",
        "integer": "int",
        "Number": "float",
        "Number (Float)": "float",
        "Float": "float",
        "float": "float",
        "list": "list",
        "List": "list",
        "Unix Timestamp": "int",
        "Unix timestamp": "int",
        "string or object": "dict",
        "Printer state flags": "dict",
    }
    if type_str.startswith("List of") or type_str.startswith("Array of"):
        return "list"
    if type_str.startswith("Map of") or type_str.endswith("or ``object"):
        return "dict"
    if type_str.startswith("String, "):
        return "str"

    if type_str in type_converter.keys():
        return type_converter[type_str]
    if type_str.startswith(":ref:"):
        return type_str
    raise Exception(f"unsure how to parse type: '{type_str}'")


def parse_member(lines: list, i: int) -> (list, int):
    """
    Parse a member item from a datamodel description.

    params:
        lines (list): list of lines from file
        i (int): current index of lines being processed

    Returns a tuple of (member_data: dict, new_index: int)
    """
    name = lines[i].split("``")[1].strip()
    type_value = parse_type("-".join(lines[i + 2].split("-")[1:]).strip().strip("`"))
    description = "-".join(lines[i + 3].split("-")[1:]).strip()
    j = 4
    while (
        i + j < len(lines)
        and not lines[i + j].strip().startswith("*")
        and not lines[i + j].strip() == ""
    ):
        description += " " + lines[i + j].strip()
        j += 1
    return (
        {
            "name": name,
            "type": type_value,
            "description": "-".join(lines[i + 3].split("-")[1:]).strip(),
            "optional": (lines[i+1].split("-")[1].strip().startswith("0..")),
        },
        i + j,
    )


def parse_class(lines: list, i: int, parent: dict = None) -> (list, int):
    """
    Parse a full datamodel and its members. Expects `i` to be
    the index of the header underline for the class name.

    params:
        lines (list): list of lines from file
        i (int): current index of lines being processed

    Returns a tuple of (class_data: dict, new_index: int)
    """
    new_class = {"name": lines[i - 1].title().replace(" ", "").strip().replace("`", ""), "members": []}
    if i - 3 > 0 and lines[i - 3].startswith(".. _"):
        new_class["reference"] = ":ref:" + lines[i - 3][4:].strip()
    while lines[i].strip() != "- Description":
        i += 1
    i += 1
    while True:
        new_member, i = parse_member(lines, i)
        new_class["members"].append(new_member)
        if i >= len(lines) or lines[i].strip() == "":
            break

    names = [m["name"] for m in new_class["members"]]
    for m in names:
        if "." in m:
            if m.split(".")[0] not in names:
                new_class["members"].append(
                    {
                        "name": m.split(".")[0].replace("`", ""),
                        "type": "dict",
                        "description": None,
                        "optional": True if True in [n.get("optional", False) for n in new_class["members"] if n["name"] == m] else False,
                    }
                )
                names.append(m.split(".")[0])
            new_class["members"] = [n for n in new_class["members"] if n["name"] != m]

    for m in new_class["members"]:
        if m["name"].endswith("{n}"):
            m["name"] = m["name"].replace("{n}", "")
            m["type"] = "list"
        elif m["name"][0] == "<" and m["name"][-1] == ">":
            m["name"] = "**kwargs"
            m["type"] = None
            m["optional"] = False

    new_class["members"] = sorted(new_class["members"], key=lambda x: x["optional"])
    if parent:
        new_class["parent"] = parent["name"]

    return (new_class, i)


def main():
    parser = argparse.ArgumentParser(
        description="create python3 classes from  `github.com:OctoPrint/Octoprint/docs/api/`"
    )
    parser.add_argument(
        "-j",
        "--json-filename",
        type=str,
        default="all_datamodels.json",
        help="name for json file containing class data",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="force overwriting of `output_dir`"
    )
    parser.add_argument("api_docs", type=str, help="location of api docs folder")
    parser.add_argument(
        "output_dir", type=str, help="output directory for python files"
    )
    args = parser.parse_args()

    try:
        if os.path.exists(args.output_dir):
            if not args.force:
                raise Exception(
                    f"'{args.output_dir}' already exists: use -f to write over contents"
                )
            shutil.rmtree(args.output_dir)
        os.makedirs(args.output_dir)

        if os.path.isfile(os.path.join(args.output_dir, args.json_filename)):
            os.remove(os.path.join(args.output_dir, args.json_filename))

        """
        Go through each file in `api_docs` and parse classes and
        their members, write data to `json_filename`.
        """
        for filename in os.listdir(args.api_docs):
            classes = []
            with open(os.path.join(args.api_docs, filename), "r") as f:
                lines = f.readlines()
                i = 0
                delimiter = "-----" if filename != "access.rst" else "~~~~~"
                subclass_delimiter = "'''''"
                while i < len(lines):
                    if lines[i].startswith(delimiter):
                        new_class, i = parse_class(lines, i)
                        classes.append(new_class)
                        parent = -1
                    elif lines[i].startswith(subclass_delimiter):
                        new_class, i = parse_class(lines, i, parent = classes[parent])
                        classes.append(new_class)
                        parent -= 1
                    else:
                        i += 1

            if len(classes) == 0:
                continue

            python_filename = filename.replace(".rst", ".py")

            json_classes = classes
            for j in json_classes:
                j["file"] = python_filename

            if os.path.isfile(os.path.join(args.output_dir, args.json_filename)):
                with open(os.path.join(args.output_dir, args.json_filename), "r") as f:
                    json_classes += json.load(f)

            with open(os.path.join(args.output_dir, args.json_filename), "w") as f:
                json.dump(json_classes, f)

        """
        Go through `json_filename` data, resolve any type references to other
        datamodels, then write to files.
        """
        with open(os.path.join(args.output_dir, args.json_filename), "r") as f:
            all_json_data = json.load(f)

        references = {}
        for c in all_json_data:
            if "reference" in c.keys():
                references[c["reference"]] = (c["name"], c["file"])

        # sort so classes with references come last in file
        all_json_data = sorted(all_json_data, key=lambda c: (True in [m["type"].startswith(":ref:") for m in c["members"] if m["type"]]))

        for c in all_json_data:
            for m in c["members"]:
                if m["type"] and m["type"].startswith(":ref:"):
                    if "<" in m["type"]:
                        type_ref = ":ref:" + m["type"].split("<")[1].split(">")[0] + ":"
                    else:
                        type_ref = ":ref:" + m["type"].split("`")[1] + ":"
                    if type_ref not in references.keys():
                        raise Exception(
                            f"unresolved class type reference: '{m['type']}'"
                        )
                    m["type"] = references[type_ref][0]

        for c in all_json_data:
            with open(os.path.join(args.output_dir, c["file"]), "a") as f:
                if f.tell() == 0 and c["file"] != "datamodel.py":
                    f.write("from .datamodel import *\n\n")
                constructor_args = ", ".join(
                    [m["name"] + (" : " + m["type"] if m["type"] else "") + (" = None" if m.get("optional", False) else "") for m in c["members"]]
                )
                assignments = f"\n        ".join(
                    [f"self.{m['name']} = {m['name']}" for m in c["members"]]
                )
                if assignments == "self.**kwargs = **kwargs":
                    assignments = PARSE_KWARGS_FORMAT
                if c.get("parent"):
                    assignments += "\n        super().__init__(**kwargs)"
                    constructor_args += ", **kwargs"
                f.write(
                    CLASS_FORMAT.format(
                        c["name"] + (f"({c['parent']})" if c.get('parent') else ""),
                        constructor_args,
                        assignments,
                    )
                )
    except Exception as e:
        raise (e)
        print(f"[!] Failed: {e}", file=sys.stderr)
        sys.exit(1)
    print("[+] done :)", file=sys.stderr)


if __name__ == "__main__":
    main()
