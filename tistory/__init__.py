#!/usr/bin/env python3

import json
import os
from shlex import quote as shlex_quote

from tistory.api import Tistory
from tistory.auth import TistoryOAuth2

def load_config(fname):
    fname = shlex_quote(fname)
    cf_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(cf_path, '../config/', fname)

    with open(config_path) as data:
        config = json.loads(data.read())

    return config

if __name__ == "__main__":
    pass