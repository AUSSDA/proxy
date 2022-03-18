#!/usr/bin/env python3

import json
import datetime

from lxml import etree

# Assume run from root directory

PROFILE = "assets/cdc25_profile_mono.xml"
DEFAULTS = "assets/defaults.json"
REPORT = "public/index.html"


def write_head():
    return """<!doctype html>
    <html class="no-js" lang="en">
    <head>
        <meta charset="utf-8">
        <title>Proxy</title>
        <style>
            body {
                margin: 20px auto;
                line-height: 1.6;
                font-size: 18px;
                color: #444;
                padding: 0 10px
            }

            h1 {
                line-height: 1.2
            }

            table {
                font-family: arial, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }

            td,
            th {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
                word-wrap: break-word;
            }

            tr:nth-child(even) {
                background-color: #dddddd;
            }

            .descr {
                margin-bottom: 25px;
                word-wrap: break-word;
            }
        </style>
    </head>
    """


def write_body_start():
    return """<body>
    <header><h1>Proxy Configuration</h1></header>
    <div class="descr">
        For further information see <a href="https://github.com/aussda/proxy">here</a>.
    </div>
    <table>
    <thead><tr>
        <th style="width:30%">XPath</th>
        <th style="width:30%">Value</th>
        <th>Constraint</th>
        <th>UI Label</th>
        <th>Type</th>
        <th>Usage note</th>
    </tr></thead>
    <tbody>
    """


def table_row(
    xpath: str, value: str, constraint: str, ui_label: str, ctype: str, notes: str
):
    return f"""<tr>
        <td class="wrap">{xpath}</td>
        <td>{value}</td>
        <td>{constraint}</td>
        <td>{ui_label}</td>
        <td>{ctype}</td>
        <td>{notes}</td>
    </tr>
    """


def write_table(j, l):
    # Iterate over config and profile info
    table = ""
    for k, v in j.items():
        for x in l:
            if x["xpath"] == k:
                constraint = x["Required"] if "Required" in x else "n/a"
                ui_label = x["CDC UI Label"] if "CDC UI Label" in x else "n/a"
                ctype = x["ElementType"] if "ElementType" in x else "n/a"
                notes = x["Usage"] if "Usage" in x else "n/a"
                table += table_row(
                    xpath=k,
                    value=v,
                    constraint=constraint,
                    ui_label=ui_label,
                    ctype=ctype,
                    notes=notes,
                )
    return table


def write_body_end():
    return f"""</tbody>
    </table>
    <p><i>Modified: {datetime.datetime.now()}</i></p>
    </body>
    </html>
    """


def main():
    # Parse file as xml
    xml_parser = etree.XMLParser(
        remove_blank_text=True,
        remove_comments=True,
        load_dtd=True,
        attribute_defaults=True,
        ns_clean=True,
    )

    # CESSDA DDI profile
    profile = etree.parse(PROFILE, parser=xml_parser)
    profile_nsmap = profile.getroot().nsmap
    profile_rules = profile.findall("//pr:Used", namespaces=profile_nsmap)

    # Get rules, description and other info from profle
    l = []
    for rule in profile_rules:
        d = {}
        d["xpath"] = rule.values()[0]
        descr = rule.getchildren()[0]
        for field in descr.itertext():
            if ": " in field:
                key, val = field.split(": ", 1)
                val = val.replace("\n                ", " ")
                d[key] = val
        l.append(d)

    # Get proxy's config
    with open(DEFAULTS, "r") as f:
        j = json.load(f)

    # Create html page
    with open(REPORT, "w") as f:
        f.write(write_head())
        f.write(write_body_start())
        f.write(write_table(j, l))
        f.write(write_body_end())


if __name__ == "__main__":
    main()
