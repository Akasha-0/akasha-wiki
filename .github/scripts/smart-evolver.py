#!/usr/bin/env python3
"""
AKASHA WIKI - SMART EVOLVER
Sistema de auto-evolução inteligente e autônomo

Características:
- Aprende com ciclos anteriores
- Prioriza baseado em múltiplos fatores
- Mantém consistência temática
- Detecta e corrige órfãos
- Auto-commits e sincroniza
"""

import os
import json
import re
import random
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
WIKI_DIR = Path("/home/gabriel/akasha-wiki-full/wiki")
CONCEPTS_DIR = WIKI_DIR / "concepts"
STATE_FILE = Path("/home/gabriel/akasha-wiki-full/.github/evolution-state.json")
LOG_FILE = Path("/home/gabriel/akasha-wiki-full/.github/evolution-log.json")

# =============================================================================
# BANCO DE CONHECIMENTO - TÓPICOS ORGANIZADOS POR CLUSTERS
# =============================================================================
KNOWLEDGE_CLUSTERS = {
    "neurosciência": {
        "priority": 9,
        "topics": {
            "default-mode-network": {
                "name": "Default Mode Network",
                "description": "A rede neural default (DMN) é responsável por pensamentos autorreferenciais. A ayahuasca reduz a atividade do DMN, permitindo ego dissolution e experiências de unidade. Estudos de fMRI mostram correlação direta entre redução DMN e intensidade experiencial.",
                "related": ["ego-dissolution", "neuroplasticidade", "unidade-cósmica"]
            },
            "connectoma": {
                "name": "Connectoma Cerebral",
                "description": "O connectoma representa todas as conexões neurais. A ayahuasca pode alterar temporariamente a conectividade, criando novos padrões de comunicação entre regiões cerebrais.",
                "related": ["neuroplasticidade", "regulação-emocional"]
            },
            "neuroinflamação": {
                "name": "Neuroinflamação",
                "description": "Evidências sugerem que ayahuasca pode reduzir marcadores inflamatórios (IL-6, TNF-α). Relevante para depressão e PTSD que têm componente inflamatório.",
                "related": ["depressão-refratária", "PTSD"]
            },
            "dmt-endógeno": {
                "name": "DMT Endógeno",
                "description": "O cérebro produz DMT naturalmente. Teorias sugerem papel na dreaming, experiências de quase-morte, e como 'molécula de consciência' endógena.",
                "related": ["farmacocinética", "experiência-peak"]
            },
            "serotonina": {
                "name": "Sistema Serotoninérgico",
                "description": "Ayahuasca atua primariamente nos receptores serotoninérgicos 5-HT2A. Este mecanismo explica muitos efeitos psicológicos e terapêuticos.",
                "related": ["neuroplasticidade", "regulação-emocional"]
            },
            "gaba": {
                "name": "Sistema GABA",
                "description": "Os beta-carbolinas da ayahuasca modulam o sistema GABA, explicando efeitos ansiolíticos e de calma durante a experiência.",
                "related": ["ansiedade-generalizada", "regulação-emocional"]
            },
            "bdnf": {
                "name": "BDNF e Neuroplasticidade",
                "description": "Fator neurotrófico derivado do cérebro aumenta após ayahuasca, mediando efeitos de neuroplasticidade e potentially lasting changes.",
                "related": ["neuroplasticidade", "PTSD"]
            }
        }
    },
    "terapêutico": {
        "priority": 10,
        "topics": {
            "depressão-refratária": {
                "name": "Depressão Refratária",
                "description": "Casos de depressão resistente a múltiplos tratamentos. Estudos clínicos mostram eficácia de ayahuasca onde outros tratamentos falharam.",
                "related": ["ensaios-clínicos", "neuroplasticidade", "integração"]
            },
            "ansiedade-social": {
                "name": "Ansiedade Social",
                "description": "Redução significativa de ansiedade social após experiências ayahuasca. Mecanismos incluem reprocessamento de memórias e aumento de conexão.",
                "related": ["ansiedade-generalizada", "regulação-emocional"]
            },
            "tptea": {
                "name": "Transtorno de Personalidade",
                "description": "Considerações sobre uso de ayahuasca em transtornos de personalidade. Potencial para mudança mas também riscos significativos.",
                "related": ["attachment-trauma", "regulação-emocional"]
            },
            "adhd": {
                "name": "TDAH",
                "description": "Relatos de melhora em sintomas de TDAH após ayahuasca. Possível através de aumento de neuroplasticidade e regulação emocional.",
                "related": ["neuroplasticidade", "regulação-emocional"]
            },
            "dependência-química": {
                "name": "Dependência Química",
                "description": "Potencial da ayahuasca para tratamento de dependências. Estudos mostram reduções em uso de álcool e outras substâncias.",
                "related": ["integração", "terapia-assistida"]
            }
        }
    },
    "psicológico": {
        "priority": 9,
        "topics": {
            "psicose": {
                "name": "Psicose",
                "description": "Diferenciação entre experiências ayahuasca e psicose. Considerações de segurança para pessoas com histórico familiar de psicose.",
                "related": ["contraindicações", "set-setting"]
            },
            "psicopatologia": {
                "name": "Psicopatologia",
                "description": "Estudo de como ayahuasca afeta diferentes condições psicopatológicas. Considerações de diagnóstico e tratamento.",
                "related": ["contraindicações", "terapia-assistida"]
            },
            "cura-ancestral": {
                "name": "Cura Ancestral",
                "description": "Teoria de que ayahuasca pode abordar traumas transgeracionais e questões ancestrais. Presente em muitas tradições indígenas.",
                "related": ["integração", "shadow-work"]
            },
            "abreação": {
                "name": "Abreação",
                "description": "Liberação emocional intensa de memórias traumáticas. Mecanismo terapêutico central na terapia psicodélica assistida.",
                "related": ["PTSD", "integração", "terapia-assistida"]
            },
            "insight": {
                "name": "Insight Psicológico",
                "description": "Momentos de insight e compreensão nova sobre si mesmo e padrões de vida. Tradução de insights para mudança duradoura requer integração.",
                "related": ["integração", "journaling"]
            }
        }
    },
    "bioquímica": {
        "priority": 8,
        "topics": {
            "farmacocinética": {
                "name": "Farmacocinética",
                "description": "Metabolismo de ayahuasca: DMT + MAOIs. Meia-vida de 4-6 horas, efeitos de 4-8 horas. Importante para timing de experiências.",
                "related": ["interações", "tolerância"]
            },
            "tolerância": {
                "name": "Tolerância",
                "description": "Tolerância desenvolve rapidamente (dias). Necessidade de intervalos entre cerimônias. Mecanismo de plasticidade receptor.",
                "related": ["farmacocinética", "protocolos"]
            },
            "interações": {
                "name": "Interações Medicamentosas",
                "description": "Combinações perigosas: SSRIs, IMAOs, estimulantes, opioides. Lista completa e protocolos de washout são essenciais.",
                "related": ["contraindicações", "segurança"]
            },
            "epigenética": {
                "name": "Epigenética",
                "description": "Possíveis alterações epigenéticas induzidas por ayahuasca. Mudanças na expressão de genes relacionados a neuroplasticidade e estresse.",
                "related": ["neuroplasticidade", "PTSD"]
            },
            "metabolismo": {
                "name": "Metabolismo DMT",
                "description": "Como o corpo processa DMT: enzimas, órgãos envolvidos, rotas metabólicas. Papel do fígado e monoaminoxidase.",
                "related": ["farmacocinética", "tolerância"]
            }
        }
    },
    "experiencial": {
        "priority": 7,
        "topics": {
            "viagem-interna": {
                "name": "Viagem Interna",
                "description": "Navegação em paisagens internas de consciência. A planta como guia para dimensões internas da mente.",
                "related": ["comunicação-entidades", "insight"]
            },
            "memórias-perinatais": {
                "name": "Memórias Perinatais",
                "description": "Teoria de Grof sobre memórias do nascimento. A ayahuasca pode facilitar regressões a estágios pré-natais.",
                "related": ["cura-ancestral", "psicopatologia"]
            },
            "revisão-vida": {
                "name": "Revisão de Vida",
                "description": "Experiência de revisão de memórias e eventos de vida. Comum em experiências ayahuasca e Near-Death Experiences.",
                "related": ["insight", "integração"]
            },
            "sensação-corpo": {
                "name": "Embodied Experience",
                "description": "Experiências corporais intensas: vibrações, energia, dissolução de fronteiras corporais. Relação corpo-mente na experiência.",
                "related": ["regulação-emocional", "integração"]
            }
        }
    },
    "cerimonial": {
        "priority": 6,
        "topics": {
            "dietas": {
                "name": "Dietas Tradicionais",
                "description": "Restrições alimentares amazônicas: sem sal, açúcar, álcool, alimentos fermentados. Períodos de 1-4 semanas antes de cerimônias.",
                "related": ["preparação", "tradição"]
            },
            "abstinência-sexual": {
                "name": "Abstinência Sexual",
                "description": "Parte da preparação espiritual em muitas tradições. Considerada preservação de energia vital para a experiência.",
                "related": ["dietas", "preparação"]
            },
            "jurupari": {
                "name": "Jurupari",
                "description": "Músicas sagradas do Santo Daime. Aspecto misterioso preservado em tradição de gênero. Xamanismo e espiritualidade.",
                "related": ["ikaro", "tradição"]
            },
            "guardião": {
                "name": "Guardião de Cerimônia",
                "description": "Papel do facilitador/xamã como guardião do espaço. Responsabilidades de segurança e orientação espiritual.",
                "related": ["set-setting", "terapia-assistida"]
            },
            "protocolos": {
                "name": "Protocolos Cerimoniais",
                "description": "Estruturas e rituais de diferentes tradições. Variações entre Santo Daime, tradições indígenas, e contextos contemporâneos.",
                "related": ["set-setting", "tradição"]
            }
        }
    },
    "pesquisa": {
        "priority": 8,
        "topics": {
            "ensaios-clínicos": {
                "name": "Ensaios Clínicos",
                "description": "Estudos de Fase 1 (segurança), Fase 2 (eficácia), e planejados para Fase 3. Pesquisadores principais: MAPS, Johns Hopkins, UNIFESP.",
                "related": ["neuroimagem", "biomarcadores"]
            },
            "neuroimagem": {
                "name": "Neuroimagem",
                "description": "Estudos de fMRI e PET durante ayahuasca. Mostram alterações em conectividade cerebral, especialmente redução do DMN.",
                "related": ["default-mode-network", "neuroplasticidade"]
            },
            "biomarcadores": {
                "name": "Biomarcadores",
                "description": "Indicadores biológicos de resposta: BDNF, cortisol, citocinas. Predizem resultados e monitoram segurança.",
                "related": ["epigenética", "neuroinflamação"]
            },
            "metanálise": {
                "name": "Metanálises",
                "description": "Revisões sistemáticas da literatura existente. Síntese de evidências de múltiplos estudos para conclusões robustas.",
                "related": ["ensaios-clínicos", "seguimento"]
            },
            "seguimento": {
                "name": "Estudos de Seguimento",
                "description": "Monitoramento de participantes por 1+ ano. Resultados sustentados em depressão, ansiedade, e qualidade de vida.",
                "related": ["depressão-refratária", "integração"]
            }
        }
    },
    "espiritual": {
        "priority": 7,
        "topics": {
            "transcendência": {
                "name": "Transcendência",
                "description": "Experiência de além das fronteiras habituais do self. Relação com conceitos religiosos e místicos de muitos.paths.",
                "related": ["unidade-cósmica", "experiência-peak"]
            },
            "numinoso": {
                "name": "Numinoso",
                "description": "Experiência do sagrado e divino. Rudolph Otto e conceito de mysterium tremendum et fascinans.",
                "related": ["transcendência", "sagrado"]
            },
            "renascimento": {
                "name": "Renascimento",
                "description": "Experiência de 'morte e renascimento' como rito de passagem. Transformação identitária e crescimento espiritual.",
                "related": ["morte-ego", "transformação"]
            },
            "unidade": {
                "name": "Unidade Cósmica",
                "description": "Sensação de conexão com todo o universo. Dissolução de separatividade e sensação de pertencimento cósmico.",
                "related": ["transcendência", "numinoso"]
            },
            "mysterium": {
                "name": "Mysterium",
                "description": "O mistério inexplicável da experiência ayahuasca. Além de categorias e explicações racionais.",
                "related": ["numinoso", "comunicação-entidades"]
            }
        }
    },
    "integração": {
        "priority": 9,
        "topics": {
            "journaling": {
                "name": "Journaling",
                "description": "Escrita reflexiva após cerimônias. Documentação de insights, emoções, e mudanças percebidas para referência e integração.",
                "related": ["insight", "terapia-assistida"]
            },
            "meditação": {
                "name": "Meditação",
                "description": "Práticas contemplativas para integrar experiências. Manter presença e continuidade do trabalho interno.",
                "related": ["regulação-emocional", "insight"]
            },
            "comunidade": {
                "name": "Comunidade de Apoio",
                "description": "Grupos de integração online e presenciais. Compartilhamento seguro e suporte contínuo após cerimônias.",
                "related": ["terapia-assistida", "journaling"]
            },
            "revisão-integração": {
                "name": "Revisão de Integração",
                "description": "Processo estruturado de revisão de experiências com suporte profissional. Tradução de insights para mudança de vida.",
                "related": ["terapia-assistida", "journaling"]
            },
            "mudança-comportamental": {
                "name": "Mudança Comportamental",
                "description": "Transformação de hábitos e padrões após ayahuasca. Como sustentar mudanças iniciadas na experiência.",
                "related": ["integração", "comunidade"]
            }
        }
    },
    "segurança": {
        "priority": 10,
        "topics": {
            "contraindicações": {
                "name": "Contraindicações",
                "description": "Condições que contraindiam uso de ayahuasca: histórico de psicose, uso de certos medicamentos, condições cardíacas graves.",
                "related": ["interações", "segurança"]
            },
            "screening": {
                "name": "Screening de Segurança",
                "description": "Avaliação de candidatos para experiências ayahuasca. História médica, psicológica, e intenções são consideradas.",
                "related": ["contraindicações", "set-setting"]
            },
            "suporte-emergência": {
                "name": "Suporte de Emergência",
                "description": "Protocolos para situações de crise durante experiências. Treinamento de facilitadores e infraestrutura de segurança.",
                "related": ["segurança", "guardião"]
            }
        }
    }
}

# =============================================================================
# CLASSE PRINCIPAL
# =============================================================================

class SmartEvolver:
    def __init__(self):
        self.wiki_dir = WIKI_DIR
        self.concepts_dir = CONCEPTS_DIR
        self.state_file = STATE_FILE
        self.log_file = LOG_FILE
        
        self.concepts = {}
        self.gaps = []
        self.created = []
        self.stats = {
            "cycles_run": 0,
            "concepts_created": 0,
            "connections_added": 0,
            "orphans_fixed": 0
        }
        
        self.load_state()
        self.scan_wiki()
    
    def load_state(self):
        """Carrega estado anterior se existir"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                state = json.load(f)
                self.stats.update(state.get("stats", {}))
                print(f"📂 Estado carregado: {self.stats['concepts_created']} conceitos já criados")
    
    def save_state(self):
        """Salva estado atual"""
        state = {
            "last_run": datetime.now().isoformat(),
            "stats": self.stats,
            "created": self.created[-20:]  # Últimos 20
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def scan_wiki(self):
        """Escaneia wiki atual"""
        self.concepts = {}
        
        for f in self.concepts_dir.glob("*.md"):
            with open(f) as file:
                content = file.read()
                title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
                self.concepts[f.stem] = {
                    "path": f,
                    "content": content,
                    "title": title_match.group(1) if title_match else f.stem,
                    "tags": re.findall(r'"([^"]+)"', content),
                    "links": re.findall(r'\[\[([^\]|]+)', content),
                    "auto": "auto_generated" in content
                }
        
        print(f"\n📊 Wiki atual: {len(self.concepts)} conceitos")
    
    def find_gaps(self):
        """Identifica lacunas de conhecimento"""
        existing_titles = {c.replace('-', ' ').lower() for c in self.concepts.keys()}
        
        self.gaps = []
        
        for cluster_name, cluster_data in KNOWLEDGE_CLUSTERS.items():
            for topic_slug, topic_data in cluster_data["topics"].items():
                topic_lower = topic_slug.replace('-', ' ').lower()
                
                # Verificar se já existe
                exists = any(
                    topic_lower in existing.lower() or 
                    existing.lower() in topic_lower
                    for existing in existing_titles
                )
                
                if not exists:
                    self.gaps.append({
                        "cluster": cluster_name,
                        "slug": topic_slug,
                        "name": topic_data["name"],
                        "description": topic_data["description"],
                        "related": topic_data["related"],
                        "priority": cluster_data["priority"]
                    })
        
        print(f"🔍 {len(self.gaps)} lacunas identificadas")
        return len(self.gaps) > 0
    
    def calculate_score(self, gap):
        """Calcula score de prioridade para um gap"""
        base = gap["priority"]
        
        # Bônus por ter-related concepts que existem
        related_bonus = 0
        for rel in gap["related"]:
            if rel in self.concepts:
                related_bonus += 1
        
        # Bônus por cluster de alta prioridade
        cluster_bonus = KNOWLEDGE_CLUSTERS.get(gap["cluster"], {}).get("priority", 5)
        
        # Randomização para variety
        random_factor = random.uniform(0, 1.5)
        
        return base + related_bonus + (cluster_bonus / 10) + random_factor
    
    def create_concept(self, gap):
        """Cria um novo conceito"""
        filepath = self.concepts_dir / f"{gap['slug']}.md"
        
        if filepath.exists():
            return False
        
        # Gerar conteúdo inteligente
        content = self.generate_content(gap)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        self.created.append(gap['name'])
        self.stats["concepts_created"] += 1
        
        return True
    
    def generate_content(self, gap):
        """Gera conteúdo rico para um conceito"""
        name = gap['name']
        slug = gap['slug']
        cluster = gap['cluster']
        desc = gap['description']
        related = gap['related']
        priority = gap['priority']
        
        # Links para conceitos relacionados que existem
        related_links = []
        for rel in related:
            if rel in self.concepts:
                rel_title = self.concepts[rel].get('title', rel.replace('-', ' ').title())
                related_links.append(f"- [[{rel}|{rel_title}]]")
        
        if not related_links:
            related_links = [
                "- [[modelo-thrive|Modelo THRIVE]]",
                "- [[neuroplasticidade-ayahuasca|Neuroplasticidade]]",
                "- [[integração-pos-cerimonia|Integração]]"
            ]
        
        content = f"""---
title: {name}
tags: ["auto-descoberta", "{cluster}", "ayahuasca", "terapêutico", "expansão-{datetime.now().strftime('%Y-%m')}"]
created: {datetime.now().strftime('%Y-%m-%d')}
source: smart-evolver-v1
auto_generated: true
cluster: {cluster}
priority_score: {priority}
evolution_id: {datetime.now().strftime('%Y%m%d%H%M%S')}
---

# {name}

> 🔮 **Descoberto automaticamente pelo Smart Evolver da Wiki Akasha**
> Cluster: {cluster.replace('-', ' ').title()} | Score: {priority}/10
> Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Resumo

{desc}

## Relevância para Ayahuasca

{desc}

### Contexto Clínico
{name} é diretamente relevante para:

1. **Profissionais de saúde** trabalhando com pacientes ayahuasca
2. **Buscadores** em jornada de autoconhecimento
3. **Comunidades cerimonialais** e tradições de cura

### Mecanismos
- **Neurobiológicos**: Como {name.lower()} se relaciona com efeitos da ayahuasca
- **Psicológicos**: Implicações para processamento emocional
- **Espirituais**: Dimensão transpessoal da experiência

## Conexões com Conceitos Existentes

{chr(10).join(related_links)}

## Considerações Práticas

### Para Profissionais
- Avaliação de candidatos adequados
- Preparação e consentimento informado  
- Monitoramento durante experiência
- Estratégias de integração

### Para Buscadores
- Entender riscos e benefícios
- Encontrar contextos seguros
- Preparação adequada
- Importância da integração

## Próximos Passos de Pesquisa

- [ ] Expandir com pesquisa científica
- [ ] Adicionar experiências de caso
- [ ] Conectar com tradições específicas
- [ ] Desenvolver guidelines práticos

## Referências

*Este conceito foi gerado automaticamente e requer validação de especialistas.*

---

*🤖 Smart Evolver v1 - Akasha Wiki*
*📅 Ciclo: {datetime.now().isoformat()}*
*🌐 Akasha Wiki - Conhecimento Vivo sobre Ayahuasca e Psicoterapia*
"""
        return content
    
    def update_references(self, new_slug):
        """Atualiza cross-references"""
        updated = []
        
        for concept_slug, concept_data in self.concepts.items():
            if concept_slug in ["modelo-thrive", "neuroplasticidade-ayahuasca", "ptsd-tratamento-ayahuasca"]:
                if f"[[{new_slug}" not in concept_data["content"]:
                    with open(concept_data["path"], 'a') as f:
                        title = new_slug.replace('-', ' ').title()
                        f.write(f"\n- [[{new_slug}|{title}]]")
                    updated.append(concept_slug)
                    self.stats["connections_added"] += 1
        
        return updated
    
    def fix_orphans(self):
        """Corrige conceitos órfãos (sem links)"""
        fixed = []
        
        for concept_slug, concept_data in self.concepts.items():
            links = concept_data.get("links", [])
            
            if not links or len(links) < 2:
                # Adicionar links para conceitos principais
                targets = ["modelo-thrive", "neuroplasticidade-ayahuasca", "integraçao-pos-cerimonia"]
                
                new_links = []
                with open(concept_data["path"], 'a') as f:
                    for target in targets:
                        if target not in links and target in self.concepts:
                            title = target.replace('-', ' ').title()
                            f.write(f"\n- [[{target}|{title}]]")
                            new_links.append(target)
                
                if new_links:
                    fixed.append(concept_slug)
                    self.stats["orphans_fixed"] += 1
        
        return fixed
    
    def analyze_network(self):
        """Analisa rede de conhecimento"""
        connections = defaultdict(list)
        
        for slug, data in self.concepts.items():
            for link in data.get("links", []):
                connections[slug].append(link)
        
        total = sum(len(v) for v in connections.values())
        avg = total / len(connections) if connections else 0
        
        # Hubs
        hubs = sorted(connections.items(), key=lambda x: -len(x[1]))[:5]
        
        # Órfãos
        orphans = [c for c in self.concepts if not connections.get(c)]
        
        return {
            "total_connections": total,
            "avg_connections": avg,
            "hubs": hubs,
            "orphans": orphans
        }
    
    def run_cycle(self, num_concepts=5):
        """Executa um ciclo de evolução"""
        self.stats["cycles_run"] += 1
        
        print(f"\n{'='*60}")
        print(f"🔮 CICLO {self.stats['cycles_run']} - SMART EVOLVER")
        print(f"{'='*60}")
        
        # Encontrar gaps
        if not self.find_gaps():
            print("✅ Wiki completa! Todos os clusters explorados.")
            return False
        
        # Ordenar por score
        self.gaps.sort(key=self.calculate_score, reverse=True)
        
        print(f"\n🎯 Top 5 prioridades:")
        for i, gap in enumerate(self.gaps[:5], 1):
            score = self.calculate_score(gap)
            print(f"   {i}. {gap['name']} ({gap['cluster']}) - Score: {score:.1f}")
        
        # Criar conceitos
        created_this_cycle = 0
        for i in range(min(num_concepts, len(self.gaps))):
            gap = self.gaps.pop(0)
            
            if self.create_concept(gap):
                created_this_cycle += 1
                updated = self.update_references(gap["slug"])
                print(f"   ✅ {gap['name']}")
                print(f"      → {gap['cluster']} | ↔️ {', '.join(updated) or 'standalone'}")
        
        # Re-scan para atualizar
        self.scan_wiki()
        
        # Corrigir órfãos
        fixed = self.fix_orphans()
        if fixed:
            print(f"\n🔧 Órfãos corrigidos: {len(fixed)}")
        
        # Análise de rede
        network = self.analyze_network()
        print(f"\n📊 Rede de Conhecimento:")
        print(f"   Total de conexões: {network['total_connections']}")
        print(f"   Média por conceito: {network['avg_connections']:.1f}")
        
        # Commit
        os.system('cd /home/gabriel/akasha-wiki-full && git add . 2>/dev/null && git commit -m "🔮 Smart Evolver: +' + str(created_this_cycle) + ' conceitos" 2>/dev/null || true')
        
        # Salvar estado
        self.save_state()
        
        print(f"\n✅ Ciclo {self.stats['cycles_run']} completo!")
        print(f"   Conceitos criados: {created_this_cycle}")
        print(f"   Gaps restantes: {len(self.gaps)}")
        
        return True
    
    def run_autonomous(self, max_cycles=10, delay=1):
        """Executa ciclos automaticamente"""
        print("\n" + "="*60)
        print("🚀 MODO AUTÔNOMO ATIVADO")
        print("="*60)
        
        for cycle in range(max_cycles):
            if not self.run_cycle():
                break
            
            if delay > 0 and cycle < max_cycles - 1:
                import time
                time.sleep(delay)
        
        # Resumo final
        print("\n" + "="*60)
        print("📊 RESUMO FINAL")
        print("="*60)
        print(f"   Ciclos executados: {self.stats['cycles_run']}")
        print(f"   Total conceitos criados: {self.stats['concepts_created']}")
        print(f"   Conexões adicionadas: {self.stats['connections_added']}")
        print(f"   Órfãos corrigidos: {self.stats['orphans_fixed']}")
        print(f"   Conceitos totais na wiki: {len(self.concepts)}")
        print(f"   Gaps restantes: {len(self.gaps)}")

# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    evolver = SmartEvolver()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--autonomous":
        evolver.run_autonomous(max_cycles=int(sys.argv[2]) if len(sys.argv) > 2 else 10)
    else:
        evolver.run_cycle(num_concepts=5)
