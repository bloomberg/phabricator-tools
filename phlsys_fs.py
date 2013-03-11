#!/usr/bin/env python
# encoding: utf-8
"""Helpers for interacting with the filesystem."""

from contextlib import contextmanager
import os


#TODO: write a docstring with doctests when we have a tempdir helper
@contextmanager
def chDirContext(newDir):
    savedPath = os.getcwd()
    os.chdir(newDir)
    try:
        yield
    finally:
        os.chdir(savedPath)
