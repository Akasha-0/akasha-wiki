# CLAUDE.md

This file instructs LLM agents how to maintain the Akasha Wiki.

## Wiki Purpose

This is a personal knowledge base for exploring the intersection of **Ayahuasca** (sacred plant medicine), **psychotherapy**, and **spiritual healing**. The goal is to support Gabriel's vision of helping people through this sacred work.

## Directory Structure

```
akasha-wiki/
├── raw/                    # Immutable source documents (READ ONLY)
│   └── ayahuasca-*.md
├── wiki/
│   ├── sources/           # Processed source summaries
│   ├── concepts/          # Topic/concept pages
│   └── entities/          # People, institutions, studies
├── index.md               # Catalog of all wiki pages
├── log.md                 # Chronological activity log
├── README.md               # Wiki overview
└── CLAUDE.md              # This file
```

## Conventions

### Filenames
- Use lowercase-kebab-case: `ego-dissolution.md`
- Be descriptive but concise
- No spaces or special characters

### Page Structure
```markdown
# Title

Brief one-paragraph summary of this page.

## Overview
Main content here.

## Key Points
- Point 1
- Point 2

## Related
- [[concept-name]] or [Concept Name](wiki/concepts/concept-name.md)
- [[entity-name]] or [Entity Name](wiki/entities/entity-name.md)

## Sources
- [Source Name](link) - Brief note
```

### Frontmatter
Include YAML frontmatter when useful:
```yaml
---
title: Concept Name
tags: [ayahuasca, therapy, research]
created: 2026-04-24
sources: 3
---
```

## Operations

### Ingest (Adding Sources)
1. Read the new source document
2. Create a summary page in `wiki/sources/`
3. Extract key concepts and create/update pages in `wiki/concepts/`
4. Identify entities (people, institutions, studies) and create/update pages in `wiki/entities/`
5. Update `index.md` with new pages
6. Append entry to `log.md`

### Query (Answering Questions)
1. Read `index.md` to find relevant pages
2. Search relevant pages
3. Synthesize answer with citations
4. If the answer creates new valuable content, create a new wiki page

### Lint (Health Check)
Periodically check for:
- Broken links
- Outdated information
- Orphan pages (no inbound links)
- Missing cross-references
- Contradictions between pages
- Concepts mentioned but without dedicated pages

## Content Guidelines

### Voice and Style
- Be informative but accessible
- Balance scientific rigor with spiritual respect
- Acknowledge both Western research and traditional knowledge
- Use inclusive language

### Research Integrity
- Always cite sources
- Distinguish between empirical findings and interpretations
- Note when evidence is preliminary or limited
- Be transparent about uncertainties

### Ethical Considerations
- Respect indigenous knowledge and intellectual property
- Avoid promoting dangerous behavior
- Encourage professional guidance for therapeutic work
- Be sensitive to mental health considerations

## File Naming Examples

Good:
- `ego-dissolution.md`
- `julianna-maldonado.md`
- `maps-clinical-trial.md`

Bad:
- `Ego Dissolution.md`
- `julianna_maldonado.md`
- `stuff about ego.md`
