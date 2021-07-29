#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2021/7/29 0029 下午 21:46 
# @Author : chang sir
# @File : __init__.py.py

from sasa import version
from sasa.api import run, train, test

import logging

__version__ = version.__version__

logging.getLogger(__name__).addHandler(logging.NullHandler())
