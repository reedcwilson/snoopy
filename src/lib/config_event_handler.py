#!/usr/local/env python

from watchdog.events import PatternMatchingEventHandler


class ConfigFileEventHandler(PatternMatchingEventHandler):
    def __init__(self, notifier, config_dir, service_dir, config_filename):
        self.notifier = notifier
        self.config_dir = config_dir
        self.service_dir = service_dir
        self.config_filename = config_filename
        PatternMatchingEventHandler.__init__(
            self,
            patterns=["*{}*".format(self.config_filename)],
            ignore_directories=True)

    def on_any_event(self, event):
        message = """The config file has been tampered with:
        file: {}""".format(event.src_path)
        self.notifier.send(
            subject="Alert!",
            message=message)
        config = ""
        local_config_file = '{}/{}'.format(
            self.config_dir,
            self.config_filename)
        runtime_config_file = '{}/{}'.format(
            self.service_dir,
            self.config_filename)
        with open(local_config_file, 'r') as f:
            config = f.read().replace("%INSTALL_DIR%", self.config_dir)
        with open(runtime_config_file, 'w') as f:
            f.write(config)
