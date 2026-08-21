from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement

from agent_eval.models.result import EvaluationRun


def write_junit_report(run: EvaluationRun, path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    suite = Element(
        "testsuite",
        name="agent-evaluation",
        tests=str(len(run.case_results)),
        failures=str(run.failed_cases),
        time=f"{sum(case.trace.total_duration_ms for case in run.case_results) / 1000:.3f}",
    )
    for case in run.case_results:
        test = SubElement(
            suite,
            "testcase",
            classname="agent_eval.dataset",
            name=case.case_id,
            time=f"{case.trace.total_duration_ms / 1000:.3f}",
        )
        if case.failures:
            failure = SubElement(
                test,
                "failure",
                message=", ".join(item.code.value for item in case.failures),
            )
            failure.text = "\n".join(f"{item.code.value}: {item.message}" for item in case.failures)
        properties = SubElement(test, "properties")
        for name, metric in sorted(case.metrics.items()):
            SubElement(properties, "property", name=name, value=f"{metric.score:.6f}")
    ElementTree(suite).write(destination, encoding="utf-8", xml_declaration=True)
    return destination
