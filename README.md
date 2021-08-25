# Proxy for Dataverse OAI-MPHt

A small man-in-the-middle script for Dataverse.

It ensures requests send by a harvesting client, such as CESSDA's Data Catalogue can parse the
files. It solves the problem of missing elements in Dataverse's OAI-MPH exports,
and enables us to be compliant with the DDI profile set out by CESSDA by using setting defaults for
any field that does not have a value.

Fundamentally, the proxy validates the presence of paths or attributes defined as xpaths in the
`assets/*_defaults.json` files. You can set the path and default values to whatever seems appropriate.

Be aware that setting values on a dataset level is not possible. That is, if there are multiple
datasets missing the _abstract_ element, the proxy will set the same default value for all.

We are considering a feature whereby we simply add a reference URL to the original dataset instead
of having values that do not mean anything.

There are different constraint levels defined by CESSDA, they are `mandatory`, `optional`, `recommended`.
The proxy is setup to ensure the existence of `mandatory` fields by default. If you would like
to also include other constraints, firstly set default values in the related `*_defaults.json` file
and then set the constraint level in `app/proxy.py`.

We also provide a a small script `app/utils.py` that generates these files based on the profile xmls.

/usr/local/glassfish4/glassfish/domains/domain1/files/**/export_ddi.cached

Installation
------------

We assume you have a running Dataverse 4.20 or later and that you have Python 3.8 installed.

clone
install dependencies
create contaj

1. Install Pipenv. For options see [here](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)
    ``` bash
    pip3 install pipenv
    ```
5. Create a cronjob
    ``` bash
    sudo crontab -e

    # Every day at 04:05 run the script
    5 4 * * * /usr/bin/python3 /opt/proxy/app/main.py
    ```
pipenv run sudo python3 app/main.py


Contact
-------

Archival Technologies at [AUSSDA](https://aussda.at)
