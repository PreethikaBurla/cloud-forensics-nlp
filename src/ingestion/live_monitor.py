import time
import os
# Swap standard Observer for the cloud-friendly PollingObserver
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

from src.nlp.log_parser import extract_entities
from src.xai.model_engine import analyze_events

WATCH_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw_logs"))

last_triggered = 0

class LogFileHandler(FileSystemEventHandler):
    # Use on_any_event to ensure we catch drops on cloud network drives
    def on_any_event(self, event):
        global last_triggered
        current_time = time.time()
        
        if not event.is_directory and event.event_type in ('created', 'modified') and (current_time - last_triggered) > 2.0:
            last_triggered = current_time
            print(f"\n🚨 CLOUD EVIDENCE DETECTED: {os.path.basename(event.src_path)}")
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
    
    print(f"👀 Live Cloud Monitor active! Listening for incoming logs at:\n{WATCH_DIRECTORY}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitor stopped.")
    observer.join()

if __name__ == "__main__":
    start_listening()