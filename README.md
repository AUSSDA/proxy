# Proxy for Dataverse OAI-MPH

A small man-in-the-middle script for Dataverse 4.20.

It acts as mediator between requests send by a harvesting client, such as CESSDA's Data Catalogue, and
Dataverse's OAI-MPH endpoint. It solves the problem of missing elements in Dataverse's OAI-MPH exports,
and enables us to be compliant with the DDI profile set out by CESSDA by using setting defaults for
any field that does not have a value.

Fundamentally, the proxy validates the pressence of paths or attributes defined as xpaths in the
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


Installation
------------

We assume you have a running Dataverse installation. Be aware
that this script has only been tested with Dataverse 4.20. You should have a running Apache server.

1. Install `mod_wsgi`

    ``` bash
     sudo apt-get install libapache2-mod-wsgi-py3 python3 python3-pip
    ```
2. Clone this repo and install the app. We recommend putting it into `/var/www`
   ``` bash
     git clone https://github.com/aussda/proxy /var/www/
     cd /var/www/
     pip3 install -e .
   ```
3. Create a new site in Apache
   ``` bash
    sudo nano /etc/apache2/sites-available/proxy.conf
   ```
4. Edit the following example config and paste it into the config file created the last step.
    ```
    <VirtualHost *:80>
            ServerName proxy.aussda.at
            ServerAdmin info@aussda.at
            WSGIScriptAlias / /var/www/proxy/apache.wsgi
            LogLevel warn
            ErrorLog ${APACHE_LOG_DIR}/proxy-error.log
            CustomLog ${APACHE_LOG_DIR}/proxy-access.log combined
    </VirtualHost>
    <VirtualHost *:443>
            ServerName proxy.aussda.at
            ServerAdmin info@aussda.at
            WSGIScriptAlias / /var/www/proxy/apache.wsgi
            LogLevel warn
            ErrorLog ${APACHE_LOG_DIR}/proxy-error.log
            CustomLog ${APACHE_LOG_DIR}/proxy-access.log combined
    </VirtualHost>
    ```
5. Enable the site and reload apache
    ``` bash
        sudo a2ensite proxy
        sudo service apache2 reload
    ```

Contact
-------

Archival Technologies at [AUSSDA](https://aussda.at)
