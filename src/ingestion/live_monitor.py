import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from src.nlp.log_parser import extract_entities
from src.xai.model_engine import analyze_events

WATCH_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw_logs"))

# Add a global cooldown timer
last_triggered = 0

class LogFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_triggered
        current_time = time.time()
        
        # Only trigger if it's a file and at least 2 seconds have passed since the last trigger
        if not event.is_directory and (current_time - last_triggered) > 2.0:
            last_triggered = current_time
            print(f"\n🚨 EVIDENCE SAVED: {os.path.basename(event.src_path)}")
            time.sleep(1)
            parsed_data = extract_entities(event.src_path)
            if parsed_data:
                analyze_events(parsed_data)

def start_listening():
    os.makedirs(WATCH_DIRECTORY, exist_ok=True)
    event_handler = LogFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIRECTORY, recursive=False)
    observer.start()
    
    print(f"👀 Live Monitor active! Listening for incoming logs at:\n{WATCH_DIRECTORY}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitor stopped.")
    observer.join()

if __name__ == "__main__":
    start_listening()