import psutil
# from fuzzywuzzy import fuzz, process

for proc in psutil.process_iter(['pid', 'name']):
    try:
        print(f"PID={proc.info['pid']}, Name={proc.info['name']}")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue
