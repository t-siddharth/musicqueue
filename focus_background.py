
import time
import win32gui
import win32process
import psutil


def get_active_window_info():
    """Get information about the currently active window."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return None, None
        
        # Get window title
        title = win32gui.GetWindowText(hwnd)
        
        # Get process name
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            process_name = process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            process_name = "Unknown"
        
        return title, process_name
    except Exception as e:
        print(f"Error getting window info: {e}")
        return None, None


def monitor_focus_changes(poll_interval=0.5):
    """Monitor for window focus changes and print when they occur.
    
    Args:
        poll_interval: Time in seconds between checks (default: 0.5)
    """
    print("Monitoring window focus changes... (Press Ctrl+C to stop)")
    
    last_title = None
    last_process = None
    
    try:
        while True:
            current_title, current_process = get_active_window_info()
            
            # Check if window has changed
            if (current_title != last_title or current_process != last_process):
                if last_title is not None:  # Skip initial state
                    print(f"Focus changed: {current_process} - {current_title}")
                
                last_title = current_title
                last_process = current_process
            
            time.sleep(poll_interval)
            
    except KeyboardInterrupt:
        print("\nStopped monitoring.")


if __name__ == "__main__":
    monitor_focus_changes()cd