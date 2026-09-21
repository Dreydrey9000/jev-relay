"""Fixed hosted endpoint and supervised local subprocess transport."""
import getpass
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import urllib.request


class ProviderUnavailable(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderUnavailable("hosted_redirect_rejected")


def hosted(request):
    key = os.environ.get("TYPESAFE_API_KEY") or os.environ.get("JEV_API_KEY")
    if not key and platform.system() == "Darwin":
        result = subprocess.run(["/usr/bin/security", "find-generic-password", "-a", getpass.getuser(), "-s", "TYPESAFE_API_KEY", "-w"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            key = result.stdout.strip()
    if not key:
        raise ProviderUnavailable("hosted_key_missing")
    body = json.dumps({**request, "model": "jev-1.13.0"}, allow_nan=False).encode()
    req = urllib.request.Request("https://api.typesafe.ai/v1/systemone", data=body, headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    # No retries: at most one billable evaluation per route invocation.
    with urllib.request.build_opener(NoRedirect).open(req, timeout=12) as response:
        raw = response.read(262145)
    if len(raw) > 262144:
        raise ProviderUnavailable("hosted_response_too_large")
    return json.loads(raw)


def load_guard(path):
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise ProviderUnavailable("guard_module_missing")
    spec = importlib.util.spec_from_file_location("jev_relay_host_guard", path)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    return guard


def local(request, config, warning_ack=False):
    # A trusted, installed guard is mandatory. Never turn it on from this code.
    if not config.get("local_enabled"):
        raise ProviderUnavailable("local_disabled")
    guard = load_guard(config["guard_module"])
    guard.MODEL_RAM_GIB["jev-relay-laya"] = 2.0
    preflight = guard.ram_preflight("jev-relay-laya", warning_ack=warning_ack)
    if not preflight["allowed"]:
        raise ProviderUnavailable(preflight["text"])
    if not os.path.isdir(config.get("model_path", "")):
        raise ProviderUnavailable("local_checkpoint_missing")
    command = [config.get("python", sys.executable), "-m", "jev_relay.laya_worker", "--model-path", config["model_path"]]
    if platform.system() == "Darwin":
        command = ["/usr/sbin/taskpolicy", "-b", "/usr/bin/nice", "-n", "10", *command]
    env = dict(os.environ, HF_HUB_OFFLINE="1", TOKENIZERS_PARALLELISM="false", PYTHONPATH=str(Path(__file__).resolve().parent.parent))
    # Protect against overlapping loads across all Relay CLI processes.
    import fcntl
    lock_path = Path(config.get("lock_path", Path.home()/".cache/jev-relay/inference.lock"))
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ProviderUnavailable("local_busy") from None
        result = guard.run_monitored_command(command, timeout=60, env=env, input_text=json.dumps(request))
    if result.returncode:
        raise ProviderUnavailable("local_worker_failed")
    if len(result.stdout.encode()) > 262144:
        raise ProviderUnavailable("local_response_too_large")
    return json.loads(result.stdout)
