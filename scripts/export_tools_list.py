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


def _is_generated_title(title: object, tool_name: str) -> bool:
    if not isinstance(title, str) or not tool_name:
        return False
    return title in {
        f"{tool_name}Arguments",
        f"{tool_name}Output",
        f"{tool_name}DictOutput",
    } or (
        title.startswith(tool_name)
        and title.endswith(("Arguments", "Output", "DictOutput"))
    )


def _is_result_envelope(schema: dict) -> bool:
    if schema.get("type") != "object":
        return False
    props = schema.get("properties")
    if not isinstance(props, dict) or list(props.keys()) != ["result"]:
        return False
    required = schema.get("required")
    if required is not None and required != ["result"]:
        return False
    title = schema.get("title")
    if isinstance(title, str) and not title.endswith(
        ("Output", "DictOutput", "Arguments")
    ):
        return False
    return True


def normalize_json_schema(schema: object, tool_name: str) -> object:
    """Strip FastMCP/Pydantic wrapper titles and single-property result envelopes."""
    if not isinstance(schema, dict):
        return schema
    current: dict = json.loads(json.dumps(schema))  # deep copy via JSON
    for _ in range(3):
        if not _is_result_envelope(current):
            break
        inner = current.get("properties", {}).get("result")
        if not isinstance(inner, dict):
            break
        current = json.loads(json.dumps(inner))
    if _is_generated_title(current.get("title"), tool_name):
        current.pop("title", None)
    if current.get("title") == "Result":
        current.pop("title", None)
    props = current.get("properties")
    if isinstance(props, dict):
        for key, prop in props.items():
            if not isinstance(prop, dict):
                continue
            auto = key[:1].upper() + key[1:] if key else key
            snake = " ".join(
                part[:1].upper() + part[1:] for part in key.split("_") if part
            )
            if prop.get("title") in {auto, snake, "Result"}:
                prop.pop("title", None)
    return current


def normalize_tool_payload(payload: dict) -> dict:
    name = str(payload.get("name") or "")
    out = dict(payload)
    if "inputSchema" in out:
        out["inputSchema"] = normalize_json_schema(out["inputSchema"], name)
    if "input_schema" in out:
        out["inputSchema"] = normalize_json_schema(out.pop("input_schema"), name)
    if "outputSchema" in out:
        out["outputSchema"] = normalize_json_schema(out["outputSchema"], name)
    if "output_schema" in out:
        out["outputSchema"] = normalize_json_schema(out.pop("output_schema"), name)
    return out


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
        tools.append(normalize_tool_payload(payload))

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
