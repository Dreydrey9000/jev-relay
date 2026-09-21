"""A deliberately small interoperable subset of the System One schema."""
import json
import math


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_request(request):
    if not isinstance(request, dict):
        raise ValueError("Request must be an object")
    if len(json.dumps(request, allow_nan=False).encode()) > 32768:
        raise ValueError("Request exceeds 32 KiB")
    if not isinstance(request.get("state"), (str, dict, list)):
        raise ValueError("state must be text, an object, or a list")
    questions = request.get("questions")
    if not isinstance(questions, dict) or not 1 <= len(questions) <= 32:
        raise ValueError("Supply 1 to 32 questions")
    for key, question in questions.items():
        if not isinstance(key, str) or not key or not isinstance(question, dict):
            raise ValueError("Questions require nonempty string IDs and object definitions")
        if not isinstance(question.get("instructions"), str) or not question["instructions"].strip():
            raise ValueError("Instructions must be nonempty text")
        kind = question.get("type")
        criteria = question.get("criteria")
        if kind == "choice":
            if not isinstance(criteria, dict) or not 2 <= len(criteria) <= 26:
                raise ValueError("Choice requires 2 to 26 named options")
            if not all(isinstance(k, str) and k and (v is None or isinstance(v, str)) for k, v in criteria.items()):
                raise ValueError("Choice options require string names and text/null descriptions")
        elif kind == "score":
            if not isinstance(criteria, list) or not 2 <= len(criteria) <= 10 or not all(isinstance(v, str) for v in criteria):
                raise ValueError("Score requires 2 to 10 text levels")
        elif kind == "noul":
            if criteria is not None and (not isinstance(criteria, dict) or set(criteria) != {"true", "false"} or not all(isinstance(v, str) for v in criteria.values())):
                raise ValueError("Noul criteria require true and false text descriptions")
        else:
            raise ValueError("Supported types: choice, score, noul")
    return {"state": request["state"], "questions": questions}


def validate_response(response, request):
    if not isinstance(response, dict) or not isinstance(response.get("answers"), dict):
        raise ValueError("Provider omitted answers")
    if set(response["answers"]) != set(request["questions"]):
        raise ValueError("Provider returned missing or extra answers")
    for key, question in request["questions"].items():
        answer = response["answers"][key]
        if not isinstance(answer, dict) or answer.get("type") != question["type"]:
            raise ValueError("Answer type mismatch")
        if question["type"] == "noul":
            if not number(answer.get("noul")) or not 0 <= answer["noul"] <= 1:
                raise ValueError("Invalid yes probability")
            continue
        labels = set(question["criteria"]) if question["type"] == "choice" else {str(i) for i in range(len(question["criteria"]))}
        probs = answer.get("probabilities")
        if not isinstance(probs, dict) or set(probs) != labels:
            raise ValueError("Probability labels do not match options")
        if not all(number(v) and 0 <= v <= 1 for v in probs.values()) or abs(sum(probs.values()) - 1) > .005:
            raise ValueError("Probabilities must be finite, in range, and sum to one")
        if question["type"] == "choice":
            if answer.get("choice") not in labels or probs[answer["choice"]] < max(probs.values()) - 1e-6:
                raise ValueError("Choice is not a maximum probability option")
        else:
            expected = sum(int(k) * v for k, v in probs.items())
            if not number(answer.get("score")) or abs(answer["score"] - expected) > .01:
                raise ValueError("Score disagrees with its distribution")
    return response
