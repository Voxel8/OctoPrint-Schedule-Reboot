# coding=utf-8
from __future__ import absolute_import

from time import sleep
from threading import Thread
import os

import octoprint.plugin

class Schedule_rebootPlugin(octoprint.plugin.SettingsPlugin,
                            octoprint.plugin.AssetPlugin,
                            octoprint.plugin.SimpleApiPlugin,
                            octoprint.plugin.TemplatePlugin):

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            # put your plugin's default settings here
        )

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            #js=["js/schedule_reboot.js"],
            #css=["css/schedule_reboot.css"],
            #less=["less/schedule_reboot.less"]
        )

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            schedule_reboot=dict(
                displayName="Schedule Reboot",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_commit",
                user="voxel8",
                repo="OctoPrint-Schedule-Reboot",
                #current=self._plugin_version,

                # update method: pip
                pip="https://github.com/voxel8/OctoPrint-Schedule-Reboot/archive/{target_version}.zip"
            )
        )

    ##~~ SimpleApiPlugin mixin

    def get_api_commands(self):
        return dict(
            schedule_reboot=[],
            cancel=[],
        )

    def on_api_command(self, command, data):

        if command == "schedule_reboot":
            self._logger.info("Scheduling reboot...")
            if not self.printer_is_printing():
                self._logger.info("Printer not in use, rebooting in 60 seconds")
                self.initiate_reboot(60)
            else:
                self._logger.info("Printer in use, will try again in 60 minutes")
                self.schedule_reboot(7200)

        elif command == "cancel":
            self._logger.info("Scheduled reboot cancelled, will try again in 60 minutes")
            self._cancel_reboot = True
            self.schedule_reboot(7200)

    #########################

    def printer_is_printing(self):
        return self._printer.is_printing() or self._printer.is_paused()

    def initiate_reboot(self, secs_from_now):
        """ Reboot machine in secs_from_now seconds, unless cancelled.
        """
        self._cancel_reboot = False
        self._reboot_thread = Thread(target=self._reboot_worker,
                                     args=(secs_from_now,))
        self._reboot_thread.start()

    def schedule_reboot(self, secs_from_now):
        """ Initiate a reboot in the future,
        """
        self._future_reboot_thread = Thread(target=self._future_reboot,
                                            args=(secs_from_now,))
        self._future_reboot_thread.start()

    def _reboot_worker(self, secs_from_now):
        remaining = secs_from_now
        while (not self._cancel_reboot) and remaining > 0:
            remaining -= 1
            sleep(1)
        if not self._cancel_reboot:
            os.system('sudo reboot now')
        else:
            self._logger.info("Reboot thread aborted")

    def _future_reboot(self, secs_from_now):
        sleep(secs_from_now)
        self.initiate_reboot(60)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Schedule Reboot"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Schedule_rebootPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

