#!/usr/bin/env python3
"""
AKASHA WIKI - Dashboard de Auto-Evolução
Gera visualização HTML do estado da wiki e do sistema de auto-evolução
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
WIKI_DIR = Path("/home/gabriel/akasha-wiki-full/wiki")
STATE_FILE = Path("/home/gabriel/akasha-wiki/.github/state/evolution-state.json")
OUTPUT_FILE = Path("/home/gabriel/akasha-wiki-full/dashboard.html")

# =============================================================================
# COLETA DE DADOS
# =============================================================================

def get_wiki_stats():
    """Estatísticas básicas da wiki"""
    concepts_dir = WIKI_DIR / "concepts"
    entities_dir = WIKI_DIR / "entities"
    sources_dir = WIKI_DIR / "sources"
    
    concepts = list(concepts_dir.glob("*.md")) if concepts_dir.exists() else []
    entities = list(entities_dir.glob("*.md")) if entities_dir.exists() else []
    sources = list(sources_dir.glob("*.md")) if sources_dir.exists() else []
    
    return {
        "concepts": len(concepts),
        "entities": len(entities),
        "sources": len(sources),
        "concept_files": [f.stem for f in concepts],
        "entity_files": [f.stem for f in entities],
    }

def analyze_connections():
    """Análise de rede de conhecimento"""
    concepts_dir = WIKI_DIR / "concepts"
    connections = defaultdict(list)
    
    for f in concepts_dir.glob("*.md"):
        with open(f) as file:
            content = file.read()
            concept = f.stem
            links = re.findall(r'\[\[([^\]|]+)', content)
            connections[concept] = [l.replace('-', ' ').lower() for l in links]
    
    # Métricas
    total_connections = sum(len(v) for v in connections.values())
    avg_connections = total_connections / len(connections) if connections else 0
    
    # Hubs (mais conectados)
    hubs = sorted(connections.items(), key=lambda x: -len(x[1]))[:7]
    
    # Conceitos órfãos
    orphans = [c for c in connections if not connections[c]]
    
    return {
        "total": total_connections,
        "average": avg_connections,
        "hubs": [{"name": h[0], "connections": len(h[1])} for h in hubs],
        "orphans": orphans
    }

def analyze_tags():
    """Análise de tags"""
    concepts_dir = WIKI_DIR / "concepts"
    tag_counts = defaultdict(int)
    
    for f in concepts_dir.glob("*.md"):
        with open(f) as file:
            content = file.read()
            tags = re.findall(r'"([^"]+)"', content)
            for tag in tags:
                if tag not in ["conceito", "ayahuasca", "pesquisa"]:
                    tag_counts[tag] += 1
    
    return sorted(tag_counts.items(), key=lambda x: -x[1])[:15]

def get_state():
    """Ler estado do último ciclo"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_cycle": "nunca", "concepts": 0}

# =============================================================================
# GERAÇÃO DO HTML
# =============================================================================

def generate_html(stats, connections, tags, state):
    """Gera o dashboard HTML"""
    
    # Calcular métricas de progresso
    total_nodes = stats["concepts"] + stats["entities"]
    connection_density = connections["total"] / total_nodes if total_nodes else 0
    
    # Status do sistema
    last_cycle = state.get("last_cycle", "nunca")
    try:
        last_dt = datetime.fromisoformat(last_cycle)
        days_ago = (datetime.now() - last_dt).days
        cycle_status = "🟢 Ativo" if days_ago < 1 else "🟡 Desatualizado" if days_ago < 3 else "🔴 Inativo"
    except:
        cycle_status = "⚪ Nunca executado"
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akasha Wiki - Dashboard de Auto-Evolução</title>
    <style>
        :root {{
            --primary: #6b4c9a;
            --secondary: #9b59b6;
            --accent: #e74c3c;
            --bg-dark: #1a1a2e;
            --bg-card: #16213e;
            --text: #eee;
            --text-muted: #888;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, var(--bg-dark), #0f3460);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 3rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: var(--text-muted);
            font-size: 1.1rem;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: var(--bg-card);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
        }}
        
        .card-title {{
            font-size: 0.85rem;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.5rem;
            letter-spacing: 1px;
        }}
        
        .card-value {{
            font-size: 3rem;
            font-weight: bold;
            color: var(--secondary);
        }}
        
        .card-subtitle {{
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        
        .status-active {{ background: #27ae60; }}
        .status-warning {{ background: #f39c12; }}
        .status-inactive {{ background: #e74c3c; }}
        
        .section {{
            background: var(--bg-card);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
        
        .section-title {{
            font-size: 1.3rem;
            margin-bottom: 1.5rem;
            color: var(--secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .concept-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
        }}
        
        .concept-tag {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .concept-count {{
            background: rgba(255,255,255,0.2);
            padding: 0.15rem 0.5rem;
            border-radius: 10px;
            font-size: 0.75rem;
        }}
        
        .hubs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }}
        
        .hub-item {{
            background: rgba(107, 76, 154, 0.2);
            padding: 1rem;
            border-radius: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .hub-name {{
            font-weight: 500;
        }}
        
        .hub-connections {{
            background: var(--secondary);
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.85rem;
        }}
        
        .progress-bar {{
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 1rem;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        
        .timeline {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        
        .timeline-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(107, 76, 154, 0.1);
            border-radius: 12px;
            border-left: 4px solid var(--secondary);
        }}
        
        .timeline-icon {{
            font-size: 1.5rem;
        }}
        
        .timeline-content {{
            flex: 1;
        }}
        
        .timeline-title {{
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}
        
        .timeline-date {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        
        footer {{
            text-align: center;
            color: var(--text-muted);
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔮 Akasha Wiki</h1>
            <p class="subtitle">Sistema de Auto-Evolução - Dashboard de Conhecimento</p>
            <p style="margin-top: 1rem;">
                <span class="status-badge status-{cycle_status.split()[0].lower()[1:]}">
                    {cycle_status} {cycle_status.split()[1] if len(cycle_status.split()) > 1 else ''}
                </span>
            </p>
        </header>
        
        <!-- Stats Cards -->
        <div class="grid">
            <div class="card">
                <div class="card-title">Conceitos</div>
                <div class="card-value">{stats['concepts']}</div>
                <div class="card-subtitle">Nodes de conhecimento</div>
            </div>
            <div class="card">
                <div class="card-title">Entidades</div>
                <div class="card-value">{stats['entities']}</div>
                <div class="card-subtitle">Organizações e fontes</div>
            </div>
            <div class="card">
                <div class="card-title">Conexões</div>
                <div class="card-value">{connections['total']}</div>
                <div class="card-subtitle">Links internos (densidade: {connection_density:.1f})</div>
            </div>
            <div class="card">
                <div class="card-title">Fontes</div>
                <div class="card-value">{stats['sources']}</div>
                <div class="card-subtitle">Referências procesadas</div>
            </div>
        </div>
        
        <!-- Network Analysis -->
        <div class="section">
            <h2 class="section-title">🌐 Rede de Conhecimento</h2>
            <div class="hubs-grid">
"""
    
    for hub in connections["hubs"]:
        html += f"""
                <div class="hub-item">
                    <span class="hub-name">{hub['name'].replace('-', ' ').title()}</span>
                    <span class="hub-connections">{hub['connections']} 🔗</span>
                </div>
"""
    
    if connections["orphans"]:
        html += """
            </div>
            <h3 style="margin-top: 2rem; color: var(--accent);">⚠️ Conceitos Órfãos (sem conexões)</h3>
            <div class="concept-list" style="margin-top: 1rem;">
"""
        for orphan in connections["orphans"][:10]:
            html += f'<span class="concept-tag">{orphan.replace("-", " ").title()}</span>'
    
    html += """
            </div>
        </div>
        
        <!-- Tags Cloud -->
        <div class="section">
            <h2 class="section-title">🏷️ Tags Mais Frequentes</h2>
            <div class="concept-list">
"""
    
    for tag, count in tags[:20]:
        html += f'<span class="concept-tag">{tag} <span class="concept-count">{count}</span></span>'
    
    html += """
            </div>
        </div>
        
        <!-- All Concepts -->
        <div class="section">
            <h2 class="section-title">📚 Todos os Conceitos</h2>
            <div class="concept-list">
"""
    
    for concept in sorted(stats["concept_files"]):
        html += f'<span class="concept-tag">{concept.replace("-", " ").title()}</span>'
    
    html += f"""
            </div>
        </div>
        
        <!-- System Status -->
        <div class="section">
            <h2 class="section-title">⚙️ Status do Sistema</h2>
            <div class="grid">
                <div>
                    <p><strong>Último ciclo:</strong> {last_cycle.split('T')[0] if 'T' in str(last_cycle) else last_cycle}</p>
                    <p><strong>Conceitos totais:</strong> {state.get('concepts', stats['concepts'])}</p>
                    <p><strong>Tema explorado:</strong> {state.get('last_theme', 'nenhum')}</p>
                </div>
                <div>
                    <p><strong>Cron job:</strong> ⏰ 8h, 14h, 20h, 2h</p>
                    <p><strong>Execuções restantes:</strong> ∞</p>
                    <p><strong>Modo:</strong> Contínuo</p>
                </div>
            </div>
            
            <h3 style="margin-top: 1.5rem; margin-bottom: 1rem;">📈 Progresso de Auto-Evolução</h3>
"""
    
    # Calcular progresso baseado em gaps preenchidos
    total_possible = 45  # Estimativa de conceitos possíveis
    progress = min((stats['concepts'] / total_possible) * 100, 100)
    
    html += f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress}%"></div>
            </div>
            <p style="margin-top: 0.5rem; color: var(--text-muted);">
                {progress:.0f}% do conhecimento mapeado ({stats['concepts']}/{total_possible} conceitos)
            </p>
        </div>
        
        <!-- Timeline -->
        <div class="section">
            <h2 class="section-title">📅 Timeline de Evolução</h2>
            <div class="timeline">
                <div class="timeline-item">
                    <span class="timeline-icon">🌱</span>
                    <div class="timeline-content">
                        <div class="timeline-title">Wiki Inicializada</div>
                        <div class="timeline-date">Research phase - conceitos básicos</div>
                    </div>
                </div>
                <div class="timeline-item">
                    <span class="timeline-icon">🔮</span>
                    <div class="timeline-content">
                        <div class="timeline-title">Sistema de Auto-Evolução Ativado</div>
                        <div class="timeline-date">Ciclos automáticos a cada 6 horas</div>
                    </div>
                </div>
                <div class="timeline-item">
                    <span class="timeline-icon pulse">🚀</span>
                    <div class="timeline-content">
                        <div class="timeline-title">Expansão Contínua</div>
                        <div class="timeline-date">Próximo ciclo: automático</div>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Akasha Wiki - Sistema de Conhecimento Vivo 🔮</p>
            <p style="margin-top: 0.5rem;">Gerado em: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """</p>
        </footer>
    </div>
</body>
</html>
"""
    
    return html

# =============================================================================
# EXECUÇÃO
# =============================================================================

def main():
    print("🔮 Gerando dashboard da Wiki Akasha...")
    
    stats = get_wiki_stats()
    connections = analyze_connections()
    tags = analyze_tags()
    state = get_state()
    
    html = generate_html(stats, connections, tags, state)
    
    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard gerado: {OUTPUT_FILE}")
    print(f"📊 Conceitos: {stats['concepts']} | Conexões: {connections['total']}")
    print(f"🔗 Hubs principais: {[h['name'] for h in connections['hubs'][:3]]}")

if __name__ == "__main__":
    main()
