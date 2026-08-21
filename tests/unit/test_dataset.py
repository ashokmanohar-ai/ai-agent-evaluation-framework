from pathlib import Path

import pytest

from agent_eval.models.dataset import EvaluationDataset, load_dataset, validate_tool_references


def test_versioned_dataset_contains_seventy_cases() -> None:
    paths = sorted(Path("datasets").glob("*/*.jsonl"))
    dataset = load_dataset(paths)
    assert len(dataset.cases) == 70
    assert len({case.id for case in dataset.cases}) == 70


def test_unknown_tool_fails_early() -> None:
    dataset = load_dataset([Path("datasets/support/support-v1.jsonl")])
    with pytest.raises(ValueError, match="absent from the policy"):
        validate_tool_references(dataset, {"get_ticket"})


def test_duplicate_ids_are_rejected() -> None:
    dataset = load_dataset([Path("datasets/support/support-v1.jsonl")])
    with pytest.raises(ValueError, match="duplicate case IDs"):
        EvaluationDataset(name="duplicate", version="1", cases=[dataset.cases[0]] * 2)
