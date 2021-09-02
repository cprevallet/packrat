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
"""
import logging
logging.basicConfig(level=logging.DEBUG)


class Handler:

    client = None
    start = 0
    activities = None

    def onDestroy(self, *args):
        Gtk.main_quit()

    def onLoginPressed(self, button):
        uname = username.get_text()
        pw = password.get_text()
        """
        Enable debug logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        """

        today = date.today()


        """
        Initialize Garmin client with credentials
        Only needed when your program is initialized
        """
        print("Garmin(email, password)")
        print("----------------------------------------------------------------------------------------")
        try:
            self.client = Garmin(uname, pw)
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            print("Error occurred during Garmin Connect Client init: %s" % err)
            quit()
        except Exception:  # pylint: disable=broad-except
            print("Unknown error occurred during Garmin Connect Client init")
            quit()


        """
        Login to Garmin Connect portal
        Only needed at start of your program
        The library will try to relogin when session expires
        """
        print("self.client.login()")
        print("----------------------------------------------------------------------------------------")
        try:
            self.client.login()
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            print("Error occurred during Garmin Connect Client login: %s" % err)
            quit()
        except Exception:  # pylint: disable=broad-except
            print("Unknown error occurred during Garmin Connect Client login")
            quit()

    def onActivitiesPressed(self, button):
        """
        Get activities data
        """
        print(self.start)
        print("self.client.get_activities(start,1)")
        print("----------------------------------------------------------------------------------------")
        try:
            self.activities = self.client.get_activities(self.start,20) # 0=start, 1=limit
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            print("Error occurred during Garmin Connect Client get activities: %s" % err)
            quit()
        except Exception:  # pylint: disable=broad-except
            print("Unknown error occurred during Garmin Connect Client get activities")
            quit()
        self.start = self.start + 20
        for activity in self.activities:
            print (activity['startTimeLocal'], activity['activityName'])
            line = activity['startTimeLocal'] + ' ' + activity['activityName'] + '\n'
            cursor_mark = textbuffer1.get_insert()
            start_iter = textbuffer1.get_iter_at_mark(cursor_mark);
            textbuffer1.insert(start_iter, line, -1);


    def onDownloadPressed(self, button):
        """
        Download an Activity
        """
        try:
            print("self.client.download_activities")
            print("----------------------------------------------------------------------------------------")
            datestr = dlactivity.get_text()
            for activity in self.activities:
                if activity['startTimeLocal'][0:10] == datestr:
                    activity_id = activity["activityId"]
                    start_time = activity["startTimeLocal"]
                    print(activity_id)
                    zip_data = self.client.download_activity(activity_id, dl_fmt=self.client.ActivityDownloadFormat.ORIGINAL)
                    output_file = f"./{str(activity_id)}.zip"
                    with open(output_file, "wb") as fb:
                        fb.write(zip_data)
                    # Extract activity zip file.
                    with zipfile.ZipFile(output_file, 'r') as zip_ref:
                        zip_ref.extractall()
                    if os.path.exists(output_file):
                      os.remove(output_file)
                    else:
                      print("The file does not exist")
                    # WARNING next line assumes that zip contents are named activity_id_ACTIVITY.fit!!!!
                    os.rename(f"./{str(activity_id)}_ACTIVITY.fit", f"./{str(start_time)}.fit")

        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ) as err:
            print("Error occurred during Garmin Connect Client get activity data: %s" % err)
            quit()
        except Exception:  # pylint: disable=broad-except
            print("Unknown error occurred during Garmin Connect Client get activity data")
            quit()


builder = Gtk.Builder()
builder.add_from_file("connect.glade")
builder.connect_signals(Handler())

window = builder.get_object("window1")
username = builder.get_object("username")
password = builder.get_object("password")
dlactivity = builder.get_object("dlactivity")
textbuffer1 = builder.get_object("textbuffer1")
password.set_visibility(False)

window.show_all()

Gtk.main()

