#!/usr/bin/env python3
"""Test Phase 2: Claude-driven visualization intelligence with TechVira case"""

from models import Event, CaseMetadata, TimelineData, VisualizationConfig
from visualizer import GanttVisualizer

# Create TechVira test data with Phase 2 VisualizationConfig
events = [
    # QUALIFIED EXECUTIVES (should be normal colors)
    Event(
        actor="Dr. Eleanor Park",
        action="served as CSO",
        target="TechVira Pharmaceuticals",
        roleType="Scientific Leadership",
        start="2019-06-15",
        end="2021-09-15",
        context="PhD Stanford Biochemistry, 15 years experience. Terminated after raising data integrity concerns.",
        milestone=False
    ),
    Event(
        actor="Marcus Hale",
        action="served as CFO",
        target="TechVira Pharmaceuticals",
        roleType="Executive Leadership",
        start="2019-01-01",
        end="2023-04-03",
        context="CPA, MBA Wharton. Resigned citing 'compliance fatigue' and disagreements with CEO.",
        milestone=False
    ),
    Event(
        actor="Dr. Sophia Martinez",
        action="served as VP Clinical Operations",
        target="TechVira Pharmaceuticals",
        roleType="Clinical Operations",
        start="2018-03-01",
        end="2022-12-20",
        context="MD, 20 years pharma experience. Terminated following disagreements over trial protocols.",
        milestone=False
    ),

    # UNQUALIFIED REPLACEMENTS (should be RED)
    Event(
        actor="Michael Brandenburg",
        action="served as CFO",
        target="TechVira Pharmaceuticals",
        roleType="Executive Leadership",
        start="2023-04-15",
        end="2024-08-01",
        context="NO finance background. College roommate of CEO. Replaced Marcus Hale.",
        milestone=False
    ),
    Event(
        actor="Timothy Brooks",
        action="served as CSO",
        target="TechVira Pharmaceuticals",
        roleType="Scientific Leadership",
        start="2021-10-01",
        end="2024-08-01",
        context="Bachelor's degree only, no research experience. Personal friend of CEO. Replaced Dr. Park.",
        milestone=False
    ),
    Event(
        actor="Gregory Patterson",
        action="served as VP Clinical Operations",
        target="TechVira Pharmaceuticals",
        roleType="Clinical Operations",
        start="2023-01-15",
        end="2024-08-01",
        context="Marketing background, no clinical experience. Former business partner of CEO.",
        milestone=False
    ),

    # OTHER EXECUTIVES
    Event(
        actor="Rebecca Stone",
        action="served as General Counsel",
        target="TechVira Pharmaceuticals",
        roleType="Legal Compliance",
        start="2018-01-01",
        end="2024-08-01",
        context="JD Harvard, 12 years pharma legal experience.",
        milestone=False
    ),
    Event(
        actor="James Whitmore",
        action="served as CEO",
        target="TechVira Pharmaceuticals",
        roleType="Executive Leadership",
        start="2017-06-01",
        end="2024-08-01",
        context="MBA Stanford, former biotech entrepreneur. Central figure in investigation.",
        milestone=False
    ),

    # KEY MILESTONES (vertical lines - only 3)
    Event(
        actor="Whistleblower",
        action="filed formal complaint",
        target="TechVira Pharmaceuticals",
        roleType="Legal",
        start="2023-03-15",
        end=None,
        context="Anonymous employee reported data manipulation and unqualified appointments to SEC.",
        milestone=True
    ),
    Event(
        actor="SEC",
        action="initiated formal investigation",
        target="TechVira Pharmaceuticals",
        roleType="Regulatory Agency",
        start="2023-10-01",
        end=None,
        context="SEC opened formal investigation into securities fraud following whistleblower complaint.",
        milestone=True
    ),
    Event(
        actor="FDA",
        action="issued warning letter",
        target="TechVira Pharmaceuticals",
        roleType="Regulatory Agency",
        start="2024-02-12",
        end=None,
        context="FDA cited manufacturing violations and inadequate quality controls.",
        milestone=True
    ),
]

case = CaseMetadata(
    name="TechVira Pharmaceuticals Leadership Timeline",
    id="SEC-2024-8892",
    type="Securities Fraud Investigation",
    start="2019-01-01",
    end="2024-08-01"
)

# Phase 2: Claude's visualization intelligence
from models import ActorHighlight

viz_config = VisualizationConfig(
    focus_actors=None,  # Show all actors
    key_milestone_events=["filed formal complaint", "initiated formal investigation", "issued warning letter"],
    actor_highlights=[
        ActorHighlight(name="Michael Brandenburg", color="#ef4444", reason="Unqualified CFO replacement - no finance background, CEO's college roommate"),
        ActorHighlight(name="Timothy Brooks", color="#ef4444", reason="Unqualified CSO replacement - Bachelor's degree only, no research experience, CEO's personal friend"),
        ActorHighlight(name="Gregory Patterson", color="#ef4444", reason="Unqualified VP Clinical Operations - marketing background, no clinical experience, CEO's business partner")
    ],
    sort_strategy="chronological",
    footer_analysis="⚠ Pattern detected: 3 qualified executives (Park, Hale, Martinez) systematically replaced with underqualified CEO associates during 2021-2023 period, preceding regulatory scrutiny",
    document_type="fraud_investigation",
    visualization_rationale="Highlighting unqualified replacements in red to show systematic pattern of cronyism"
)

timeline_data = TimelineData(case=case, events=events, visualization_config=viz_config)

# Test visualization
print("[TEST] Creating Phase 2 visualizer...")
visualizer = GanttVisualizer()

print("[TEST] Generating color map...")
from extractor import EventExtractor
extractor = EventExtractor(api_key="dummy")  # Just for color palette generation
color_map = extractor.generate_color_palette(events)

print("[TEST] Generating Gantt chart with Phase 2 intelligence...")
print("  - Expecting RED bars for: Michael Brandenburg, Timothy Brooks, Gregory Patterson")
print("  - Expecting 3 milestone vertical lines only")
print("  - Expecting Claude's footer analysis about pattern detection")

try:
    output_path = visualizer.generate_gantt(timeline_data, color_map, "output/techvira_phase2.png")
    print(f"[SUCCESS] Phase 2 chart generated at: {output_path}")
    print("\nVerify the chart shows:")
    print("  ✓ 8 stakeholders as horizontal bars")
    print("  ✓ 3 actors highlighted in RED (Brandenburg, Brooks, Patterson)")
    print("  ✓ Only 3 milestone vertical lines")
    print("  ✓ Footer shows pattern analysis about qualified executives being replaced")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
