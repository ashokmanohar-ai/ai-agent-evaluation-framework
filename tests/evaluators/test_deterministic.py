from agent_eval.evaluators.deterministic import (
    GroundingEvaluator,
    SequenceEvaluator,
    TaskCompletionEvaluator,
    ToolArgumentEvaluator,
    ToolSelectionEvaluator,
)
from agent_eval.models.enums import FailureCode, MetricStatus
from tests.helpers import make_case, make_trace, tool_call


async def test_correct_tool_and_argument_pass() -> None:
    case = make_case(
        required_tools=["get_ticket"],
        expected_tool_arguments={"get_ticket": {"ticket_id": "INC-101"}},
    )
    trace = make_trace(
        calls=[tool_call("get_ticket", {"ticket_id": "INC-101"}, {"status": "OPEN"})]
    )
    assert (await ToolSelectionEvaluator().evaluate(case, trace)).status == MetricStatus.PASS
    assert (await ToolArgumentEvaluator().evaluate(case, trace)).status == MetricStatus.PASS


async def test_wrong_tool_fails() -> None:
    case = make_case(required_tools=["get_ticket"])
    trace = make_trace(calls=[tool_call("search_knowledge", {}, {})])
    result = await ToolSelectionEvaluator().evaluate(case, trace)
    assert result.status == MetricStatus.FAIL
    assert {failure.code for failure in result.failures} == {
        FailureCode.MISSING_TOOL,
        FailureCode.WRONG_TOOL,
    }


async def test_forbidden_tool_is_critical_failure() -> None:
    case = make_case(forbidden_tools=["delete_user"])
    trace = make_trace(calls=[tool_call("delete_user", {}, {"deleted": True})])
    result = await ToolSelectionEvaluator().evaluate(case, trace)
    assert result.score == 0
    assert result.failures[0].code == FailureCode.FORBIDDEN_TOOL
    assert result.failures[0].severity.value == "CRITICAL"


async def test_wrong_argument_fails() -> None:
    case = make_case(
        required_tools=["get_ticket"],
        expected_tool_arguments={"get_ticket": {"ticket_id": "INC-101"}},
    )
    trace = make_trace(calls=[tool_call("get_ticket", {"ticket_id": "INC-110"}, {})])
    result = await ToolArgumentEvaluator().evaluate(case, trace)
    assert result.status == MetricStatus.FAIL
    assert result.failures[0].code == FailureCode.WRONG_ARGUMENT


async def test_date_equivalent_argument_passes() -> None:
    case = make_case(
        expected_tool_arguments={
            "schedule_support": {
                "slot": {"value": "2026-08-22T00:00:00+00:00", "match": "date_equivalent"}
            }
        }
    )
    trace = make_trace(calls=[tool_call("schedule_support", {"slot": "2026-08-22T14:30:00Z"}, {})])
    assert (await ToolArgumentEvaluator().evaluate(case, trace)).status == MetricStatus.PASS


async def test_correct_final_answer_without_execution_fails() -> None:
    case = make_case(required_tools=["create_ticket"], expected_facts={"ticket_id": "INC-9"})
    trace = make_trace(final_output={"ticket_id": "INC-9"})
    result = await TaskCompletionEvaluator().evaluate(case, trace)
    assert result.status == MetricStatus.FAIL
    assert FailureCode.TASK_NOT_COMPLETED in {failure.code for failure in result.failures}


async def test_wrong_sequence_fails() -> None:
    case = make_case(ordered_steps=["check_user_entitlement", "request_access"])
    trace = make_trace(step_names=["request_access", "check_user_entitlement"])
    result = await SequenceEvaluator().evaluate(case, trace)
    assert result.status == MetricStatus.FAIL
    assert result.failures[0].code == FailureCode.WRONG_SEQUENCE


async def test_unsupported_claim_fails_grounding() -> None:
    case = make_case(expected_facts={"status": "OPEN"})
    trace = make_trace(final_output={"status": "OPEN"})
    result = await GroundingEvaluator().evaluate(case, trace)
    assert result.status == MetricStatus.FAIL
    assert result.failures[0].code == FailureCode.UNSUPPORTED_CLAIM
