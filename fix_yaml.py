import re
with open('.github/workflows/manual-deploy.yml', 'r') as f:
    lines = f.readlines()

# Исправляем отступы
fixed_lines = []
for line in lines:
    # Считаем начальные пробелы
    indent = len(line) - len(line.lstrip())
    
    if indent == 1:
        # Один пробел -> 2 пробела
        line = '  ' + line.lstrip()
    elif indent == 2:
        # Два пробела -> 4 пробела  
        line = '    ' + line.lstrip()
    elif indent == 3:
        # Три пробела -> 6 пробелов
        line = '      ' + line.lstrip()
    elif indent == 4:
        # Четыре пробела -> 8 пробелов
        line = '        ' + line.lstrip()
    
    fixed_lines.append(line.rstrip())

with open('.github/workflows/manual-deploy.yml', 'w') as f:
    f.write('\n'.join(fixed_lines) + '\n')
