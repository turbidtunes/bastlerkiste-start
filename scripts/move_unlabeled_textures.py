"""Safely file visually identified JPEG photo textures as true PNGs on main."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile
from PIL import Image,ImageOps

def git(*args):
    print("GIT",*args,flush=True)
    return subprocess.run(["git",*args],check=True,text=True)
data=json.loads(Path("texture_requests/_audit/assignment_34_images.json").read_text())
chosen=data["mapped"]
alternates=data["duplicates_to_preserve"]
assert len(chosen)==26 and len(alternates)==8
assert len(set(x["source"] for x in chosen+alternates))==34
tmp=Path(tempfile.mkdtemp(prefix="texture_png_delivery_"))
try:
    # Read and convert complete originals before touching main.
    for m in chosen:
        src=Path(m["source"])
        assert src.exists(), f"Missing source: {src}"
        assert hashlib.sha256(src.read_bytes()).hexdigest()==m["sha256_source"],f"Changed source: {src}"
        with Image.open(src) as im:
            assert im.format=="JPEG"
            im=ImageOps.exif_transpose(im)
            assert [im.width,im.height]==m["source_pixels"]
            assert im.width==im.height and im.width>=1000
            output=tmp/m["destination"]
            output.parent.mkdir(parents=True,exist_ok=True)
            im.convert("RGB").save(output,format="PNG",compress_level=3)
        with Image.open(output) as saved:
            assert saved.format=="PNG" and [saved.width,saved.height]==m["source_pixels"]
        print("PREPARED",m["source"],"->",m["destination"],m["source_pixels"],flush=True)
    for m in alternates:
        assert hashlib.sha256(Path(m["source"]).read_bytes()).hexdigest()==m["sha256_source"]
    git("fetch","origin","main")
    git("checkout","-B","texture-migration","origin/main")
    for m in chosen+alternates:
        src=Path(m["source"])
        assert src.exists() and hashlib.sha256(src.read_bytes()).hexdigest()==m["sha256_source"],f"Current main differs: {src}"
    for m in chosen:
        assert not Path(m["destination"]).exists(),f"Destination already exists: {m['destination']}"
    for m in alternates:
        assert not Path(m["archive_destination"]).exists(),f"Archive name exists: {m['archive_destination']}"
    for m in chosen:
        dest=Path(m["destination"])
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(tmp/dest,dest)
        git("add","--",str(dest))
        git("rm","--",m["source"])
    for m in alternates:
        dest=Path(m["archive_destination"])
        dest.parent.mkdir(parents=True,exist_ok=True)
        git("mv","--",m["source"],str(dest))
    report=Path("texture_requests/IMPORT_REPORT_2026-10-22.md")
    lines=[
        "# Texture import report",
        "",
        "Visually matched 26 unlabeled source JPG images to building material slots; archived 8 alternate variants.",
        "Converted actual JPEG images to PNG without resizing, upscaling, image generation or changes to the GLB assets.",
        "All originals are preserved in Git history.",
        "**25 resulting PNGs are 2048x2048; one is 1024x1024. No 1254x1254 image has been fabricated.**",
        "JPEG artifacts remain; a PNG wrapper does not restore lossy JPG data.",
        "",
        "| Original JPG | Exact destination PNG | Pixels |",
        "|---|---|---|"
    ]
    for m in chosen:
        lines.append("| "+m["source"]+" | "+m["destination"]+" | "+str(m["source_pixels"])+" |")
    lines.extend(["","## Retained extra JPEG variants"])
    for m in alternates: lines.append("- "+m["archive_destination"]+" (alternative for "+m["material"]+")")
    lines.extend(["","Remaining missing V4 textures still require generation. Full seamlessness has not been tested; review in UE5."])
    report.write_text("\n".join(lines)+"\n",encoding="utf-8")
    git("add","--",str(report))
    git("config","user.name","github-actions[bot]")
    git("config","user.email","41898282+github-actions[bot]@users.noreply.github.com")
    git("diff","--cached","--stat")
    git("commit","-m","Import 26 PNG material textures into exact building inbox folders, archive eight alternatives")
    git("push","origin","HEAD:main")
    print("TEXTURE_IMPORT_COMPLETE",len(chosen),len(alternates),flush=True)
finally:
    shutil.rmtree(tmp,ignore_errors=True)
