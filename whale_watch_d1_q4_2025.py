import xml.etree.ElementTree as ET

ns = {'n': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}
root = ET.parse(r'C:\Users\thadd\AppData\Local\Temp\openclaw-web-fetch-d26629cfa57229d2.log').getroot()
rows=[]
for it in root.findall('.//n:infoTable', ns):
    name=(it.find('n:nameOfIssuer', ns).text or '').replace('&amp;', '&')
    cusip=it.find('n:cusip', ns).text or ''
    val=it.find('n:value', ns).text or '0'
    shrs=it.find('n:shrsOrPrnAmt/n:sshPrnamt', ns).text or '0'
    rows.append({'name':name,'cusip':cusip,'value_000':int(val),'shares':int(shrs)})
rows.sort(key=lambda x:-x['value_000'])
for r in rows[:20]:
    print(f"{r['name']:35} {r['value_000']:>12,} {r['shares']:>12,}")
print('---')
print('Total positions:', len(rows))
