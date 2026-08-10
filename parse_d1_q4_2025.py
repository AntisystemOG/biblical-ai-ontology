import xml.etree.ElementTree as ET

ns = {'n': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}
root = ET.parse(r'C:\Users\thadd\AppData\Local\Temp\d1_infotable_clean.xml').getroot()
rows=[]
for it in root.findall('n:infoTable', ns):
    name=(it.find('n:nameOfIssuer', ns).text or '').replace('&amp;', '&')
    val=it.find('n:value', ns).text or '0'
    shrs=it.find('n:shrsOrPrnAmt/n:sshPrnamt', ns).text or '0'
    rows.append((name, int(val), int(shrs)))
rows.sort(key=lambda x:-x[1])
for name, val, shrs in rows[:20]:
    print(f'{name:35} {val:>12,} {shrs:>12,}')
print('--- Total positions:', len(rows))
