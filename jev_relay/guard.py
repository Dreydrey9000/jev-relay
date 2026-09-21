"""Standalone macOS/Linux guard; hosts may supply a stricter compatible guard.

Never enables local AI. No persisted warning acknowledgements. No model downloads.
"""
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import time
import urllib.request
import json

MODEL_RAM_GIB = {"jev-relay-laya": 2.0}
DISABLED = Path.home()/".config/jev-relay/DISABLED"
HOST_DISABLED = Path.home()/".codex/local-ai-router/DISABLED"


def free_memory_percent():
    if platform.system() == "Darwin":
        result = subprocess.run(["/usr/bin/memory_pressure"], capture_output=True, text=True, timeout=5)
        match = re.search(r"System-wide memory free percentage:\s*(\d+)%", result.stdout)
        return float(match.group(1)) if match else None
    if platform.system() == "Linux":
        values = dict((line.split(':')[0], int(line.split()[1])) for line in Path('/proc/meminfo').read_text().splitlines())
        return 100 * values['MemAvailable'] / values['MemTotal']
    return None


def ram_preflight(model, warning_ack=False):
    if DISABLED.exists() or HOST_DISABLED.exists():
        return {"allowed":False,"hard_block":True,"text":"LOCAL_KILL_SWITCH: local inference is disabled"}
    free = free_memory_percent()
    disk = shutil.disk_usage(Path.home()).free / 1024**3
    if free is None or free < 20 or disk < 10:
        return {"allowed":False,"hard_block":True,"text":"RESOURCE_BLOCK: memory unknown/below 20% or disk below 10 GiB"}
    if platform.system() == "Darwin":
        thermal = subprocess.run(["/usr/bin/pmset", "-g", "therm"],capture_output=True,text=True,timeout=5)
        if thermal.returncode or "No thermal warning level has been recorded" not in thermal.stdout:
            return {"allowed":False,"hard_block":True,"text":"THERMAL_BLOCK: thermal status is not clear"}
    resident = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/ps",timeout=1) as response:
            resident = bool(json.load(response).get("models"))
    except OSError:
        pass
    if (free < 40 or disk < 25 or resident) and not warning_ack:
        return {"allowed":False,"hard_block":False,"text":f"RESOURCE_WARNING: free memory {free:.0f}%; free disk {disk:.1f} GiB; another Ollama model resident: {resident}. Explicit approval required."}
    return {"allowed":True,"hard_block":False}


def run_monitored_command(command, timeout, env=None, input_text=None):
    process = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env,start_new_session=True)
    start=time.monotonic();critical=0;pending=input_text
    try:
        while True:
            try:
                stdout,stderr=process.communicate(input=pending,timeout=2)
                return subprocess.CompletedProcess(command,process.returncode,stdout,stderr)
            except subprocess.TimeoutExpired:
                pending=None
                free=free_memory_percent()
                critical=critical+1 if free is None or free <= 10 else 0
                if DISABLED.exists() or HOST_DISABLED.exists() or time.monotonic()-start >= timeout or shutil.disk_usage(Path.home()).free/1024**3 < 10 or critical >= 3:
                    raise RuntimeError("LOCAL_GUARD_STOP")
    except BaseException:
        if process.poll() is None:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGKILL);process.communicate()
        raise
