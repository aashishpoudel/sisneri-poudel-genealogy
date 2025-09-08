# ...place this in a utility script...
import re
from collections import defaultdict

calls = defaultdict(list)
with open("genealogy_poudel_data.py") as f:
    for i, line in enumerate(f, 1):
        m = re.match(r'(\w+)\.add_child(?:ren)?\(', line)
        if m:
            calls[m.group(1)].append(i)

for person, lines in calls.items():
    if len(lines) > 1:
        print(f"{person} called add_child/add_children {len(lines)} times at lines {lines}")