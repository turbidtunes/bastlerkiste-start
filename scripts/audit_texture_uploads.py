"""Generate visual contact sheets for unlabeled JPG photo-texture uploads.

Only for inventory/identification; NO reformatting of source images.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageOps
import base64, json, io, math, hashlib
BASE=Path("texture_requests")
OUT=Path("texture_requests/_audit")
OUT.mkdir(parents=True,exist_ok=True)
files=sorted(BASE.glob("*.jpg"))
assert files, "No JPGs"
records=[]
font=ImageFont.load_default()
CHUNK=12
for start in range(0,len(files),CHUNK):
    chunk=files[start:start+CHUNK]
    cellw,cellh=270,306
    grid=Image.new("RGB",(4*cellw,3*cellh),(243,242,240))
    pen=ImageDraw.Draw(grid)
    for k,path in enumerate(chunk):
        j=start+k
        im=Image.open(path)
        im.load()
        if im.mode!="RGB":im=im.convert("RGB")
        thumb=ImageOps.fit(im,(256,256),method=Image.Resampling.LANCZOS)
        avg=tuple(int(x) for x in ImageStat.Stat(im.resize((64,64))).mean[:3])
        v=ImageStat.Stat(im.resize((64,64))).stddev[:3]
        records.append({
          "index":j+1,"name":path.name,"size_bytes":path.stat().st_size,
          "width":im.width,"height":im.height,"format":"JPEG",
          "mean_rgb":avg,"std_rgb":tuple(round(x,1) for x in v),
          "sha256":hashlib.sha256(path.read_bytes()).hexdigest()
        })
        x=(k%4)*cellw+7;y=(k//4)*cellh+7
        grid.paste(thumb,(x,y+35))
        pen.text((x+2,y+2),f"#{j+1:02d}  {path.stem[-8:]}",fill=(0,0,0),font=font)
        pen.text((x+2,y+19),f"{im.width}x{im.height}  rgb={avg}",fill=(0,0,0),font=font)
    stream=io.BytesIO()
    grid.save(stream,format="JPEG",quality=75,optimize=True,subsampling=0)
    number=start//CHUNK+1
    p=OUT/f"sheet_{number:02d}.b64.txt"
    p.write_text(base64.b64encode(stream.getvalue()).decode("ascii"),encoding="ascii")
    print(p,"base64_chars",p.stat().st_size)
(OUT/"index.json").write_text(json.dumps({"files":records,"count":len(records)},indent=2))
print("AUDIT_CONTACT_SHEETS_OK",len(files))
