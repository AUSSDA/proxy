# Proxy for Dataverse OAI-MPH

This script ensures [CESSDA's Data Catalogue](https://datacatalogue.cessda.eu/?publisher.publisher[0]=Austrian%20Social%20Science%20Data%20Archive%20%28AUSSDA%29) can request OAI files from AUSSDA's Dataverse.


Setup
-----

The checks if paths or attributes are present. It adds default entries for any missing element in [Dataverse's OAI exports](https://guides.dataverse.org/en/latest/admin/harvestserver.html), and enables AUSSDA to be compliant with the constraints of the DDI profile defined by CESSDA. These are defined as [xpath](https://de.wikipedia.org/wiki/XPath) in the `assets/*_defaults.json` files.

The `assets/*_defaults.json` files relate to the different constraint levels defined by CESSDA - they are `mandatory`,`optional`, `recommended`. By default the proxy is setup to ensure the existence of `mandatory` field. **You have to populate `assets/mandatory_defaults.json` with default values**. These values will be visible at the Data Catalogue. 

If you want to enable another constraint level, simply edit CONSTRAINT_LEVEL in `app/proxy.py` (line 31). If you would like to add other, custom metadata fields in the export, create a new file named `assets/custom_defaults.json`, add xpaths and set default values.

Be aware that setting values on a dataset level is not possible. If there are multiple datasets missing the _abstract_ element, the proxy will set the same default value for all. You cannot define abstract `A` for one datafile and abstract `B` for another datafile.

Generating defaults
-------------------

We also provide a a small script `app/utils.py` that generates these files based on the profile xmls. It generatex xpaths from an DDI profile.

```
$ python3 app/utils.py --help
usage: utils.py [-h] [-c CONSTRAINT] [-p PROFILE]

Creates a json file for each field/attribute per constraint level

optional arguments:
  -h, --help            show this help message and exit
  -c CONSTRAINT, --constraint CONSTRAINT
  -p PROFILE, --profile PROFILE
```

For example to process the `cdc25_profile.xml`, run this command to generate a `mandatory_defaultsl.json`

```bash
$ python3 app/utils.py -p assets/cdc25_profile_mono.xml 
```

You should now have an empty `mandatory_defaultsl.json` file

```bash
$ cat assets/mandatory_defaults.json 
{
  "/codeBook/@xml:lang": "",
  "/codeBook/@xsi:schemaLocation": "",
  "/codeBook/stdyDscr/citation/titlStmt/titl": "",
  "/codeBook/stdyDscr/citation/titlStmt/IDNo": "",
  "/codeBook/stdyDscr/citation/titlStmt/IDNo/@agency": "",
  "/codeBook/stdyDscr/citation/holdings/@URI": "",
  "/codeBook/stdyDscr/citation/distStmt/distrbtr": "",
  "/codeBook/stdyDscr/citation/distStmt/distDate/@date": "",
  "/codeBook/stdyDscr/stdyInfo/abstract": "",
  "/codeBook/stdyDscr/stdyInfo/sumDscr/collDate/@event": ""
}%                                                                                                                                                    

```

Installation
------------

We assume you have a running Dataverse 4.20 or later and that you have Python 3.8 installed.

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
    * 4 * * * /usr/bin/su - dataverse -c 'sh /etc/dataverse/proxy/run'
    ```


Contact
-------

Archival Technologies at [AUSSDA](https://aussda.at)
