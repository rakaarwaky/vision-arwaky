import logging
import sys
from src.surfaces import mcp


def main():
    """Entry point for the mcp-vision server."""
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger = logging.getLogger("mcp-vision")
    logger.info("Starting Vision MCP Server")
    mcp.run()


if __name__ == "__main__":
    main()
