#!/usr/bin/env python3

"""
Contact:  info@aussda.at

This is a small script for modifying Dataverse's DDI exports such that
they compley with CESSDA's requirements.

Tested on Dataverse 5.4.1
"""

# ------------------------------------------------------------------------- #
# Dependency imports
# ------------------------------------------------------------------------- #

import json
import logging
import os
import sys
from pathlib import Path

from lxml import etree

# ------------------------------------------------------------------------- #
# Globals / Defaults
# ------------------------------------------------------------------------- #


FILE_ROOT = "/usr/local/payara5"  # default for payara5
CONSTRAINT_LEVEL = "mandatory"  # mandatory, optional, recommended
NSMAP = {
    "xlmns": "http://www.openarchives.org/OAI/2.0/",
    "ddi": "ddi:codebook:2_5",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xsi": "http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd",
}

# ------------------------------------------------------------------------- #
# Util functions
# ------------------------------------------------------------------------- #


def read_json_file(filename):
    try:
        with open(filename, encoding="utf-8") as file:
            return json.load(file)
    except:
        print("[ERROR] File with default values not found. Check utils.py")
        sys.exit(1)


def pretty_xml(xml, indent=False):
    return etree.tostring(xml, pretty_print=indent, encoding=str)


def save_xml(xml, filename, indent=True):
    with open(filename, "w") as f:
        f.write(pretty_xml(xml, indent))


# ------------------------------------------------------------------------- #
# Metadata formatting
# ------------------------------------------------------------------------- #


def format_metadata(filename) -> str:
    # Setup response as XML
    xml_parser = etree.XMLParser(
        remove_blank_text=True,
        remove_comments=True,
        load_dtd=True,
        attribute_defaults=True,
        ns_clean=True,
        encoding="utf-8",
    )
    xml = etree.XML(filename, parser=xml_parser)
    metadata = xml.xpath("//xlmns:metadata", namespaces=NSMAP)[0]

    # Get default values with CONSTRAINT_LEVEL from data_file location in .cfg
    root_path, _ = os.path.split(os.path.dirname(os.path.realpath(__file__)))
    filename = os.path.join(root_path, f"/assets/{CONSTRAINT_LEVEL}_defaults.json")
    defaults = read_json_file(filename)

    # ToDo: Exception handling with XPathEvalError and XPathSyntaxError
    # Iterate over paths and set default values if no value present
    for rule, value in defaults.items():
        path, attrib, ns = None, None, None
        path = gen_metadata_xpath(rule)
        if "@" in path:
            # Attribute rule
            path, attrib = path.split("@")
            if ":" in attrib:
                # Attribute rule with namespace
                ns, attrib = attrib.split(":")

            # Remove trailing slash for xpath
            path = path[:-1] if path[-1] == "/" else path

            # Get first element matching path
            el = metadata.xpath(path, namespaces=NSMAP)
            if len(el) == 0:
                el = add_element_xpath(metadata, path)
            else:
                el = el[0]
            attrib_exists = any([attrib in a for a in el.attrib.keys()])
            if not attrib_exists:
                # Add namespace to attrib if needed
                if ns is not None:
                    attrib = "{" + NSMAP[ns] + "}" + attrib
                # Set attribute with default value

                el.set(attrib, value)
        else:
            # Element rule
            el = metadata.xpath(path, namespaces=NSMAP)
            if len(el) == 0:
                el = add_element_xpath(metadata, path)
            else:
                el = el[0]
            # Keep text if exist, otherwise use default
            if len(el.text) == 0:
                el.text = value

    return pretty_xml(xml, indent=True)


def gen_metadata_xpath(path: str):
    # Only add namespce after /codebook/
    _, item = path.split("/codeBook")

    # Seperate attribute from path
    if "@" in item:
        p, attrib = item.split("/@")
    else:
        p = item

    # Modify only if path is not just /codeBook/
    if len(p) > 1:
        p = [f"ddi:{i}" for i in p.split("/")[1:]]
        p = "/".join([i for i in p])

    # Merge together
    if "@" in item:
        if len(p) > 1:
            full = "//ddi:codeBook/" + p + "/@" + attrib
        else:
            # Edge case at root of /codeBook/
            full = "//ddi:codeBook/" + "@" + attrib
    else:
        full = "//ddi:codeBook/" + p

    # Return without whitespaces
    return full.strip()


def add_element_xpath(metadata: etree._Element, path: str):
    # Assume last piece of path is not found
    elements = path.split("/")
    existing, new = "/".join([p for p in elements[:-1]]), elements[-1].split(":")[1]
    # ToDo: verify len() > 1 or in other words that existing actually exists
    existing_element = metadata.xpath(existing, namespaces=NSMAP)[0]
    new = etree.SubElement(existing_element, new)

    return new


# ------------------------------------------------------------------------- #
# Main
# ------------------------------------------------------------------------- #


def main():
    p = Path(FILE_ROOT)
    files = list(p.glob("**/*ddi.cached"))
    for filename in files:
        with open(file, "r+") as f:
            pass


if __name__ == "__main__":
    main()
