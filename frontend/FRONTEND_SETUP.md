# Frontend Setup - Logistics AI Agent UI

## ✅ Completed

### 1. Project Initialization
- ✅ React + Vite project created
- ✅ Tailwind CSS configured
- ✅ Dependencies installed:
  - react-router-dom (routing)
  - lucide-react (icons)
  - axios (API calls)
  - recharts (charts)
  - leaflet & react-leaflet (maps)
  - html2canvas (screenshots)

### 2. Configuration Files Created
- ✅ `tailwind.config.js` - Tailwind configuration
- ✅ `postcss.config.js` - PostCSS configuration
- ✅ `.env` - Environment variables
- ✅ `src/index.css` - Tailwind directives + custom styles
- ✅ `src/services/api.js` - Complete API service layer

### 3. Directory Structure
```
frontend/
├── src/
│   ├── components/     (for reusable UI components)
│   ├── pages/          (for page components)
│   ├── services/       ✅ api.js created
│   └── utils/          (for helper functions)
├── .env                ✅ created
├── tailwind.config.js  ✅ created
└── postcss.config.js   ✅ created
```

---

## 📝 What's Next - Remaining Components

### Phase 1: Core App Structure (30 min)
1. **src/App.jsx** - Main app with React Router
2. **src/components/Layout.jsx** - Header, sidebar, footer
3. **src/components/Navbar.jsx** - Navigation bar

### Phase 2: Landing Page (20 min)
4. **src/pages/Home.jsx** - Landing page with quick stats
5. **src/components/QuickStatsCard.jsx** - Stats display

### Phase 3: AI Chat Interface (45 min)
6. **src/pages/AgentMode.jsx** - Natural language interface
7. **src/components/ChatInterface.jsx** - Chat UI
8. **src/components/ThinkingProcess.jsx** - AI thinking display
9. **src/components/RouteResults.jsx** - Results with explanation

### Phase 4: Direct Solver Interface (30 min)
10. **src/pages/DirectMode.jsx** - Manual parameter entry
11. **src/components/ParameterForm.jsx** - Form for parameters
12. **src/components/ResultsDisplay.jsx** - Raw results

### Phase 5: Comparison View (Research Paper) (40 min)
13. **src/pages/CompareView.jsx** - Side-by-side comparison
14. **src/components/ComparisonTable.jsx** - Metrics comparison
15. **src/components/ExportButton.jsx** - Screenshot/export

### Phase 6: Route Visualization (35 min)
16. **src/components/RouteMap.jsx** - Leaflet map with routes
17. **src/components/RouteDetails.jsx** - Route details panel

### Phase 7: Utilities (15 min)
18. **src/utils/exportHelpers.js** - Screenshot & CSV export
19. **src/utils/formatters.js** - Data formatting functions

**Total Estimated Time: ~3.5 hours**

---

## 🚀 Quick Start Commands

### Development Server
```bash
cd frontend
npm run dev
```

The app will run at: **http://localhost:5173**

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

---

## 🎯 Key Features to Implement

### 1. Landing Page
- Quick stats dashboard (orders, vehicles)
- Two big buttons: "AI Mode" and "Manual Mode"
- Recent queries history
- System status indicator

### 2. AI Chat Interface (Primary User Flow)
```
User Flow:
1. User types natural language query
2. Shows "AI is thinking..." with animated steps
3. Displays results with:
   - Natural language explanation
   - Route map visualization
   - Cost breakdown
   - Metrics (time, distance, emissions)
4. Action buttons: Approve, Adjust, Export
```

### 3. Direct Solver (Baseline Comparison)
```
User Flow:
1. User selects orders & vehicles from dropdowns
2. Sets objective (minimize cost/distance/time)
3. Sets constraints
4. Click "Solve"
5. Shows raw results (less explanation than AI mode)
```

### 4. Comparison View (For Research Paper Screenshots)
```
Side-by-side layout:
┌─────────────────────┬─────────────────────┐
│  🤖 Agent Approach  │  ⚙️ Direct Solver  │
│  Input: NL query    │  Input: Parameters  │
│  Cost: $222.80      │  Cost: $220.15      │
│  Time: 23.0s        │  Time: 18.5s        │
│  Explanation: ✅    │  Explanation: ❌    │
└─────────────────────┴─────────────────────┘

[📸 Screenshot for Paper] button
```

---

## 🎨 Design Guidelines

### Colors (from Tailwind config)
- Primary: Blue (#0ea5e9)
- Success: Green (#10b981)
- Warning: Yellow (#f59e0b)
- Error: Red (#ef4444)
- Background: White (#ffffff)
- Text: Gray-900 (#111827)

### Typography
- Headers: font-bold text-2xl md:text-3xl
- Body: text-base text-gray-700
- Small: text-sm text-gray-500

### Spacing
- Card padding: p-6 md:p-8
- Section gaps: space-y-6
- Button padding: px-6 py-3

---

## 🔌 API Integration Example

```javascript
import logisticsAPI from './services/api';

// Example: Ask Agent
async function handleAgentQuery() {
  try {
    const result = await logisticsAPI.askAgent(
      "Route 10 deliveries with 2 vehicles",
      { maxIterations: 5, includeExplanation: true }
    );

    console.log('Response:', result.response_text);
    console.log('Tools used:', result.tools_called);
    console.log('Execution time:', result.execution_time_seconds);
  } catch (error) {
    console.error('Error:', error);
  }
}

// Example: Direct Solver
async function handleDirectSolver() {
  const orderIds = ['O001', 'O002', 'O003'];
  const vehicleIds = ['V001', 'V002'];

  const result = await logisticsAPI.solveDirect(
    orderIds,
    vehicleIds,
    { objective: 'minimize_cost' }
  );

  console.log('Routes:', result.routes);
}
```

---

## 📦 Component Examples

### Example: Simple Stats Card
```jsx
function StatsCard({ icon, label, value, color }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className={`text-${color}-500 mb-2`}>{icon}</div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-gray-500 text-sm">{label}</div>
    </div>
  );
}
```

### Example: Loading Spinner
```jsx
function LoadingSpinner({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
}
```

---

## 🐛 Common Issues & Solutions

### Issue: API Connection Failed
**Solution**: Make sure backend is running at http://localhost:8000
```bash
# In backend directory
python scripts/start_api.py
```

### Issue: Tailwind styles not working
**Solution**: Restart dev server after Tailwind config changes
```bash
# Stop server (Ctrl+C) then:
npm run dev
```

### Issue: Map not displaying
**Solution**: Import Leaflet CSS in index.css (already done)

---

## 🎬 Next Step

**Run this command to continue development:**
```bash
cd frontend
npm run dev
```

Then I'll create the remaining React components in the next response!

---

**Status**: ✅ Foundation Complete | 📝 Ready for Component Development
