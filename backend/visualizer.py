import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict
import os
from models import TimelineData, Event

class GanttVisualizer:
    def __init__(self):
        self.fig_width = 1600
        self.fig_height = 900
        self.output_format = "html"  # Default to interactive HTML

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

    def generate_gantt(self, timeline_data: TimelineData, color_map: Dict[str, str], output_path: str = "output/timeline.png") -> str:
        """
        Generate professional Gantt chart using Plotly - matches NexVira template exactly.

        Key features:
        - Horizontal bars for employment/tenure periods (Y-axis = people, X-axis = timeline)
        - Milestone markers as vertical lines with annotations
        - Color-coded by role type
        - Duration labels on bars
        - Professional dark theme
        """

        events = timeline_data.events
        case = timeline_data.case
        viz_config = timeline_data.visualization_config

        # Separate duration events (bars) from point events (milestones)
        bar_events = [e for e in events if e.end is not None]
        milestone_events = [e for e in events if e.milestone or e.end is None]

        # Apply Claude's visualization config
        if viz_config:
            # Filter to focus actors if specified (e.g., "show executives only")
            if viz_config.focus_actors:
                bar_events = [e for e in bar_events if e.actor in viz_config.focus_actors]

            # Filter milestones to only key ones
            if viz_config.key_milestone_events:
                milestone_events = [e for e in milestone_events if e.action in viz_config.key_milestone_events]

        if not bar_events:
            raise ValueError("No events with duration found. Need start AND end dates for bars.")

        # Build actor list (one row per person/entity)
        actors = []
        seen = set()
        for event in bar_events:
            if event.actor not in seen:
                actors.append(event.actor)
                seen.add(event.actor)

        # Sort actors: suspicious/highlighted actors go to BOTTOM, normal actors at TOP
        # This creates visual grouping where concerning actors are grouped together at bottom
        if viz_config and viz_config.actor_highlights:
            highlighted_names = {h.name for h in viz_config.actor_highlights}
            normal_actors = [a for a in actors if a not in highlighted_names]
            suspicious_actors = [a for a in actors if a in highlighted_names]
            # Normal actors first (will be at top), suspicious at end (will be at bottom)
            actors = normal_actors + suspicious_actors

        # Reverse so first person appears at top
        actors = actors[::-1]
        actor_to_y = {actor: i for i, actor in enumerate(actors)}

        # Build colored actor names for Y-axis (actors with highlights get colored names)
        colored_actor_names = []
        actor_colors_map = {}  # Map actor name -> color for Y-axis labels

        if viz_config and viz_config.actor_highlights:
            for actor in actors:
                # Check if this actor has a highlight
                highlight_color = None
                for highlight in viz_config.actor_highlights:
                    if highlight.name == actor:
                        highlight_color = highlight.color
                        break

                if highlight_color:
                    # Color this actor name
                    actor_colors_map[actor] = highlight_color
                    colored_actor_names.append(f'<span style="color:{highlight_color}"><b>{actor}</b></span>')
                else:
                    actor_colors_map[actor] = '#1f2937'  # Dark gray for non-highlighted
                    colored_actor_names.append(actor)
        else:
            # No highlights - all names are dark gray
            colored_actor_names = actors
            actor_colors_map = {actor: '#1f2937' for actor in actors}

        # Create figure
        fig = go.Figure()

        # Add horizontal bars as rectangles
        for event in bar_events:
            y_pos = actor_to_y[event.actor]
            start_dt = self.parse_date(event.start)
            end_dt = self.parse_date(event.end)

            duration_label = self.calculate_duration_label(event.start, event.end)

            # Apply Claude's legal highlighting (flexible colors based on legal analysis)
            highlight_reason = None
            if viz_config and viz_config.actor_highlights:
                # Find if this actor has a highlight directive from Claude
                for highlight in viz_config.actor_highlights:
                    if highlight.name == event.actor:
                        color = highlight.color
                        highlight_reason = highlight.reason
                        break
                else:
                    # No highlight - use default color map
                    color = color_map.get(event.roleType, "#3b82f6")
            else:
                # No viz config - use default color map
                color = color_map.get(event.roleType, "#3b82f6")

            # Add rectangle for the bar
            fig.add_shape(
                type="rect",
                x0=start_dt,
                x1=end_dt,
                y0=y_pos - 0.25,
                y1=y_pos + 0.25,
                fillcolor=color,
                line=dict(color='#ffffff', width=1.5),
                opacity=0.85
            )

            # Add duration label annotation
            # Calculate midpoint using total_seconds to avoid timedelta serialization issues
            delta_seconds = (end_dt - start_dt).total_seconds()
            mid_date = start_dt + timedelta(seconds=delta_seconds / 2)

            fig.add_annotation(
                x=mid_date,
                y=y_pos,
                text=duration_label,
                showarrow=False,
                font=dict(color='white', size=11, family='Inter, sans-serif'),
                xanchor='center',
                yanchor='middle'
            )

            # Build hover template with optional legal reasoning
            hover_text = (
                f"<b>{event.actor}</b><br>" +
                f"Role: {event.roleType}<br>" +
                f"Action: {event.action}<br>" +
                f"Period: {event.start} to {event.end}<br>" +
                f"Duration: {duration_label}<br>" +
                f"Context: {event.context}<br>"
            )

            # Add Claude's legal reasoning if this actor is highlighted
            if highlight_reason:
                hover_text += f"<br><b>Legal Note:</b> {highlight_reason}<br>"

            hover_text += "<extra></extra>"

            # Add invisible trace for hover (one per event)
            fig.add_trace(go.Scatter(
                x=[mid_date],
                y=[y_pos],
                mode='markers',
                marker=dict(size=0.1, color=color, opacity=0),
                hovertemplate=hover_text,
                showlegend=False
            ))

        # Add milestone markers (vertical lines with annotations)
        for milestone in milestone_events:
            milestone_dt = self.parse_date(milestone.start)

            # Add vertical line
            fig.add_vline(
                x=milestone_dt,
                line=dict(color='#9ca3af', dash='dot', width=2),  # Gray for white background
                opacity=0.7
            )

            # Add annotation at top
            fig.add_annotation(
                x=milestone_dt,
                y=len(actors) - 0.5,
                text=milestone.action,
                textangle=-45,
                showarrow=False,
                font=dict(size=9, color='#4b5563', family='Inter, sans-serif'),  # Darker gray for readability
                xanchor='left',
                yanchor='bottom'
            )

        # Add horizontal grid lines BETWEEN rows to create lanes (like NexVira)
        # Lines at -0.5, 0.5, 1.5, 2.5, ..., len(actors)-0.5
        for i in range(-1, len(actors)):
            fig.add_hline(
                y=i + 0.5,
                line=dict(color='#d1d5db', width=1),
                opacity=0.5
            )

        # Calculate statistics for header
        actor_count = len(actors)
        milestone_count = len(milestone_events)
        date_range = f"{case.start} to {case.end}" if case.start and case.end else ""

        # Build header with statistics (like NexVira)
        # Use Claude's title override if provided (for cases where standard title insufficient)
        if viz_config and viz_config.title_override:
            title_parts = [f"<b>{viz_config.title_override}</b>"]
        else:
            title_parts = [f"<b>{case.name}</b>"]

        subtitle_parts = []
        if case.type:
            subtitle_parts.append(case.type)
        if case.id:
            subtitle_parts.append(f"CASE NO. {case.id}")
        if subtitle_parts:
            title_parts.append(" • ".join(subtitle_parts))

        # Add statistics line
        stats_parts = []
        if date_range:
            stats_parts.append(date_range)
        if actor_count:
            stats_parts.append(f"{actor_count} stakeholders")
        if milestone_count:
            stats_parts.append(f"{milestone_count} key milestones")
        if stats_parts:
            title_parts.append(" • ".join(stats_parts))

        # Configure layout with WHITE background theme (like NexVira reference)
        fig.update_layout(
            title=dict(
                text="<br>".join(title_parts),
                font=dict(size=18, color='#1f2937', family='Inter, sans-serif'),
                x=0.5,
                xanchor='center',
                y=0.97,
                yanchor='top'
            ),
            xaxis=dict(
                title='Timeline',
                showgrid=True,
                gridcolor='#d1d5db',  # Darker grid for square-by-square effect
                gridwidth=1,
                zeroline=False,
                tickfont=dict(size=9, color='#6b7280', family='Inter, sans-serif'),
                title_font=dict(size=12, color='#374151', family='Inter, sans-serif'),
                type='date',
                dtick='M3',  # Show tick every 3 months (like NexVira: Apr 2019, Jul 2019, Oct 2019...)
                tickformat='%b %Y',  # Format: "Jan 2020", "Apr 2020", etc.
                tickangle=-45  # Angle labels for readability
            ),
            yaxis=dict(
                title='',
                showgrid=False,  # We'll add grid lines manually BETWEEN rows
                zeroline=False,
                tickfont=dict(size=11, family='Inter, sans-serif'),
                tickvals=list(range(len(actors))),
                ticktext=colored_actor_names,  # Use colored names!
                range=[-0.5, len(actors) - 0.5]  # Adjust range to center bars in lanes
            ),
            plot_bgcolor='#ffffff',  # WHITE background
            paper_bgcolor='#f9fafb',  # Very light gray paper
            font=dict(family='Inter, sans-serif', color='#1f2937'),
            height=max(600, len(actors) * 60 + 200),
            width=self.fig_width,
            margin=dict(l=350, r=100, t=140, b=100),  # Much more left margin (350px) for spacing between names and bars
            hovermode='closest'
        )

        # Add legend for role types
        legend_items = {}
        for event in bar_events:
            if event.roleType not in legend_items:
                legend_items[event.roleType] = color_map.get(event.roleType, "#3b82f6")

        # AUTO-DETECT: If Claude flagged suspicious actors, add ONE "Suspicious Appointment" entry
        # This is Claude's decision entirely - nothing hardcoded
        if viz_config and viz_config.actor_highlights:
            # Just add one entry - use red color as default
            legend_items["⚠ Suspicious Appointment"] = "#ef4444"

        # Add invisible traces for legend
        for role, color in sorted(legend_items.items()):
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color=color, symbol='square'),
                name=role,
                showlegend=True
            ))

        # Position legend at top center in horizontal row - NO BOX (like NexVira)
        fig.update_layout(
            legend=dict(
                title=dict(text='Role Types', font=dict(size=10, color='#6b7280')),
                font=dict(size=9, color='#6b7280', family='Inter, sans-serif'),
                bgcolor='rgba(0,0,0,0)',  # Transparent background - NO BOX
                bordercolor='rgba(0,0,0,0)',  # No border
                borderwidth=0,
                orientation='h',  # Horizontal orientation
                x=0.5,  # Center horizontally
                y=1.04,  # Position just below stats line
                xanchor='center',
                yanchor='bottom'
            )
        )

        # Add footer analysis note (like NexVira pattern explanation)
        # Use Claude's analysis if available, otherwise fallback to automatic detection
        footer_text = None

        if viz_config and viz_config.footer_analysis:
            # Use Claude's intelligent pattern analysis
            footer_text = viz_config.footer_analysis
        else:
            # Fallback: Analyze patterns in the data automatically
            terminations = [e for e in bar_events if 'terminated' in e.context.lower() or 'resigned' in e.context.lower()]
            replacements = [e for e in bar_events if 'replacement' in e.action.lower() or 'interim' in e.action.lower()]

            footer_notes = []
            if terminations:
                footer_notes.append(f"⚠ {len(terminations)} leadership changes during investigation period")
            if replacements:
                footer_notes.append(f"Note: {len(replacements)} interim/replacement appointments")
            if milestone_events:
                footer_notes.append(f"Key milestones: {', '.join([m.action for m in milestone_events[:3]])}")

            if footer_notes:
                footer_text = " • ".join(footer_notes)

        if footer_text:
            fig.add_annotation(
                text=footer_text,
                xref="paper",
                yref="paper",
                x=0.5,
                y=-0.1,
                xanchor='center',
                yanchor='top',
                showarrow=False,
                font=dict(size=9, color='#6b7280', family='Inter, sans-serif'),  # Dark gray for white background
                align='center'
            )

        # Save BOTH HTML (for viewing) and PNG (for downloading)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        html_path = output_path.replace('.png', '.html')
        png_path = output_path

        # 1. Save interactive HTML for display
        config = {
            'displayModeBar': False,  # Hide entire Plotly toolbar
            'displaylogo': False,
            'responsive': True
        }
        fig.write_html(html_path, config=config)
        print(f"[SUCCESS] Interactive HTML saved to {html_path}")

        # 2. Save static PNG for download
        chart_height = max(600, len(actors) * 60 + 200)
        fig.write_image(png_path, width=self.fig_width, height=chart_height, scale=2)
        print(f"[SUCCESS] PNG saved to {png_path}")

        # Return both paths as tuple (html_path, png_path)
        return (html_path, png_path)
