"""Repair Codex H04 glTF in Python without Blender or Ubuntu apt mirrors.

Preserves materials, named nodes and independent doors/furniture. Reconstructs
manifold architecture across material seams, stitches matching positions and
closes only bounded genuine holes. Never generates textures or new modelling.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import json
import numpy as np
import trimesh
from pygltflib import GLTF2, BufferView, Accessor
from shapely.geometry import Polygon
from shapely.ops import triangulate

ROOT=Path("/workspace/church_work")
ORIG=Path("/workspace/inbox/grand_fond_parish_church/grand_fond_parish_church.glb")
OUT=ROOT/"clean.glb"
g=GLTF2().load(str(ORIG))
source=g.binary_blob()

def data(index):
    a=g.accessors[index]
    bv=g.bufferViews[a.bufferView]
    typ={5126:"<f4",5125:"<u4",5123:"<u2",5121:"u1"}[a.componentType]
    width={"SCALAR":1,"VEC2":2,"VEC3":3,"VEC4":4}[a.type]
    offset=(bv.byteOffset or 0)+(a.byteOffset or 0)
    return np.frombuffer(source,dtype=typ,count=a.count*width,offset=offset).reshape((-1,width))

coords=[]
face_mats=[]
face_cols=[]
mat_to_node={}
original=0
for ni,node in enumerate(g.nodes):
    if node.mesh is None or node.name.startswith(("Door","Ph_")):
        continue
    mesh=g.meshes[node.mesh]
    for pi,p in enumerate(mesh.primitives):
        mat=p.material
        if mat in mat_to_node and mat_to_node[mat]!=(ni,pi):
            raise RuntimeError(f"Duplicate architecture material {mat}: refuse ambiguous repair")
        mat_to_node[mat]=(ni,pi)
        v=data(p.attributes.POSITION).astype(np.float64)
        tris=data(p.indices).ravel().reshape((-1,3)).astype(np.int64)
        original+=len(tris)
        # Material of every source triangle is retained through the stitch.
        coords.append(v[tris])
        face_mats.extend([mat]*len(tris))
        if p.attributes.COLOR_0 is not None:
            c=data(p.attributes.COLOR_0).astype(np.float32)
            face_cols.extend(c[tris].mean(axis=1))
        else:
            face_cols.extend(np.tile(np.array([[1.,1.,1.]],dtype=np.float32),(len(tris),1)))
if not coords:
    raise RuntimeError("No architecture found in raw Codex GLB")
xyz=np.concatenate(coords).reshape((-1,3))
materials=np.asarray(face_mats,dtype=np.int32)
colors=np.asarray(face_cols,dtype=np.float32)
# Vertices in different glTF material primitives are only connected in world
# space. Stitch by 0.01 mm coordinate key, preserving real shapes/openings.
quant=np.round(xyz,5)
unique, inverse=np.unique(quant,axis=0,return_inverse=True)
vertex_sums=np.zeros_like(unique,dtype=np.float64)
np.add.at(vertex_sums,inverse,xyz)
counts=np.bincount(inverse,minlength=len(unique))
vertices=vertex_sums/counts[:,None]
faces=inverse.reshape((-1,3))
areas=np.linalg.norm(np.cross(vertices[faces[:,1]]-vertices[faces[:,0]],
                                vertices[faces[:,2]]-vertices[faces[:,0]]),axis=1)*.5
good=(areas>1e-10)&(faces[:,0]!=faces[:,1])&(faces[:,1]!=faces[:,2])&(faces[:,0]!=faces[:,2])
print("STITCH",len(vertices),"vertices",len(faces),"faces,",
      int((~good).sum()),"degenerate",flush=True)
faces=faces[good];materials=materials[good];colors=colors[good]
triangles_seen=set();keep=[]
for i,f in enumerate(faces):
    key=tuple(sorted(map(int,f)))
    if key not in triangles_seen:
        triangles_seen.add(key);keep.append(i)
faces=faces[keep];materials=materials[keep];colors=colors[keep]
shell=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)

def boundary_edges(m):
    edge_count=np.bincount(m.edges_unique_inverse,minlength=len(m.edges_unique))
    return m.edges_unique[edge_count==1], m.edges_unique[edge_count>2]

bound,nonman=boundary_edges(shell)
print("PRE_REPAIR_BOUNDARIES",len(bound),"NONMANIFOLD",len(nonman),flush=True)
if len(nonman):
    raise RuntimeError(f"Architecture has {len(nonman)} nonmanifold edges pre-repair")
if len(bound)>250:
    raise RuntimeError(f"Too many open boundary edges ({len(bound)}) for safe automatic stitch")

# Associate each open edge with its original face for fill material continuity.
edge_sources=defaultdict(list)
for i,tri in enumerate(faces):
    for a,b in ((tri[0],tri[1]),(tri[1],tri[2]),(tri[2],tri[0])):
        edge_sources[tuple(sorted((int(a),int(b))))].append(i)
adj=defaultdict(set)
for a,b in bound:
    a,b=int(a),int(b);adj[a].add(b);adj[b].add(a)
if any(len(v)!=2 for v in adj.values()):
    raise RuntimeError("Open boundary chain branches: automatic hole fill unsafe")
unused={tuple(sorted((int(a),int(b)))) for a,b in bound}
added_faces=[];added_mats=[];added_colors=[]
loops=[]
while unused:
    a,b=min(unused)
    path=[a,b];unused.remove((a,b))
    prev,cur=a,b
    while cur!=a:
        choices=[x for x in sorted(adj[cur]) if x!=prev]
        if not choices:
            raise RuntimeError("Unclosed boundary contour")
        nxt=choices[0];edge=tuple(sorted((cur,nxt)))
        if edge not in unused:
            if nxt==a:
                break
            raise RuntimeError("Reused/overlapping boundary contour")
        unused.remove(edge)
        prev,cur=cur,nxt
        if cur!=a:
            path.append(cur)
        if len(path)>250:
            raise RuntimeError("Runaway contour")
    if len(path)<3:
        raise RuntimeError("Boundary contour too short")
    loops.append(path)
    loopxyz=vertices[path]
    center=loopxyz.mean(axis=0)
    _,_,vt=np.linalg.svd(loopxyz-center,full_matrices=False)
    projected=(loopxyz-center)@vt[:2].T
    polygon=Polygon(projected)
    if not polygon.is_valid or polygon.area<1e-12:
        raise RuntimeError("Cannot triangulate degenerate boundary opening")
    tri2d=triangulate(polygon)
    src=[edge_sources[tuple(sorted((path[i],path[(i+1)%len(path)])))]
         for i in range(len(path))]
    src=[k for group in src for k in group]
    mat=Counter(int(materials[x]) for x in src).most_common(1)[0][0]
    color=colors[src].mean(axis=0) if src else np.array([1.,1.,1.])
    added=0
    for poly in tri2d:
        if not polygon.covers(poly.representative_point()):
            continue
        pcoords=np.asarray(poly.exterior.coords)[:3]
        indices=[]
        for point in pcoords:
            delta=np.linalg.norm(projected-point[None,:],axis=1)
            j=int(np.argmin(delta))
            if delta[j]>1e-5:
                raise RuntimeError("Hole triangulation produced a non-boundary vertex")
            indices.append(path[j])
        if len(set(indices))<3:
            continue
        added_faces.append(indices);added_mats.append(mat);added_colors.append(color)
        added+=1
    if not added:
        raise RuntimeError("Cannot fill detected contour")
    print("FILL_LOOP",len(path),"vertices ->",added,"triangles",flush=True)

if added_faces:
    faces=np.vstack((faces,np.asarray(added_faces,dtype=np.int64)))
    materials=np.concatenate((materials,np.asarray(added_mats,dtype=np.int32)))
    colors=np.vstack((colors,np.asarray(added_colors,dtype=np.float32)))
shell=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
newbound,newnon=boundary_edges(shell)
print("POST_REPAIR_TOPOLOGY",len(newbound),"boundary",len(newnon),"nonmanifold",flush=True)
if len(newbound) or len(newnon):
    raise RuntimeError("Python repair did not close complete architectural shell")
# Reorient whole connected solids, respecting nested cutouts and material seams.
trimesh.repair.fix_normals(shell,multibody=True)
if not shell.is_watertight:
    raise RuntimeError("Repaired architecture is still not watertight")

# Append new architecture accessors, retaining untouched original doors,
# placeholder meshes, hinge transformations, material extras, and metadata.
blob=bytearray(source)
def accessor(arr,kind,component):
    a=np.asarray(arr,dtype=np.float32 if component==5126 else np.uint32)
    while len(blob)%4:blob.append(0)
    offset=len(blob);blob.extend(a.tobytes())
    vi=len(g.bufferViews)
    g.bufferViews.append(BufferView(buffer=0,byteOffset=offset,byteLength=a.nbytes))
    kw=dict(bufferView=vi,componentType=component,count=len(a),type=kind)
    if kind=="VEC3" and component==5126:
        kw.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
    idx=len(g.accessors);g.accessors.append(Accessor(**kw))
    return idx

for mat,(ni,pi) in mat_to_node.items():
    selected=np.flatnonzero(materials==mat)
    if not len(selected):
        raise RuntimeError(f"Empty architecture material {g.materials[mat].name}")
    tri=vertices[shell.faces[selected]]
    n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-15)
    ref=np.tile([0.,0.,1.],(len(n),1))
    ref[np.abs(n[:,2])>.95]=[0.,1.,0.]
    u=np.cross(ref,n)
    u/=np.maximum(np.linalg.norm(u,axis=1)[:,None],1e-15)
    v=np.cross(n,u)
    tex=np.stack([np.einsum("tij,tj->ti",tri,u),
                  np.einsum("tij,tj->ti",tri,v)],axis=-1)
    positions=tri.reshape((-1,3)).astype(np.float32)
    normals=np.repeat(n,3,axis=0).astype(np.float32)
    uv=tex.reshape((-1,2)).astype(np.float32)
    indices=np.arange(len(positions),dtype=np.uint32)
    p=g.meshes[g.nodes[ni].mesh].primitives[pi]
    p.attributes.POSITION=accessor(positions,"VEC3",5126)
    p.attributes.NORMAL=accessor(normals,"VEC3",5126)
    p.attributes.TEXCOORD_0=accessor(uv,"VEC2",5126)
    if g.materials[mat].name=="glass":
        p.attributes.COLOR_0=accessor(np.repeat(colors[selected],3,axis=0),"VEC3",5126)
    p.indices=accessor(indices,"SCALAR",5125)
    g.meshes[g.nodes[ni].mesh].name=g.nodes[ni].name

g.buffers[0].byteLength=len(blob)
g.set_binary_blob(bytes(blob))
g.asset.generator="Codex Grand-Fond H04 | Python watertight multi-material repair"
g.save_binary(str(OUT))
test=GLTF2().load(str(OUT))
if len(test.nodes)!=len(g.nodes) or not OUT.is_file() or OUT.stat().st_size<100000:
    raise RuntimeError("Repaired GLB failed binary round trip")
stats={
    "source_triangles":original, "output_architecture_triangles":int(len(shell.faces)),
    "stitched_vertices":int(len(vertices)), "removed_degenerate":int((~good).sum()),
    "holes_closed":len(loops), "faces_added":len(added_faces),
    "boundary_edges":len(newbound),"nonmanifold_edges":len(newnon),
    "watertight":bool(shell.is_watertight),"output_bytes":OUT.stat().st_size}
(ROOT/"repair_python_stats.json").write_text(json.dumps(stats,indent=2),encoding="utf-8")
print("PYTHON_GLTF_REPAIR_OK",json.dumps(stats),flush=True)
