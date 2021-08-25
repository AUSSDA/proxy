# Proxy for Dataverse OAI-MPHt

This script ensures requests send by CESSDA's Data Catalogue can parse the the OAI files. It solves the problem of missing elements in Dataverse's OAI-MPH exports, and enables us to be compliant with the DDI profile set out by CESSDA by using setting defaults for any field that does not have a value.

The script validates the presence of paths or attributes defined as xpaths in the `assets/*_defaults.json` files. You can set the path and default values to whatever seems appropriate.

Be aware that setting values on a dataset level is not possible. If there are multiple datasets missing the _abstract_ element, the proxy will set the same default value for all.

There are different constraint levels defined by CESSDA, they are `mandatory`,`optional`, `recommended`. The proxy is setup to ensure the existence of `mandatory` fields by default. If you would like to also include other constraints, firstly set default values in the related `*_defaults.json` file and then set the constraint level in `app/proxy.py`.

We also provide a a small script `app/utils.py` that generates these files based on the profile xmls.


Installation
------------

We assume you have a running Dataverse 4.20 or later and that you have Python 3.8 installed.

clone
install dependencies
create contaj

1. Clone the repostiory somewhere. We recommend something like `/etc/dataverse`.
    ``` bash
    mkdir /etc/dataverse
    git clone https://github.com/aussda/proxy /etc/dataverse
    ```
2. Install Pipenv if not already present. For options see [here](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)
    ``` bash
    pip3 install pipenv
    ```
3. Install the dependencies
   ``` bash
    cd /etc/dataverse
    pipenv install
   ```
4. Create a cronjob that runs the script periodically
    ``` bash
    sudo crontab -e

    # Every day at 04:00 run the script. Output to logs
    * 4 * * *  pipenv run sudo python3 /etc/dataverse/proxy/app/main.py > etc/dataverse/proxy/cron.log 2>&1
    ```


Contact
-------

Archival Technologies at [AUSSDA](https://aussda.at)
