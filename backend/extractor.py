import anthropic
import json
import os
import asyncio
from typing import List, Dict
from models import Event, CaseMetadata, TimelineData

class EventExtractor:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def extract_events(self, text: str, user_request: str = None) -> TimelineData:
        """
        Extract structured events from legal document text using Claude.

        Args:
            text: Raw text from legal document
            user_request: Optional specific request like "analyze executives" or "show stakeholder timeline"

        Returns:
            TimelineData with metadata and structured events
        """

        # Build user context
        user_context = f"\n\n**User Request**: {user_request}" if user_request else "\n\n**User Request**: General stakeholder timeline analysis"

        prompt = f"""You are an expert timeline analyst. Your goal: Read this document like a human analyst, understand what the user wants to visualize, then create a Gantt chart that tells the story.

{user_context}

================================================================================
STEP 1: UNDERSTAND THE USER'S REQUEST
================================================================================

The user tells you WHAT they want to visualize. Common patterns:
- "stakeholders" / "people" → Chart showing PEOPLE on Y-axis (employment timelines)
- "departments" / "divisions" → Chart showing DEPARTMENTS on Y-axis (spending, activity periods)
- "by organization" / "entities" → Chart showing COMPANIES/ENTITIES on Y-axis
- "phases" / "stages" → Chart showing PROJECT PHASES on Y-axis
- "regulatory timeline" → Chart showing REGULATORY ACTORS and key events
- Or ANY other request - be flexible!

Your job: Figure out what "unit" should appear on the Y-axis based on the user's request.

================================================================================
STEP 2: READ THE DOCUMENT AND EXTRACT WHAT'S RELEVANT
================================================================================

Based on what the user requested, extract the relevant information:

**If user wants PEOPLE/STAKEHOLDERS:**
- Extract all people mentioned (executives, employees, regulators, etc.)
- Note their roles, employment periods (start/end dates)
- Identify anyone with problematic qualifications or suspicious backgrounds
- Format: "[Name] - [Title] ([Status])" where status is "Original", "Qualified", or "Unqualified - [Reason]"

**If user wants DEPARTMENTS:**
- Extract department names and their activity periods
- Note spending amounts, budget changes, key initiatives
- Format: "[Department Name]" with roleType describing function

**If user wants ENTITIES/ORGANIZATIONS:**
- Extract organization names and their involvement periods
- Note their role in the case (plaintiff, defendant, regulator, etc.)
- Format: "[Organization Name]" with roleType describing their role

**If user wants PHASES/STAGES:**
- Extract project/case phases (e.g., "Discovery Phase", "Trial Phase", "Appeals")
- Note start/end dates for each phase
- Format: "[Phase Name]" with context explaining what happened

**General principle:** The "actor" field is flexible - it's whatever unit the user wants on the Y-axis.

================================================================================
STEP 3: FIND KEY MILESTONE EVENTS (ALWAYS REQUIRED)
================================================================================

Regardless of what's on the Y-axis, you MUST extract milestone events (however many you deem necessay, but please necessary only) that mark important moments:
- Regulatory actions (investigations, complaints, enforcement)
- Major business events (deals, recalls, restatements)
- Legal events (filings, verdicts, settlements)
- Key dates that matter to the story

These will appear as VERTICAL DOTTED LINES on the chart.

================================================================================
STEP 4: IDENTIFY WHAT TO HIGHLIGHT
================================================================================

Based on the document, identify anything suspicious or problematic:
- **For people**: Unqualified appointments, conflicts of interest, suspicious timing
- **For departments**: Budget irregularities, suspicious activity timing
- **For entities**: Conflicts of interest, problematic relationships
- **For phases**: Delays, problems, irregularities

Highlight these in RED (#ef4444) with a legal explanation of why it matters.

================================================================================
OUTPUT FORMAT
================================================================================

**HORIZONTAL BAR EVENTS** (the main units on Y-axis):

For each unit (person, department, entity, phase), create:
- **actor**: The label for this Y-axis row
  * People: "[Name] - [Title] ([Status])"
  * Departments: "[Department Name]"
  * Entities: "[Organization Name]"
  * Phases: "[Phase Name]"

- **action**: What they did (e.g., "served as CEO", "operated", "managed litigation phase")
- **target**: What they affected (company, project, case)
- **roleType**: Their category/function (adapt to context)
- **start**: Start date (YYYY-MM-DD, YYYY-MM, or YYYY)
- **end**: End date (REQUIRED for bars; use "2024-08-15" if ongoing)
- **context**: 1-2 sentences of background
- **milestone**: false

**MILESTONE EVENTS** (vertical dotted lines):

For 3-5 key events:
- **actor**: Who/what took action
- **action**: What happened
- **target**: Who/what was affected
- **roleType**: Event category ("Regulatory Agency", "Legal Event", "Corporate Event")
- **start**: Exact date (YYYY-MM-DD)
- **end**: null (ALWAYS null)
- **context**: Why it matters
- **milestone**: true

================================================================================
VISUALIZATION STRATEGY
================================================================================

1. **Focus**: Should you show all units or filter to specific ones based on user request?
2. **Highlights**: Which units have problems? Add to actor_highlights with RED color and legal reason
3. **Key milestones**: Which 3-5 events to emphasize?
4. **Footer**: One sentence summarizing the key pattern

Show your reasoning in a <thinking> section before JSON output.

<thinking>
1. What does the user want to visualize? (People? Departments? Entities? Phases? Something else?)
2. What type of document is this? What's the story?
3. What units did I extract for the Y-axis? (List them all)
4. What 3-5 milestone events mark the key moments?
5. Did I find anything suspicious or problematic? What should be highlighted in red and why?
6. Should I show all units or filter to specific ones based on user's request?
7. What's the key pattern to summarize in the footer?
</thinking>

```json
{{
  "case": {{
    "name": "...",
    "id": "...",
    "type": "...",
    "start": "...",
    "end": "..."
  }},
  "events": [
    {{"actor": "...", "action": "...", "target": "...", "roleType": "...", "start": "...", "end": "...", "context": "...", "milestone": false}},
    ...
  ],
  "visualization_config": {{
    "focus_actors": null,
    "key_milestone_events": ["...", "...", "..."],
    "actor_highlights": [
      {{"name": "Person Name - Title (Unqualified - Reason)", "color": "#ef4444", "reason": "Why this is legally significant"}}
    ],
    "sort_strategy": "chronological",
    "title_override": null,
    "footer_analysis": "Pattern summary in 1-2 sentences",
    "document_type": "fraud_investigation",
    "visualization_rationale": "Brief explanation of visualization choice"
  }}
}}
```

================================================================================
DOCUMENT TEXT
================================================================================

{text[:50000]}"""

        # Use Claude 3 Opus with STREAMING for real-time thinking
        print(f"[DEBUG] Using Claude 3 Opus with streaming for extraction...")

        accumulated_text = ""
        thinking_buffer = ""
        in_thinking_block = False

        # Stream response from Claude in REAL-TIME (use synchronous streaming with async yields)
        with self.client.messages.stream(
            model="claude-3-opus-20240229",
            max_tokens=4096,  # Claude Opus maximum
            temperature=0,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        ) as stream:
            for text_chunk in stream.text_stream:
                accumulated_text += text_chunk

                # Yield control to event loop
                await asyncio.sleep(0)

                # Check if we're entering or exiting thinking block
                if "<thinking>" in text_chunk and not in_thinking_block:
                    in_thinking_block = True
                    thinking_buffer = ""
                    continue

                if "</thinking>" in text_chunk and in_thinking_block:
                    in_thinking_block = False
                    # Flush any remaining thinking
                    if thinking_buffer:
                        yield {"type": "thinking", "content": thinking_buffer.strip()}
                        thinking_buffer = ""
                    continue

                # If we're in thinking block, buffer and yield line by line
                if in_thinking_block:
                    thinking_buffer += text_chunk

                    # Yield complete lines as they come
                    while "\n" in thinking_buffer:
                        line, thinking_buffer = thinking_buffer.split("\n", 1)
                        if line.strip():
                            yield {"type": "thinking", "content": line.strip()}
                            await asyncio.sleep(0)  # Yield control after each line

        print(f"[SUCCESS] Claude API streaming completed")

        # Parse final accumulated response
        response_text = accumulated_text

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0].strip()
        else:
            json_str = response_text.strip()

        data = json.loads(json_str)

        # Validate and yield final structured data
        timeline_data = TimelineData(**data)
        yield {"type": "complete", "data": timeline_data}

    def generate_color_palette(self, events: List[Event]) -> Dict[str, str]:
        """
        Generate color palette based on extracted role types.
        Using neutral, muted colors similar to NexVira reference for better readability.
        """
        unique_roles = list(set(event.roleType for event in events))

        # Neutral, muted color palette (like NexVira) - easier on eyes, professional
        colors = [
            "#6b9bd1",  # Muted blue - Executive Leadership
            "#7cb89d",  # Muted green/teal - Technology/Scientific
            "#b08968",  # Muted brown - Legal/Compliance
            "#d4a574",  # Muted tan/beige - Clinical Operations
            "#9b8aad",  # Muted purple - Regulatory Affairs
            "#a8c5d1",  # Soft blue-gray - Finance
            "#c9ada7",  # Soft mauve - Board/Advisory
            "#8fa998",  # Sage green - Operations
            "#b5aa7d",  # Soft olive - HR/Admin
            "#98a8b8",  # Soft slate - Other
        ]

        return {role: colors[i % len(colors)] for i, role in enumerate(unique_roles)}
