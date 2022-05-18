#!/usr/bin/env python3

# ------------------------------------------------------------------------- #
# Dependency imports
# ------------------------------------------------------------------------- #

from country_codes import ISO3166 as cc

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

root = Path(__file__).parent.parent

fmt = "%(asctime)s::%(levelname)s::%(message)s"
logging.basicConfig(filename=root / "proxy.log", filemode="a", format=fmt, level=logging.INFO)

FILE_ROOT = Path("/usr/local/payara5")  # default for payara5
DEFAULTS = root / "assets/defaults.json"


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


def gen_metadata_xpath(path):
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


def add_element_xpath(metadata, path):
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

def is_gfk(xml):
    de = gen_metadata_xpath("/codeBook/stdyDscr/citation/distStmt/depositr")
    da = gen_metadata_xpath("/codeBook/docDscr/citation/verStmt/version/@date")

    depositor = xml.xpath(de, namespaces=NSMAP)
    vdate = xml.xpath(da, namespaces=NSMAP)
    
    if len(depositor) > 0 and len(vdate) > 0:
        if depositor[0].text == "GfK Austria" and date.fromisoformat(vdate[0]) < date.fromisoformat("2022-01-18"):
            return True
    else:
        return False
           
def set_text(el, value, p):
    if el.text == None:
        el.text = value
        logging.debug('Element "%s" added text "%s"', p, value)
    else:
        logging.debug('Element "%s" already set to "%s"', p, el.text)

def set_attribute(el, attrib, ns, p, xml, value, force=False):
    # Special conditions
    if p == gen_metadata_xpath("/codeBook/@xml:lang") and is_gfk(xml):
        value = "de"
        force = True
        logging.debug("Attribute value for GfK file")
    if p == gen_metadata_xpath("/codeBook/stdyDscr/stdyInfo/subject/keyword/@vocabURI"):
        force = True
        logging.debug("Override vocabURI")
    if p == gen_metadata_xpath("/codeBook/stdyDscr/citation/holdings/@URI"):
        val = xml.xpath(gen_metadata_xpath("/codeBook/docDscr/citation/titlStmt/IDNo"), namespaces=NSMAP)[0]
        _, u = val.text.split(":")
        url = "https://doi.org/" + u
        value = url
        logging.debug(f"Generated holdings URL '{value}'")
    if p == gen_metadata_xpath("/codeBook/stdyDscr/citation/distStmt/distDate/@date"):
        val = xml.xpath(gen_metadata_xpath("/codeBook/docDscr/citation/distStmt/distDate"), namespaces=NSMAP)[0]
        value = val.text
        logging.debug(f"Copied date '{value}' from distDate")
    if p == gen_metadata_xpath("/codeBook/stdyDscr/stdyInfo/sumDscr/nation/@abbr"):
        val = xml.xpath(gen_metadata_xpath("/codeBook/stdyDscr/stdyInfo/sumDscr/nation"), namespaces=NSMAP)[0]
        iso_code = cc.get(val.text)
        value = iso_code if iso_code is not None else "ZZ"  # ZZ == unkown or unspecified country
        logging.debug(f"Got nation abbrevation of nation '{val.text}' -> '{value}'")


    # See if element contains attribute
    attrib_exists = any([attrib in a for a in el.attrib.keys()])
    if not attrib_exists:
        # Add namespace to attrib if needed
        if ns is not None:
            attrib = "{" + NSMAP[ns] + "}" + attrib
        # Set attribute with default value
        logging.debug('Attribute "%s" set to "%s"', p, value)
        el.set(attrib, value)
    else:
        v = [a for a in el.attrib if attrib in a][0]
        if force:
            val = el.attrib[v]
            el.attrib[v] = value
            logging.debug('Forced overwrite attribute on "%s" from "%s" set to "%s"', p, val, value)
        else:
            val = el.attrib[v]
            if len(val) > 0:
                logging.debug('Attribute "%s" already present, set to "%s"', p, val)
            else:
                el.attrib[v] = value
                logging.debug('Attribute "%s" set to "%s"', p, value)


def attribute_rule(p, value, xml):
    # Separate attribute e.g. @abbr or @xml:lang from path
    ns = None
    path, attrib = p.split("@")
    # Ensure that last element is not a slash so that we can find element
    path = path[:-1] if path[-1] == "/" else path
    if ":" in attrib:
        # Attribute rule with namespace
        ns, attrib = attrib.split(":")

    # Use first occurance if element exists, add if it does not
    el = xml.xpath(path, namespaces=NSMAP)
    if len(el) == 0:
        logging.debug('Element "%s" added' , p)
        el = add_element_xpath(xml, path)
        set_attribute(el, attrib, ns, p, xml, value)
    else:
        for e in el:
            set_attribute(e, attrib, ns, p, xml, value)


def element_rule(p, value, xml):
    # Element rule, e.g. nation
    el = xml.xpath(p, namespaces=NSMAP)
    if len(el) == 0:  # element does not exist
        el = add_element_xpath(xml, p)
        logging.debug('Element "%s" added', p)
        set_text(el, value, p)
    else:
        for e in el:
            s = gen_metadata_xpath("/codeBook/stdyDscr/stdyInfo/subject/keyword")
            if e.text == "Social Sciences" and p == s:
                logging.debug(f"Removed element at {e}")
                e.getparent().remove(e) 

            set_text(e, value, p)


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
        defaults = read_json_file(str(DEFAULTS))
        # Iterate over paths and set default values if no value present
        for rule, value in defaults.items():
            # Get current file
            xml = etree.parse(filename, parser=xml_parser)   

            # Verfiy element or attribute
            p = gen_metadata_xpath(rule)
            if "@" in p:
                attribute_rule(p, value, xml)
            else:
                element_rule(p, value, xml)

            # Save to file on every change. Terribly inefficient. 
            # TODO change to memory caching.
            new = pretty_xml(xml, indent=True)
            with open(filename, "w") as f:
                f.write(new)

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
    files = list(FILE_ROOT.glob("**/domain1/files/**/export_oai_ddi.cached"))
    for filename in files:
        logging.info("Processng file %s", filename)
        format_metadata(str(filename))
    logging.info("Done. Processed %s files.", len(files))


if __name__ == "__main__":
     main()
