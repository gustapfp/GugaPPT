import structlog
import sys

structlog.configure(
    # ...
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    # ...
)

logger = structlog.get_logger()
