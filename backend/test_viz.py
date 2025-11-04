#!/usr/bin/env python3
"""Quick test script to verify visualization works"""

from models import Event, CaseMetadata, TimelineData
from visualizer import GanttVisualizer

# Create test data
events = [
    Event(
        actor="Dr. Eleanor Park",
        action="served as CSO",
        target="NexVira",
        roleType="Scientific Leadership",
        start="2019-06-15",
        end="2021-09-15",
        context="Terminated after raising data integrity concerns",
        milestone=False
    ),
    Event(
        actor="Marcus Hale",
        action="served as CFO",
        target="NexVira",
        roleType="Financial Leadership",
        start="2019-01-01",
        end="2023-04-03",
        context="Resigned citing compliance fatigue",
        milestone=False
    ),
    Event(
        actor="FDA",
        action="informal inquiry",
        target="NexVira",
        roleType="Regulatory Agency",
        start="2023-03-15",
        end=None,
        context="Inquiry about manufacturing logs",
        milestone=True
    )
]

case = CaseMetadata(
    name="NovExa Therapeutics Leadership Timeline",
    id="2024-CV-10321",
    type="Securities Fraud Investigation",
    start="2019-01-01",
    end="2024-08-01"
)

timeline_data = TimelineData(case=case, events=events)

# Test visualization
print("[TEST] Creating visualizer...")
visualizer = GanttVisualizer()

print("[TEST] Generating color map...")
color_map = {
    "Scientific Leadership": "#06b6d4",
    "Financial Leadership": "#3b82f6",
    "Regulatory Agency": "#ef4444"
}

print("[TEST] Generating Gantt chart...")
try:
    output_path = visualizer.generate_gantt(timeline_data, color_map, "output/test_timeline.png")
    print(f"[SUCCESS] Chart generated at: {output_path}")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
