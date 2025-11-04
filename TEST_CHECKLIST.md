# NexVira Test Document - End-to-End Verification Checklist

## Test Document Created
✅ **File**: `/Users/sehpark/Downloads/litigation/test_nexvira_complete.pdf`

## What the Test Document Contains

### Stakeholders (11 total)
1. **Dr. Amanda Chen** - CEO/CSO (March 2019 - Sept 2021) - QUALIFIED, terminated after raising concerns
2. **Marcus Wellington** - CFO (Jan 2020 - April 2023) - QUALIFIED, resigned citing compliance issues
3. **Dr. Sarah Park** - VP Clinical Ops (June 2020 - Dec 2022) - QUALIFIED, terminated after flagging safety concerns
4. **Jennifer Kowalski** - General Counsel (April 2020 - March 2024) - QUALIFIED, resigned over governance issues
5. **Dr. Robert Pemberton** - CTO (Feb 2019 - Present) - QUALIFIED, marginalized but still employed
6. **Catherine Morris** - VP Clinical Ops (March 2020 - Jan 2023) - QUALIFIED, terminated after Dr. Park
7. **David Tran** - VP Regulatory Affairs (Aug 2020 - Present) - QUALIFIED, marginalized but still employed
8. **James Whitmore** - CEO (Sept 2021 - Present, previously COO from Jan 2019) - Central figure in investigation
9. **Michael Brandenburg** - VP Clinical Ops (Nov 2022 - Present) - ⚠️ UNQUALIFIED (college roommate, marketing degree, no pharma experience)
10. **Timothy Brooks** - General Counsel (March 2024 - Present) - ⚠️ UNQUALIFIED (brother-in-law, unaccredited law school, no regulatory experience)
11. **Gregory Patterson** - CFO (May 2023 - Present) - ⚠️ UNQUALIFIED (brother-in-law, suspended CPA license)
12. **Sophia Ramirez** - VP Regulatory Affairs (Sept 2023 - Present) - ⚠️ CO-OPTED (qualified but promoted after showing loyalty)

### Key Milestones (7 total)
1. **Phase II Clinical Trial Begins** - Jan 15, 2019
2. **Phase II Trial Safety Concerns Identified** - June 10, 2021
3. **Whistleblower Complaint Filed** - March 15, 2023
4. **SEC Formal Investigation Initiated** - Oct 1, 2023
5. **FDA Warning Letter Issued** - Feb 12, 2024
6. **Financial Restatement Announced** - May 20, 2024
7. **Product Recall and Trial Suspension** - July 8, 2024

### Pattern to Detect
- **Systematic replacement of qualified executives with unqualified CEO associates**
- **Timeline**: Sept 2021 (Dr. Chen terminated) → May 2023 (Patterson appointed CFO)
- **4 Suspicious Actors**: Brandenburg, Brooks, Patterson, Ramirez
- **Personal Connections**: College roommate, brother-in-law (2x), loyalty-based promotion

## Expected System Behavior

### Phase 1: Document Analysis (Claude AI)
When user uploads `test_nexvira_complete.pdf` with request "stakeholders":

✅ **Should Recognize**:
- Document type: Securities fraud investigation
- Case metadata: CASE NO. 2024-CV-8892, "NexVira Therapeutics Leadership Timeline"
- Date range: March 2019 - August 2024

✅ **Should Extract**:
- All 11 stakeholders with accurate employment periods
- All 7 milestone events as vertical lines
- Role types: Executive Leadership, Scientific Leadership, Clinical Operations, Legal Compliance, etc.

✅ **Should Identify Suspicious Actors** (CRITICAL):
- **Michael Brandenburg** - Red highlight (unqualified replacement, college roommate)
- **Timothy Brooks** - Red highlight (unqualified replacement, brother-in-law, unaccredited degree)
- **Gregory Patterson** - Red highlight (unqualified replacement, brother-in-law, suspended license)
- **Sophia Ramirez** - Red/Orange highlight (co-opted after showing loyalty)

✅ **Should NOT Highlight** (CRITICAL):
- Dr. Sarah Park (whistleblower)
- Dr. Amanda Chen (raised concerns)
- Marcus Wellington (compliance champion)
- Jennifer Kowalski (resigned over governance)
- Dr. Robert Pemberton, Catherine Morris, David Tran (qualified professionals)

✅ **Should Generate VisualizationConfig**:
```json
{
  "focus_actors": null,  // Show all stakeholders
  "key_milestone_events": [
    "Phase II Clinical Trial Begins",
    "Whistleblower Complaint Filed",
    "SEC Formal Investigation Initiated",
    "FDA Warning Letter Issued",
    "Product Recall and Trial Suspension"
  ],
  "actor_highlights": [
    {
      "name": "Michael Brandenburg",
      "color": "#ef4444",
      "reason": "Unqualified VP Clinical Operations - Bachelor's in Marketing, no pharma experience, CEO's college roommate"
    },
    {
      "name": "Timothy Brooks",
      "color": "#ef4444",
      "reason": "Unqualified General Counsel - Unaccredited law school, no regulatory experience, CEO's brother-in-law"
    },
    {
      "name": "Gregory Patterson",
      "color": "#ef4444",
      "reason": "Unqualified CFO - Suspended CPA license, CEO's brother-in-law"
    },
    {
      "name": "Sophia Ramirez",
      "color": "#f97316",
      "reason": "Qualified but co-opted - Promoted after demonstrating loyalty to CEO"
    }
  ],
  "footer_analysis": "⚠ Pattern detected: 4 qualified executives (Chen, Park, Morris, Wellington) systematically replaced with underqualified CEO associates during Sept 2021 - May 2023 period, immediately preceding regulatory scrutiny",
  "document_type": "fraud_investigation"
}
```

### Phase 2: Visualization Generation

✅ **Layout**:
- White background (#ffffff)
- Square grid pattern (gridlines between lanes)
- Each actor in their own horizontal lane (bars BETWEEN gridlines, not ON them)
- Actor names on left aligned with center of their lane
- 350px left margin for spacing between names and bars

✅ **Actor Sorting**:
- Normal actors at TOP: Dr. Chen, Wellington, Dr. Park, Kowalski, Dr. Pemberton, Morris, Tran, Whitmore
- Suspicious actors GROUPED AT BOTTOM: Brandenburg, Brooks, Patterson, Ramirez

✅ **Colored Elements** (CRITICAL):
- Brandenburg: RED bar + RED name on left
- Brooks: RED bar + RED name on left
- Patterson: RED bar + RED name on left
- Ramirez: ORANGE bar + ORANGE name on left
- All other actors: Neutral muted colors (blue, green, brown) + dark gray names (#1f2937)

✅ **Milestone Markers**:
- 5-7 vertical dotted gray lines (#9ca3af) at key dates
- Annotations at top with rotated text (-45°)
- Examples: "Phase II Trial Begins", "Whistleblower Complaint Filed", etc.

✅ **Duration Labels**:
- On each bar: "2y 6m", "1y 10m", etc.
- Example: Catherine Morris should show "2y 10m" (March 2020 - Jan 2023)

✅ **Timeline Overlap Visibility**:
- Michael Brandenburg (Nov 2022 start) overlaps with Catherine Morris (Jan 2023 end)
- Visual should show Brandenburg joined 2 months BEFORE Morris left
- This timing pattern should be clearly visible in the chart

✅ **Header**:
- Title: "NexVira Therapeutics Leadership Timeline"
- Subtitle: "Securities Fraud Investigation • CASE NO. 2024-CV-8892"
- Stats: "March 1, 2019 to August 1, 2024 • 11 stakeholders • 5-7 key milestones"

✅ **Legend**:
- Top center, horizontal layout
- NO BOX (transparent background, no border)
- Shows role types with colored squares: Executive Leadership, Scientific Leadership, Clinical Operations, etc.

✅ **Footer**:
- Pattern analysis explaining the systematic replacement
- Example: "⚠ Pattern detected: 4 qualified executives systematically replaced with underqualified CEO associates during Sept 2021 - May 2023 period"

✅ **Colors** (Neutral, Muted Palette):
- Role colors: #6b9bd1 (blue), #7cb89d (green/teal), #b08968 (brown), etc.
- Suspicious highlights: #ef4444 (red), #f97316 (orange)
- Background: #ffffff (white)
- Grid: #d1d5db (light gray)

## Test Procedure

### Step 1: Upload PDF
1. Open frontend at http://localhost:3000 or http://localhost:5173
2. Upload `/Users/sehpark/Downloads/litigation/test_nexvira_complete.pdf`
3. Enter request: "stakeholders"

### Step 2: Monitor Processing
Watch the streaming progress:
- ✅ Document loaded
- ✅ Text extraction (should show ~13,000 words)
- ✅ Claude AI analysis (should show thinking process)
- ✅ Event extraction (should find 11 actors, 5-7 milestones)
- ✅ Visualization generation
- ✅ Chart complete

### Step 3: Verify Chart Output
Open generated chart at `/Users/sehpark/Downloads/litigation/backend/output/timeline.png`

**Visual Inspection Checklist**:
- [ ] White background with square grid pattern
- [ ] 11 horizontal lanes (one per stakeholder)
- [ ] 4 actors at bottom with RED bars and RED names (Brandenburg, Brooks, Patterson) + 1 ORANGE (Ramirez)
- [ ] All other actors have neutral colors and dark gray names
- [ ] 5-7 vertical dotted lines at milestone dates
- [ ] Duration labels on each bar (e.g., "2y 10m")
- [ ] Legend at top center without box
- [ ] Footer with pattern analysis
- [ ] Header with case info and statistics
- [ ] Bars sit BETWEEN gridlines in their own lanes
- [ ] Names on left are centered in lanes
- [ ] Brandenburg bar starts before Morris bar ends (overlap visible)

### Step 4: Verify Data Accuracy
Check specific details:
- [ ] Catherine Morris: March 1, 2020 - January 5, 2023 (Duration: ~2y 10m)
- [ ] Michael Brandenburg: November 1, 2022 - August 1, 2024 (Duration: ~1y 9m)
- [ ] Overlap: Brandenburg starts 2 months before Morris leaves
- [ ] Dr. Sarah Park: NOT highlighted (she's a whistleblower, not suspicious)
- [ ] Pattern analysis mentions "Sept 2021 - May 2023" replacement period

## What Can Go Wrong (Previous Issues)

### Issue 1: Wrong Actors Highlighted
❌ **Problem**: Dr. Sarah Park highlighted yellow (she's a good whistleblower)
✅ **Fix**: Updated Claude prompt with CRITICAL rules to ONLY highlight suspicious actors

### Issue 2: Actors Not Grouped
❌ **Problem**: Suspicious actors scattered throughout chart
✅ **Fix**: Sorting logic groups suspicious actors at bottom

### Issue 3: Bars On Gridlines
❌ **Problem**: Bars sitting on gridlines instead of in lanes
✅ **Fix**: Disabled auto-grid, added manual horizontal lines at half-integer positions

### Issue 4: Harsh Colors
❌ **Problem**: Neon colors harsh on eyes
✅ **Fix**: Changed to neutral, muted palette (#6b9bd1, #7cb89d, etc.)

### Issue 5: Legend in Box
❌ **Problem**: Legend had gray background and border
✅ **Fix**: Made legend transparent with no border

### Issue 6: User Request Not Respected
❌ **Problem**: "Focus on regulatory events" showed all 10 people instead of filtering
✅ **Fix**: Added CRITICAL instructions in Claude prompt to filter based on user intent

## Backend Code Files Involved

### `/Users/sehpark/Downloads/litigation/backend/extractor.py`
- Lines 69-80: Mandatory milestone events (3-5 required)
- Lines 96-101: CRITICAL user request filtering
- Lines 103-111: CRITICAL highlighting rules (ONLY suspicious actors)
- Lines 206-227: Neutral color palette

### `/Users/sehpark/Downloads/litigation/backend/visualizer.py`
- Lines 83-90: Group suspicious actors at bottom
- Lines 96-119: Colored actor names for flagged actors only
- Lines 224-231: Manual horizontal gridlines between lanes
- Lines 287-294: Y-axis configuration for lane-based layout
- Lines 315-329: Legend without box
- Lines 296-302: White background theme

### `/Users/sehpark/Downloads/litigation/backend/models.py`
- ActorHighlight: Flexible highlighting with color and legal reasoning
- VisualizationConfig: Claude's visualization directives
- TimelineData: Complete data structure for visualization

## Success Criteria

✅ **System successfully handles the NexVira scenario if**:
1. All 11 stakeholders extracted with accurate dates
2. 5-7 milestone vertical lines appear
3. ONLY 4 suspicious actors highlighted (Brandenburg, Brooks, Patterson, Ramirez)
4. Suspicious actors grouped at bottom with red bars and red names
5. Whistleblowers and compliance champions NOT highlighted
6. Pattern analysis appears in footer explaining Sept 2021 - May 2023 replacements
7. Chart uses white background with neutral colors
8. Bars sit in lanes between gridlines
9. Duration calculations accurate (e.g., Catherine Morris = 2y 10m)
10. Timing overlaps visible (Brandenburg starts before Morris leaves)

## Testing Dynamic Requests

After verifying the base "stakeholders" request, test these variations:

### Test 2: "Focus on regulatory events"
**Expected**: Should show ONLY:
- David Tran (VP Regulatory Affairs)
- Sophia Ramirez (VP Regulatory Affairs)
- Key milestones: FDA Warning Letter, SEC Investigation, Product Recall

### Test 3: "Show executives only"
**Expected**: Should show ONLY C-suite:
- Dr. Amanda Chen (CEO/CSO)
- James Whitmore (CEO)
- Marcus Wellington (CFO)
- Gregory Patterson (CFO)
- Jennifer Kowalski (General Counsel)
- Timothy Brooks (General Counsel)

### Test 4: "Analyze clinical operations team"
**Expected**: Should show ONLY:
- Dr. Sarah Park (VP Clinical Ops)
- Catherine Morris (VP Clinical Ops)
- Michael Brandenburg (VP Clinical Ops)
- Milestones: Phase II Trial events

---

**Status**: PDF created ✅
**Next Step**: Upload PDF through frontend and verify all checklist items
**Backend**: Running on port 8000
**Frontend**: Available at localhost:3000 or localhost:5173
