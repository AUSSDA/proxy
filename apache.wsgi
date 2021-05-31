#!/usr/bin/env python3

# Add current working dir to python path
import sys, os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

import logging, string, secrets
from app.proxy import app as application

# Log to stderr
logging.basicConfig(stream=sys.stderr)

# Generate secret key
alphabet = string.ascii_letters + string.digits
application.secret_key = ''.join(secrets.choice(alphabet) for i in range(8))
