"""
Generate System Architecture Diagram for Research Paper
Uses Graphviz to create publication-quality figures
"""

from graphviz import Digraph
import os

def create_architecture_diagram():
    """Create comprehensive system architecture diagram"""

    dot = Digraph(comment='Logistics AI Agent System Architecture',
                  format='png',
                  engine='dot')

    # Set graph attributes for professional appearance
    dot.attr(rankdir='TB',
             splines='ortho',
             nodesep='0.5',
             ranksep='0.8',
             fontname='Arial',
             fontsize='11',
             bgcolor='white')

    # Default node style
    dot.attr('node',
             shape='box',
             style='rounded,filled',
             fontname='Arial',
             fontsize='10',
             height='0.4',
             margin='0.15,0.1')

    # ============= Layer 1: User Interfaces =============
    with dot.subgraph(name='cluster_user') as c:
        c.attr(label='User Layer',
               style='filled',
               color='#e1f5ff',
               fontsize='12',
               fontname='Arial Bold')

        c.node('web', 'Web Interface\n(React + Vite)',
               fillcolor='#90caf9')
        c.node('api_client', 'REST API Client\n(cURL/Postman)',
               fillcolor='#90caf9')
        c.node('nl_query', 'Natural Language\nQuery',
               fillcolor='#64b5f6',
               shape='note')

    # ============= Layer 2: API Gateway =============
    with dot.subgraph(name='cluster_gateway') as c:
        c.attr(label='API Gateway',
               style='filled',
               color='#d0f4de',
               fontsize='12',
               fontname='Arial Bold')

        c.node('fastapi', 'FastAPI Server\n(Port 8000)',
               fillcolor='#81c784')
        c.node('validation', 'Request Validation\n& Routing',
               fillcolor='#66bb6a')

    # ============= Layer 3: Orchestrator =============
    with dot.subgraph(name='cluster_orchestrator') as c:
        c.attr(label='Orchestrator Layer (LLM Agent)',
               style='filled',
               color='#ffe5ec',
               fontsize='12',
               fontname='Arial Bold')

        c.node('langchain', 'LangChain\nAgentExecutor',
               fillcolor='#ef5350',
               fontcolor='white')
        c.node('gpt4', 'OpenAI GPT-4\nTurbo',
               fillcolor='#e53935',
               fontcolor='white',
               shape='hexagon')
        c.node('parser', 'Query Parser &\nIntent Recognition',
               fillcolor='#f48fb1')
        c.node('orchestrate', 'Tool Selection &\nOrchestration',
               fillcolor='#f48fb1')
        c.node('validate_constraint', 'Constraint\nValidator',
               fillcolor='#f48fb1')
        c.node('response_gen', 'Response\nGenerator',
               fillcolor='#f48fb1')

    # ============= Layer 4: Tool Suite =============
    with dot.subgraph(name='cluster_tools') as c:
        c.attr(label='Tool Suite (9 Specialized Functions)',
               style='filled',
               color='#fff3b0',
               fontsize='12',
               fontname='Arial Bold')

        # Database Tools
        with c.subgraph(name='cluster_db_tools') as db:
            db.attr(label='Database Tools',
                    style='dashed',
                    color='#ffa726')
            db.node('get_orders', 'get_orders', fillcolor='#ffcc80')
            db.node('get_vehicles', 'get_vehicles', fillcolor='#ffcc80')
            db.node('get_depot', 'get_depot', fillcolor='#ffcc80')

        # Optimization Tools
        with c.subgraph(name='cluster_opt_tools') as opt:
            opt.attr(label='Optimization Tools',
                     style='dashed',
                     color='#ffa726')
            opt.node('solve_vrp', 'solve_vrp\n(OR-Tools)', fillcolor='#ffb74d')
            opt.node('calc_distance', 'calculate_distance\n_matrix (OSRM)', fillcolor='#ffb74d')

        # Analytics Tools
        with c.subgraph(name='cluster_analytics') as ana:
            ana.attr(label='Analytics Tools',
                     style='dashed',
                     color='#ffa726')
            ana.node('calc_economics', 'calculate_route\n_economics', fillcolor='#ffa726')
            ana.node('validate_tool', 'validate\n_constraints', fillcolor='#ffa726')

        # Scenario Tools
        with c.subgraph(name='cluster_scenario') as scn:
            scn.attr(label='Scenario Tools',
                     style='dashed',
                     color='#ffa726')
            scn.node('compare_scenarios', 'compare\n_scenarios', fillcolor='#ff9800')
            scn.node('analyze_sens', 'analyze\n_sensitivity', fillcolor='#ff9800')

    # ============= Layer 5: Data Layer =============
    with dot.subgraph(name='cluster_data') as c:
        c.attr(label='Data Layer',
               style='filled',
               color='#e5e5e5',
               fontsize='12',
               fontname='Arial Bold')

        c.node('sqlite', 'SQLite Database\n(Orders, Vehicles,\nDepots)',
               fillcolor='#bdbdbd',
               shape='cylinder')
        c.node('osrm', 'OSRM Routing\nEngine',
               fillcolor='#9e9e9e',
               fontcolor='white',
               shape='cylinder')
        c.node('config', 'Configuration\n(.env)',
               fillcolor='#bdbdbd',
               shape='note')

    # ============= Layer 6: External Services =============
    with dot.subgraph(name='cluster_external') as c:
        c.attr(label='External Services',
               style='filled',
               color='#f8edeb',
               fontsize='12',
               fontname='Arial Bold')

        c.node('openai_api', 'OpenAI API\n(GPT-4 Model)',
               fillcolor='#d32f2f',
               fontcolor='white',
               shape='doubleoctagon')
        c.node('ortools', 'Google OR-Tools\n(CP-SAT Solver)',
               fillcolor='#c62828',
               fontcolor='white',
               shape='doubleoctagon')

    # ============= Layer 7: Output =============
    with dot.subgraph(name='cluster_output') as c:
        c.attr(label='Output Layer',
               style='filled',
               color='#cfe2f3',
               fontsize='12',
               fontname='Arial Bold')

        c.node('json_out', 'Routing Solutions\n(JSON)',
               fillcolor='#64b5f6')
        c.node('maps', 'Visual Maps\n(Leaflet.js)',
               fillcolor='#64b5f6')
        c.node('scenarios_out', 'Scenario\nComparisons',
               fillcolor='#64b5f6')
        c.node('warnings', 'Constraint\nWarnings',
               fillcolor='#ff9800',
               fontcolor='white')

    # ============= Connections =============

    # User → API Gateway
    dot.edge('web', 'fastapi', color='#1976d2')
    dot.edge('api_client', 'fastapi', color='#1976d2')
    dot.edge('nl_query', 'fastapi', color='#1976d2', style='dashed')

    # API Gateway → Orchestrator
    dot.edge('fastapi', 'validation', color='#388e3c')
    dot.edge('validation', 'langchain', color='#388e3c')

    # Within Orchestrator
    dot.edge('langchain', 'gpt4', color='#c62828', dir='both')
    dot.edge('gpt4', 'parser', color='#c62828')
    dot.edge('parser', 'orchestrate', color='#c62828')
    dot.edge('orchestrate', 'validate_constraint', color='#c62828')
    dot.edge('validate_constraint', 'response_gen', color='#c62828')

    # Orchestrator → External Services
    dot.edge('gpt4', 'openai_api', color='#d32f2f', style='dashed', dir='both')

    # Orchestrator → Tools
    dot.edge('orchestrate', 'get_orders', color='#f57c00')
    dot.edge('orchestrate', 'get_vehicles', color='#f57c00')
    dot.edge('orchestrate', 'get_depot', color='#f57c00')
    dot.edge('orchestrate', 'solve_vrp', color='#f57c00')
    dot.edge('orchestrate', 'calc_distance', color='#f57c00')
    dot.edge('orchestrate', 'calc_economics', color='#f57c00')
    dot.edge('orchestrate', 'validate_tool', color='#f57c00')
    dot.edge('orchestrate', 'compare_scenarios', color='#f57c00')
    dot.edge('orchestrate', 'analyze_sens', color='#f57c00')

    # Tools → Data Layer
    dot.edge('get_orders', 'sqlite', color='#757575')
    dot.edge('get_vehicles', 'sqlite', color='#757575')
    dot.edge('get_depot', 'sqlite', color='#757575')
    dot.edge('calc_distance', 'osrm', color='#757575')
    dot.edge('calc_economics', 'config', color='#757575', style='dashed')
    dot.edge('validate_tool', 'config', color='#757575', style='dashed')

    # Tools → External Services
    dot.edge('solve_vrp', 'ortools', color='#c62828', style='dashed')

    # Orchestrator → Output
    dot.edge('response_gen', 'json_out', color='#1976d2')
    dot.edge('json_out', 'maps', color='#1976d2', style='dashed')
    dot.edge('json_out', 'scenarios_out', color='#1976d2', style='dashed')
    dot.edge('validate_constraint', 'warnings', color='#ff6f00')

    # Output → User
    dot.edge('json_out', 'web', color='#1976d2')
    dot.edge('maps', 'web', color='#1976d2', style='dashed')
    dot.edge('scenarios_out', 'web', color='#1976d2', style='dashed')
    dot.edge('warnings', 'web', color='#ff6f00')

    return dot


def create_simplified_diagram():
    """Create simplified version for presentations"""

    dot = Digraph(comment='Logistics AI Agent - Simplified',
                  format='png',
                  engine='dot')

    dot.attr(rankdir='TB',
             splines='spline',
             nodesep='1.0',
             ranksep='1.2',
             fontname='Arial',
             fontsize='14',
             bgcolor='white')

    dot.attr('node',
             shape='box',
             style='rounded,filled',
             fontname='Arial',
             fontsize='12',
             height='0.6',
             width='2.5',
             margin='0.2')

    # Main components
    dot.node('user', 'User Interface\n(Web + API)',
             fillcolor='#64b5f6')
    dot.node('agent', 'AI Agent\n(GPT-4 + LangChain)',
             fillcolor='#ef5350',
             fontcolor='white',
             width='3.0')
    dot.node('tools', 'Tool Suite\n(9 Specialized Functions)',
             fillcolor='#ffa726',
             width='3.0')
    dot.node('data', 'Data Sources\n(DB, OSRM, Config)',
             fillcolor='#9e9e9e',
             fontcolor='white')
    dot.node('output', 'Optimized Routes\n+ Constraint Warnings',
             fillcolor='#66bb6a')

    # Connections
    dot.edge('user', 'agent', label='Natural Language\nQuery',
             fontsize='10', color='#1976d2', penwidth='2')
    dot.edge('agent', 'tools', label='Tool Calls\n(JSON)',
             fontsize='10', color='#f57c00', penwidth='2')
    dot.edge('tools', 'data', label='Data Access',
             fontsize='10', color='#757575', penwidth='2')
    dot.edge('data', 'tools', label='Results',
             fontsize='10', color='#757575', penwidth='2', style='dashed')
    dot.edge('tools', 'agent', label='Outputs',
             fontsize='10', color='#f57c00', penwidth='2', style='dashed')
    dot.edge('agent', 'output', label='Synthesized\nResponse',
             fontsize='10', color='#388e3c', penwidth='2')
    dot.edge('output', 'user', label='JSON/HTML',
             fontsize='10', color='#1976d2', penwidth='2')

    # Add external services on the side
    dot.node('openai', 'OpenAI API',
             fillcolor='#d32f2f',
             fontcolor='white',
             shape='cylinder',
             width='1.5')
    dot.node('ortools_ext', 'OR-Tools',
             fillcolor='#c62828',
             fontcolor='white',
             shape='cylinder',
             width='1.5')

    dot.edge('agent', 'openai', label='LLM\nCalls',
             fontsize='9', color='#d32f2f', style='dashed')
    dot.edge('tools', 'ortools_ext', label='VRP\nSolving',
             fontsize='9', color='#c62828', style='dashed')

    return dot


if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('figures', exist_ok=True)

    print("Generating comprehensive architecture diagram...")
    comprehensive = create_architecture_diagram()
    comprehensive.render('figures/fig_architecture_comprehensive',
                         cleanup=True,
                         view=False)
    print("✓ Saved: figures/fig_architecture_comprehensive.png")

    print("\nGenerating simplified architecture diagram...")
    simplified = create_simplified_diagram()
    simplified.render('figures/fig_architecture_simplified',
                      cleanup=True,
                      view=False)
    print("✓ Saved: figures/fig_architecture_simplified.png")

    print("\n" + "="*60)
    print("DIAGRAM GENERATION COMPLETE")
    print("="*60)
    print("\nGenerated files:")
    print("1. figures/fig_architecture_comprehensive.png - Detailed system architecture")
    print("2. figures/fig_architecture_simplified.png - Simplified for presentations")
    print("\nUse these in your research paper, slides, or documentation.")
    print("\nTo install Graphviz (if not already installed):")
    print("  pip install graphviz")
    print("  # Also install Graphviz system package:")
    print("  # Windows: choco install graphviz")
    print("  # Mac: brew install graphviz")
    print("  # Linux: sudo apt-get install graphviz")
