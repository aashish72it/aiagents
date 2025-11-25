
import logging
import sys
from config import DEBUG

logger = logging.getLogger("aiagents")
handler = logging.StreamHandler(sys.stdout)
fmt = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s - %(message)s")
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
