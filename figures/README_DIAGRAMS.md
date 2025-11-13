# System Architecture Diagrams - Usage Guide

This directory contains multiple versions of the system architecture diagram for the research paper.

## Available Diagrams

### 1. **Mermaid Diagram** (`architecture_diagram.md`)
- **Format**: Mermaid.js markup
- **Use case**: GitHub README, documentation websites, Notion, GitLab
- **Rendering**:
  - Copy the mermaid code block
  - Paste into https://mermaid.live for PNG/SVG export
  - Or use Mermaid plugins in VS Code, Obsidian, etc.

### 2. **ASCII Text Diagram** (`architecture_ascii.txt`)
- **Format**: Plain text with Unicode box-drawing characters
- **Use case**: Direct inclusion in LaTeX papers, plain text documentation
- **Advantages**: No dependencies, works anywhere
- **Usage in LaTeX**:
  ```latex
  \begin{figure}[h]
  \centering
  \begin{verbatim}
  [Paste ASCII diagram here]
  \end{verbatim}
  \caption{System Architecture}
  \label{fig:architecture}
  \end{figure}
  ```

### 3. **Graphviz Python Script** (`generate_architecture_diagram.py`)
- **Format**: Python script using Graphviz library
- **Generates**: PNG images (publication quality)
- **Usage**:
  ```bash
  # Install Graphviz first
  pip install graphviz

  # Run the script
  python figures/generate_architecture_diagram.py
  ```
- **Output**:
  - `fig_architecture_comprehensive.png` - Full detailed diagram
  - `fig_architecture_simplified.png` - Simplified for presentations

### 4. **Detailed Documentation** (`architecture_diagram.md`)
- Contains:
  - Full architecture description
  - Layer-by-layer breakdown
  - Information flow examples
  - Performance metrics
  - Technology stack

---

## Recommended Usage for Research Paper

### For IEEE/ACM Style Papers

**Figure 1: System Architecture**

Use the **Graphviz comprehensive diagram**:
```bash
python figures/generate_architecture_diagram.py
```

Insert in LaTeX:
```latex
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/fig_architecture_comprehensive.png}
\caption{Modular architecture of the AI-powered logistics planning system showing four core layers: User Interfaces (blue), API Gateway (green), LLM Orchestrator (red), and Tool Suite (orange). The system integrates external services (OpenAI GPT-4, Google OR-Tools, OSRM) and accesses operational data to generate routing solutions with constraint validation.}
\label{fig:architecture}
\end{figure*}
```

---

### For Presentations/Slides

Use the **simplified Graphviz diagram**:
- Clearer for audiences
- Less visual clutter
- Better for PDF export

```bash
python figures/generate_architecture_diagram.py
# Use: fig_architecture_simplified.png
```

---

### For Online Documentation

Use the **Mermaid diagram**:
- Renders natively on GitHub, GitLab, Notion
- Interactive on Mermaid.live
- Can be exported to SVG (scalable, sharp)

From `architecture_diagram.md`:
```markdown
```mermaid
graph TB
    [diagram code here]
```
```

---

## Customization

### Changing Colors in Graphviz Script

Edit `generate_architecture_diagram.py`:

```python
# Example: Change User Layer color
c.attr(label='User Layer',
       color='#YOUR_HEX_COLOR',  # Change this
       fillcolor='#YOUR_HEX_COLOR')
```

### Changing Layout

For horizontal layout (left-to-right):
```python
dot.attr(rankdir='LR')  # Change from 'TB' to 'LR'
```

### Adding New Components

In `generate_architecture_diagram.py`:
```python
# Add a new node
c.node('my_component', 'My Component\nDescription',
       fillcolor='#COLOR')

# Add a connection
dot.edge('my_component', 'target_component',
         label='Connection Label',
         color='#COLOR')
```

---

## Exporting to Different Formats

### PNG (High Resolution)
```bash
python generate_architecture_diagram.py
# Already generates PNG at 300 DPI
```

### SVG (Scalable Vector)
In `generate_architecture_diagram.py`, change:
```python
dot = Digraph(format='svg')  # Change from 'png'
```

### PDF (LaTeX-friendly)
```python
dot = Diagraph(format='pdf')
```

### Using Mermaid CLI
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i architecture_diagram.md -o architecture.png -w 2000

# Generate SVG
mmdc -i architecture_diagram.md -o architecture.svg

# Generate PDF
mmdc -i architecture_diagram.md -o architecture.pdf
```

---

## LaTeX Integration Examples

### Method 1: Direct PNG inclusion
```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\textwidth]{figures/fig_architecture_comprehensive.png}
\caption{System architecture diagram.}
\label{fig:arch}
\end{figure}
```

### Method 2: TikZ (for programmatic diagrams)
If you prefer LaTeX-native diagrams, convert the architecture to TikZ format.
See: https://www.overleaf.com/learn/latex/LaTeX_Graphics_using_TikZ

### Method 3: Inkscape (for fine-tuning)
1. Generate SVG from Graphviz
2. Open in Inkscape
3. Edit text, colors, layout
4. Export to PDF for LaTeX

---

## Color Scheme

The diagrams use a consistent color scheme:

| Layer               | Color Code | Color Name    |
|---------------------|------------|---------------|
| User Layer          | `#e1f5ff`  | Light Blue    |
| API Gateway         | `#d0f4de`  | Light Green   |
| Orchestrator        | `#ffe5ec`  | Light Pink    |
| Tool Suite          | `#fff3b0`  | Light Yellow  |
| Data Layer          | `#e5e5e5`  | Light Gray    |
| External Services   | `#f8edeb`  | Light Beige   |
| Output Layer        | `#cfe2f3`  | Pale Blue     |

**Nodes:**
- User components: Blue (`#64b5f6`)
- Agent/LLM: Red (`#ef5350`)
- Tools: Orange (`#ffa726`)
- Data: Gray (`#9e9e9e`)
- External: Dark Red (`#d32f2f`)

---

## Troubleshooting

### Graphviz not found
```bash
# Windows (using Chocolatey)
choco install graphviz

# Mac
brew install graphviz

# Linux (Ubuntu/Debian)
sudo apt-get install graphviz

# Verify installation
dot -V
```

### Python import error
```bash
pip install graphviz
```

### Mermaid rendering issues
- Use https://mermaid.live for guaranteed rendering
- Check syntax: https://mermaid-js.github.io/mermaid/#/

### Large file size
For smaller PNG files:
```python
# In generate_architecture_diagram.py
dot.attr(dpi='150')  # Reduce from default 300
```

---

## Citation

When using these diagrams in publications, cite as:

```bibtex
@misc{logistics_ai_architecture,
  title={AI-Powered Logistics Planning System Architecture},
  author={[Your Name]},
  year={2025},
  note={System design for natural language vehicle routing optimization}
}
```

---

## Quick Start

**For research paper:**
```bash
# 1. Generate PNG diagrams
python figures/generate_architecture_diagram.py

# 2. Insert in LaTeX
\includegraphics[width=\textwidth]{figures/fig_architecture_comprehensive.png}
```

**For slides:**
```bash
# Use simplified version
# Output: fig_architecture_simplified.png
```

**For GitHub README:**
```bash
# Copy Mermaid code from architecture_diagram.md
# Paste into README.md in a ```mermaid code block
```

---

## Support

For diagram customization or issues:
1. Review the Graphviz documentation: https://graphviz.org/documentation/
2. Review Mermaid syntax: https://mermaid-js.github.io/mermaid/
3. Check LaTeX graphics guide: https://www.overleaf.com/learn/latex/Inserting_Images

---

**Last Updated:** 2025-01-13
**Version:** 1.0
**Author:** [Your Name]
