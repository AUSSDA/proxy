#!/usr/bin/env python3

import sys
import logging
import string
import secrets

from proxy import app as application

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/proxy/")

alphabet = string.ascii_letters + string.digits
application.secret_key = ''.join(secrets.choice(alphabet) for i in range(8))

