#!/usr/bin/env python3

"""
Contact:  info@aussda.at

This is a small flask application that serves as reverse proxy and acts
as man-in-the-middle. It passes a request to Dataverse's OAI endpoint, and
adds all deafault values from the _defaults.json files.

Tested only with Dataverse 4.20.
"""

# ------------------------------------------------------------------------- #
# Dependency imports
# ------------------------------------------------------------------------- #

import requests
import os
import sys
import json
import logging

from flask import Flask, jsonify, request, Response, make_response
from lxml import etree

# ------------------------------------------------------------------------- #
# Globals / Defaults
# ------------------------------------------------------------------------- #

app = Flask(__name__)

logging.basicConfig(level=logging.WARNING)

HOSTNAME = "https://data.aussda.at"
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


def place_request(path: str, query: str) -> str:
    # Allow only to reach the OAI-MPH endpoint
    if not path == "oai":
        app.loggger.warning("Invalid endpoint")
        return None

    # Generate url and place request
    url = f"{HOSTNAME}/{path}?{query}"
    try:
        req_raw = requests.get(url)
    except:
        app.logger.warning("Request could not be placed")
        return None
    app.logger.info(f"Successfully placed proxied request to '{url}'")
    # Modify xml for compliance
    req_format = format_metadata(req_raw)
    return req_format


def format_metadata(req_raw) -> str:
    # Setup response as XML
    xml_parser = etree.XMLParser(
        remove_blank_text=True,
        remove_comments=True,
        load_dtd=True,
        attribute_defaults=True,
        ns_clean=True,
        encoding="utf-8",
    )
    app.logger.debug(f"Parsing response {req_raw.content}")
    xml = etree.XML(req_raw.content, parser=xml_parser)
    metadata = xml.xpath("//xlmns:metadata", namespaces=NSMAP)[0]
    app.logger.debug(f"Parsed XML: {pretty_xml(xml)}")

    # Get default values with CONSTRAINT_LEVEL
    filename = f"assets/{CONSTRAINT_LEVEL}_defaults.json"
    app.logger.debug(f"Reading rules file {filename}")
    defaults = read_json_file(filename)

    # ToDo: Exception handling with XPathEvalError and XPathSyntaxError
    # Iterate over paths and set default values if no value present
    for rule, value in defaults.items():
        path, attrib, ns = None, None, None

        app.logger.info(f"Ensuring rule '{path}'")
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
            app.logger.debug(f"Querying path '{path}'")
            el = metadata.xpath(path, namespaces=NSMAP)
            if len(el) == 0:
                el = add_element_xpath(metadata, path)
            else:
                app.logger.debug(f"Got element {el[0]}")
                el = el[0]

            app.logger.debug(f"Attributes at element are {el.attrib.keys()}")
            attrib_exists = any([attrib in a for a in el.attrib.keys()])
            if not attrib_exists:
                # Add namespace to attrib if needed
                if ns is not None:
                    attrib = "{" + NSMAP[ns] + "}" + attrib
                # Set attribute with default value
                app.logger.info(f"Setting attribute '{attrib}' to default '{value}'")
                el.set(attrib, value)
        else:
            # Element rule
            el = metadata.xpath(path, namespaces=NSMAP)
            if len(el) == 0:
                app.logger.debug(f"Path not found, adding")
                el = add_element_xpath(metadata, path)
            else:
                app.logger.debug(f"Found path. Got element {el[0]}")
                el = el[0]

            # Keep text if exist, otherwise use default
            if len(el.text) == 0:
                app.logger.info(f"Setting text to {value}")
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
    app.logger.debug(f"Added element {new}")
    return new


# ------------------------------------------------------------------------- #
# Web APIs
# ------------------------------------------------------------------------- #


@app.route("/health")
def health():
    """Minimal health check"""
    return jsonify({"stauts": "ok"})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET"])
def proxy(path):
    """Endpoint for harvesting"""

    query = str(request.query_string, "utf-8")
    valid_file = place_request(path, query)
    if valid_file is None:
        resp = make_response("<p>ERROR - Please contact info@aussda.at</p>", 500)
    else:
        resp = make_response(valid_file)
        resp.headers["Content-Type"] = "text/xml;charset=utf-8"
    return resp


# ------------------------------------------------------------------------- #
# Main
# ------------------------------------------------------------------------- #

if __name__ == "__main__":
    # WARNING: DO NOT RUN IN PRODUCTION.
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)
