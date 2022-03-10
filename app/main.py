#!/usr/bin/env python3

# ------------------------------------------------------------------------- #
# Dependency imports
# ------------------------------------------------------------------------- #

import json
import logging
import os
import sys
import shutil

from datetime import date, timedelta
from pathlib import Path


from lxml import etree

# ------------------------------------------------------------------------- #
# Globals / Defaults
# ------------------------------------------------------------------------- #

fmt = "%(asctime)s::%(levelname)s::%(message)s"
logging.basicConfig(filename="proxy.log", format=fmt, level=logging.DEBUG)

# TODO (dmel): Set back to proper file root
FILE_ROOT = "/home/daniel/Downloads"
# FILE_ROOT = "/usr/local/payara5"  # default for payara5
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


def gen_metadata_xpath(path: str):
    """Returns a properly formated xpath that lxml can read.
    Used as intermediate step to get an element in an xml
    from a specified rule in the defaults.json
    """

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
    """Creates a properly formated xpath that lxml can use.
    Used to create new elements in the XML file at the
    correct position.
    """

    # Assume last piece of path is not found
    elements = path.split("/")
    existing_el, new_el = (
        "/".join([p for p in elements[:-1]]),
        elements[-1].split(":")[1],
    )
    root_el = metadata.xpath(existing_el, namespaces=NSMAP)
    if len(root_el) > 0:  # superpath exists
        new = etree.SubElement(root_el[0], new_el)
        return new
    else:  # superpath does not exist
        new = etree.SubElement(metadata.getroot(), new_el)
        return new


def attribute_rule(p, xml):
    # Attribute rule, e.g. @abbr or @xml:lang
    path, attrib = p.split("@")
    if ":" in attrib:
        # Attribute rule with namespace
        ns, attrib = attrib.split(":")

    # Ensure that last element is not a slash so that we can find element
    path = path[:-1] if path[-1] == "/" else path

    # See if element exists, add if it doesnt
    el = xml.xpath(path, namespaces=NSMAP)
    if len(el) == 0:
        logging.info('Adding element "%s"', rule)
        el = add_element_xpath(xml, path)
        logging.debug(path)
    else:
        el = el[0]

    # See if element contains attribute
    attrib_exists = any([attrib in a for a in el.attrib.keys()])
    if not attrib_exists:
        # Add namespace to attrib if needed
        if ns is not None:
            attrib = "{" + NSMAP[ns] + "}" + attrib
        # Set attribute with default value
        logging.info('Attribute set to "%s" on "%s"', value, rule)
        el.set(attrib, value)
    else:
        logging.info('Attribute "%s" already present', rule)


def element_rule(p, xml):
    # Element rule, e.g. nation
    el = xml.xpath(p, namespaces=NSMAP)
    if len(el) == 0:  # element does not exist
        el = add_element_xpath(xml, path)
        logging.debug(path)
        logging.info('Added element "%s"', rule)

    # TODO Make two occurences of element possible
    # TODO Fix bug where text is not added and requires rerun
    for e in el:
        # Keep text if exist, otherwise use default
        if e.text == None:
            e.text = value
            logging.info('Adding text "%s" on "%s"', value, rule)
        else:
            logging.info('Element "%s" already set to "%s"', rule, e.text)


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
        root_path, _ = os.path.split(os.path.dirname(os.path.realpath(__file__)))
        defaults_filename = root_path + "/assets/defaults.json"
        defaults = read_json_file(defaults_filename)

        # Iterate over paths and set default values if no value present
        for rule, value in defaults.items():
            p, attrib, ns = None, None, None

            # Adds xml namespaces so that lxml can find elemenst
            p = gen_metadata_xpath(rule)
            # Verfiy element or attribute
            if "@" in p:
                attribute_rule(p, xml)
            else:
                element_rule(p, xml)

        return pretty_xml(xml, indent=True)

    except etree.XMLSyntaxError:
        logging.error("XMLSyntaxError at %s", filename)
    except etree.XPathEvalError:
        logging.error("XPathEvalError at %s", filename)
    except etree.XPathSyntaxError:
        logging.error("XPathSyntaxError at %s", filename)

    return None


# ------------------------------------------------------------------------- #
# Main
# ------------------------------------------------------------------------- #


def main():
    logging.info("Starting run")

    p = Path(FILE_ROOT)
    files = list(p.glob("**/export_oai_ddi.cached"))
    # TODO Set back once deploy
    #    files = list(p.glob("**/domain1/files/**/export_oai_ddi.cached"))
    for filename in files:
        logging.info("Processng file %s", filename)
        new = format_metadata(str(filename))
        if new is not None:
            with open(filename, "w") as f:
                f.write(new)

    logging.info("Done. Processed %s files.", len(files))


if __name__ == "__main__":
    main()
