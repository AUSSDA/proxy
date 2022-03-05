#!/usr/bin/env python3

import argparse
import json
import sys
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
    assert all(
        True for c in constraint if c in ["Mandatory", "Optional", "Recommended"]
    )
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
            for c in constraint:
                if f"Required: {c}" in field:
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

    filename = "assets/defaults.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def main(args) -> None:
    p = argparse.ArgumentParser(
        description="Creates a json file for each field/attribute per constraint level"
    )
    p.add_argument(
        "-c",
        "--constraint",
        action="append",
        help="Mandatory, recommended, optional constraint level",
    )
    p.add_argument(
        "-p",
        "--profile",
        default="assets/cdc25_profile_mono.xml",
        help="The location of the file to parse",
    )
    args = p.parse_args()
    gen_rules_defaults(constraint=args.constraint, profile=args.profile)


if __name__ == "__main__":
    main(sys.argv[1:])
