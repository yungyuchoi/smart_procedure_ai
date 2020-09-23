# Copyright 2018 Zinnotech, all rights reserved

import os

class Defaults(object):
    """Default parameters for a typical installation"""
    # database connection information
    DB_HOST = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'ai_test'
    DB_USER = os.getenv('USER', 'zinnotech')
    DB_ADMUSER = 'zinnotech'
