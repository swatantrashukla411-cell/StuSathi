import subprocess
import time
import re
import os
import sys

print("[1/3] Starting Backend (8001)...")
backend_proc = subprocess.Popen(
    [sys.executable, "run_backend.py"],
    cwd=os.path.dirname(os.path.abspath(__file__)),
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
)

print("[2/3] Starting Next.js Web (3000)...")
node_exe = r"C:\Users\shukl\AppData\Local\Microsoft\WinGet\Packages\OpenJS.NodeJS.LTS_Microsoft.Winget.Source_8wekyb3d8bbwe\node-v24.17.0-win-x64\node.exe"
web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "apps", "web")
web_proc = subprocess.Popen(
    [node_exe, os.path.join("node_modules", "next", "dist", "bin", "next"), "dev", "-p", "3000"],
    cwd=web_dir,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
)

print("Waiting 6 seconds for servers to initialize...")
time.sleep(6)

print("[3/3] Starting Cloudflare Public Tunnel...")
cf_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloudflared.exe")
cf_proc = subprocess.Popen(
    [cf_exe, "tunnel", "--url", "http://localhost:3000"],
    stderr=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    errors="ignore"
)

public_url = None
start_time = time.time()
while time.time() - start_time < 30:
    line = cf_proc.stderr.readline()
    if not line:
        time.sleep(0.5)
        continue
    print(line.strip())
    match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
    if match:
        public_url = match.group(0)
        break

if public_url:
    with open("public_url.txt", "w", encoding="utf-8") as f:
        f.write(public_url)
    print("\n" + "="*70)
    print("[SUCCESS] CAMPUSPILOT IS LIVE ON THE INTERNET!")
    print(f"[URL] PUBLIC HTTPS: {public_url}")
    print("="*70 + "\n")
else:
    print("Could not find public URL in 30 seconds.")

try:
    cf_proc.wait()
except KeyboardInterrupt:
    cf_proc.terminate()
    backend_proc.terminate()
    web_proc.terminate()
