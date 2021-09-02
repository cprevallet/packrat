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
    def onDestroy(self, *args):
        Gtk.main_quit()

    def onButtonPressed(self, button):
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
            client = Garmin(uname, pw)
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
        print("client.login()")
        print("----------------------------------------------------------------------------------------")
        try:
            client.login()
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

        """
        Get activities data
        """
        print("client.get_activities(0,1)")
        print("----------------------------------------------------------------------------------------")
        try:
            activities = client.get_activities(5,2) # 0=start, 1=limit
            #startTime = datetime.datetime(2021, 8, 30, 0, 0)
            #endTime = datetime.datetime(2021, 9, 1, 23, 59)
            """
            Payment required.  Grr....
            """
            #activities = client.get_activities_by_date(startTime.isoformat(timespec='milliseconds'), endTime.isoformat(timespec='milliseconds'), None)
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

        """
        Download an Activity
        """
        try:
            for activity in activities:
                activity_id = activity["activityId"]
                print("client.download_activities(%s)", activity_id)
                print("----------------------------------------------------------------------------------------")
                zip_data = client.download_activity(activity_id, dl_fmt=client.ActivityDownloadFormat.ORIGINAL)
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
password.set_visibility(False)
cal1 = builder.get_object("cal1")

window.show_all()

Gtk.main()

