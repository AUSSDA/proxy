# Proxy for Dataverse OAI-MPH

This script ensures [CESSDA's Data Catalogue](https://datacatalogue.cessda.eu/?publisher.publisher[0]=Austrian%20Social%20Science%20Data%20Archive%20%28AUSSDA%29) can request metadata from AUSSDA's Dataverse. It ensures the files are in correct [DDI profile structure](https://cmv.cessda.eu/documentation/profiles.html) so that data can be presented in [CESSDA's Datacatalogue](https://datacatalogue.cessda.eu/).


Dataverse exports its file metadata through [OAI exports](https://guides.dataverse.org/en/latest/admin/harvestserver.html). The proxy checks if elements (e.g. `nation`) and their attributes (e.g. `@abbr`) are present, and if they are not it adds default entries 

The proxy's configuration happens through `assets/defaults.json` and defined through [xpaths](https://de.wikipedia.org/wiki/XPath)). By default the proxy is setup to ensure the existence `mandatory` profile elements and attributes are present. **You have to populate the default file with paths and default values**. These values will be visible at the Data Catalogue. The proxy also **puts the DOI links of the file in the correct element** so that they are visible in the datacatalogue.

Be aware that setting specific metadata on a dataset is not possible. If there are multiple datasets missing the _abstract_ element, the proxy will set the same default value for all. You cannot define abstract `A` for one datafile and abstract `B` for another datafile, they will have the same abstract. 

Generating defaults
-------------------

We also provide a a small script `assets/gen_defaults.py` that generates these files based on the DDI profile XML. Please see [CESSDA's profile documentation](https://cmv.cessda.eu/profiles/cdc/ddi-2.5/1.0.4/profile-mono.xml) on how to populate these values.

```
$ python3 assets/gen_defaults.py --help
usage: gen_defaults.py [-h] [-c CONSTRAINT] [-p PROFILE]

Creates a json file for each field/attribute per constraint level

optional arguments:
  -h, --help            show this help message and exit
  -c CONSTRAINT, --constraint CONSTRAINT
                        Mandatory, recommended, optional constraint level
  -p PROFILE, --profile PROFILE
                        The location of the file to parse

```

For example to process the `cdc25_profile.xml` and to pass the mandatory and recommended constraints, run this command:

```bash
$ python3 assets/gen_defaults.py -c Mandatory -c Recommended 
```

You should now have an empty `defaults.json` file

```bash
$ cat assets/defaults.json 
{
  "/codeBook/@xml:lang": "",
  "/codeBook/@xsi:schemaLocation": "",
  "/codeBook/stdyDscr/citation/titlStmt/titl": "",
  "/codeBook/stdyDscr/citation/titlStmt/IDNo": "",
  "/codeBook/stdyDscr/citation/titlStmt/IDNo/@agency": "",
  "/codeBook/stdyDscr/citation/holdings/@URI": "",
  "/codeBook/stdyDscr/citation/rspStmt/AuthEnty": "",
  "/codeBook/stdyDscr/citation/distStmt/distrbtr": "",
  "/codeBook/stdyDscr/citation/distStmt/distDate/@date": "",
  "/codeBook/stdyDscr/stdyInfo/subject/keyword": "",
  "/codeBook/stdyDscr/stdyInfo/subject/keyword/@vocab": "",
  "/codeBook/stdyDscr/stdyInfo/subject/topcClas": "",
  "/codeBook/stdyDscr/stdyInfo/subject/topcClas/@vocab": "",
  "/codeBook/stdyDscr/stdyInfo/subject/topcClas/@vocabURI": "",
  "/codeBook/stdyDscr/stdyInfo/abstract": "",
  "/codeBook/stdyDscr/stdyInfo/sumDscr/collDate/@event": "",
  "/codeBook/stdyDscr/stdyInfo/sumDscr/collDate/@date": "",
  "/codeBook/stdyDscr/stdyInfo/sumDscr/nation": "",
  "/codeBook/stdyDscr/stdyInfo/sumDscr/nation/@abbr": "",
  "/codeBook/stdyDscr/stdyInfo/sumDscr/anlyUnit": "",
  "/codeBook/stdyDscr/stdyInfo/sumDscr/anlyUnit/concept": "",
  "/codeBook/stdyDscr/stdyInfo/sumDscr/anlyUnit/concept/@vocab": "",
  "/codeBook/stdyDscr/method/dataColl/timeMeth": "",
  "/codeBook/stdyDscr/method/dataColl/timeMeth/concept/@vocab": "",
  "/codeBook/stdyDscr/method/dataColl/sampProc/concept/@vocab": "",
  "/codeBook/stdyDscr/method/dataColl/collMode": "",
  "/codeBook/stdyDscr/method/dataColl/collMode/concept/@vocab": "",
  "/codeBook/stdyDscr/dataAccs/useStmt/restrctn": "",
  "/codeBook/fileDscr/fileTxt/fileName": ""
}
```

Installation
------------

We assume you have a running **Dataverse 4.20** or later and that you have **Python 3.8** or later installed.

1. Clone the repostiory somewhere. We recommend something like `/etc/dataverse`.
    ``` bash
    mkdir /etc/dataverse
    git clone https://github.com/aussda/proxy /etc/dataverse
    ```
2. Install requirements
    ``` bash
    pip3 install -r /etc/dataverse/proxy/requirements.txt
    ```
4. Create a cronjob that runs the script periodically
    ``` bash
    sudo crontab -e

    # Every day at 04:00 run the script.
    0 4 * * * /usr/bin/su - dataverse -c 'python3 /etc/dataverse/proxy/app/main.py'
    ```

Note that Dataverse [automatically generates metadata exports](https://guides.dataverse.org/en/5.6/admin/metadataexport.html) daily, so we need to run the script daily as well. If you would like to **revert the changes**, you will need to delte all existing exports and request a `reExportAll`.

Configuration page
------------------

You can create a simple, more user friendly `.html` page that shows the proxy's configuraton. Simply run:

``` bash
python3 public/gen_report.py
```



Contribution and contact
-------------------------

We are happy for any pull requests! 

You can reach Archival Technologies at [AUSSDA](https://aussda.at)
