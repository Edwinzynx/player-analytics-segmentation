"""One-time download of Microsoft's schemas; normal builds validate offline."""
import json
from pathlib import Path
from urllib.parse import urldefrag, urljoin
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
BASE='https://developer.microsoft.com/json-schemas/'
TARGET=ROOT/'scripts/powerbi_schemas'
ROOTS=[
 'fabric/pbip/pbipProperties/1.0.0/schema.json',
 'fabric/item/report/definitionProperties/2.0.0/schema.json',
 'fabric/item/semanticModel/definitionProperties/1.0.0/schema.json',
 'fabric/item/report/definition/versionMetadata/1.0.0/schema.json',
 'fabric/item/report/definition/report/3.0.0/schema.json',
 'fabric/item/report/definition/pagesMetadata/1.0.0/schema.json',
 'fabric/item/report/definition/page/2.0.0/schema.json',
 'fabric/item/report/definition/visualContainer/2.1.0/schema.json']

def main():
    pending=[BASE+p for p in ROOTS]; seen=set()
    while pending:
        url=pending.pop()
        if url in seen: continue
        if not url.startswith(BASE): raise ValueError(url)
        data=json.load(urlopen(url,timeout=45)); seen.add(url)
        dest=TARGET/url.removeprefix(BASE); dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        def walk(obj):
            if isinstance(obj,dict):
                if '$ref' in obj:
                    ref=urldefrag(urljoin(url,obj['$ref']))[0]
                    if ref!=url: pending.append(ref)
                for v in obj.values(): walk(v)
            elif isinstance(obj,list):
                for v in obj: walk(v)
        walk(data)
        print(url)
    (TARGET/'sources.json').write_text(json.dumps(sorted(seen),indent=2)+'\n')

if __name__=='__main__': main()
