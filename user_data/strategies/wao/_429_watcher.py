import time
import watchdog.events
import watchdog.observers
import os
from pathlib import Path
from wao.brain_config import BrainConfig
from commons.notifier import Notifier


class _429_Watcher(watchdog.events.PatternMatchingEventHandler):

    def __init__(self):
        watchdog.events.PatternMatchingEventHandler.__init__(self,
                                                             ignore_directories=True, case_sensitive=False)

    def on_created(self, event):
        file = str(event.src_path)
        if os.path.isfile(file):
            content = Path(file).read_text()
            time.sleep(1)  # this sleep makes the watcher wait to avoid overlapping
            print("sending message on: "+str(content))
            notifier = Notifier(BrainConfig.MODE)
            notifier.post_request(str(content))

    # def on_modified(self, event):
    #     print("_429_Watcher:on_modified: file name = " + str(event.src_path))
