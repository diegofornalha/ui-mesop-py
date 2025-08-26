#!/usr/bin/env python3
"""
Fix syntax issues in in_memory_manager.py
"""

import re

# Read the file
with open('service/server/in_memory_manager.py', 'r') as f:
    content = f.read()

# Fix uuid.uuid4( -> uuid.uuid4()
content = re.sub(r'uuid\.uuid4\((?!\))', r'uuid.uuid4()', content)

# Fix Part(root= issues
content = content.replace('Part(\n                root=DataPart(', 'DataPart(')
content = content.replace(')\n            ),', '),')

# Write back
with open('service/server/in_memory_manager.py', 'w') as f:
    f.write(content)

print("Fixed in_memory_manager.py")