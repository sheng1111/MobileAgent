"""
MobileAgent Source Modules

Core modules for AI agent device automation:
- adb_helper: ADB command wrapper
- logger: Unified logging
- executor: Deterministic execution with Element-First strategy
- tool_router: Unified MCP/ADB tool interface
- state_tracker: Navigation state machine and visited tracking
- patrol: Social media patrol automation
"""

from .logger import get_logger, logger
from .adb_helper import ADBHelper

# Import new modules (may require additional dependencies)
try:
    from .executor import (
        DeterministicExecutor,
        Element,
        ScreenState,
        ActionResult,
        ExecutionResult
    )
except ImportError:
    pass

try:
    from .tool_router import ToolRouter, ToolType
except ImportError:
    pass

try:
    from .state_tracker import (
        StateTracker,
        NavigationState,
        VisitedItem,
        generate_post_id
    )
except ImportError:
    pass

try:
    from .patrol import (
        PatrolStateMachine,
        PatrolConfig,
        PatrolReport,
        patrol
    )
except ImportError:
    pass
