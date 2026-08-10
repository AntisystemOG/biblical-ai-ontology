import re
path = r'C:\Users\thadd\AppData\Local\Temp\openclaw-web-fetch-cfa0bfd3c558689b.log'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()
start = text.index('<?xml version="1.0" ?>')
xml = text[start:]
xml = re.sub(r'---\s*$', '', xml).strip()
xml = xml.replace('&amp;', '&amp;amp;')
out = r'C:\Users\thadd\AppData\Local\Temp\d1_infotable_clean.xml'
with open(out, 'w', encoding='utf-8') as f:
    f.write(xml)
print('clean xml written, length', len(xml))
