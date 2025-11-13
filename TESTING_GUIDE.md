# 🧪 Comprehensive Testing Guide for Research Paper

## Document Purpose
This guide provides step-by-step instructions for testing all features of the Logistics AI Agent and capturing screenshots for your research paper.

---

## 📋 Table of Contents
1. [Setup & Prerequisites](#setup--prerequisites)
2. [Feature 1: Natural Language AI Agent with Route Avoidance](#feature-1-natural-language-ai-agent-with-route-avoidance)
3. [Feature 2: Constraint-Aware Optimization](#feature-2-constraint-aware-optimization)
4. [Feature 3: Scenario Planning (What-If Analysis)](#feature-3-scenario-planning-what-if-analysis)
5. [Performance Comparison Tests](#performance-comparison-tests)
6. [Screenshots for Paper Figures](#screenshots-for-paper-figures)

---

## Setup & Prerequisites

### Start the System
```bash
# Terminal 1 - Backend
python scripts/start_api.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Access URLs
- **Frontend**: http://localhost:5174
- **Backend API Docs**: http://localhost:8000/docs
- **AI Agent Page**: http://localhost:5174/agent
- **Direct Solver Page**: http://localhost:5174/direct
- **Scenarios Page**: http://localhost:5174/scenarios

### Screenshot Tool
- Use **Browser DevTools** (F12) to set consistent viewport size: 1920x1080
- Or use built-in "Camera" button in the app interface

---

## Feature 1: Natural Language AI Agent with Route Avoidance

### Test Case 1.1: Basic Routing Query

**Where to Put Query**: AI Agent Page (`/agent`)

**Query to Test**:
```
```

**Expected Output**:
- ✅ AI should call tools: `get_orders`, `get_vehicles`, `solve_vrp`, `calculate_route_economics`
- ✅ Response includes:
  - Route summary for each vehicle
  - Total cost breakdown (fuel + labor + fixed)
  - Total distance and time
  - CO2 emissions
  - Formatted with headers, metrics cards, bullet points

**Screenshot to Capture**:
- **Figure 1a**: Full AI response showing formatted output with metrics cards
- **Figure 1b**: Tools Used section showing tool chain

**File Name**: `fig1_basic_routing.png`

---

### Test Case 1.2: Natural Language Route Avoidance

**Where to Put Query**: AI Agent Page (`/agent`)

**Query to Test**:
```
Route 8 deliveries with 2 vehicles but don't use route 4 and route 7
```

**Expected Output**:
- ✅ AI should understand "don't use" and apply route exclusion
- ✅ Orders O004 and O007 should NOT appear in routes
- ✅ Other orders distributed across 2 vehicles
- ✅ Response explains which orders were excluded

**Screenshot to Capture**:
- **Figure 2a**: AI response showing route exclusion acknowledgment
- **Figure 2b**: Routes display showing O004 and O007 are missing
- **Figure 2c**: Detailed route list verifying exclusion

**File Name**: `fig2_route_avoidance.png`

---

### Test Case 1.3: Cold-Chain Priority Routing

**Where to Put Query**: AI Agent Page (`/agent`)

**Query to Test**:
```
Route all cold-chain orders with minimum vehicles, prioritize delivery speed
```

**Expected Output**:
- ✅ AI filters orders with `requires_cold_chain: true`
- ✅ Optimization objective set to `minimize_time`
- ✅ Routes show cold-chain orders delivered within 2-hour limit
- ✅ If violations exist, shows warning box

**Screenshot to Capture**:
- **Figure 3**: Cold-chain routing with constraint validation
- Highlight any constraint violation warnings in red boxes

**File Name**: `fig3_cold_chain_routing.png`

---

## Feature 2: Constraint-Aware Optimization

### Test Case 2.1: Driver Overtime Violation Detection

**Where to Put Query**: AI Agent Page (`/agent`) or Direct Mode (`/direct`)

**Setup**: Route many orders with few vehicles to trigger overtime

**Query (AI Mode)**:
```
Route 15 deliveries with only 2 vehicles, minimize distance
```

**Or Direct Mode Settings**:
- Orders: `O001,O002,O003,O004,O005,O006,O007,O008,O009,O010,O011,O012,O013,O014,O015`
- Vehicles: `V001,V002`
- Objective: Minimize Distance

**Expected Output**:
- ✅ Optimization completes successfully
- ✅ **RED WARNING BOX** appears if routes exceed 8 hours:
  ```
  ⏰ Driver Overtime Violation
  Route exceeds 8.0-hour driver limit by 125 minutes (2.1 hours)
  Vehicle: V001

  Recommended Action: Add more vehicles to reduce route duration
  ```

**Screenshot to Capture**:
- **Figure 4**: Constraint violation warning box (red border, detailed message)
- Show full route details with time exceeding 480 minutes

**File Name**: `fig4_overtime_violation.png`

---

### Test Case 2.2: Cold-Chain Time Limit Violation

**Where to Put Query**: AI Agent Page or Direct Mode

**Setup**: Route cold-chain orders with insufficient vehicles

**Query (AI Mode)**:
```
Route 10 cold-chain orders with only 1 vehicle
```

**Expected Output**:
- ✅ **CRITICAL WARNING BOX** appears:
  ```
  🧊 Cold-Chain Time Limit Exceeded (CRITICAL)
  Cold-chain order O015 delivered after 145 min (limit: 120 min = 2.0 hours)
  Vehicle: V001

  Recommended Action: Prioritize cold-chain orders or assign dedicated refrigerated vehicles
  ```

**Screenshot to Capture**:
- **Figure 5**: Critical cold-chain violation warning
- Highlight severity level (CRITICAL vs WARNING)

**File Name**: `fig5_cold_chain_violation.png`

---

### Test Case 2.3: Constraint-Compliant Routing

**Where to Put Query**: Direct Mode (`/direct`)

**Settings**:
- Orders: `O001,O002,O003,O004,O005`
- Vehicles: `V001,V002,V003`
- Objective: Minimize Cost

**Expected Output**:
- ✅ All routes complete within 8 hours
- ✅ All cold-chain orders delivered within 2 hours
- ✅ **NO WARNING BOXES** appear
- ✅ Green success message

**Screenshot to Capture**:
- **Figure 6**: Clean routing solution with no violations
- Show metrics summary

**File Name**: `fig6_compliant_routing.png`

---

## Feature 3: Scenario Planning (What-If Analysis)

### Test Case 3.1: Baseline vs Fuel Price Spike

**Where to Put Query**: Scenarios Page (`/scenarios`)

**Configuration**:

**Base Parameters**:
- Order IDs: `O001,O002,O003,O004,O005`
- Vehicle IDs: `V001,V002`

**Scenarios** (keep default pre-loaded scenarios):
```json
{
  "baseline": {
    "description": "Current conditions"
  },
  "fuel_spike": {
    "description": "25% fuel price increase",
    "fuel_price_per_liter": 1.875
  },
  "rush_hour": {
    "description": "Heavy traffic (20% slower)",
    "avg_speed_reduction": 0.2
  }
}
```

**Steps**:
1. Navigate to http://localhost:5174/scenarios
2. Keep default values (already filled)
3. Click **"Run Comparison"** button
4. Wait 30-60 seconds for results

**Expected Output**:
- ✅ Comparison table shows 3 scenarios side-by-side
- ✅ Metrics displayed:
  - Total Cost
  - Distance
  - Time
  - Emissions
  - Number of Routes
- ✅ Differences vs baseline shown:
  - Cost delta in USD and %
  - Time delta in minutes
  - Emissions delta in kg
- ✅ Color coding: Green for baseline, Red for worst, Blue for others

**Screenshot to Capture**:
- **Figure 7**: Full scenarios comparison table
- **Figure 8**: Insights box showing best/worst scenarios
- **Table 1 Data**: Export CSV for LaTeX table

**File Names**:
- `fig7_scenarios_comparison.png`
- `fig8_scenarios_insights.png`
- `table1_scenarios_data.csv` (click "Export CSV" button)

---

### Test Case 3.2: Fleet Size Comparison

**Where to Put Query**: Scenarios Page (`/scenarios`)

**Configuration**:
- Order IDs: `O001,O002,O003,O004,O005,O006,O007,O008,O009,O010`
- Vehicle IDs: `V001,V002`

**Custom Scenarios**:
```json
{
  "baseline": {
    "description": "2 vehicles"
  },
  "add_one_vehicle": {
    "description": "Add 1 vehicle (total: 3)",
    "num_vehicles": 3
  },
  "reduce_to_one": {
    "description": "Only 1 vehicle",
    "num_vehicles": 1
  }
}
```

**Steps**:
1. Replace order IDs and scenarios JSON
2. Click "Run Comparison"
3. Wait for results

**Expected Output**:
- ✅ Shows cost vs fleet size trade-off
- ✅ More vehicles = higher fixed costs but lower labor costs
- ✅ Fewer vehicles = overtime violations possible

**Screenshot to Capture**:
- **Figure 9**: Fleet size comparison showing cost trade-offs

**File Name**: `fig9_fleet_size_comparison.png`

---

### Test Case 3.3: Traffic Impact Analysis

**Where to Put Query**: Scenarios Page

**Scenarios**:
```json
{
  "baseline": {
    "description": "Normal traffic"
  },
  "light_traffic": {
    "description": "10% speed reduction",
    "avg_speed_reduction": 0.1
  },
  "heavy_traffic": {
    "description": "30% speed reduction",
    "avg_speed_reduction": 0.3
  },
  "severe_congestion": {
    "description": "50% speed reduction",
    "avg_speed_reduction": 0.5
  }
}
```

**Expected Output**:
- ✅ Time increases proportionally with traffic severity
- ✅ Labor costs increase due to longer routes
- ✅ Distance remains constant (same roads, just slower)

**Screenshot to Capture**:
- **Figure 10**: Traffic sensitivity analysis

**File Name**: `fig10_traffic_sensitivity.png`

---

## Performance Comparison Tests

### Test Case 4.1: AI Agent vs Direct Solver Speed

**Purpose**: Show computational overhead of AI agent

**Test Setup**:

**Scenario A - AI Agent**:
1. Go to AI Agent page
2. Query: "Route 10 deliveries with 2 vehicles"
3. Record execution time from response

**Scenario B - Direct Solver**:
1. Go to Direct Mode page
2. Orders: `O001,O002,O003,O004,O005,O006,O007,O008,O009,O010`
3. Vehicles: `V001,V002`
4. Click "Solve VRP"
5. Record execution time from response

**Data to Record**:
```
| Mode          | Execution Time | Tool Calls | Solution Quality |
|---------------|---------------|------------|------------------|
| AI Agent      | ~25-30s       | 4 tools    | Cost: $XXX       |
| Direct Solver | ~15-20s       | 1 tool     | Cost: $XXX       |
```

**Expected Finding**:
- AI agent is 30-50% slower due to LLM reasoning
- Both produce identical or near-identical solutions (within 5%)
- AI provides natural language explanation + tool chain visibility

**Screenshot to Capture**:
- **Figure 11a**: AI agent response with execution time
- **Figure 11b**: Direct solver response with execution time
- **Table 2**: Performance comparison data

**File Name**: `fig11_performance_comparison.png`

---

### Test Case 4.2: Solution Quality Comparison

**Purpose**: Verify AI agent doesn't compromise optimization quality

**Test Setup**:
Run same problem 5 times:
- 3 times via AI agent (with different phrasing)
- 2 times via direct solver

**Queries**:
1. AI: "Route 8 orders with 2 vehicles, minimize cost"
2. AI: "Optimize delivery routes for 8 orders using 2 vehicles, keep costs low"
3. AI: "Find cheapest routing plan for 8 deliveries with 2 vehicles"
4. Direct: Orders O001-O008, Vehicles V001-V002, Objective: Minimize Cost
5. Direct: (repeat)

**Data to Record**:
```
| Trial | Mode   | Total Cost | Distance | Time | Status  |
|-------|--------|-----------|----------|------|---------|
| 1     | AI     | $327.50   | 210.6km  | 672m | OPTIMAL |
| 2     | AI     | $327.50   | 210.6km  | 672m | OPTIMAL |
| 3     | AI     | $329.20   | 212.1km  | 678m | OPTIMAL |
| 4     | Direct | $327.50   | 210.6km  | 672m | OPTIMAL |
| 5     | Direct | $327.50   | 210.6km  | 672m | OPTIMAL |
```

**Analysis**:
- Average deviation: <5%
- All solutions marked OPTIMAL by solver
- Conclusion: AI agent maintains solution quality

**Screenshot to Capture**:
- **Table 3**: Solution quality comparison

**File Name**: `table3_solution_quality.csv`

---

## Screenshots for Paper Figures

### Recommended Figure Placement

**Section: Introduction**
- *Figure 1*: System architecture diagram (create separately)

**Section: Methodology**
- *Figure 2*: AI Agent interface screenshot (Test Case 1.1)
- *Figure 3*: Route exclusion demo (Test Case 1.2)

**Section: Constraint-Aware Optimization**
- *Figure 4*: Driver overtime violation warning (Test Case 2.1)
- *Figure 5*: Cold-chain violation warning (Test Case 2.2)
- *Figure 6*: Compliant routing example (Test Case 2.3)

**Section: Scenario Planning**
- *Figure 7*: Scenarios comparison table (Test Case 3.1)
- *Figure 8*: Scenario insights panel (Test Case 3.1)
- *Figure 9*: Fleet size comparison (Test Case 3.2)
- *Figure 10*: Traffic sensitivity (Test Case 3.3)

**Section: Evaluation**
- *Figure 11*: Performance comparison (Test Case 4.1)

**Section: Results**
- *Table 1*: Scenario comparison metrics (exported CSV from Test Case 3.1)
- *Table 2*: Performance benchmarks (Test Case 4.1)
- *Table 3*: Solution quality comparison (Test Case 4.2)

---

## Screenshot Quality Guidelines

### Before Taking Screenshots

1. **Set Browser Size**: 1920x1080 for consistency
2. **Clear Browser Cache**: Ensure clean UI
3. **Zoom Level**: 100% (no zoom in/out)
4. **Hide DevTools**: F12 to close
5. **Full Screen**: F11 for clean screenshots

### What to Capture

**Good Screenshot Checklist**:
- ✅ Clear, readable text (no blurriness)
- ✅ All relevant UI elements visible
- ✅ Highlight important sections (draw red boxes in image editor after)
- ✅ Include URL bar to show page context
- ✅ Capture entire result area (scroll if needed, take multiple shots)

**Bad Screenshot Mistakes**:
- ❌ Partial results cut off
- ❌ Tiny font size (zoom in if needed)
- ❌ Developer console visible
- ❌ Personal information visible

### Post-Processing

Use image editor (e.g., Paint, Photoshop) to:
1. **Add annotations**: Red rectangles around key areas
2. **Add labels**: "A", "B", "C" for multi-part figures
3. **Crop**: Remove unnecessary whitespace
4. **Resize**: Keep width at 1200-1600px for paper
5. **Save as**: PNG format (lossless quality)

---

## Export Data for Tables

### How to Export CSV from Scenarios Page

1. Run scenario comparison (Test Case 3.1)
2. Wait for results to load
3. Click **"Export CSV"** button at bottom
4. Save as `table1_scenarios_data.csv`

### Convert CSV to LaTeX Table

Use online tool: https://www.tablesgenerator.com/

**Steps**:
1. Go to tablesgenerator.com
2. Select "LaTeX Tables"
3. Click "Import CSV"
4. Upload your CSV file
5. Customize table style
6. Click "Generate"
7. Copy LaTeX code to paper

**Example LaTeX Output**:
```latex
\begin{table}[h]
\centering
\caption{Scenario Comparison Results for 10 Deliveries with 2 Vehicles}
\label{tab:scenario_comparison}
\begin{tabular}{|l|r|r|r|r|r|}
\hline
Scenario & Total Cost (\$) & Distance (km) & Time (min) & Emissions (kg) & vs Baseline (\%) \\
\hline
Baseline & 327.50 & 210.6 & 672 & 52.7 & - \\
Fuel Spike (+25\%) & 386.25 & 210.6 & 672 & 52.7 & +18.0\% \\
Rush Hour (-20\% speed) & 327.50 & 210.6 & 840 & 52.7 & +25.0\% (time) \\
\hline
\end{tabular}
\end{table}
```

---

## Testing Timeline (Recommended)

**Day 1: Basic Features**
- Test Cases 1.1 - 1.3 (Natural Language AI)
- Capture Figures 1-3

**Day 2: Constraints**
- Test Cases 2.1 - 2.3 (Constraint Validation)
- Capture Figures 4-6

**Day 3: Scenarios**
- Test Cases 3.1 - 3.3 (What-If Analysis)
- Capture Figures 7-10
- Export CSV data

**Day 4: Performance**
- Test Cases 4.1 - 4.2 (Benchmarking)
- Capture Figure 11
- Compile Tables 2-3

**Day 5: Review & Annotation**
- Review all screenshots
- Add annotations and labels
- Organize files for paper submission

---

## Troubleshooting

### Issue: Backend Not Responding
**Solution**: Restart backend
```bash
# Find process
netstat -ano | findstr :8000
# Kill it
taskkill //F //PID <PID>
# Restart
python scripts/start_api.py
```

### Issue: Frontend Shows Blank Page
**Solution**: Clear cache and reload
```
Ctrl + Shift + R (hard reload)
```

### Issue: Scenarios Take Too Long
**Solution**: Reduce order count
- Use 3-5 orders instead of 10
- Scenarios will complete in 15-20 seconds

### Issue: Screenshots Too Large
**Solution**: Compress images
- Use TinyPNG.com to reduce file size
- Keep quality at 85-90%

---

## Final Checklist for Paper Submission

**Screenshots Captured**:
- [ ] Figure 1: Basic AI routing
- [ ] Figure 2: Route avoidance
- [ ] Figure 3: Cold-chain routing
- [ ] Figure 4: Overtime violation
- [ ] Figure 5: Cold-chain violation
- [ ] Figure 6: Compliant routing
- [ ] Figure 7: Scenarios comparison
- [ ] Figure 8: Scenario insights
- [ ] Figure 9: Fleet size comparison
- [ ] Figure 10: Traffic sensitivity
- [ ] Figure 11: Performance comparison

**Data Tables Exported**:
- [ ] Table 1: Scenarios CSV
- [ ] Table 2: Performance benchmarks
- [ ] Table 3: Solution quality data

**Documentation**:
- [ ] All test cases executed successfully
- [ ] Results match expected outputs
- [ ] Screenshots annotated and labeled
- [ ] CSV files converted to LaTeX

---

## Contact for Questions

If you encounter any issues during testing:
1. Check backend logs: `python scripts/start_api.py`
2. Check browser console: F12 → Console tab
3. Refer to `ENHANCED_FEATURES.md` for feature documentation

Good luck with your research paper! 🚀
