"""Reassemble the two Blender files and verify SHA-256. Python standard library only."""
import hashlib,json,os
from pathlib import Path
root=Path(__file__).resolve().parent
for f in json.loads((root/'downloads.json').read_text()):
    target=root/f['name'];tmp=target.with_suffix('.blend.tmp');digest=hashlib.sha256();size=0
    try:
        with tmp.open('wb') as out:
            for name in f['parts']:
                data=(root/name).read_bytes();out.write(data);digest.update(data);size+=len(data)
        if size!=f['bytes'] or digest.hexdigest()!=f['sha256']:
            raise ValueError('Checksum mismatch: '+f['name'])
        os.replace(tmp,target);print('OK: '+str(target))
    finally:
        if tmp.exists():tmp.unlink()
