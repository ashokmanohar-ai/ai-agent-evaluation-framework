class AgentEvaluationError(Exception):
    """Base exception for framework errors."""


class DatasetValidationError(AgentEvaluationError):
    """Raised before execution when a dataset is inconsistent or invalid."""


class JudgeProviderError(AgentEvaluationError):
    """Raised when a judge provider response is missing or malformed."""


class QualityGateError(AgentEvaluationError):
    """Raised when strict quality-gate handling is requested and the gate fails."""
