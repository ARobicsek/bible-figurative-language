"""Force stop processes using port 5000."""

import subprocess

# PIDs using port 5000
pids = ['55020', '36592', '38772']

for pid in pids:
    try:
        # Try normal kill first
        result = subprocess.run(
            ['taskkill', '/PID', pid, '/F'],
            capture_output=True,
            text=True
        )
        print(f"PID {pid}: {result.stdout.strip()}")
    except Exception as e:
        print(f"PID {pid}: Error - {e}")

print("\nDone. Check if port 5000 is now free with:")
print("netstat -ano | findstr :5000")
