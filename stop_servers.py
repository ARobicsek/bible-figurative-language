"""Stop all running Flask api_server.py processes."""

import subprocess
import sys

# Get all Python processes
result = subprocess.run(
    ['wmic', 'process', 'where', 'name="python.exe"', 'get', 'ProcessId,CommandLine', '/format:csv'],
    capture_output=True,
    text=True
)

pids_to_kill = []
for line in result.stdout.split('\n'):
    if 'api_server.py' in line and line.strip():
        parts = line.split(',')
        if len(parts) >= 3:
            try:
                pid = parts[2].strip()
                if pid and pid.isdigit():
                    pids_to_kill.append(pid)
            except:
                pass

if not pids_to_kill:
    print("No Flask servers found running.")
    sys.exit(0)

print(f"Found {len(pids_to_kill)} Flask server(s) to stop: {pids_to_kill}")

for pid in pids_to_kill:
    try:
        subprocess.run(['taskkill', '/PID', pid, '/F'], check=True, capture_output=True)
        print(f"Stopped process {pid}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop process {pid}: {e}")

print("\nAll Flask servers stopped. You can now restart with:")
print("python web/api_server.py")
