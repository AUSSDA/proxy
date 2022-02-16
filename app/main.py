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
import shutil
import datetime
from pathlib import Path

import lxml
from lxml import etree

# ------------------------------------------------------------------------- #
# Globals / Defaults
# ------------------------------------------------------------------------- #

logging.basicConfig(filename="proxy.log", format="%(asctime)s::%(levelname)s::%(message)s")

FILE_ROOT = "/usr/local/payara5"  # default for payara5
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
        with open(filename, encoding="utf-8") as f:
            return json.load(f)
    except:
        logging.error("File with default values not found.")
        sys.exit(1)


def pretty_xml(xml, indent=False):
    return etree.tostring(xml, method="xml", pretty_print=indent, encoding=str)


def save_xml(xml, filename, indent=True):
    with open(filename, "w") as f:
        f.write(pretty_xml(xml, indent))


# ------------------------------------------------------------------------- #
# Metadata formatting
# ------------------------------------------------------------------------- #


def format_metadata(filename):
    # Setup response as XML
    xml_parser = etree.XMLParser(
        remove_blank_text=True,
        remove_comments=True,
        load_dtd=True,
        attribute_defaults=True,
        ns_clean=True,
        encoding="utf-8",
    )

    try:
        xml = etree.parse(filename, parser=xml_parser)
        # Get default values with CONSTRAINT_LEVEL from data_file location in .cfg
        root_path, _ = os.path.split(os.path.dirname(os.path.realpath(__file__)))
        defaults_filename = root_path + f"/assets/defaults.json"
        defaults = read_json_file(defaults_filename)

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
                el = xml.xpath(path, namespaces=NSMAP)
                if len(el) == 0:
                    el = add_element_xpath(xml, path)
                else:
                    el = el[0]
                attrib_exists = any([attrib in a for a in el.attrib.keys()])
                if not attrib_exists:
                    # Add namespace to attrib if needed
                    if ns is not None:
                        attrib = "{" + NSMAP[ns] + "}" + attrib
                    # Set attribute with default value
                    logging.info(f"{el}: Setting  {attrib} to {value}")
                    el.set(attrib, value)
            else:
                # Element rule
                el = xml.xpath(path, namespaces=NSMAP)
                if len(el) == 0: # element does not exist
                    el = add_element_xpath(xml, path)
                    logging.info(f"{el}: Added element {path}")
                else: # one or multiple instances of element exist
                    for e in el:
                        # Keep text if exist, otherwise use default
                        if e.text == None:
                            e.text = value
                            logging.info(f"{el}: Adding text {value}")
                
        return pretty_xml(xml, indent=True)

    except lxml.etree.XMLSyntaxError:
        logging.error("XMLSyntaxError at %s", filename)
    except lxml.etree.XPathEvalError:
        logging.error("XPathEvalError at %s", filename)
    except lxml.etree.XPathSyntaxError:
        logging.error("XPathSyntaxError at %s", filename)

    return None


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
    existing_el, new_el = "/".join([p for p in elements[:-1]]), elements[-1].split(":")[1]
    root_el = metadata.xpath(existing_el, namespaces=NSMAP) 
    if len(root_el) > 0: # superpath exists
        new = etree.SubElement(root_el[0], new_el)
        return new
    else: # superpath does not exist
        new = etree.SubElement(metadata.getroot(), new_el)
        return new


# ------------------------------------------------------------------------- #
# Main
# ------------------------------------------------------------------------- #


def main():
    startDate = datetime.datetime.now()
    logging.info(f"Starting run at {startDate}")
    p = Path(FILE_ROOT)
    files = list(p.glob("**/domain1/files/**/export_oai_ddi.cached"))
    for filename in files:
        logging.info(filename)
        p = Path(Path.cwd() / "backups/")
        q = p / filename.relative_to(filename.anchor)
        q.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(filename, q)    
        new = format_metadata(str(filename))
        if new is not None:
            with open(filename, "w") as f:
                f.write(new)
    endDate = datetime.datetime.now()
    logging.info(f"Done at {endDate}. Updated {len(files)} files.")

if __name__ == "__main__":
    main()
