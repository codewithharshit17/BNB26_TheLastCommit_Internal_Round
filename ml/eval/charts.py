import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


class ChartDataError(ValueError):
    """Raised when required metrics are missing or malformed."""


DEFAULT_METRICS = Path("eval/out/metrics.json")
DEFAULT_OUTPUT = Path("eval/out/charts")


def load_metrics(path=DEFAULT_METRICS):
    """Load metrics JSON without changing or recomputing its values."""
    metrics_path = Path(path)
    try:
        return json.loads(metrics_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ChartDataError(f"metrics file not found: {metrics_path}") from exc
    except json.JSONDecodeError as exc:
        raise ChartDataError(f"invalid metrics JSON: {metrics_path}") from exc


def _context(metrics):
    return f"seed {metrics.get('seed', 'unknown')} | n={metrics.get('dataset_size', 'unknown')}"


def _save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160, bbox_inches="tight", format="png")
    plt.close(fig)
    return path


def _bars(labels, values, title, ylabel, path, subtitle):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values)
    ax.set_title(f"{title}\n{subtitle}")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1)
    ax.grid(axis="y", alpha=0.25)
    for index, value in enumerate(values):
        ax.text(index, value + 0.025, f"{value:.3f}", ha="center", va="bottom")
    fig.tight_layout()
    return _save(fig, path)


def _grouped_bars(labels, series, title, ylabel, path, subtitle):
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    width = 0.8 / len(series)
    for index, (name, values) in enumerate(series.items()):
        ax.bar(x + (index - (len(series) - 1) / 2) * width, values, width, label=name)
    ax.set_xticks(x, labels)
    ax.set_title(f"{title}\n{subtitle}")
    ax.set_xlabel("Number of probes")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    return _save(fig, path)


def _probe_values(section):
    labels = ["0", "1", "2"]
    try:
        information_gain = [section[label]["information_gain"]["accuracy"] for label in labels]
        random_values = [section[label]["random"]["accuracy"] for label in labels]
    except (KeyError, TypeError) as exc:
        raise ChartDataError("probe metrics must contain 0, 1, and 2 entries with accuracy") from exc
    return labels, {"Information gain": information_gain, "Random": random_values}


def _classifier_chart(metrics, output_dir):
    try:
        section = metrics["classifier"]["supported_label"]
        values = [section["logistic_regression"]["accuracy"], section["gradient_boosting"]["accuracy"]]
    except (KeyError, TypeError) as exc:
        raise ChartDataError("supported-label classifier metrics are missing") from exc
    return _bars(
        ["Logistic Regression", "Gradient Boosting"],
        values,
        "Supported-label classifier accuracy",
        "Accuracy",
        output_dir / "classifier_accuracy.png",
        _context(metrics),
    )


def _probe_chart(metrics, section_name, filename, title, output_dir):
    try:
        section = metrics[section_name]
        if section_name == "confusable":
            section = section["probes"]
        labels, series = _probe_values(section)
    except KeyError as exc:
        raise ChartDataError(f"missing metrics section: {section_name}") from exc
    return _grouped_bars(labels, series, title, "Accuracy", output_dir / filename, _context(metrics))


def _false_resolution_chart(metrics, output_dir):
    try:
        section = metrics["false_resolution"]
        values = [section["naive_false_resolution_rate"], section["relearn_false_resolution_rate"]]
    except (KeyError, TypeError) as exc:
        raise ChartDataError("false-resolution metrics are missing") from exc
    return _bars(
        ["Naive", "Re:Learn"],
        values,
        "False-resolution rate",
        "Fraction",
        output_dir / "false_resolution.png",
        _context(metrics),
    )


def _heldout_chart(metrics, output_dir):
    try:
        section = metrics["held_out"]
        values = [section["unknown_fraction"], section["confidently_mislabelled_fraction"]]
    except (KeyError, TypeError) as exc:
        raise ChartDataError("held-out safety metrics are missing") from exc
    return _bars(
        ["Unknown", "Confidently mislabelled"],
        values,
        "Held-out misconception safety",
        "Fraction",
        output_dir / "heldout_safety.png",
        _context(metrics),
    )


def _ablations_chart(metrics, output_dir):
    if "ablations" not in metrics:
        return None
    try:
        variants = ["full", "without_interpreter_match", "without_confidence"]
        models = ["logistic_regression", "gradient_boosting"]
        series = {
            "Logistic Regression": [metrics["ablations"][variant][models[0]]["accuracy"] for variant in variants],
            "Gradient Boosting": [metrics["ablations"][variant][models[1]]["accuracy"] for variant in variants],
        }
    except (KeyError, TypeError) as exc:
        raise ChartDataError("ablation metrics are incomplete") from exc
    return _grouped_bars(
        ["Full", "Without match", "Without confidence"],
        series,
        "Classifier feature ablations",
        "Accuracy",
        output_dir / "ablations.png",
        _context(metrics),
    )


def generate_charts(metrics_path=DEFAULT_METRICS, output_dir=DEFAULT_OUTPUT):
    """Generate all available evaluation charts from an existing metrics file."""
    metrics = load_metrics(metrics_path)
    output_dir = Path(output_dir)
    generated = [
        _classifier_chart(metrics, output_dir),
        _probe_chart(metrics, "probes", "probe_overall.png", "Probe strategy accuracy", output_dir),
        _probe_chart(metrics, "confusable", "probe_confusable.png", "Confusable-subset probe accuracy", output_dir),
        _false_resolution_chart(metrics, output_dir),
        _heldout_chart(metrics, output_dir),
    ]
    ablations = _ablations_chart(metrics, output_dir)
    if ablations is not None:
        generated.append(ablations)
    return generated


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate Re:Learn evaluation charts")
    parser.add_argument("--metrics", default=str(DEFAULT_METRICS))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    generated = generate_charts(args.metrics, args.output)
    for path in generated:
        print(path)


if __name__ == "__main__":
    main()
