#!/usr/bin/env python3
"""
Generate a focused GEDCOM HTML family tree for one person.

The output includes:
- the main person
- direct descendants of the main person
- direct ancestors from both father and mother sides up to N generations
- spouse(s) of the main person

It intentionally excludes siblings, uncles, aunts, cousins, nieces, nephews,
and spouses outside the main person.
"""

import argparse
import html
import json
import re
from collections import defaultdict
from pathlib import Path


DEFAULT_PERSON = "Aashish Poudel"
DEFAULT_ANCESTOR_GENERATIONS = 3
DEFAULT_GEDCOM = "/Users/aashishpoudel/repos/sisneri-poudel-genealogy/data/Aashish_family.ged"
NEPALI_GIVEN_NAME_FALLBACKS = {
    "Aarvi": "आरवी",
    "Aashish": "आशिष",
    "Aayan": "आयन",
    "Adwik": "अद्विक",
}
NEPALI_SURNAME_FALLBACKS = {
    "Poudel": "पौडेल",
}


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").replace("/", " ")).strip()


def output_filename_for(name: str) -> str:
    cleaned = normalize_name(name).lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = cleaned.strip("_") or "family_tree"
    return f"{cleaned}.html"


def nepali_digits(value) -> str:
    return str(value).translate(str.maketrans("0123456789", "०१२३४५६७८९"))


def fallback_nepali_name(node: dict, default_name: str) -> str:
    given_name = node.get("given_name", "").strip()
    surname = node.get("surname", "").strip()
    nepali_given = NEPALI_GIVEN_NAME_FALLBACKS.get(given_name)
    nepali_surname = NEPALI_SURNAME_FALLBACKS.get(surname)
    if nepali_given and nepali_surname:
        return f"{nepali_given} {nepali_surname}"
    if nepali_given:
        return nepali_given
    return default_name


class GEDCOMParser:
    def __init__(self, gedcom_path):
        self.gedcom_path = Path(gedcom_path)
        self.individuals = {}
        self.families = {}

    def parse(self):
        current_id = None
        current_family_id = None
        current_event = None
        current_note_id = None

        with self.gedcom_path.open("r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")
                if not line:
                    continue

                parts = line.split(" ", 2)
                try:
                    level = int(parts[0])
                except ValueError:
                    continue

                xref = None
                tag = ""
                value = ""
                if len(parts) >= 2 and parts[1].startswith("@") and parts[1].endswith("@"):
                    xref = parts[1].strip("@")
                    rest = parts[2] if len(parts) > 2 else ""
                    rest_parts = rest.split(" ", 1)
                    tag = rest_parts[0] if rest_parts else ""
                    value = rest_parts[1] if len(rest_parts) > 1 else ""
                else:
                    tag = parts[1] if len(parts) > 1 else ""
                    value = parts[2] if len(parts) > 2 else ""

                if level == 0:
                    current_event = None
                    current_note_id = None
                    if tag == "INDI":
                        current_id = xref or value.strip("@")
                        current_family_id = None
                        self.individuals[current_id] = {
                            "id": current_id,
                            "name": "",
                            "given_name": "",
                            "surname": "",
                            "nepali_name": "",
                            "birth": "",
                            "birth_place": "",
                            "death": "",
                            "sex": "",
                            "notes": "",
                            "famc": [],
                            "fams": [],
                            "parents": [],
                            "children": [],
                        }
                    elif tag == "FAM":
                        current_family_id = xref or value.strip("@")
                        current_id = None
                        self.families[current_family_id] = {
                            "id": current_family_id,
                            "husband": "",
                            "wife": "",
                            "children": [],
                        }
                    else:
                        current_id = None
                        current_family_id = None
                    continue

                if current_id and current_id in self.individuals:
                    person = self.individuals[current_id]
                    if level == 1:
                        current_event = tag if tag in {"BIRT", "DEAT"} else None
                        if tag == "NAME":
                            person["name"] = normalize_name(value)
                        elif tag == "GIVN":
                            person["given_name"] = value.strip()
                        elif tag == "SURN":
                            person["surname"] = value.strip()
                        elif tag == "SEX":
                            person["sex"] = value.strip()
                        elif tag == "FAMC":
                            fam_id = value.strip("@")
                            if fam_id not in person["famc"]:
                                person["famc"].append(fam_id)
                        elif tag == "FAMS":
                            fam_id = value.strip("@")
                            if fam_id not in person["fams"]:
                                person["fams"].append(fam_id)
                        elif tag == "NOTE":
                            current_note_id = current_id
                            note = value.strip()
                            person["notes"] = note
                            if note.startswith("Bio notes:"):
                                person["nepali_name"] = note.replace("Bio notes:", "", 1).strip()
                    elif level == 2:
                        if tag == "DATE" and current_event == "BIRT":
                            person["birth"] = value.strip()
                        elif tag == "DATE" and current_event == "DEAT":
                            person["death"] = value.strip()
                        elif tag == "PLAC" and current_event == "BIRT":
                            person["birth_place"] = value.strip()
                        elif tag == "GIVN":
                            person["given_name"] = value.strip()
                        elif tag == "SURN":
                            person["surname"] = value.strip()
                        elif tag == "CONT" and current_note_id == current_id:
                            continuation = value.strip()
                            person["notes"] = (person["notes"] + " " + continuation).strip()
                            if person["notes"].startswith("Bio notes:"):
                                person["nepali_name"] = person["notes"].replace("Bio notes:", "", 1).strip()

                elif current_family_id and current_family_id in self.families:
                    family = self.families[current_family_id]
                    if level == 1 and tag == "HUSB":
                        family["husband"] = value.strip("@")
                    elif level == 1 and tag == "WIFE":
                        family["wife"] = value.strip("@")
                    elif level == 1 and tag == "CHIL":
                        child_id = value.strip("@")
                        if child_id not in family["children"]:
                            family["children"].append(child_id)

        self._build_relationships()
        return self

    def _build_relationships(self):
        for family in self.families.values():
            parents = [pid for pid in [family.get("husband"), family.get("wife")] if pid]
            for child_id in family["children"]:
                if child_id not in self.individuals:
                    continue
                child = self.individuals[child_id]
                for parent_id in parents:
                    if parent_id in self.individuals and parent_id not in child["parents"]:
                        child["parents"].append(parent_id)
                    if parent_id in self.individuals and child_id not in self.individuals[parent_id]["children"]:
                        self.individuals[parent_id]["children"].append(child_id)


class FocusedPersonTreeGenerator:
    def __init__(self, parser: GEDCOMParser):
        self.parser = parser
        self.individuals = parser.individuals
        self.families = parser.families

    def generate(self, main_person: str, num_ancestor_generations: int):
        main_id = self._find_person_by_full_name(main_person)
        if not main_id:
            raise ValueError(f"Could not find main person: {main_person}")

        selected = {}
        links = set()

        def add_person(person_id, generation, path):
            if not person_id or person_id not in self.individuals:
                return False
            if person_id in selected:
                existing = selected[person_id]
                if abs(generation) < abs(existing["generation"]):
                    existing["generation"] = generation
                    existing["path"] = path
                return False
            selected[person_id] = {"generation": generation, "path": path}
            return True

        add_person(main_id, 0, "m")
        self._collect_spouses(main_id, selected, links)
        self._collect_ancestors(main_id, num_ancestor_generations, selected, links, "a")
        self._collect_descendants(main_id, selected, links, "d")

        nodes = []
        for person_id, meta in selected.items():
            person = self.individuals[person_id]
            nodes.append({
                "id": person_id,
                "name": person["name"] or "(unknown)",
                "given_name": person["given_name"] or person["name"] or "(unknown)",
                "surname": person["surname"],
                "nepali_name": person["nepali_name"],
                "birth": person["birth"],
                "birth_place": person["birth_place"],
                "death": person["death"],
                "sex": person["sex"],
                "notes": person["notes"],
                "generation": meta["generation"],
                "path": meta["path"],
                "is_main": person_id == main_id,
                "is_spouse": meta.get("is_spouse", False),
            })

        links_list = [{"source": source, "target": target} for source, target in sorted(links)]
        output_path = Path(__file__).resolve().parents[1] / output_filename_for(main_person)
        output_path.write_text(self._create_html(main_person, nodes, links_list, num_ancestor_generations), encoding="utf-8")
        print(f"Focused family tree generated: {output_path}")
        print(f"People shown: {len(nodes)}")
        return output_path

    def _find_person_by_full_name(self, name: str):
        wanted = normalize_name(name).lower()
        exact_matches = []
        contains_matches = []
        for person_id, person in self.individuals.items():
            full = normalize_name(person["name"])
            given_surname = normalize_name(f"{person['given_name']} {person['surname']}")
            candidates = {full.lower(), given_surname.lower()}
            if wanted in candidates:
                exact_matches.append(person_id)
            elif wanted and any(wanted in c for c in candidates):
                contains_matches.append(person_id)
        if exact_matches:
            return exact_matches[0]
        if contains_matches:
            return contains_matches[0]
        return None

    def _parent_ids_for(self, person_id):
        person = self.individuals.get(person_id)
        if not person:
            return []
        ordered = []
        for fam_id in person["famc"]:
            family = self.families.get(fam_id)
            if not family:
                continue
            for parent_id in [family.get("husband"), family.get("wife")]:
                if parent_id and parent_id in self.individuals and parent_id not in ordered:
                    ordered.append(parent_id)
        for parent_id in person["parents"]:
            if parent_id in self.individuals and parent_id not in ordered:
                ordered.append(parent_id)
        return ordered

    def _collect_ancestors(self, person_id, remaining, selected, links, path):
        if remaining <= 0:
            return
        parent_ids = self._parent_ids_for(person_id)
        for idx, parent_id in enumerate(parent_ids):
            parent_path = f"{path}{idx}"
            generation = selected[person_id]["generation"] - 1
            added = parent_id not in selected
            selected.setdefault(parent_id, {"generation": generation, "path": parent_path})
            if added:
                selected[parent_id] = {"generation": generation, "path": parent_path}
            links.add((parent_id, person_id))
            self._collect_ancestors(parent_id, remaining - 1, selected, links, parent_path)

    def _children_for(self, person_id):
        person = self.individuals.get(person_id)
        if not person:
            return []
        ordered = []
        for fam_id in person["fams"]:
            family = self.families.get(fam_id)
            if not family:
                continue
            for child_id in family["children"]:
                if child_id in self.individuals and child_id not in ordered:
                    ordered.append(child_id)
        for child_id in person["children"]:
            if child_id in self.individuals and child_id not in ordered:
                ordered.append(child_id)
        return ordered

    def _spouse_ids_for(self, person_id):
        person = self.individuals.get(person_id)
        if not person:
            return []
        ordered = []
        for fam_id in person["fams"]:
            family = self.families.get(fam_id)
            if not family:
                continue
            for spouse_id in [family.get("husband"), family.get("wife")]:
                if spouse_id and spouse_id != person_id and spouse_id in self.individuals and spouse_id not in ordered:
                    ordered.append(spouse_id)
        return ordered

    def _collect_spouses(self, person_id, selected, links):
        for idx, spouse_id in enumerate(self._spouse_ids_for(person_id)):
            if spouse_id not in selected:
                selected[spouse_id] = {"generation": 0, "path": f"s{idx:03d}", "is_spouse": True}

    def _collect_descendants(self, person_id, selected, links, path):
        child_ids = self._children_for(person_id)
        for idx, child_id in enumerate(child_ids):
            child_path = f"{path}{idx:03d}"
            generation = selected[person_id]["generation"] + 1
            if child_id not in selected:
                selected[child_id] = {"generation": generation, "path": child_path}
                self._collect_descendants(child_id, selected, links, child_path)
            for parent_id in self._parent_ids_for(child_id):
                if parent_id in selected:
                    links.add((parent_id, child_id))

    def _create_html(self, main_person, nodes, links, num_ancestor_generations):
        nodes_json = json.dumps(nodes, ensure_ascii=False)
        links_json = json.dumps(links, ensure_ascii=False)
        main_node = next((node for node in nodes if node.get("is_main")), {})
        nepali_name = main_node.get("nepali_name") or fallback_nepali_name(main_node, main_person)
        nepali_generation_count = nepali_digits(num_ancestor_generations)
        safe_header_title = html.escape(f"{nepali_name}को वंशावली ({main_person} Family Tree)")
        safe_subtitle = html.escape(
            f"प्रत्यक्ष पुर्खा {nepali_generation_count} पुस्ता र वंशजहरू "
            f"(Direct Ancestors {num_ancestor_generations} generations/Descendents)"
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_header_title}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        :root {{
            --bg: #f7f9fb;
            --card: #ffffff;
            --text: #1f2a37;
            --muted: #6b7280;
            --ring: #1abc9c;
            --line: #e5eef4;
            --shadow: 0 10px 30px rgba(0,0,0,.06);
            --header-height: 104px;
            --control-top: 125px;
            --legend-top: 184px;
            --control-width: 112px;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #fef8e7 0%, #fffbf0 100%);
            color: #3d3d3d;
            overflow: hidden;
            height: 100vh;
        }}

        .page-header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999;
            background: var(--bg);
            border-bottom: 1px solid var(--line);
            box-shadow: 0 2px 8px rgba(0,0,0,.05);
        }}

        .header-wrap {{
            padding: 16px 20px;
        }}

        .crumbs a {{
            color: var(--muted);
            text-decoration: none;
            font: 14px system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        }}

        .crumbs a:hover {{
            text-decoration: underline;
            color: var(--text);
        }}

        .header-title {{
            color: var(--text);
            margin: 6px 0 0;
            text-align: center;
            font: 600 31px/1.2 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        }}

        .header-subtitle {{
            color: var(--muted);
            margin-top: 4px;
            text-align: center;
            font: 15px/1.4 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        }}

        body.embedded-tree .page-header {{
            display: none;
        }}

        #container {{
            width: 100%;
            height: calc(100vh - var(--header-height));
            margin-top: var(--header-height);
            position: relative;
            overflow: auto;
            background: linear-gradient(135deg, #fef8e7 0%, #fffbf0 100%);
        }}

        body.embedded-tree #container {{
            height: 100vh;
            margin-top: 0;
        }}

        .hidden-tree {{
            display: none;
        }}

        svg {{
            display: block;
            margin: auto;
        }}

        .link {{
            fill: none;
            stroke: rgba(180, 140, 80, 0.4);
            stroke-width: 4px;
        }}

        .node {{
            cursor: pointer;
        }}

        .node-group {{
            transition: all 0.3s ease;
        }}

        .node-rect {{
            rx: 8;
            ry: 8;
            stroke-width: 2.5px;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
            transition: all 0.3s ease;
        }}

        .node.male .node-rect {{
            fill: #e8f4f8;
            stroke: #7fb3d5;
        }}

        .node.female .node-rect {{
            fill: #fce8f3;
            stroke: #e8a8c8;
        }}

        .node.unknown .node-rect {{
            fill: #f5f5f5;
            stroke: #c0c0c0;
        }}

        .node.main-person .node-rect {{
            fill: #fff8dc !important;
            stroke: #d4af37 !important;
            stroke-width: 3px !important;
            filter: drop-shadow(0 0 8px rgba(212, 175, 55, 0.6)) !important;
        }}

        .node:hover .node-rect {{
            filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.3));
            stroke-width: 3px;
        }}

        .node-text {{
            font-size: 21px;
            font-weight: bold;
            text-anchor: middle;
            pointer-events: none;
            fill: #3d3d3d;
            text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
        }}

        .node-date {{
            font-size: 12px;
            text-anchor: middle;
            fill: #6b6b6b;
            text-shadow: 0 1px 1px rgba(255, 255, 255, 0.5);
            pointer-events: none;
        }}

        .tooltip {{
            position: fixed;
            background: rgba(255, 248, 220, 0.98);
            color: #3d3d3d;
            padding: 12px 16px;
            border-radius: 6px;
            border-left: 4px solid #d4af37;
            font-size: 13px;
            pointer-events: none;
            z-index: 1000;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
            max-width: 300px;
            display: none;
        }}

        .tooltip.visible {{
            display: block;
        }}

        .tooltip-title {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 6px;
            color: #8b6914;
        }}

        .tooltip-line {{
            margin: 3px 0;
            line-height: 1.3;
        }}

        .controls {{
            position: fixed;
            top: var(--control-top);
            right: 20px;
            width: var(--control-width);
            background: #d4af37;
            padding: 0;
            border-radius: 4px;
            border: 2px solid #d4af37;
            z-index: 998;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}

        .control-btn {{
            background: #d4af37;
            color: #3d3d3d;
            border: none;
            padding: 7px 14px;
            width: 100%;
            border-radius: 4px;
            cursor: pointer;
            margin: 0;
            font-size: 18px;
            font-weight: bold;
            white-space: nowrap;
            transition: all 0.3s ease;
        }}

        .control-btn:hover {{
            background: #e8c547;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(212, 175, 55, 0.4);
        }}

        body.embedded-tree .controls {{
            top: 14px;
        }}

        .tree-legend {{
            position: fixed;
            top: var(--legend-top);
            right: 20px;
            width: var(--control-width);
            z-index: 998;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1px;
        }}

        .legend-row {{
            display: flex;
            align-items: center;
            height: 32px;
        }}

        .legend-icon {{
            width: 24px;
            height: 32px;
            filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.18));
        }}

        .legend-icon.male {{
            color: #7fb3d5;
        }}

        .legend-icon.female {{
            color: #e8a8c8;
        }}

        body.embedded-tree .tree-legend {{
            top: 64px;
        }}
    </style>
</head>
<body>
    <header class="page-header">
        <div class="header-wrap">
            <nav class="crumbs" aria-label="Breadcrumb">
                <a href="index.html">← Back to Home</a>
            </nav>
            <h1 class="header-title">{safe_header_title}</h1>
            <div class="header-subtitle">{safe_subtitle}</div>
        </div>
    </header>

    <div id="container">
        <svg aria-hidden="true" class="hidden-tree" id="tree-horizontal"></svg>
        <svg id="tree-vertical"></svg>
    </div>

    <div class="controls">
        <button class="control-btn" onclick="fitView()">Fit View</button>
    </div>

    <div aria-label="Gender color key" class="tree-legend">
        <div class="legend-row">
            <svg aria-hidden="true" class="legend-icon male" viewBox="0 0 24 32">
                <circle cx="12" cy="4" fill="currentColor" r="3.2"></circle>
                <path d="M8 8h8c1.4 0 2.5 1.1 2.5 2.5v8.2h-2.8V31h-3V19.5h-1.4V31h-3V18.7H5.5v-8.2C5.5 9.1 6.6 8 8 8z" fill="currentColor"></path>
            </svg>
        </div>
        <div class="legend-row">
            <svg aria-hidden="true" class="legend-icon female" viewBox="0 0 24 32">
                <circle cx="12" cy="4" fill="currentColor" r="3.2"></circle>
                <path d="M8.7 8h6.6l4.2 12h-3.2L18 31h-3.1l-1.3-11h-3.2L9.1 31H6l1.7-11H4.5L8.7 8z" fill="currentColor"></path>
            </svg>
        </div>
    </div>

    <div id="tooltip" class="tooltip"></div>

    <script>
        const sourceNodesData = {nodes_json};
        const linksData = {links_json};

        const nodeWidth = 211;
        const nodeHeight = 100;
        const nodeSpacingX = 280;
        const generationSpacingY = 160;
        const verticalColumnSpacingX = 340;
        const verticalNodeSpacingY = 128;
        const headerMargin = 14;
        const margin = {{ top: 80, right: 120, bottom: 120, left: 120 }};
        const renderStates = new Map();
        const embeddedInFrame = window.self !== window.top;

        if (embeddedInFrame) {{
            document.body.classList.add('embedded-tree');
        }}

        function measuredHeaderHeight() {{
            if (embeddedInFrame) return 0;
            const header = document.querySelector('.page-header');
            return header ? Math.ceil(header.getBoundingClientRect().height) : 104;
        }}

        function updateLayoutChrome() {{
            const headerHeight = measuredHeaderHeight();
            const controlTop = embeddedInFrame ? headerMargin : headerHeight + headerMargin;
            document.documentElement.style.setProperty('--header-height', `${{headerHeight}}px`);
            document.documentElement.style.setProperty('--control-top', `${{controlTop}}px`);
            requestAnimationFrame(() => {{
                const controls = document.querySelector('.controls');
                const legendTop = controls
                    ? Math.ceil(controls.getBoundingClientRect().bottom + 10)
                    : controlTop + 60;
                document.documentElement.style.setProperty('--legend-top', `${{legendTop}}px`);
            }});
            return headerHeight;
        }}

        function cloneNodes() {{
            return sourceNodesData.map(node => ({{ ...node }}));
        }}

        function orderedRows(nodes) {{
            const rows = d3.group(nodes, d => d.generation);
            const generations = Array.from(rows.keys()).sort((a, b) => a - b);
            return {{ rows, generations }};
        }}

        function sortByPath(a, b) {{
            return d3.ascending(a.path, b.path) || d3.ascending(a.name, b.name);
        }}

        function applyHorizontalLayout(nodes, links) {{
            const nodeById = new Map(nodes.map(node => [node.id, node]));
            const {{ rows, generations }} = orderedRows(nodes);
            const maxRowCount = d3.max(Array.from(rows.values()), row => row.length) || 1;
            let svgWidth = Math.max(1200, (maxRowCount - 1) * nodeSpacingX + margin.left + margin.right + nodeWidth);
            const svgHeight = Math.max(800, (generations.length - 1) * generationSpacingY + margin.top + margin.bottom + nodeHeight);
            const minGeneration = d3.min(generations) || 0;
            const centerX = svgWidth / 2;
            const mainNode = nodes.find(node => node.is_main);
            const parentLinksByTarget = d3.group(links, link => link.target);
            const maxAncestorDepth = Math.abs(Math.min(0, minGeneration));

            generations.forEach(generation => {{
                (rows.get(generation) || []).forEach(node => {{
                    node.y = margin.top + (generation - minGeneration) * generationSpacingY;
                }});
            }});

            if (mainNode) {{
                mainNode.x = centerX;
            }}

            const spouseNodes = nodes.filter(node => node.is_spouse).sort(sortByPath);
            spouseNodes.forEach((node, index) => {{
                node.x = centerX + (index + 1) * nodeSpacingX;
            }});

            for (let childGeneration = 0; childGeneration > minGeneration; childGeneration--) {{
                const children = (rows.get(childGeneration) || []).sort(sortByPath);
                children.forEach(child => {{
                    if (!Number.isFinite(child.x)) return;
                    const parents = (parentLinksByTarget.get(child.id) || [])
                        .map(link => nodeById.get(link.source))
                        .filter(parent => parent && parent.generation === childGeneration - 1)
                        .sort(sortByPath);
                    if (!parents.length) return;

                    const parentGeneration = childGeneration - 1;
                    const parentOffset = Math.max(
                        nodeSpacingX / 2,
                        nodeSpacingX * Math.pow(2, maxAncestorDepth - Math.abs(parentGeneration) - 1)
                    );

                    if (parents.length === 1) {{
                        parents[0].x = child.x;
                    }} else {{
                        const pairWidth = (parents.length - 1) * parentOffset * 2;
                        const startX = child.x - pairWidth / 2;
                        parents.forEach((parent, index) => {{
                            parent.x = startX + index * parentOffset * 2;
                        }});
                    }}
                }});
            }}

            generations
                .filter(generation => generation > 0)
                .forEach(generation => {{
                    const row = (rows.get(generation) || []).sort(sortByPath);
                    const rowWidth = (row.length - 1) * nodeSpacingX;
                    const startX = (mainNode?.x || centerX) - rowWidth / 2;
                    row.forEach((node, index) => {{
                        node.x = startX + index * nodeSpacingX;
                    }});
                }});

            const minX = d3.min(nodes, node => node.x - nodeWidth / 2) || 0;
            if (minX < margin.left) {{
                const shiftRight = margin.left - minX;
                nodes.forEach(node => node.x += shiftRight);
            }}
            const maxX = d3.max(nodes, node => node.x + nodeWidth / 2) || svgWidth;
            if (maxX > svgWidth - margin.right) {{
                svgWidth = maxX + margin.right;
            }}

            return {{ svgWidth, svgHeight }};
        }}

        function applyVerticalLayout(nodes, links) {{
            const nodeById = new Map(nodes.map(node => [node.id, node]));
            const parentLinksByTarget = d3.group(links, link => link.target);
            const childLinksBySource = d3.group(links, link => link.source);
            const {{ rows, generations }} = orderedRows(nodes);
            const maxColumnCount = d3.max(Array.from(rows.values()), row => row.length) || 1;
            const minGeneration = d3.min(generations) || 0;
            const svgWidth = Math.max(1200, (generations.length - 1) * verticalColumnSpacingX + margin.left + margin.right + nodeWidth);
            let svgHeight = Math.max(800, (maxColumnCount - 1) * verticalNodeSpacingY + margin.top + margin.bottom + nodeHeight);
            let nextLeafY = margin.top + nodeHeight / 2;

            nodes.forEach(node => {{
                node.x = margin.left + (node.generation - minGeneration) * verticalColumnSpacingX;
            }});

            function displayedParentsFor(node) {{
                return (parentLinksByTarget.get(node.id) || [])
                    .map(parentLink => nodeById.get(parentLink.source))
                    .filter(parent => parent && parent.generation === node.generation - 1)
                    .sort(sortByPath);
            }}

            function displayedChildrenFor(node) {{
                const seen = new Set();
                return (childLinksBySource.get(node.id) || [])
                    .map(childLink => nodeById.get(childLink.target))
                    .filter(child => {{
                        if (!child || child.generation !== node.generation + 1 || seen.has(child.id)) {{
                            return false;
                        }}
                        seen.add(child.id);
                        return true;
                    }})
                    .sort(sortByPath);
            }}

            function placeAncestorSubtree(node) {{
                if (!node || Number.isFinite(node.y)) return node?.y;

                const parents = displayedParentsFor(node);
                if (!parents.length) {{
                    node.y = nextLeafY;
                    nextLeafY += verticalNodeSpacingY;
                    return node.y;
                }}

                parents.forEach(parent => placeAncestorSubtree(parent));
                node.y = d3.mean(parents, parent => parent.y);
                return node.y;
            }}

            const mainNode = nodes.find(node => node.is_main);
            if (mainNode) {{
                placeAncestorSubtree(mainNode);
            }}

            const spouseNodes = nodes.filter(node => node.is_spouse).sort(sortByPath);
            spouseNodes.forEach((node, index) => {{
                if (mainNode && Number.isFinite(mainNode.y)) {{
                    node.y = mainNode.y + (index + 1) * verticalNodeSpacingY;
                }}
            }});

            generations
                .filter(generation => generation <= 0)
                .forEach(generation => {{
                    (rows.get(generation) || [])
                        .filter(node => !node.is_spouse)
                        .sort(sortByPath)
                        .forEach(node => placeAncestorSubtree(node));
                }});

            let nextDescendantLeafY = 0;
            function placeDescendantSubtree(node) {{
                if (!node) return 0;
                if (Number.isFinite(node.descY)) return node.descY;

                const children = displayedChildrenFor(node);
                if (!children.length) {{
                    node.descY = nextDescendantLeafY;
                    nextDescendantLeafY += verticalNodeSpacingY;
                    return node.descY;
                }}

                children.forEach(child => placeDescendantSubtree(child));
                node.descY = d3.mean(children, child => child.descY);
                return node.descY;
            }}

            const descendantRoots = (rows.get(1) || []).sort(sortByPath);
            descendantRoots.forEach(root => placeDescendantSubtree(root));

            if (descendantRoots.length) {{
                const firstRootParents = displayedParentsFor(descendantRoots[0])
                    .filter(parent => Number.isFinite(parent.y));
                const descendantAnchorY = firstRootParents.length
                    ? d3.mean(firstRootParents, parent => parent.y)
                    : mainNode?.y || margin.top;
                const descendantTop = d3.min(descendantRoots, root => root.descY);
                const descendantBottom = d3.max(descendantRoots, root => root.descY);
                const descendantShiftY = descendantAnchorY - (descendantTop + descendantBottom) / 2;

                generations
                    .filter(generation => generation > 0)
                    .forEach(generation => {{
                        (rows.get(generation) || []).forEach(node => {{
                            if (Number.isFinite(node.descY)) {{
                                node.y = node.descY + descendantShiftY;
                            }}
                        }});
                    }});
            }}

            const minY = d3.min(nodes, node => node.y - nodeHeight / 2) || 0;
            if (minY < margin.top) {{
                const shiftDown = margin.top - minY;
                nodes.forEach(node => node.y += shiftDown);
            }}

            const maxY = d3.max(nodes, node => node.y + nodeHeight / 2) || svgHeight;
            if (maxY > svgHeight - margin.bottom) {{
                svgHeight = maxY + margin.bottom;
            }}

            return {{ svgWidth, svgHeight }};
        }}

        function wrapText(text, maxChars = 16) {{
            text = text || '(unknown)';
            if (text.length <= maxChars) return [text];
            const words = text.split(' ');
            const lines = [];
            let currentLine = '';
            for (let word of words) {{
                if ((currentLine + word).length <= maxChars) {{
                    currentLine += (currentLine ? ' ' : '') + word;
                }} else {{
                    if (currentLine) lines.push(currentLine);
                    currentLine = word;
                }}
            }}
            if (currentLine) lines.push(currentLine);
            return lines;
        }}

        function linkPath(link, nodeById, orientation, parentLinksByTarget) {{
            const source = nodeById.get(link.source);
            const target = nodeById.get(link.target);
            if (!source || !target) return '';
            const x0 = source.x;
            const y0 = source.y;
            const x1 = target.x;
            const y1 = target.y;

            if (orientation === 'vertical') {{
                if (source.generation === target.generation) {{
                    const sourceExitX = x0 + nodeWidth / 2;
                    const targetEntryX = x1 + nodeWidth / 2;
                    return `M${{sourceExitX}},${{y0}}L${{sourceExitX}},${{y1}}L${{targetEntryX}},${{y1}}`;
                }}

                const sourceExitX = x0 + nodeWidth / 2;
                const targetEntryX = x1 - nodeWidth / 2;
                const trunkX = (sourceExitX + targetEntryX) / 2;
                const parents = (parentLinksByTarget.get(link.target) || [])
                    .map(parentLink => nodeById.get(parentLink.source))
                    .filter(parent => parent && parent.generation === source.generation);
                if (parents.length < 2) {{
                    return `M${{sourceExitX}},${{y0}}L${{trunkX}},${{y0}}L${{trunkX}},${{y1}}L${{targetEntryX}},${{y1}}`;
                }}
                const parentYs = parents.length ? parents.map(parent => parent.y) : [y0];
                const parentTopY = d3.min([...parentYs, y1]);
                const parentBottomY = d3.max([...parentYs, y1]);
                return `M${{sourceExitX}},${{y0}}L${{trunkX}},${{y0}}M${{trunkX}},${{parentTopY}}L${{trunkX}},${{parentBottomY}}M${{trunkX}},${{y1}}L${{targetEntryX}},${{y1}}`;
            }}

            const midY = (y0 + y1) / 2;
            return `M${{x0}},${{y0}}L${{x0}},${{midY}}L${{x1}},${{midY}}L${{x1}},${{y1}}`;
        }}

        function parentKey(parents) {{
            return parents.map(parent => parent.id).sort().join('|');
        }}

        function buildRenderedLinks(links, nodeById, orientation, parentLinksByTarget) {{
            if (orientation !== 'vertical') {{
                return links.map(link => ({{
                    path: linkPath(link, nodeById, orientation, parentLinksByTarget)
                }}));
            }}

            const rendered = [];
            const groupedChildren = new Map();

            for (const [targetId, parentLinks] of parentLinksByTarget.entries()) {{
                const target = nodeById.get(targetId);
                if (!target) continue;
                const parents = parentLinks
                    .map(parentLink => nodeById.get(parentLink.source))
                    .filter(parent => parent && parent.generation === target.generation - 1)
                    .sort(sortByPath);

                if (parents.length < 2) {{
                    parentLinks.forEach(parentLink => {{
                        rendered.push({{
                            path: linkPath(parentLink, nodeById, orientation, parentLinksByTarget)
                        }});
                    }});
                    continue;
                }}

                const key = `${{parentKey(parents)}}:${{target.generation}}`;
                if (!groupedChildren.has(key)) {{
                    groupedChildren.set(key, {{ parents, children: [] }});
                }}
                groupedChildren.get(key).children.push(target);
            }}

            groupedChildren.forEach(group => {{
                const parents = group.parents;
                const children = group.children.sort(sortByPath);
                const sourceExitX = d3.max(parents, parent => parent.x + nodeWidth / 2);
                const targetEntryX = d3.min(children, child => child.x - nodeWidth / 2);
                const availableWidth = Math.max(1, targetEntryX - sourceExitX);

                if (children.length < 2) {{
                    const child = children[0];
                    const trunkX = sourceExitX + availableWidth / 2;
                    const parentYs = parents.map(parent => parent.y);
                    const parentTopY = d3.min([...parentYs, child.y]);
                    const parentBottomY = d3.max([...parentYs, child.y]);
                    parents.forEach(parent => {{
                        rendered.push({{ path: `M${{parent.x + nodeWidth / 2}},${{parent.y}}L${{trunkX}},${{parent.y}}` }});
                    }});
                    rendered.push({{ path: `M${{trunkX}},${{parentTopY}}L${{trunkX}},${{parentBottomY}}` }});
                    rendered.push({{ path: `M${{trunkX}},${{child.y}}L${{child.x - nodeWidth / 2}},${{child.y}}` }});
                    return;
                }}

                let parentTrunkX = sourceExitX + Math.min(90, Math.max(40, availableWidth * 0.28));
                let childTrunkX = targetEntryX - Math.min(90, Math.max(40, availableWidth * 0.28));
                if (childTrunkX <= parentTrunkX + 24) {{
                    parentTrunkX = sourceExitX + availableWidth / 3;
                    childTrunkX = sourceExitX + availableWidth * 2 / 3;
                }}

                const parentYs = parents.map(parent => parent.y);
                const childYs = children.map(child => child.y);
                const parentTopY = d3.min(parentYs);
                const parentBottomY = d3.max(parentYs);
                const parentMidY = d3.mean(parentYs);
                const childTopY = d3.min(childYs);
                const childBottomY = d3.max(childYs);

                parents.forEach(parent => {{
                    rendered.push({{ path: `M${{parent.x + nodeWidth / 2}},${{parent.y}}L${{parentTrunkX}},${{parent.y}}` }});
                }});
                rendered.push({{ path: `M${{parentTrunkX}},${{parentTopY}}L${{parentTrunkX}},${{parentBottomY}}` }});
                rendered.push({{ path: `M${{parentTrunkX}},${{parentMidY}}L${{childTrunkX}},${{parentMidY}}` }});
                rendered.push({{ path: `M${{childTrunkX}},${{childTopY}}L${{childTrunkX}},${{childBottomY}}` }});
                children.forEach(child => {{
                    rendered.push({{ path: `M${{childTrunkX}},${{child.y}}L${{child.x - nodeWidth / 2}},${{child.y}}` }});
                }});
            }});

            return rendered;
        }}

        function renderTree(svgSelector, nodes, links, dimensions, orientation) {{
            const nodeById = new Map(nodes.map(node => [node.id, node]));
            const parentLinksByTarget = d3.group(links, link => link.target);
            const renderedLinks = buildRenderedLinks(links, nodeById, orientation, parentLinksByTarget);
            const svg = d3.select(svgSelector)
                .attr('width', dimensions.svgWidth)
                .attr('height', dimensions.svgHeight);
            const g = svg.append('g');

            g.selectAll('.link')
                .data(renderedLinks)
                .enter()
                .append('path')
                .attr('class', 'link')
                .attr('d', d => d.path);

            const nodeGroups = g.selectAll('.node')
                .data(nodes)
                .enter()
                .append('g')
                .attr('class', d => {{
                    let cls = 'node-group node ';
                    if (d.sex === 'M') cls += 'male';
                    else if (d.sex === 'F') cls += 'female';
                    else cls += 'unknown';
                    if (d.is_main) cls += ' main-person';
                    return cls;
                }})
                .attr('transform', d => `translate(${{d.x}},${{d.y}})`)
                .on('mouseover', function(e, d) {{
                    const tooltip = document.getElementById('tooltip');
                    tooltip.classList.add('visible');
                    let tooltipHTML = `<div class="tooltip-title">${{d.name}}</div>`;
                    if (d.birth) tooltipHTML += `<div class="tooltip-line"><strong>DOB:</strong> ${{d.birth}}</div>`;
                    if (d.birth_place) tooltipHTML += `<div class="tooltip-line"><strong>Place:</strong> ${{d.birth_place}}</div>`;
                    if (d.death) tooltipHTML += `<div class="tooltip-line"><strong>DOD:</strong> ${{d.death}}</div>`;
                    if (d.notes) {{
                        let cleanNotes = d.notes.startsWith('Bio notes:') ? d.notes.replace('Bio notes:', '').trim() : d.notes;
                        if (cleanNotes) tooltipHTML += `<div class="tooltip-line">${{cleanNotes}}</div>`;
                    }}
                    if (!d.birth && !d.birth_place && !d.death && !d.notes) {{
                        tooltipHTML += `<div class="tooltip-line"><em>No additional information</em></div>`;
                    }}
                    tooltip.innerHTML = tooltipHTML;
                    tooltip.style.left = (e.pageX + 10) + 'px';
                    tooltip.style.top = (e.pageY + 10) + 'px';
                }})
                .on('mousemove', e => {{
                    const tooltip = document.getElementById('tooltip');
                    tooltip.style.left = (e.pageX + 10) + 'px';
                    tooltip.style.top = (e.pageY + 10) + 'px';
                }})
                .on('mouseout', () => document.getElementById('tooltip').classList.remove('visible'));

            nodeGroups.append('rect')
                .attr('class', 'node-rect')
                .attr('width', nodeWidth)
                .attr('height', nodeHeight)
                .attr('x', -nodeWidth / 2)
                .attr('y', -nodeHeight / 2);

            const textGroups = nodeGroups.append('g').attr('class', 'text-container');

            textGroups.append('text')
                .attr('class', 'node-text node-name')
                .attr('x', 0)
                .attr('y', 0)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .each(function(d) {{
                    const lines = wrapText(d.given_name || d.name, 16);
                    const lineHeight = 1.1;
                    const totalHeight = (lines.length - 1) * lineHeight * 13 / 2;
                    lines.forEach((line, i) => {{
                        d3.select(this).append('tspan')
                            .attr('x', 0)
                            .attr('dy', i === 0 ? -totalHeight : lineHeight + 'em')
                            .text(line);
                    }});
                }});

            textGroups.append('text')
                .attr('class', 'node-date')
                .attr('x', 0)
                .attr('y', 32)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .text(d => {{
                    let dateStr = '';
                    if (d.birth) dateStr += d.birth.split(' ').pop();
                    if (d.death) dateStr += ' - ' + d.death.split(' ').pop();
                    return dateStr;
                }});

            const zoom = d3.zoom().on('zoom', e => g.attr('transform', e.transform));
            svg.call(zoom);
            renderStates.set(svgSelector, {{ svg, g, zoom }});
        }}

        const horizontalNodes = cloneNodes();
        renderTree(
            '#tree-horizontal',
            horizontalNodes,
            linksData,
            applyHorizontalLayout(horizontalNodes, linksData),
            'horizontal'
        );

        const verticalNodes = cloneNodes();
        renderTree(
            '#tree-vertical',
            verticalNodes,
            linksData,
            applyVerticalLayout(verticalNodes, linksData),
            'vertical'
        );

        function activeSvgSelector() {{
            return '#tree-vertical';
        }}

        function fitView() {{
            const state = renderStates.get(activeSvgSelector());
            if (!state) return;
            const headerHeight = updateLayoutChrome();
            const bbox = state.g.node().getBBox();
            const fullWidth = window.innerWidth;
            const fullHeight = window.innerHeight - headerHeight;
            const scale = Math.min(1, 0.9 / Math.max(bbox.width / fullWidth, bbox.height / fullHeight));
            const translate = [
                (fullWidth - bbox.width * scale) / 2 - bbox.x * scale,
                (fullHeight - bbox.height * scale) / 2 - bbox.y * scale
            ];
            state.svg.transition().duration(750).call(
                state.zoom.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
        }}

        window.addEventListener('resize', () => {{
            updateLayoutChrome();
            fitView();
        }});

        updateLayoutChrome();
        setTimeout(fitView, 200);
    </script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(
        description="Generate a focused family tree for one person from GEDCOM."
    )
    parser.add_argument("main_person", nargs="?", default=DEFAULT_PERSON)
    parser.add_argument("num_ancestor_generation", nargs="?", type=int, default=DEFAULT_ANCESTOR_GENERATIONS)
    parser.add_argument("gedcom_filepath", nargs="?", default=DEFAULT_GEDCOM)
    args = parser.parse_args()

    gedcom_parser = GEDCOMParser(args.gedcom_filepath).parse()
    FocusedPersonTreeGenerator(gedcom_parser).generate(
        args.main_person,
        max(0, args.num_ancestor_generation),
    )


if __name__ == "__main__":
    main()
