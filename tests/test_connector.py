"""
Tests for Connector Methods
"""

import os
import unittest
from io import BytesIO, StringIO
import pandas as pd
from source.connector import Connector

class TestConnectorMethods(unittest.TestCase):
    """
    Testing the S3BUcketConnector class
    """
    