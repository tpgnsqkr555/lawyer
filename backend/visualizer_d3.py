import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
from models import TimelineData, Event

class D3GanttVisualizer:
    """
    Clean D3.js/SVG visualizer with Claude Artifacts-style interactions.
    - Hover tooltips only (no zoom, pan, drag)
    - PNG export button
    - Fits viewport without scrolling
    - Professional styling matching NexVira reference
    """

    def __init__(self):
        self.fig_width = 1600
        self.fig_height = 900

    def parse_date(self, date_str: str) -> datetime:
        """Parse flexible date formats: YYYY-MM-DD, YYYY-MM, or YYYY"""
        date_str = date_str.strip()

        if len(date_str) == 4:  # YYYY
            return datetime.strptime(date_str + "-01-01", "%Y-%m-%d")
        elif len(date_str) == 7:  # YYYY-MM
            return datetime.strptime(date_str + "-01", "%Y-%m-%d")
        else:  # YYYY-MM-DD
            return datetime.strptime(date_str, "%Y-%m-%d")

    def calculate_duration_label(self, start_date: str, end_date: str) -> str:
        """Calculate duration like '5y 5m' format"""
        start = self.parse_date(start_date)
        end = self.parse_date(end_date)

        delta = end - start
        years = delta.days // 365
        months = (delta.days % 365) // 30

        if years > 0 and months > 0:
            return f"{years}y {months}m"
        elif years > 0:
            return f"{years}y"
        elif months > 0:
            return f"{months}m"
        else:
            days = delta.days
            return f"{days}d"

    def generate_gantt(self, timeline_data: TimelineData, color_map: Dict[str, str], output_path: str = "output/timeline.html") -> str:
        """
        Generate professional Gantt chart using D3.js/SVG.

        Key features:
        - Horizontal bars for employment/tenure periods
        - Milestone markers as vertical dotted lines
        - Hover tooltips (no other interactions)
        - PNG export button at top
        - Auto-fits viewport
        """

        events = timeline_data.events
        case = timeline_data.case
        viz_config = timeline_data.visualization_config

        # Separate duration events (bars) from point events (milestones)
        bar_events = [e for e in events if e.end is not None]
        milestone_events = [e for e in events if e.milestone or e.end is None]

        # Apply visualization config
        if viz_config:
            if viz_config.focus_actors:
                bar_events = [e for e in bar_events if e.actor in viz_config.focus_actors]

        if not bar_events:
            raise ValueError("No events with duration found. Need start AND end dates for bars.")

        # Build actor list
        actors = []
        seen = set()
        for event in bar_events:
            if event.actor not in seen:
                actors.append(event.actor)
                seen.add(event.actor)

        # Sort actors: suspicious at bottom, normal at top
        if viz_config and viz_config.actor_highlights:
            highlighted_names = {h.name for h in viz_config.actor_highlights}
            normal_actors = [a for a in actors if a not in highlighted_names]
            suspicious_actors = [a for a in actors if a in highlighted_names]
            actors = normal_actors + suspicious_actors

        actors = actors[::-1]  # Reverse so first appears at top

        # Build data structure for JavaScript
        chart_data = {
            "case": {
                "name": case.name,
                "id": case.id,
                "type": case.type,
                "start": case.start,
                "end": case.end
            },
            "actors": actors,
            "bar_events": [],
            "milestone_events": [],
            "actor_highlights": {},
            "color_map": color_map,
            "footer_text": viz_config.footer_analysis if viz_config else "",
            "stats": {
                "actor_count": len(actors),
                "milestone_count": len(milestone_events),
                "date_range": f"{case.start} to {case.end}" if case.start and case.end else ""
            }
        }

        # Add bar events with colors and highlights
        for event in bar_events:
            # Determine color
            color = color_map.get(event.roleType, "#3b82f6")
            highlight_reason = None

            if viz_config and viz_config.actor_highlights:
                for highlight in viz_config.actor_highlights:
                    if highlight.name == event.actor:
                        color = highlight.color
                        highlight_reason = highlight.reason
                        chart_data["actor_highlights"][event.actor] = {
                            "color": highlight.color,
                            "reason": highlight.reason
                        }
                        break

            duration_label = self.calculate_duration_label(event.start, event.end)

            chart_data["bar_events"].append({
                "actor": event.actor,
                "action": event.action,
                "target": event.target,
                "roleType": event.roleType,
                "start": event.start,
                "end": event.end,
                "context": event.context,
                "color": color,
                "duration_label": duration_label,
                "highlight_reason": highlight_reason
            })

        # Add milestone events
        for milestone in milestone_events:
            chart_data["milestone_events"].append({
                "actor": milestone.actor,
                "action": milestone.action,
                "target": milestone.target,
                "start": milestone.start,
                "context": milestone.context
            })

        # Generate legend items
        legend_items = {}
        for event in bar_events:
            if event.roleType not in legend_items:
                legend_items[event.roleType] = color_map.get(event.roleType, "#3b82f6")

        if viz_config and viz_config.actor_highlights:
            legend_items["⚠ Suspicious Appointment"] = "#ef4444"

        chart_data["legend_items"] = legend_items

        # Generate HTML with embedded D3.js visualization
        html_content = self._generate_html_template(chart_data)

        # Save HTML file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"[SUCCESS] D3.js visualization saved to {output_path}")
        return output_path

    def _generate_html_template(self, data: dict) -> str:
        """Generate standalone HTML with embedded D3.js visualization"""

        data_json = json.dumps(data, indent=2)

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data["case"]["name"]} - Timeline</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f9fafb;
            color: #1f2937;
            padding: 20px;
        }}

        #container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 20px;
        }}

        #export-btn {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            transition: background 0.2s;
            z-index: 1000;
        }}

        #export-btn:hover {{
            background: #2563eb;
        }}

        #export-btn:active {{
            background: #1d4ed8;
        }}

        #chart {{
            position: relative;
            width: 100%;
            overflow: visible;
        }}

        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 16px;
            border-radius: 6px;
            font-size: 13px;
            line-height: 1.5;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 1000;
            max-width: 400px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }}

        .tooltip.visible {{
            opacity: 1;
        }}

        .tooltip strong {{
            font-weight: 600;
            display: block;
            margin-bottom: 4px;
        }}

        .axis-label {{
            font-size: 11px;
            fill: #6b7280;
        }}

        .grid-line {{
            stroke: #d1d5db;
            stroke-width: 1;
            opacity: 0.5;
        }}

        .actor-label {{
            font-size: 11px;
            font-weight: 400;
        }}

        .milestone-line {{
            stroke: #9ca3af;
            stroke-width: 2;
            stroke-dasharray: 4,4;
            opacity: 0.7;
        }}

        .milestone-label {{
            font-size: 9px;
            fill: #4b5563;
            text-anchor: start;
        }}

        .duration-label {{
            font-size: 11px;
            fill: white;
            text-anchor: middle;
            pointer-events: none;
        }}

        .bar-rect {{
            stroke: white;
            stroke-width: 1.5;
            opacity: 0.85;
            cursor: pointer;
            transition: opacity 0.2s;
        }}

        .bar-rect:hover {{
            opacity: 1;
        }}

        .legend-item {{
            font-size: 9px;
            fill: #6b7280;
        }}

        .title {{
            font-size: 18px;
            font-weight: 600;
            fill: #1f2937;
            text-anchor: middle;
        }}

        .subtitle {{
            font-size: 12px;
            fill: #6b7280;
            text-anchor: middle;
        }}

        .footer {{
            font-size: 9px;
            fill: #6b7280;
            text-anchor: middle;
        }}
    </style>
</head>
<body>
    <div id="container">
        <button id="export-btn" onclick="exportToPNG()">📥 Export as PNG</button>
        <div id="chart"></div>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
        // Chart data
        const data = {data_json};

        // Configuration
        const margin = {{ top: 140, right: 100, bottom: 100, left: 350 }};
        const width = Math.min(window.innerWidth - 40, 1600) - margin.left - margin.right;
        const rowHeight = 60;
        const barHeight = 15;
        const height = data.actors.length * rowHeight;

        // Create SVG
        const svg = d3.select("#chart")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);

        const g = svg.append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

        // Parse dates
        const parseDate = d3.timeParse("%Y-%m-%d");
        const parseDateFlexible = (dateStr) => {{
            if (dateStr.length === 4) return parseDate(dateStr + "-01-01");
            if (dateStr.length === 7) return parseDate(dateStr + "-01");
            return parseDate(dateStr);
        }};

        // Get date range
        const allDates = data.bar_events.flatMap(e => [parseDateFlexible(e.start), parseDateFlexible(e.end)]);
        const minDate = d3.min(allDates);
        const maxDate = d3.max(allDates);

        // Scales
        const xScale = d3.scaleTime()
            .domain([minDate, maxDate])
            .range([0, width]);

        const yScale = d3.scaleBand()
            .domain(data.actors)
            .range([0, height])
            .padding(0.3);

        // Add grid lines
        const xAxis = d3.axisBottom(xScale)
            .ticks(d3.timeMonth.every(3))
            .tickFormat(d3.timeFormat("%b %Y"));

        g.append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0,${{height}})`)
            .call(xAxis)
            .selectAll("text")
            .attr("class", "axis-label")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");

        // Add vertical grid lines
        g.append("g")
            .attr("class", "grid")
            .selectAll("line")
            .data(xScale.ticks(d3.timeMonth.every(3)))
            .enter()
            .append("line")
            .attr("class", "grid-line")
            .attr("x1", d => xScale(d))
            .attr("x2", d => xScale(d))
            .attr("y1", 0)
            .attr("y2", height);

        // Add horizontal grid lines between rows
        data.actors.forEach((actor, i) => {{
            if (i > 0) {{
                g.append("line")
                    .attr("class", "grid-line")
                    .attr("x1", 0)
                    .attr("x2", width)
                    .attr("y1", yScale(actor))
                    .attr("y2", yScale(actor));
            }}
        }});

        // Add Y-axis labels
        const yAxis = g.append("g")
            .attr("class", "y-axis");

        data.actors.forEach(actor => {{
            const isHighlighted = data.actor_highlights[actor];
            const color = isHighlighted ? data.actor_highlights[actor].color : '#1f2937';
            const fontWeight = isHighlighted ? 600 : 400;

            yAxis.append("text")
                .attr("class", "actor-label")
                .attr("x", -10)
                .attr("y", yScale(actor) + yScale.bandwidth() / 2)
                .attr("dy", "0.35em")
                .attr("text-anchor", "end")
                .attr("fill", color)
                .attr("font-weight", fontWeight)
                .text(actor);
        }});

        // Add milestone lines FIRST (so they're behind bars)
        data.milestone_events.forEach(milestone => {{
            const x = xScale(parseDateFlexible(milestone.start));

            // Vertical dotted line
            g.append("line")
                .attr("class", "milestone-line")
                .attr("x1", x)
                .attr("x2", x)
                .attr("y1", -20)
                .attr("y2", height);

            // Label at top
            g.append("text")
                .attr("class", "milestone-label")
                .attr("x", x + 5)
                .attr("y", -25)
                .attr("transform", `rotate(-45,${{x + 5}},-25)`)
                .text(milestone.action);
        }});

        // Add bars
        const bars = g.selectAll(".bar")
            .data(data.bar_events)
            .enter()
            .append("g")
            .attr("class", "bar");

        bars.append("rect")
            .attr("class", "bar-rect")
            .attr("x", d => xScale(parseDateFlexible(d.start)))
            .attr("y", d => yScale(d.actor) + (yScale.bandwidth() - barHeight) / 2)
            .attr("width", d => xScale(parseDateFlexible(d.end)) - xScale(parseDateFlexible(d.start)))
            .attr("height", barHeight)
            .attr("fill", d => d.color)
            .attr("rx", 3)
            .attr("ry", 3);

        // Add duration labels
        bars.append("text")
            .attr("class", "duration-label")
            .attr("x", d => (xScale(parseDateFlexible(d.start)) + xScale(parseDateFlexible(d.end))) / 2)
            .attr("y", d => yScale(d.actor) + yScale.bandwidth() / 2 + 4)
            .text(d => d.duration_label);

        // Hover tooltips
        const tooltip = d3.select("#tooltip");

        bars.on("mouseover", function(event, d) {{
            let html = `<strong>${{d.actor}}</strong>`;
            html += `<br>Role: ${{d.roleType}}`;
            html += `<br>Action: ${{d.action}}`;
            if (d.target) html += `<br>Target: ${{d.target}}`;
            html += `<br>Period: ${{d.start}} to ${{d.end}}`;
            html += `<br>Duration: ${{d.duration_label}}`;
            html += `<br>Context: ${{d.context}}`;
            if (d.highlight_reason) {{
                html += `<br><br><strong>Legal Note:</strong> ${{d.highlight_reason}}`;
            }}

            tooltip.html(html)
                .classed("visible", true)
                .style("left", (event.pageX + 15) + "px")
                .style("top", (event.pageY - 15) + "px");
        }})
        .on("mousemove", function(event) {{
            tooltip.style("left", (event.pageX + 15) + "px")
                .style("top", (event.pageY - 15) + "px");
        }})
        .on("mouseout", function() {{
            tooltip.classed("visible", false);
        }});

        // Add title
        const titleY = -100;
        svg.append("text")
            .attr("class", "title")
            .attr("x", (width + margin.left + margin.right) / 2)
            .attr("y", titleY)
            .text(data.case.name);

        // Add subtitle
        let subtitle = "";
        if (data.case.type) subtitle += data.case.type;
        if (data.case.id) subtitle += (subtitle ? " • " : "") + `CASE NO. ${{data.case.id}}`;

        if (subtitle) {{
            svg.append("text")
                .attr("class", "subtitle")
                .attr("x", (width + margin.left + margin.right) / 2)
                .attr("y", titleY + 20)
                .text(subtitle);
        }}

        // Add stats
        let stats = "";
        if (data.stats.date_range) stats += data.stats.date_range;
        if (data.stats.actor_count) stats += (stats ? " • " : "") + `${{data.stats.actor_count}} stakeholders`;
        if (data.stats.milestone_count) stats += (stats ? " • " : "") + `${{data.stats.milestone_count}} key milestones`;

        if (stats) {{
            svg.append("text")
                .attr("class", "subtitle")
                .attr("x", (width + margin.left + margin.right) / 2)
                .attr("y", titleY + 40)
                .text(stats);
        }}

        // Add legend
        const legendY = titleY + 65;
        const legendItems = Object.entries(data.legend_items);
        const legendSpacing = 120;
        const legendStartX = (width + margin.left + margin.right) / 2 - (legendItems.length * legendSpacing) / 2;

        legendItems.forEach(([role, color], i) => {{
            const x = legendStartX + i * legendSpacing;

            svg.append("rect")
                .attr("x", x)
                .attr("y", legendY - 5)
                .attr("width", 10)
                .attr("height", 10)
                .attr("fill", color)
                .attr("rx", 2);

            svg.append("text")
                .attr("class", "legend-item")
                .attr("x", x + 15)
                .attr("y", legendY + 3)
                .text(role);
        }});

        // Add footer
        if (data.footer_text) {{
            svg.append("text")
                .attr("class", "footer")
                .attr("x", (width + margin.left + margin.right) / 2)
                .attr("y", height + margin.top + margin.bottom - 20)
                .text(data.footer_text);
        }}

        // PNG Export function
        function exportToPNG() {{
            const button = document.getElementById('export-btn');
            button.textContent = '⏳ Exporting...';
            button.disabled = true;

            html2canvas(document.getElementById('container'), {{
                scale: 2,
                backgroundColor: '#ffffff'
            }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = '{data["case"]["name"].replace(" ", "_")}_timeline.png';
                link.href = canvas.toDataURL('image/png');
                link.click();

                button.textContent = '📥 Export as PNG';
                button.disabled = false;
            }});
        }}
    </script>
</body>
</html>'''

        return html
