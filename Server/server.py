import atexit
import configparser
import glob
import json
import logging
import os
import shutil
import threading
import time
import tkinter as tk
import tkinter.ttk as ttk
from io import StringIO
from pathlib import Path, WindowsPath
from tkinter import font

import astroplan
import numpy as np
import tksheet
from astropy import coordinates as coord
from astropy import table
from astropy import time as astrotime
from astropy import units as u
from astroquery import mpc

import logging
import os
import platform
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

class pyObsServer:
    def __init__(self, serverHome="./", **kwargs):
        # Private attributes
        self._config = configparser.ConfigParser(allow_no_value=True)
        self._execution_thread = None
        self._status_log_thread = None
        self._wcs_threads = []
        self._execution_event = threading.Event()
        self._status_event = threading.Event()
        self._status_log_update_event = threading.Event()

        """ Create config files under config path 
        self._config_path = self._telhome / "config"
        self._schedules_path = self._telhome / "schedules"
        self._images_path = self._telhome / "images"
        self._logs_path = self._telhome / "logs"
        self._temp_path = self._telhome / "tmp"
        """

        """ Read from config to create User objects """ 
        """ Read from config to create observables list. """
        """ Read from config to create Sites """
        """ Create observatories under sites and so on """
        """ Update external info like MPC and alerts. """
        """ Unit test to check access to all devices is as expected. """
        """ Create a schedule based on lat and long of all available observatories. """
        """ Execute the schedule """
        
        """ Execute the Server listener & dispatch handlers for calls """
        


    def readConfig(self )
        """ Read the config 

    

