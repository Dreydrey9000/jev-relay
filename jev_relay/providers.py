"""Fixed hosted endpoint and supervised local subprocess transport."""
import getpass
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import urllib.parse
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


LOOPBACK = ("127.0.0.1", "localhost", "::1")


def openjev(request, config):
    """Local OpenJev verdict service (POST /decide, one question per call). Loopback only:
    this is the routine lane, so request text must never leave the machine."""
    url = config.get("openjev_url", "http://127.0.0.1:8940")
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in LOOPBACK:
        raise ProviderUnavailable("openjev_url_must_be_loopback")
    state = request["state"] if isinstance(request["state"], str) else json.dumps(request["state"])
    answers = {}
    for key, q in request["questions"].items():
        kind = q["type"]
        if kind == "choice":
            labels = {(desc or name): name for name, desc in q["criteria"].items()}
        elif kind == "score":
            labels = {text: str(i) for i, text in enumerate(q["criteria"])}
        else:
            labels = {"true": "true", "false": "false"}
        if len(labels) != (len(q["criteria"]) if kind != "noul" else 2):
            raise ProviderUnavailable("openjev_duplicate_option_text")
        body = json.dumps({"type": kind, "question": q["instructions"], "options": list(labels), "state": state}).encode()
        req = urllib.request.Request(url.rstrip("/") + "/decide", data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.build_opener(NoRedirect).open(req, timeout=config.get("openjev_timeout", 20)) as resp:
                out = json.loads(resp.read(262144))
        except Exception:
            raise ProviderUnavailable("openjev_unreachable") from None
        dist = {labels[k]: float(v) for k, v in (out.get("distribution") or {}).items() if k in labels}
        total = sum(dist.values())
        if total <= 0:
            raise ProviderUnavailable("openjev_empty_distribution")
        # OpenJev drops its "insufficient evidence" mass; renormalize over the real options.
        probs = {name: dist.get(name, 0.0) / total for name in labels.values()}
        abstain = bool(out.get("abstain"))
        if kind == "noul":
            answers[key] = {"type": "noul", "noul": probs["true"], "abstain": abstain}
        elif kind == "choice":
            answers[key] = {"type": "choice", "choice": max(probs, key=probs.get), "probabilities": probs, "abstain": abstain}
        else:
            answers[key] = {"type": "score", "score": sum(int(k) * v for k, v in probs.items()), "probabilities": probs, "abstain": abstain}
    return {"answers": answers, "model": "openjev:" + str(out.get("model", "unknown"))}


LOCAL_TIMEOUT_DEFAULT, LOCAL_TIMEOUT_MIN, LOCAL_TIMEOUT_MAX = 180, 10, 600


def local_timeout(config):
    """Seconds one supervised local job may run before the guard stops it. Was a fixed 60, but a cold
    Laya load alone passed that on a Mac with full swap (2026-10-13). Bounded so config cannot remove it."""
    value = config.get("local_timeout", LOCAL_TIMEOUT_DEFAULT)
    if type(value) not in (int, float) or not LOCAL_TIMEOUT_MIN <= value <= LOCAL_TIMEOUT_MAX:
        raise ProviderUnavailable("local_timeout_must_be_%s_to_%s_seconds" % (LOCAL_TIMEOUT_MIN, LOCAL_TIMEOUT_MAX))
    return value


def local(request, config, warning_ack=False):
    # A trusted, installed guard is mandatory. Never turn it on from this code.
    if not config.get("local_enabled"):
        raise ProviderUnavailable("local_disabled")
    if config.get("local_backend") == "openjev":
        # An already-running service, not a model load, so the RAM guard does not apply.
        return openjev(request, config)
    timeout = local_timeout(config)
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
        result = guard.run_monitored_command(command, timeout=timeout, env=env, input_text=json.dumps(request))
    if result.returncode:
        raise ProviderUnavailable("local_worker_failed")
    if len(result.stdout.encode()) > 262144:
        raise ProviderUnavailable("local_response_too_large")
    return json.loads(result.stdout)
