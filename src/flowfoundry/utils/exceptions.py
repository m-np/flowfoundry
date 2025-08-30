# src/flowfoundry/utils/exceptions.py
from __future__ import annotations


class FFError(Exception):
    """Base class for all FlowFoundry-specific exceptions."""


class FFConfigError(FFError):
    """Raised when there is a configuration issue."""


class FFRegistryError(FFError):
    """Raised when a registry lookup fails."""


class FFDependencyError(FFError):
    """Raised when a required dependency is missing."""


class FFExecutionError(FFError):
    """Raised when execution of a strategy or step fails."""


class FFIngestionError(FFError):
    """Raised when ingestion of input data fails."""
