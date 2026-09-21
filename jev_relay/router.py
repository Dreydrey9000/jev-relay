"""Fallback policy. Request content never chooses a provider or grants authority."""
import re
from . import providers
from .schema import validate_request, validate_response


SECRET_HINT = re.compile(r"-----BEGIN .*PRIVATE KEY-----|\bBearer\s+\S+|\b(?:sk|ghp|gho)[_-][A-Za-z0-9]{16,}", re.I)


def route(request, config=None, *, importance="routine", cloud_allowed=False, sensitive=True, warning_ack=False, local_call=None, hosted_call=None):
    request = validate_request(request)
    if importance not in ("routine", "important"):
        raise ValueError("importance must be routine or important")
    config = config or {}
    result = {"status": "review", "provider": "frontier", "requires_review": True, "answers": {}, "attempts": []}
    if importance == "important":
        import json
        if not cloud_allowed or sensitive or SECRET_HINT.search(json.dumps(request)):
            result["reason"] = "cloud_not_authorized_for_this_input"
            return result
        provider, call = "jev", hosted_call or providers.hosted
    else:
        provider = "local"
        call = local_call or (lambda req: providers.local(req, config, warning_ack))
    try:
        response = validate_response(call(request), request)
    except Exception as exc:
        # Never return exception text that could contain provider credentials or state.
        detail = str(exc) if isinstance(exc, providers.ProviderUnavailable) else type(exc).__name__
        result["attempts"].append({"provider": provider, "outcome": "unavailable", "reason": detail})
        result["reason"] = "provider_unavailable_or_invalid"
        return result
    result.update(provider=provider, answers=response["answers"], model=response.get("model"), usage=response.get("usage"))
    result["attempts"].append({"provider": provider, "outcome": "answered"})
    if provider == "local":
        result["reason"] = "local_shadow_advice_requires_agent_review"
    else:
        result.update(status="advisory", reason="important_advice_requires_agent_review")
    return result
