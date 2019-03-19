import logging

from watchdog.events import FileSystemEventHandler




class HasteFSEventHandler(FileSystemEventHandler):
    # Note: these methods are invoked not on the main thread!

    def __init__(self, callback):
        self.callback = callback

    def on_any_event(self, event):
        """Catch-all event handler.

        :param event:
            The event object representing the file system event.
        :type event:
            :class:`FileSystemEvent`
        """
        logging.debug(f'on_any_event {event}')

    def on_modified(self, event):
        """Called when a file or directory is modified.

        :param event:
            Event representing file/directory modification.
        :type event:
            :class:`DirModifiedEvent` or :class:`FileModifiedEvent`
        """

        # Under MacOSX -- doesn't seem to catch 'echo 'foo' > test-tmp/inner/foo5.txt'
        self.callback(event)

    def on_created(self, event):
        """Called when a file or directory is modified.

        :param event:
            Event representing file/directory modification.
        :type event:
            :class:`DirModifiedEvent` or :class:`FileModifiedEvent`
        """
        self.callback(event)
