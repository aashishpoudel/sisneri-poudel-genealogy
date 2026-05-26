#!/usr/bin/env python3
"""
GEDCOM to HTML Family Tree Converter
Parses GEDCOM genealogy files and creates an interactive visual family tree in HTML.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class GEDCOMParser:
    """Parse GEDCOM files and extract family relationships."""
    
    def __init__(self, gedcom_path):
        self.gedcom_path = Path(gedcom_path)
        self.individuals = {}  # id -> person data
        self.families = {}     # id -> family data
        self.current_id = None
        self.current_family_id = None
        
    def parse(self):
        """Parse the GEDCOM file."""
        with open(self.gedcom_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip('\n')
                if not line:
                    continue
                    
                # Parse GEDCOM line format: level [id] tag [value]
                parts = line.split(None, 2)  # Split on whitespace, max 3 parts
                level = int(parts[0])
                
                # Check if second part is an ID (starts with @)
                if len(parts) > 1 and parts[1].startswith('@'):
                    # Format: level id tag [value]
                    ident = parts[1]
                    # Need to parse tag and value from remaining string
                    rest = line.split(None, 2)
                    tag = rest[2] if len(rest) > 2 else ''
                    value = rest[3] if len(rest) > 3 else ''
                else:
                    # Format: level tag [value]
                    tag = parts[1] if len(parts) > 1 else ''
                    value = parts[2] if len(parts) > 2 else ''
                    ident = None
                
                # Handle individual records
                if tag == 'INDI' and level == 0:
                    self.current_id = ident.strip('@') if ident else value.strip('@')
                    self.individuals[self.current_id] = {
                        'id': self.current_id,
                        'name': '',
                        'nepali_name': '',
                        'birth': '',
                        'birth_place': '',
                        'death': '',
                        'sex': '',
                        'notes': '',
                        'parents': [],
                        'spouses': [],
                        'children': []
                    }
                
                # Handle family records
                elif tag == 'FAM' and level == 0:
                    self.current_family_id = ident.strip('@') if ident else value.strip('@')
                    self.families[self.current_family_id] = {
                        'id': self.current_family_id,
                        'husband': '',
                        'wife': '',
                        'children': []
                    }
                
                # Handle names
                elif tag == 'NAME' and level == 1 and self.current_id:
                    # GEDCOM format: First /Last/
                    name = value.replace('/', '').strip()
                    self.individuals[self.current_id]['name'] = name
                
                # Handle birth dates
                elif tag == 'BIRT' and level == 1:
                    # Mark that birth data follows
                    pass
                elif tag == 'DATE' and level == 2 and self.current_id:
                    if self.individuals[self.current_id]['birth'] == '':
                        self.individuals[self.current_id]['birth'] = value.strip()
                
                # Handle birth place
                elif tag == 'PLAC' and level == 2 and self.current_id:
                    if self.individuals[self.current_id]['birth_place'] == '':
                        self.individuals[self.current_id]['birth_place'] = value.strip()
                
                # Handle death dates
                elif tag == 'DEAT' and level == 1:
                    pass
                elif tag == 'DATE' and level == 2 and self.current_id:
                    if self.individuals[self.current_id]['death'] == '':
                        self.individuals[self.current_id]['death'] = value.strip()
                
                # Handle notes/comments and extract Nepali name
                elif tag == 'NOTE' and level == 1 and self.current_id:
                    note_text = value.strip()
                    self.individuals[self.current_id]['notes'] = note_text
                    # Extract Nepali name from "Bio notes: [Nepali name]" format
                    if note_text.startswith('Bio notes:'):
                        nepali_part = note_text.replace('Bio notes:', '').strip()
                        self.individuals[self.current_id]['nepali_name'] = nepali_part
                elif tag == 'CONT' and level == 2 and self.current_id:
                    # Continuation of notes
                    if self.individuals[self.current_id]['notes']:
                        self.individuals[self.current_id]['notes'] += ' ' + value.strip()
                    else:
                        self.individuals[self.current_id]['notes'] = value.strip()
                
                # Handle sex
                elif tag == 'SEX' and level == 1 and self.current_id:
                    self.individuals[self.current_id]['sex'] = value.strip()
                
                # Handle family links
                elif tag == 'FAMC' and level == 1 and self.current_id:
                    # Child in family
                    family_id = value.strip('@')
                    if family_id in self.families:
                        if self.current_id not in self.families[family_id]['children']:
                            self.families[family_id]['children'].append(self.current_id)
                
                elif tag == 'FAMS' and level == 1 and self.current_id:
                    # Spouse in family
                    pass
                
                elif tag == 'HUSB' and level == 1 and self.current_family_id:
                    self.families[self.current_family_id]['husband'] = value.strip('@')
                
                elif tag == 'WIFE' and level == 1 and self.current_family_id:
                    self.families[self.current_family_id]['wife'] = value.strip('@')
                
                elif tag == 'CHIL' and level == 1 and self.current_family_id:
                    child_id = value.strip('@')
                    if child_id not in self.families[self.current_family_id]['children']:
                        self.families[self.current_family_id]['children'].append(child_id)
        
        # Post-process to build relationships
        self._build_relationships()
        return self
    
    def _build_relationships(self):
        """Build parent-child and spouse relationships."""
        for family_id, family in self.families.items():
            # Husband-wife relationship
            if family['husband'] and family['husband'] in self.individuals:
                if family['wife'] and family['wife'] not in self.individuals[family['husband']]['spouses']:
                    self.individuals[family['husband']]['spouses'].append(family['wife'])
            
            if family['wife'] and family['wife'] in self.individuals:
                if family['husband'] and family['husband'] not in self.individuals[family['wife']]['spouses']:
                    self.individuals[family['wife']]['spouses'].append(family['husband'])
            
            # Parent-child relationships
            for child_id in family['children']:
                if child_id in self.individuals:
                    if family['husband'] and family['husband'] not in self.individuals[child_id]['parents']:
                        self.individuals[child_id]['parents'].append(family['husband'])
                    if family['wife'] and family['wife'] not in self.individuals[child_id]['parents']:
                        self.individuals[child_id]['parents'].append(family['wife'])
                        
                if family['husband'] and family['husband'] in self.individuals:
                    if child_id not in self.individuals[family['husband']]['children']:
                        self.individuals[family['husband']]['children'].append(child_id)
                
                if family['wife'] and family['wife'] in self.individuals:
                    if child_id not in self.individuals[family['wife']]['children']:
                        self.individuals[family['wife']]['children'].append(child_id)


class FamilyTreeHTMLGenerator:
    """Generate interactive HTML family tree visualization."""
    
    def __init__(self, parser):
        self.parser = parser
        self.individuals = parser.individuals
        self.families = parser.families
        self.html = ""
    
    def generate(self, output_path: str = "family_tree.html", ancestor_name: str = None, descendant_name: str = None):
        """Generate the HTML file. Optionally highlight direct line between ancestor and descendant."""
        self.ancestor_name = ancestor_name
        self.descendant_name = descendant_name
        html_content = self._create_html()
        Path(output_path).write_text(html_content, encoding='utf-8')
        print(f"Family tree generated: {output_path}")
        return output_path
    
    def _find_person_by_name(self, name: str):
        """Find a person by name."""
        for person_id, person in self.individuals.items():
            if name.lower() in person['name'].lower():
                return person_id
        return None
    
    def _find_path_to_ancestor(self, person_id, target_id, visited=None):
        """Find path from person up to ancestor using FAMC (parent family)."""
        if visited is None:
            visited = set()
        
        if person_id in visited:
            return None
        visited.add(person_id)
        
        if person_id == target_id:
            return [person_id]
        
        if person_id not in self.individuals:
            return None
        
        person = self.individuals[person_id]
        
        # Trace up through parents using FAMC relationship
        for parent_id in person['parents']:
            path = self._find_path_to_ancestor(parent_id, target_id, visited.copy())
            if path:
                return [person_id] + path
        
        return None
    
    def _find_path_down_to_descendant(self, person_id, target_id, visited=None):
        """Find path from ancestor down to descendant using children."""
        if visited is None:
            visited = set()
        
        if person_id in visited:
            return None
        visited.add(person_id)
        
        if person_id == target_id:
            return [person_id]
        
        if person_id not in self.individuals:
            return None
        
        person = self.individuals[person_id]
        
        # Trace down through children
        for child_id in person['children']:
            path = self._find_path_down_to_descendant(child_id, target_id, visited.copy())
            if path:
                return [person_id] + path
        
        return None
    
    def _mark_direct_line(self, trees):
        """Mark nodes in direct line from ancestor to descendant."""
        if not self.ancestor_name or not self.descendant_name:
            return [], {}
        
        ancestor_id = self._find_person_by_name(self.ancestor_name)
        descendant_id = self._find_person_by_name(self.descendant_name)
        
        if not ancestor_id or not descendant_id:
            print(f"Warning: Could not find '{self.ancestor_name}' or '{self.descendant_name}'")
            if ancestor_id:
                print(f"  Found ancestor: {self.individuals[ancestor_id]['name']}")
            if descendant_id:
                print(f"  Found descendant: {self.individuals[descendant_id]['name']}")
            return [], {}
        
        # Find path from ancestor down to descendant
        path = self._find_path_down_to_descendant(ancestor_id, descendant_id)
        
        if path:
            print(f"Direct line found with {len(path)} people:")
            # Create mapping of person ID to sequence number
            line_numbers = {}
            for idx, pid in enumerate(path, 1):
                line_numbers[pid] = idx
                print(f"  {idx}. {self.individuals[pid]['name']}")
            return path, line_numbers
        else:
            print(f"Warning: No path found from {self.ancestor_name} to {self.descendant_name}")
            return [], {}
    
    def _build_tree_structure(self):
        """Build a hierarchical tree structure for the family."""
        # Find root individuals (those with no parents)
        roots = []
        for person_id, person in self.individuals.items():
            if not person['parents']:
                roots.append(person_id)
        
        # If no roots found, just use the first few individuals
        if not roots:
            roots = list(self.individuals.keys())[:5]
        
        # Build tree recursively
        trees = []
        visited = set()
        
        def build_node(person_id):
            if person_id in visited or person_id not in self.individuals:
                return None
            visited.add(person_id)
            
            person = self.individuals[person_id]
            
            # Split name into given and surname
            name = person['name'] or '(unknown)'
            given_name = name
            surname = ''
            
            if '/' in name:
                parts = name.split('/')
                given_name = parts[0].strip()
                surname = parts[1].strip() if len(parts) > 1 else ''
            
            node = {
                'id': person_id,
                'name': name,
                'given_name': given_name,
                'surname': surname,
                'nepali_name': person['nepali_name'],
                'birth': person['birth'],
                'birth_place': person['birth_place'],
                'death': person['death'],
                'sex': person['sex'],
                'notes': person['notes'],
                'children': []
            }
            
            # Add children
            for child_id in person['children']:
                child_node = build_node(child_id)
                if child_node:
                    node['children'].append(child_node)
            
            return node
        
        for root_id in roots:
            tree = build_node(root_id)
            if tree:
                trees.append(tree)
        
        return trees
    
    def _create_html(self) -> str:
        """Create the complete HTML document."""
        trees = self._build_tree_structure()
        direct_line, line_numbers = self._mark_direct_line(trees)
        direct_line_set = set(direct_line)
        trees_json = json.dumps(trees)
        direct_line_json = json.dumps(direct_line)
        line_numbers_json = json.dumps(line_numbers)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Family Tree</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        :root{{
            --bg: #f7f9fb;
            --card: #ffffff;
            --text: #1f2a37;
            --muted: #6b7280;
            --primary: #0d6efd;
            --ring: #1abc9c;
            --line: #e5eef4;
            --shadow: 0 10px 30px rgba(0,0,0,.06);
            --radius: 16px;
            --radius-sm: 12px;
        }}
        @media (prefers-color-scheme: dark){{
            :root{{
                --bg: #0b1320;
                --card: #0f1a2b;
                --text: #e5eef7;
                --muted: #99a3b2;
                --primary: #7ab8ff;
                --ring: #34d399;
                --line: #1f2a37;
                --shadow: 0 10px 30px rgba(0,0,0,.35);
            }}
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
            max-width: 100%;
            margin: 0;
            padding: 16px 20px;
        }}
        
        .crumbs {{
            display: inline-block;
            margin: 0;
            padding: 0;
        }}
        
        .crumbs a {{
            color: var(--muted);
            text-decoration: none;
            font-size: 14px;
            transition: color .2s ease;
        }}
        
        .crumbs a:hover {{
            text-decoration: underline;
            color: var(--text);
        }}
        
        .header-title {{
            font-weight: 500;
            color: var(--text);
            margin: 6px 0 0;
            letter-spacing: .2px;
            line-height: 1.2;
            text-align: center;
        }}
        
        .title-nepali {{
            font-size: 22px;
            font-weight: 600;
            margin: 0;
        }}

        .gen-dot-inline {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border: 2px solid currentColor;
            border-radius: 9999px;
            font: 700 16px/1.1 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
            color: #1abc9c;
            background: currentColor;
            vertical-align: middle;
            margin: 0 .18em;
            user-select: none;
        }}

        .gen-dot-inline span {{
            color: #fff;
        }}

        .title-english-inline {{
            white-space: nowrap;
        }}
        
        #container {{
            margin-top: 169px;
        }}
        
        .language-tabs {{
            position: fixed;
            top: 90px;
            left: 0;
            right: 0;
            z-index: 998;
            display: flex;
            background: #2c3e50;
            border-bottom: 2px solid #34495e;
        }}
        
        .lang-tab {{
            flex: 1;
            padding: 12px;
            color: #fff;
            text-align: center;
            cursor: pointer;
            background: #34495e;
            border: none;
            font-size: 38px;
            font-weight: 500;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 65px;
            line-height: 1;
        }}
        
        .lang-tab:hover {{
            background: #4a606f;
        }}
        
        .lang-tab.active {{
            background: #1abc9c;
            font-weight: bold;
        }}
        
        #container {{
            margin-top: 169px;
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
        
        #container {{
            width: 100%;
            height: 100%;
            position: relative;
            overflow: auto;
            background: linear-gradient(135deg, #fef8e7 0%, #fffbf0 100%);
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
        
        .node.on-direct-line .node-rect {{
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
        
        .node-name.nepali-text {{
            font-size: 36px;
        }}
        
        .node-date {{
            font-size: 12px;
            text-anchor: middle;
            fill: #6b6b6b;
            text-shadow: 0 1px 1px rgba(255, 255, 255, 0.5);
            pointer-events: none;
        }}
        
        .node-circle {{
            fill: #d4af37;
            stroke: #d4af37;
            stroke-width: 2;
        }}
        
        .node-circle-text {{
            font-size: 30px;
            font-weight: bold;
            text-anchor: middle;
            dominant-baseline: central;
            fill: white;
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
            top: 230px;
            right: 20px;
            width: 200px;
            background: rgba(255, 248, 220, 0.95);
            padding: 15px 20px;
            border-radius: 8px;
            border: 2px solid #d4af37;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}
        
        .control-btn {{
            background: #d4af37;
            color: #3d3d3d;
            border: none;
            padding: 8px 14px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px 5px 5px 5px;
            font-size: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        
        .control-btn:hover {{
            background: #e8c547;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(212, 175, 55, 0.4);
        }}
        
        .legend {{
            position: fixed;
            top: 325px;
            right: 20px;
            width: 200px;
            background: rgba(255, 248, 220, 0.95);
            padding: 15px 20px;
            border-radius: 8px;
            border: 2px solid #d4af37;
            font-size: 12px;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}
        
        .legend-item {{
            margin: 6px 0;
            display: flex;
            align-items: center;
        }}
        
        .legend-box {{
            width: 16px;
            height: 16px;
            margin-right: 10px;
            border-radius: 2px;
            border: 1.5px solid #999;
        }}
        
        .male {{ background: #e8f4f8; }}
        .female {{ background: #fce8f3; }}
        .direct-line {{ background: #fff8dc; border: 2px solid #d4af37 !important; }}
    </style>
</head>
<body>
    <header class="page-header">
        <div class="header-wrap">
            <nav class="crumbs" aria-label="Breadcrumb">
                <a href="index.html">← Back to Home</a>
            </nav>
            <h1 class="header-title">
                <div class="title-nepali">सोमनाथ <span class="gen-dot-inline" aria-label="पुस्ता 1"><span>1</span></span> <strong>→</strong> गोपाल <span class="gen-dot-inline" aria-label="पुस्ता 32"><span>32</span></span> <span class="title-english-inline">(Somnath <span class="gen-dot-inline" aria-label="Generation 1"><span>1</span></span> <strong>→</strong> Gopal <span class="gen-dot-inline" aria-label="Generation 32"><span>32</span></span>)</span></div>
            </h1>
        </div>
    </header>
    
    <div class="language-tabs">
        <button class="lang-tab active" onclick="switchLanguage('nepali')">नेपाली</button>
        <button class="lang-tab" onclick="switchLanguage('english')">English</button>
    </div>
    
    <div id="container">
        <svg id="tree"></svg>
    </div>
    
    <div class="controls">
        <button class="control-btn" onclick="fitView()">Fit View</button>
    </div>
    
    <div class="legend">
        <div style="margin-bottom: 10px; font-weight: bold; color: #8b6914;">Legend</div>
        <div class="legend-item"><div class="legend-box male"></div> Male</div>
        <div class="legend-item"><div class="legend-box female"></div> Female</div>
        <div class="legend-item"><div class="legend-box direct-line"></div> Direct Line</div>
    </div>
    
    <div id="tooltip" class="tooltip"></div>
    
    <script>
        let currentLanguage = 'nepali';  // Default language is Nepali
        
        function switchLanguage(lang) {{
            currentLanguage = lang;
            
            // Update tab active state
            document.querySelectorAll('.lang-tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Update all node text based on language
            document.querySelectorAll('.node-group').forEach(nodeGroup => {{
                const personId = nodeGroup.getAttribute('data-personId');
                const person = findPersonInTrees(personId);
                const nameElement = nodeGroup.querySelector('.node-name');
                
                if (person && nameElement) {{
                    if (currentLanguage === 'nepali' && person.nepali_name) {{
                        // For Nepali, display the nepali_name with larger font
                        const nepaliLines = wrapText(person.nepali_name, 16);
                        updateTspans(nameElement, nepaliLines);
                        nameElement.classList.add('nepali-text');
                    }} else {{
                        // For English, display given name with normal font
                        const englishLines = wrapText(person.given_name || person.name, 16);
                        updateTspans(nameElement, englishLines);
                        nameElement.classList.remove('nepali-text');
                    }}
                }}
            }});
        }}
        
        function updateTspans(textElement, lines) {{
            if (!textElement) return;
            
            // Remove all existing tspans
            textElement.querySelectorAll('tspan').forEach(tspan => tspan.remove());
            
            // Add new tspans with updated text
            const lineHeight = 1.1;
            const totalHeight = (lines.length - 1) * lineHeight * 13 / 2;
            
            lines.forEach((line, i) => {{
                const tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
                tspan.setAttribute('x', '0');
                tspan.setAttribute('dy', i === 0 ? -totalHeight : lineHeight + 'em');
                tspan.textContent = line;
                textElement.appendChild(tspan);
            }});
        }}
        
        function findPersonInTrees(personId) {{
            function searchNode(node) {{
                if (node.id === personId) return node;
                for (let child of node.children) {{
                    const result = searchNode(child);
                    if (result) return result;
                }}
                return null;
            }}
            for (let tree of treesData) {{
                const result = searchNode(tree);
                if (result) return result;
            }}
            return null;
        }}
        
        const treesData = {trees_json};
        const directLineIds = {direct_line_json};
        const lineNumbers = {line_numbers_json};
        
        const margin = {{ top: 80, right: 100, bottom: 80, left: 100 }};
        let svgWidth = Math.max(1600, window.innerWidth);
        let svgHeight = Math.max(1200, window.innerHeight);
        
        const svg = d3.select('#tree')
            .attr('width', svgWidth)
            .attr('height', svgHeight);
        
        const container = d3.select('#container');
        
        let g = svg.append('g')
            .attr('transform', `translate(${{margin.left}},${{margin.top}})`);
        

        
        // Helper function to wrap text - more aggressive wrapping
        function wrapText(text, maxChars = 12) {{
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
        
        const treeLayout = d3.tree()
            .separation((a, b) => (a.parent === b.parent ? 0.8 : 1.2));
        treesData.forEach((treeData, treeIndex) => {{
            const hierarchy = d3.hierarchy(treeData);
            
            // Calculate dimensions - HIGHLY COMPACT
            const nodeCount = hierarchy.descendants().length;
            const width = Math.max(400, nodeCount * 75);  // Reduced to 75 pixels per node for tight packing
            const height = 400 + (hierarchy.height * 120);
            
            treeLayout.size([width, height]);
            
            const root = treeLayout(hierarchy);
            
            // Offset each tree vertically
            const yOffset = treeIndex * (height + 200);
            
            // Draw links
            g.selectAll(`.link-tree-${{treeIndex}}`)
                .data(root.links())
                .enter()
                .append('path')
                .attr('class', `link link-tree-${{treeIndex}}`)
                .attr('d', d => {{
                    const x0 = d.source.x;
                    const y0 = d.source.y + yOffset;
                    const x1 = d.target.x;
                    const y1 = d.target.y + yOffset;
                    
                    // Orthogonal path: vertical down, then horizontal
                    const midY = (y0 + y1) / 2;
                    return `M${{x0}},${{y0}}L${{x0}},${{midY}}L${{x1}},${{midY}}L${{x1}},${{y1}}`;
                }});
            
            // Draw nodes
            const nodeGroups = g.selectAll(`.node-tree-${{treeIndex}}`)
                .data(root.descendants())
                .enter()
                .append('g')
                .attr('class', d => {{
                    let cls = 'node-group node ';
                    if (d.data.sex === 'M') cls += 'male';
                    else if (d.data.sex === 'F') cls += 'female';
                    else cls += 'unknown';
                    
                    if (directLineIds.includes(d.data.id)) {{
                        cls += ' on-direct-line';
                    }}
                    return cls;
                }})
                .attr('data-personId', d => d.data.id)
                .attr('transform', d => `translate(${{d.x}},${{d.y + yOffset}})`)
                .on('mouseover', function(e, d) {{
                    d3.select(this).select('.node-rect')
                        .transition()
                        .duration(200);
                    
                    const tooltip = document.getElementById('tooltip');
                    tooltip.classList.add('visible');
                    
                    let tooltipHTML = `<div class="tooltip-title">${{d.data.name}}</div>`;
                    
                    if (d.data.birth) {{
                        tooltipHTML += `<div class="tooltip-line"><strong>DOB:</strong> ${{d.data.birth}}</div>`;
                    }}
                    
                    if (d.data.birth_place) {{
                        tooltipHTML += `<div class="tooltip-line"><strong>Place:</strong> ${{d.data.birth_place}}</div>`;
                    }}
                    
                    if (d.data.notes) {{
                        // Clean up the notes by removing "Bio notes: " prefix if present
                        let cleanNotes = d.data.notes;
                        if (cleanNotes.startsWith('Bio notes:')) {{
                            cleanNotes = cleanNotes.replace('Bio notes:', '').trim();
                        }}
                        // Only show notes if there's actual content after cleaning
                        if (cleanNotes) {{
                            tooltipHTML += `<div class="tooltip-line">${{cleanNotes}}</div>`;
                        }}
                    }}
                    
                    if (!d.data.birth && !d.data.birth_place && !d.data.notes) {{
                        tooltipHTML += `<div class="tooltip-line"><em>No additional information</em></div>`;
                    }}
                    
                    tooltip.innerHTML = tooltipHTML;
                    tooltip.style.left = (e.pageX + 10) + 'px';
                    tooltip.style.top = (e.pageY + 10) + 'px';
                }})
                .on('mousemove', (e) => {{
                    const tooltip = document.getElementById('tooltip');
                    tooltip.style.left = (e.pageX + 10) + 'px';
                    tooltip.style.top = (e.pageY + 10) + 'px';
                }})
                .on('mouseout', function() {{
                    document.getElementById('tooltip').classList.remove('visible');
                }});
            
            // Add rectangles - larger to accommodate more wrapped text
            nodeGroups.append('rect')
                .attr('class', 'node-rect')
                .attr('width', 211)
                .attr('height', 100)
                .attr('x', -106)
                .attr('y', -50);
            
            // Add circled number for direct line individuals
            nodeGroups.each(function(d) {{
                if (lineNumbers[d.data.id] !== undefined) {{
                    const circleNum = lineNumbers[d.data.id];
                    const circleX = -150;  // Position further left for breathing space
                    const circleY = 0;     // Vertically centered
                    const circleRadius = 28;  // 20% bigger (was 23)
                    
                    d3.select(this).append('circle')
                        .attr('class', 'node-circle')
                        .attr('cx', circleX)
                        .attr('cy', circleY)
                        .attr('r', circleRadius);
                    
                    d3.select(this).append('text')
                        .attr('class', 'node-circle-text')
                        .attr('x', circleX)
                        .attr('y', circleY)
                        .text(circleNum);
                }}
            }});
            
            // Add text group container for proper vertical centering
            const textGroups = nodeGroups.append('g')
                .attr('class', 'text-container');
            
            // Add name text - supports both English (given + surname) and Nepali names
            textGroups.append('text')
                .attr('class', d => {{
                    // Add nepali-text class if Nepali name is available (default language)
                    let cls = 'node-text node-name';
                    if (d.data.nepali_name) {{
                        cls += ' nepali-text';
                    }}
                    return cls;
                }})
                .attr('x', 0)
                .attr('y', 0)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .each(function(d) {{
                    // Display Nepali name by default if available, otherwise English
                    const displayName = d.data.nepali_name 
                        ? d.data.nepali_name 
                        : (d.data.given_name || '(unknown)');
                    
                    const lines = wrapText(displayName, 16);
                    d3.select(this)
                        .selectAll('tspan')
                        .remove();
                    const lineHeight = 1.1;
                    const totalHeight = (lines.length - 1) * lineHeight * 13 / 2;
                    lines.forEach((line, i) => {{
                        d3.select(this).append('tspan')
                            .attr('x', 0)
                            .attr('dy', i === 0 ? -totalHeight : lineHeight + 'em')
                            .text(line);
                    }});
                }});
            
            // Add surname text (only for English, hidden by default)
            textGroups.append('text')
                .attr('class', 'node-text node-surname')
                .attr('x', 0)
                .attr('y', 12)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .each(function(d) {{
                    const surname = d.data.surname || '';
                    if (!surname) {{
                        d3.select(this).text('');
                        return;
                    }}
                    const lines = wrapText(surname, 16);
                    d3.select(this)
                        .selectAll('tspan')
                        .remove();
                    const lineHeight = 1.1;
                    const totalHeight = (lines.length - 1) * lineHeight * 13 / 2;
                    lines.forEach((line, i) => {{
                        d3.select(this).append('tspan')
                            .attr('x', 0)
                            .attr('dy', i === 0 ? -totalHeight : lineHeight + 'em')
                            .text(line);
                    }});
                }});
            
            // Add year text - at bottom, centered
            textGroups.append('text')
                .attr('class', 'node-date')
                .attr('x', 0)
                .attr('y', 32)
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'central')
                .text(d => {{
                    let dateStr = '';
                    if (d.data.birth) {{
                        const year = d.data.birth.split(' ').pop();
                        dateStr += year;
                    }}
                    if (d.data.death) {{
                        const year = d.data.death.split(' ').pop();
                        dateStr += ' - ' + year;
                    }}
                    return dateStr;
                }});
        }});
        
        // Update SVG height based on content
        const bbox = g.node().getBBox();
        svgHeight = bbox.height + margin.top + margin.bottom + 100;
        svg.attr('height', svgHeight);
        
        // Zoom behavior
        const zoom = d3.zoom()
            .on('zoom', (e) => {{
                g.attr('transform', e.transform);
            }});
        
        svg.call(zoom);
        
        function fitView() {{
            const bbox = g.node().getBBox();
            const fullWidth = window.innerWidth;
            const fullHeight = window.innerHeight;
            
            const scale = 0.9 / Math.max(
                bbox.width / fullWidth,
                bbox.height / fullHeight
            );
            
            const translate = [
                (fullWidth - bbox.width * scale) / 2 - bbox.x * scale,
                (fullHeight - bbox.height * scale) / 2 - bbox.y * scale
            ];
            
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
        }}
        
        // Initial fit
        setTimeout(fitView, 200);
    </script>
</body>
</html>"""
        return html


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gedcom_family_tree.py <gedcom_file> [output.html] [--ancestor NAME] [--descendant NAME]")
        print("\nExample: python gedcom_family_tree.py myfamily.ged family_tree.html --ancestor Somnath --descendant Gopal")
        sys.exit(1)
    
    gedcom_file = sys.argv[1]
    output_file = "family_tree.html"
    ancestor_name = None
    descendant_name = None
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--ancestor' and i + 1 < len(sys.argv):
            ancestor_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--descendant' and i + 1 < len(sys.argv):
            descendant_name = sys.argv[i + 1]
            i += 2
        elif not sys.argv[i].startswith('--'):
            output_file = sys.argv[i]
            i += 1
        else:
            i += 1
    
    try:
        # Parse GEDCOM
        print(f"Parsing {gedcom_file}...")
        parser = GEDCOMParser(gedcom_file)
        parser.parse()
        print(f"Found {len(parser.individuals)} individuals")
        
        # Generate HTML
        print("Generating family tree visualization...")
        generator = FamilyTreeHTMLGenerator(parser)
        generator.generate(output_file, ancestor_name, descendant_name)
        
        print(f"\n✓ Family tree successfully generated!")
        print(f"  Output: {output_file}")
        print(f"  Open in a web browser to view the interactive tree")
        
    except FileNotFoundError:
        print(f"Error: File '{gedcom_file}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
