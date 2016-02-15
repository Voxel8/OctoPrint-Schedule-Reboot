/*
 * View model for OctoPrint-Schedule_reboot
 *
 * Author: Jack Minardi
 * License: AGPLv3
 */
$(function() {
    function Schedule_rebootViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.
    }

    // view model class, parameters for constructor, container to bind to
    OCTOPRINT_VIEWMODELS.push([
        Schedule_rebootViewModel,

        // e.g. loginStateViewModel, settingsViewModel, ...
        [ /* "loginStateViewModel", "settingsViewModel" */ ],

        // e.g. #settings_plugin_schedule_reboot, #tab_plugin_schedule_reboot, ...
        [ /* ... */ ]
    ]);
});
