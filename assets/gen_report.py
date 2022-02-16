#!/usr/bin/env python3

"""Quick and dirty script to generate a html that shows the proxy configuration"""

import json
import datetime

from lxml import etree

def head() -> str:
    return """
    <!doctype html>
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
        </style>
    </head>
    """

def body_start() -> str:
    return """
    <body>
    <header><h1>Proxy Configuration</h1></header>
    XPath: Location of element in file <br/>
    Value: The value visible in data catalogue<br/>
    Constraint: Is the field required, mandatory, optional <br/>
    UI Label: The name of the field in data catalogue<br/>
    <br/>
    <table>
    <thead><tr>
        <th>XPath</th>
        <th>Value</th>
        <th>Constraint</th>
        <th>UI Label</th>
        <th>Type</th>
        <th>Usage note</th>
    </tr></thead>
    <tbody>
    """

def table_row(xpath: str, value: str, constraint: str, ui_label: str, ctype: str, notes: str) -> str:
    return f"""
    <tr>
        <td class="wrap">{xpath}</td>
        <td>{value}</td>
        <td>{constraint}</td>
        <td>{ui_label}</td>
        <td>{ctype}</td>
        <td>{notes}</td>
    </tr>
    """

def body_end() -> str:
    return f"""
    </tbody>
    </table>
    <p><i>Modified: {datetime.datetime.now()}</i></p>
    </body>
    </html>
    """

profile = "cdc25_profile_mono.xml"

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

with open("defaults.json", "r") as f:
    j = json.load(f)

with open("report.html", "w") as f:
    f.write(head())
    f.write(body_start())
    for k, v in j.items():
        for x in l:
            if x["xpath"] == k:
                constraint = x["Required"] if "Required" in x else "n/a"
                ui_label = x["CDC UI Label"] if "CDC UI Label" in x else "n/a"
                ctype = x["ElementType"] if "ElementType" in x else "n/a"
                notes = x["Usage"] if "Usage" in x else "n/a"
                f.write(table_row(xpath=k, value=v, constraint=constraint, ui_label=ui_label, ctype=ctype, notes=notes))
    f.write(body_end())
