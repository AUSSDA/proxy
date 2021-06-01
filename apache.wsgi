#!/usr/bin/env python3

# Add current working dir to python path
import sys, os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)

# Import and start app
from app.proxy import app as application

# Generate secret key
import string, secrets
alphabet = string.ascii_letters + string.digits
application.secret_key = ''.join(secrets.choice(alphabet) for i in range(8))
