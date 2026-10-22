import sys,json,re,struct,collections,math
sys.path.insert(0,'/workspace/build_libs')
import numpy as np,trimesh,manifold3d as mf
from pygltflib import GLTF2
from scipy.spatial.transform import Rotation
p='/workspace/inbox/grand_fond_parish_church/grand_fond_parish_church.glb'
g=GLTF2().load(p);blob=g.binary_blob()
def data(i):
 a=g.accessors[i];v=g.bufferViews[a.bufferView];dtype={5126:'<f4',5125:'<u4',5123:'<u2'}[a.componentType];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a.type]
 return np.frombuffer(blob,dtype=dtype,count=a.count*n,offset=(v.byteOffset or 0)+(a.byteOffset or 0)).reshape(a.count,n)
all_mesh=[];node_mesh={};bad=[];triangles=0
for node in g.nodes:
 pieces=[]
 rot=Rotation.from_quat(node.rotation or [0,0,0,1]).as_matrix();pos=np.array(node.translation or [0,0,0])
 for pr in g.meshes[node.mesh].primitives:
  v=data(pr.attributes.POSITION);n=data(pr.attributes.NORMAL);uv=data(pr.attributes.TEXCOORD_0);f=data(pr.indices).reshape(-1,3)
  triangles+=len(f)
  if not(np.isfinite(v).all() and np.isfinite(n).all() and np.isfinite(uv).all()):bad.append((node.name,'nonfinite'))
  t=trimesh.Trimesh(v,f,process=False)
  if (t.area_faces<1e-10).any():bad.append((node.name,'zero_area',int((t.area_faces<1e-10).sum())))
  dots=np.einsum('ij,ij->i',t.face_normals,n[f].mean(axis=1))
  if (dots<-.01).any():bad.append((node.name,'reversed_normals',int((dots<-.01).sum())))
  norms=np.linalg.norm(n,axis=1)
  if np.max(abs(norms-1))>.005:bad.append((node.name,'bad_normals',float(np.max(abs(norms-1)))))
  if not node.name.startswith(('Ph_','Door')):
   if node.name!=g.materials[pr.material].name:bad.append((node.name,'material_name'))
  t.vertices=v@rot.T+pos;pieces.append(t)
 t=trimesh.util.concatenate(pieces);t.merge_vertices(digits_vertex=5)
 node_mesh[node.name]=t
 if not node.name.startswith(('Ph_','Door')):all_mesh.append(t)
 else:
  if not t.is_watertight:bad.append((node.name,'not_watertight'))
shell=trimesh.util.concatenate(all_mesh);shell.merge_vertices(digits_vertex=5)
edgecounts=np.bincount(shell.edges_unique_inverse)
summary={'triangles':triangles,'nodes':len(g.nodes),'door_leaves':sum(n.name.startswith('Door') for n in g.nodes),'placeholders':sum(n.name.startswith('Ph_') for n in g.nodes),'shell_watertight':shell.is_watertight,'winding_consistent':shell.is_winding_consistent,'boundary_edges':int((edgecounts==1).sum()),'nonmanifold_edges':int((edgecounts>2).sum()),'bounds_gltf':shell.bounds.tolist(),'embedded_images':len(g.images),'issues':bad}
print(json.dumps(summary,indent=2))
json.dump(summary,open('/workspace/church_work/validation.json','w'),indent=2)
# Intersections of placeholder boxes against architecture; boxes must be local and closed.
def manifold(mesh):
 mesh=mesh.copy();mesh.merge_vertices(digits_vertex=5)
 return mf.Manifold(mf.Mesh(np.float32(mesh.vertices),np.uint32(mesh.faces)))
shellman=manifold(shell)
collisions=[]
if shellman.status()==mf.Error.NoError:
 for name,t in node_mesh.items():
  if not name.startswith(('Ph_','Door')):continue
  man=manifold(t)
  if man.status()!=mf.Error.NoError:continue
  intersection=shellman^man
  vol=intersection.volume()
  if vol>1e-6:collisions.append((name,round(vol,6)))
print('Architecture intersections',collisions)
json.dump(collisions,open('/workspace/church_work/collisions.json','w'),indent=2)
