from collections import Counter


def accuracy(predictions, labels):
    """Return accuracy and count without hiding an empty evaluation set."""
    predictions = list(predictions)
    labels = list(labels)
    if len(predictions) != len(labels):
        raise ValueError("predictions and labels must have equal length")
    return {"accuracy": None if not labels else sum(p == y for p, y in zip(predictions, labels)) / len(labels), "count": len(labels)}


def per_class(predictions, labels):
    """Return compact per-class counts for deterministic JSON output."""
    result = {}
    classes = sorted(set(predictions) | set(labels))
    for label in classes:
        tp = sum(p == label and y == label for p, y in zip(predictions, labels))
        actual = sum(y == label for y in labels)
        result[str(label)] = {"correct": tp, "actual": actual, "recall": None if actual == 0 else tp / actual}
    return result


def report(predictions, labels):
    result = accuracy(predictions, labels)
    result["per_class"] = per_class(predictions, labels)
    return result
