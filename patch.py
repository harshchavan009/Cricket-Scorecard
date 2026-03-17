import re

with open('app.py', 'r') as f:
    content = f.read()

# Add responsive sizing to all bar/scatter charts
content = re.sub(r'fig(\d*)\.update_layout\(', r'fig\1.update_layout(margin=dict(l=20, r=20, t=40, b=20), ', content)
content = re.sub(r"fig_(\w+)\.update_layout\(", r"fig_\1.update_layout(margin=dict(l=20, r=20, t=40, b=20), ", content)

with open('app.py', 'w') as f:
    f.write(content)
