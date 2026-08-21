from pathlib import Path

from agent_eval.models.dataset import load_dataset
from agent_eval.policies.loader import load_tool_policy


def test_datasets_cannot_reference_host_command_tools() -> None:
    dataset = load_dataset(sorted(Path("datasets").glob("*/*.jsonl")))
    referenced = {
        tool
        for case in dataset.cases
        for tool in (
            case.expectations.required_tools + list(case.expectations.expected_tool_arguments)
        )
    }
    dangerous = {"shell", "exec", "subprocess", "delete_file", "write_file"}
    assert not referenced.intersection(dangerous)


def test_policy_marks_destructive_demo_tools_forbidden() -> None:
    policy = load_tool_policy("config/tool-policy.yaml")
    assert policy["delete_user"]["classification"] == "FORBIDDEN"
    assert policy["delete_account"]["classification"] == "FORBIDDEN"
