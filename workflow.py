"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    from html import escape
    totals = {}
    for row in data['sales']:
        if type(row['revenue']) not in (float, int) or row['revenue'] < 0:
            raise ValueError('Chart revenue must be nonnegative')
        totals[row['category']] = totals.get(row['category'], 0) + row['revenue']
    if not totals:
        raise ValueError('At least one category is required')
    maximum = max(totals.values()) or 1
    bars = []
    for index, (category, revenue) in enumerate(sorted(totals.items())):
        y = 60 + index * 70
        bars.append(f'<text x="20" y="{y + 20}">{escape(category)}</text><rect x="190" y="{y}" width="{500 * revenue / maximum}" height="30" fill="#2459b8"/><text x="700" y="{y + 20}">{revenue}</text>')
    chart = f'<svg xmlns="http://www.w3.org/2000/svg" width="850" height="{120 + len(totals) * 70}"><rect width="100%" height="100%" fill="white"/><text x="20" y="30">Revenue by category ({escape(data["currency"])}) — zero baseline</text>{"".join(bars)}</svg>'
    (agent.output / 'sales.svg').write_text(chart, encoding='utf8')
    note = await agent.ask('explain_chart', 'Explain these category totals and one limitation; do not infer causes.', totals, 'Electronics contributes 2000 USD and Accessories 200 USD. This is a snapshot, not a trend.')
    return {'totals': totals, 'chart': 'sales.svg', 'explanation': note}
