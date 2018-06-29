# coding=utf-8
from __future__ import absolute_import
import re
import octoprint.plugin
import os

class EmergencyStopPlugin(octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
                       octoprint.plugin.EventHandlerPlugin,
                       octoprint.plugin.OctoPrintPlugin):

    def powerOff(self):
        script=self._settings.get(["powerOffCmd"])
        self._logger.info("Run power off script \"%s\"" % script)
        os.system(script)

    def powerOn(self):
        script=self._settings.get(["powerOnCmd"])
        self._logger.info("Run power on script \"%s\"" % script)
        os.system(script)

    def on_after_startup(self):
        self._logger.info("Starting...")


    def get_settings_defaults(self):
        return dict(enabled="False",
            powerOffCmd="/home/pi/powerOff.sh",
            powerOnCmd="/home/pi/powerOn.sh",
            powerOffPrinterInputRegex="Error",
            powerOnEventRegex="Connecting",
            powerOffEventRegex="(Disconnected|PrintFailed|PowerOff|EStop|PrintCancelling|Error|Shutdown)")

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
            dict(type="settings", custom_bindings=False)
        ]

    def isEnabled(self):
        return str(self._settings.get(["enabled"]))=="True"

    def parse_firmware_line(self, comm, line, *args, **kwargs):
        if not self.isEnabled():
            return line

        if len(self._settings.get(["powerOffPrinterInputRegex"])) > 0:
            regex=re.compile(self._settings.get(["powerOffPrinterInputRegex"]))
            if regex.search(line) != None:
                self._logger.info("Printer input matches to %s --> poweroff" % self._settings.get(["powerOffPrinterInputRegex"]))
                self.powerOff()
        return line

    def get_assets(self):
        return dict(
            js=["js/emergencystopplugin.js"],
            css=["css/emergencystopplugin.css"],
            less=["less/emergencystopplugin.less"]
        )

    def on_event(self, event, payload):
        if not self.isEnabled():
            return

        if len(self._settings.get(["powerOffEventRegex"])) > 0:
            regex=re.compile(self._settings.get(["powerOffEventRegex"]))
            if regex.search(event) != None:
                self._logger.info("Event matches to %s --> powerOff" % self._settings.get(["powerOffEventRegex"]))
                self.powerOff()
        if len(self._settings.get(["powerOnEventRegex"])) > 0:
            regex=re.compile(self._settings.get(["powerOnEventRegex"]))
            if regex.search(event) != None:
                self._logger.info("Event matches to %s --> powerOn" % self._settings.get(["powerOnEventRegex"]))
                self.powerOn()

__plugin_name__ = "EmergencyStopPlugin"
__plugin_implementation__ = EmergencyStopPlugin()
__plugin_hooks__ = {"octoprint.comm.protocol.gcode.received": __plugin_implementation__.parse_firmware_line}
