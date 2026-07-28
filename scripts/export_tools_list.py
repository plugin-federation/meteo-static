#!/usr/bin/env python3
"""Export MCP tools/list to a JSON file for offline CI validation.

Usage:
    python scripts/export_tools_list.py --output ci/tools-list.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export tools/list from meteo-static")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("ci/tools-list.json"),
        help="Output path for ListToolsResult JSON",
    )
    parser.add_argument(
        "--command",
        default=sys.executable,
        help="Python (or other) executable used to start the MCP server",
    )
    parser.add_argument(
        "--server",
        default="src/server.py",
        help="Server entry script",
    )
    return parser.parse_args()


async def export_tools_list(command: str, server: str) -> dict:
    params = StdioServerParameters(
        command=command,
        args=[server],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()

    tools: list[dict] = []
    for tool in result.tools:
        # Prefer model_dump when available (pydantic v2)
        if hasattr(tool, "model_dump"):
            payload = tool.model_dump(mode="json", exclude_none=True)
        elif hasattr(tool, "dict"):
            payload = tool.dict(exclude_none=True)
        else:
            payload = {
                "name": tool.name,
                "description": getattr(tool, "description", None),
                "inputSchema": getattr(tool, "inputSchema", None),
            }
        tools.append(payload)

    out: dict = {"tools": tools}
    next_cursor = getattr(result, "nextCursor", None)
    if next_cursor:
        out["nextCursor"] = next_cursor
    return out


def main() -> None:
    args = parse_args()
    data = asyncio.run(export_tools_list(args.command, args.server))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(data['tools'])} tools to {args.output}")


if __name__ == "__main__":
    main()
