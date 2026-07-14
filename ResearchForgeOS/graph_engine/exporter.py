from __future__ import annotations

import json
from io import BytesIO
from typing import Any

from PIL import Image, ImageDraw


class GraphExporter:
    def export_json(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, indent=2, sort_keys=True)

    def export_svg(self, payload: dict[str, Any]) -> str:
        nodes = payload.get("nodes", [])
        edges = payload.get("edges", [])
        positions = {
            item["node_id"]: item
            for item in payload.get("layout", {}).get("positions", [])
            if isinstance(item, dict) and item.get("node_id")
        }
        width = 1600
        height = 1000
        lines = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="-800 -500 1600 1000">',
            '<rect x="-800" y="-500" width="1600" height="1000" fill="#f8fafc"/>',
        ]
        for edge in edges:
            source = positions.get(edge.get("source_node_id"))
            target = positions.get(edge.get("target_node_id"))
            if not source or not target:
                continue
            lines.append(
                f'<line x1="{source["x"]}" y1="{source["y"]}" x2="{target["x"]}" y2="{target["y"]}" '
                'stroke="#94a3b8" stroke-width="1.4" opacity="0.68"/>'
            )
        for node in nodes:
            position = positions.get(node.get("id"))
            if not position:
                continue
            radius = max(7.0, min(28.0, float(node.get("size", 24)) / 2))
            color = str(node.get("color", "#334155"))
            label = self._escape(str(node.get("label", node.get("name", "")))[:34])
            lines.append(
                f'<circle cx="{position["x"]}" cy="{position["y"]}" r="{radius}" fill="{color}" '
                'stroke="#0f172a" stroke-width="1"/>'
            )
            lines.append(
                f'<text x="{position["x"] + radius + 4}" y="{position["y"] + 4}" '
                'font-family="Inter, Arial, sans-serif" font-size="12" fill="#0f172a">'
                f"{label}</text>"
            )
        lines.append("</svg>")
        return "\n".join(lines)

    def export_png(self, payload: dict[str, Any]) -> bytes:
        image = Image.new("RGB", (1600, 1000), "#f8fafc")
        draw = ImageDraw.Draw(image)
        positions = {
            item["node_id"]: item
            for item in payload.get("layout", {}).get("positions", [])
            if isinstance(item, dict) and item.get("node_id")
        }

        def project(x: float, y: float) -> tuple[float, float]:
            return x + 800, y + 500

        for edge in payload.get("edges", []):
            source = positions.get(edge.get("source_node_id"))
            target = positions.get(edge.get("target_node_id"))
            if source and target:
                draw.line(
                    [project(source["x"], source["y"]), project(target["x"], target["y"])],
                    fill="#94a3b8",
                    width=2,
                )
        for node in payload.get("nodes", []):
            position = positions.get(node.get("id"))
            if not position:
                continue
            x, y = project(position["x"], position["y"])
            radius = max(7.0, min(28.0, float(node.get("size", 24)) / 2))
            color = str(node.get("color", "#334155"))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color, outline="#0f172a")
            draw.text((x + radius + 4, y - 6), str(node.get("label", node.get("name", "")))[:34], fill="#0f172a")
        output = BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()

    def _escape(self, value: str) -> str:
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
