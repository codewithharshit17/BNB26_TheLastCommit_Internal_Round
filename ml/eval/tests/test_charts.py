import hashlib
import json

from ml.eval.charts import generate_charts, load_metrics


METRICS_PATH = "eval/out/metrics.json"
EXPECTED = {
    "classifier_accuracy.png",
    "probe_overall.png",
    "probe_confusable.png",
    "false_resolution.png",
    "heldout_safety.png",
    "ablations.png",
}


def test_metrics_json_loads():
    metrics = load_metrics(METRICS_PATH)
    assert metrics["seed"] == 42
    assert "probes" in metrics


def test_expected_charts_are_generated(tmp_path):
    generated = generate_charts(METRICS_PATH, tmp_path)
    assert {path.name for path in generated} == EXPECTED
    assert {path.name for path in tmp_path.glob("*.png")} == EXPECTED


def test_chart_generation_is_deterministic(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    generate_charts(METRICS_PATH, first)
    generate_charts(METRICS_PATH, second)
    for name in EXPECTED:
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest(first / name) == digest(second / name)


def test_missing_llm_metrics_do_not_break_generation(tmp_path):
    metrics = load_metrics(METRICS_PATH)
    metrics.pop("llm_zero_shot", None)
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")
    generated = generate_charts(path, tmp_path / "charts")
    assert {item.name for item in generated} == EXPECTED


def test_missing_ablations_skips_only_ablation_chart(tmp_path):
    metrics = load_metrics(METRICS_PATH)
    metrics.pop("ablations", None)
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps(metrics), encoding="utf-8")
    output = tmp_path / "charts"
    generated = generate_charts(path, output)
    names = {item.name for item in generated}
    assert "ablations.png" not in names
    assert names == EXPECTED - {"ablations.png"}
