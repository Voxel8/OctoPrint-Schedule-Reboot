# coding=utf-8
from __future__ import absolute_import

import os
from time import sleep
from threading import Thread
import octoprint.plugin
from octoprint.events import eventManager, Events
import flask

Events.SCHEDULE_REBOOT_EVENT = "ScheduleReboot"


class Schedule_rebootPlugin(octoprint.plugin.SimpleApiPlugin):

    def __init__(self):
        self.remaining = None

    def get_api_commands(self):
        return dict(
            schedule_reboot=[],
            cancel=[],
            reboot_now=[]
        )

    def on_api_command(self, command, data):
        log_msg = None
        if command == "schedule_reboot":
            self._logger.info("Scheduling reboot...")
            self.initial_check()

        elif command == "cancel":
            log_msg = "Scheduled reboot cancelled, trying again in 60 minutes"
            self._logger.info(log_msg)
            self._cancel_reboot = True
            self.schedule_reboot(3600)

        elif command == "reboot_now":
            log_msg = "Reboot called immediately"
            self._logger.info(log_msg)
            os.system('sudo reboot')

    def on_api_get(self, request):
        return flask.jsonify(duration=self.remaining)

    def printer_is_printing(self):
        return self._printer.is_printing() or self._printer.is_paused()

    def initial_check(self):
        if not self.printer_is_printing():
            log_msg = "Printer not in use, rebooting in 60 seconds"
            self._logger.info(log_msg)
            self.initiate_reboot(60)
        else:
            log_msg = "Printer in use, will try again in 60 minutes"
            self._logger.info(log_msg)
            self.schedule_reboot(3600)

    def initiate_reboot(self, secs_from_now):
        """ Reboot machine in secs_from_now seconds, unless cancelled.
        """
        # Only initiate a reboot if there isn't another one running
        if self.remaining is None:
            self._cancel_reboot = False
            self._reboot_thread = Thread(target=self._reboot_worker,
                                         args=(secs_from_now,))
            self._reboot_thread.daemon = True
            self._reboot_thread.start()
            payload = {'duration': secs_from_now}
            eventManager().fire(Events.SCHEDULE_REBOOT_EVENT, payload)
        else:
            self._logger.info(
                "Warning: Reboot scheduled while one already queued")

    def schedule_reboot(self, secs_from_now):
        """ Initiate a reboot in the future,
        """
        self._future_reboot_thread = Thread(target=self._future_reboot,
                                            args=(secs_from_now,))
        self._future_reboot_thread.daemon = True
        self._future_reboot_thread.start()

    def _reboot_worker(self, secs_from_now):
        self.remaining = secs_from_now
        while (not self._cancel_reboot) and self.remaining > 0:
            self.remaining -= 1
            sleep(1)
            if not self._cancel_reboot:
                payload = {'duration': self.remaining}
                eventManager().fire(Events.SCHEDULE_REBOOT_EVENT, payload)
        if not self._cancel_reboot:
            if not self.printer_is_printing():
                self._logger.info("Executing reboot...")
                os.system('sudo reboot')
            else:
                self._logger.info("Printer in use, will try again in 60 "
                                  "minutes")
                self.remaining = None
                self.schedule_reboot(3600)
        else:
            self.remaining = None
            self._logger.info("Reboot thread aborted")

    def _future_reboot(self, secs_from_now):
        sleep(secs_from_now)
        self.initial_check()

__plugin_name__ = "Schedule Reboot"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Schedule_rebootPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {}
