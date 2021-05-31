# Proxy for Dataverse OAI-MPH

A small man-in-the-middle script for Dataverse 4.20.

It acts as mediator between requests send by a harvesting client, such as CESSDA's Data Catalogue, and
Dataverse's OAI-MPH endpoint.

This solves the problem of some missing elements in Dataverse's OAI-MPH exports, and enables compliance
with the DDI profile set out by CESSDA.

Fundamentally, the proxy validates the pressence of paths or attributes defined in the `assets/*_defaults.json` files. You can set the default values to whatever seems appropriate.

We also provide a a small script `app/utils.py` that generates these files based on the profile xml's.

Installation
------------

We assume you have a running Dataverse installation. Be aware
that this script has only been tested with Dataverse 4.20. You should have a running Apache server.

1. Install `mod_wsgi`

    ``` bash
     sudo apt-get install libapache2-mod-wsgi-py3 python3 python3-pip
    ```
2. Clone this repo and install the app. We recommend putting it into `/var/www`. If you do not want to put it there, you will need to edit `app/apache.wsgi`. You will also need to install all requirements.
   ``` bash
     git clone https://github.com/aussda/proxy /var/www/proxy
     cd /var/www/proxy
     pip3 install -r requirements.txt
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
            WSGIScriptAlias / /var/www/proxy/app/apache.wsgi
            LogLevel warn
            ErrorLog ${APACHE_LOG_DIR}/proxy-error.log
            CustomLog ${APACHE_LOG_DIR}/proxy-access.log combined
    </VirtualHost>
    <VirtualHost *:443>
            ServerName proxy.aussda.at
            ServerAdmin info@aussda.at
            WSGIScriptAlias / /var/www/proxy/app/apache.wsgi
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
