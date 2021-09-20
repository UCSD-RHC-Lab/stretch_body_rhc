#!/usr/bin/env python
from __future__ import print_function
import time
import stretch_body.robot as robot
import os, fnmatch
import subprocess
from colorama import Fore, Back, Style
import argparse
import stretch_body.hello_utils as hu
hu.print_stretch_re_use()


parser=argparse.ArgumentParser(description='Check that all robot hardware is present and reporting sane values')
args=parser.parse_args()
