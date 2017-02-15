#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests


def short(url):
    short_url = requests.get(
        "http://is.gd/create.php",
        {"format": "simple", "url": url}
    )
    return short_url.content.decode("utf-8")
