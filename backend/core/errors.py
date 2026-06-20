class AIServiceError(Exception):
    """Raised when an AI provider call fails after retry."""


class LowConfidenceError(Exception):
    """Raised when an AI result falls below the confidence threshold even after re-scoring."""


class OntologyNotFoundError(Exception):
    """Raised when a referenced ontology object, link, or event does not exist."""
