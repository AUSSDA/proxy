#!/usr/bin/env python3

"""
Util functions.

Mainly to generate the _default.json files. Run this as script.
"""

import sys
import argparse
import json

from os import path
from lxml import etree


def gen_rules(
    constraint: str = "Mandatory", profile: str = "assets/cdc25_profile_mono.xml"
) -> None:
    """
    Generator yielding all xpaths for specified constraint.

    Parameters:
    constraint (str): one of ["Mandatory", "Optional", "Recommended"]
    profile (str): local file name
    """

    # Ensure that parameters are valid
    assert constraint in ["Mandatory", "Optional", "Recommended"]
    assert path.isfile(profile)

    # Parse file as xml
    xml_parser = etree.XMLParser(
        remove_blank_text=True,
        remove_comments=True,
        load_dtd=True,
        attribute_defaults=True,
        ns_clean=True,
    )
    profile = etree.parse(profile, parser=xml_parser)
    # Namespaces so query can be placed
    profile_nsmap = profile.getroot().nsmap
    # Query all rules
    profile_rules = profile.findall("//pr:Used", namespaces=profile_nsmap)

    # Iterate over fields in rule, if constraint is there, return xpath
    for rule in profile_rules:
        for field in rule.itertext():
            if f"Required: {constraint}" in field:
                yield rule.attrib["xpath"]


def gen_rules_defaults(
    constraint: str = "Mandatory", profile: str = "assets/cdc25_profile_mono.xml"
) -> None:
    """
    Saves a json to the local filesystem
    """

    data = {}
    for rule in gen_rules(constraint, profile):
        data[rule] = ""

    filename = f"assets/{constraint.lower()}_defaults.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def main(args) -> None:
    p = argparse.ArgumentParser(
        description="Creates a json file for each field/attribute per constraint level"
    )
    p.add_argument("-c", "--constraint", type=str, default="Mandatory")
    p.add_argument("-p", "--profile", type=str, default="../assets/cdc25_profile_mono.xml")
    args = p.parse_args()

    gen_rules_defaults(constraint=args.constraint, profile=args.profile)


if __name__ == "__main__":
    main(sys.argv[1:])
