import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
import posixpath
import os.path


WATCH_DIR = "/Volumes/Code/main_service/"
DEST_DIR = "/home/jon/code/main_service/"
IGNORED = ['.idea', '.git']


def relevant(src):
    parts = src.split('/')

    if not os.path.exists(src):
        return False

    if os.path.isdir(src):
        return False

    for part in parts:
        if part in IGNORED:
            return False

    return True


def on_created(event):
    destination_path = event.src_path.replace(WATCH_DIR, '')
    if relevant(event.src_path):
        subprocess.run(["scp", event.src_path, "jon@pc.local:%s" % posixpath.join(DEST_DIR, destination_path)])


def on_deleted(event):
    destination_path = event.src_path.replace(WATCH_DIR, '')
    if relevant(event.src_path):
        subprocess.run(['ssh', 'jon@pc.local', 'rm %s' % posixpath.join(DEST_DIR, destination_path)])


def on_modified(event):
    destination_path = event.src_path.replace(WATCH_DIR, '')
    if relevant(event.src_path):
        subprocess.run(["scp", event.src_path, "jon@pc.local:%s" % posixpath.join(DEST_DIR, destination_path)])


def on_moved(event):
    on_deleted(event)
    destination_path = event.dest_path.replace(WATCH_DIR, '')
    if relevant(event.dest_path):
        subprocess.run(["scp", event.dest_path, "jon@pc.local:%s" % posixpath.join(DEST_DIR, destination_path)])


if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified
    my_event_handler.on_moved = on_moved
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, WATCH_DIR, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()