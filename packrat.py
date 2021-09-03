#!/usr/bin/env python3

from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)

from datetime import date
import datetime

import zipfile
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

"""
Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
"""


class Handler:
    start = 0
    client = None
    activities = None 

    def onDestroy(self, *args):
        Gtk.main_quit()

    def _updateText(self, line):
        """
        Update the activities text buffer.
        """
        line = line + "\n"
        end_iter = textbuffer1.get_end_iter()
        textbuffer1.insert(end_iter, line, -1);

    def getActivities(self):
        """
        Get activities data
        """
        try:
            self.activities = self.client.get_activities(self.start,20) # 0=start, 1=limit
            for activity in self.activities:
                self._updateText(activity['startTimeLocal'] + ' ' + activity['activityName'])
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            self._updateText("Error occurred during Garmin Connect Client get activities: %s" % err)
        except Exception:  # pylint: disable=broad-except
            self._updateText("Unknown error occurred during Garmin Connect Client get activities")
        
        
    def onLoginPressed(self, button):
        uname = username.get_text()
        pw = password.get_text()
        self.start = 0
        self.activities = None
        """
        Initialize Garmin client with credentials
        Only needed when your program is initialized
        """
        if not self.client:
            try:
                self.client = Garmin(uname, pw)
            except (
                GarminConnectConnectionError,
                GarminConnectAuthenticationError,
                GarminConnectTooManyRequestsError,
            ) as err:
                self._updateText("Unable to log in: %s" % err)
            except Exception:  # pylint: disable=broad-except
                self._updateText("Unknown error occurred during Garmin Connect Client init")

        """
        Login to Garmin Connect portal
        Only needed at start of your program
        The library will try to relogin when session expires
        """
        self._updateText("Attempting login.")
        try:
            self.client.login()
            self._updateText("Login succeeded. ")
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            self._updateText("Error occurred during Garmin Connect Client login: %s" % err)
        except Exception:  # pylint: disable=broad-except
            self._updateText("Unknown error occurred during Garmin Connect Client login")
        self.getActivities()

    def onEarlierPressed(self, button):
        self.start = self.start + 20
        self.getActivities()

    def onLatestPressed(self, button):
        self.start = 0
        self.getActivities()

    def onSavePressed(self, button):
        """
        Download and save an Activity
        """
        try:
            self._updateText("Attempting download.")
            datestr = activityDate.get_text()
            for activity in self.activities:
                if activity['startTimeLocal'][0:10] == datestr:
                    activity_id = activity["activityId"]
                    start_time = activity["startTimeLocal"]
                    zip_data = self.client.download_activity(activity_id, dl_fmt=self.client.ActivityDownloadFormat.ORIGINAL)
                    self._updateText("Download succeeded.")
                    self._updateText("Unzipping download.")
                    output_file = str(activity_id) + '.zip'
                    with open(output_file, "wb") as fb:
                        fb.write(zip_data)
                    # Extract activity zip file.
                    with zipfile.ZipFile(output_file, 'r') as zip_ref:
                        zip_ref.extractall()
                    if os.path.exists(output_file):
                      os.remove(output_file)
                    else:
                      self._updateText("The file does not exist")
                    # WARNING next line assumes that zip contents are named activity_id_ACTIVITY.fit!!!!
                    oldfilename = str(activity_id) + '_ACTIVITY.fit'
                    # Bloody stupid Windows doesn't like spaces or colons in filenames.
                    newfilename = str(start_time).replace(' ', '_').replace(':', '-') + '.fit'
                    os.rename(oldfilename, newfilename)
                    self._updateText("Unzipping download succeeded.")

        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            self._updateText("Error occurred during Garmin Connect Client get activity data: %s" % err)
        except Exception:  # pylint: disable=broad-except
            self._updateText("Unknown error occurred during Garmin Connect Client get activity data")


builder = Gtk.Builder()
builder.add_from_file("packrat.glade")

window = builder.get_object("window1")
username = builder.get_object("username")
password = builder.get_object("password")
activityDate = builder.get_object("activityDate")
textbuffer1 = builder.get_object("textbuffer1")
password.set_visibility(False)

builder.connect_signals(Handler())

window.show_all()

Gtk.main()

