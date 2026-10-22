exec(open('/workspace/church_work/validate.py').read().replace("p='/workspace/inbox/grand_fond_parish_church/grand_fond_parish_church.glb'","p='/workspace/church_work/clean.glb'"))
from scipy.spatial.transform import Rotation
issues=[]
phs={k:manifold(t) for k,t in node_mesh.items() if k.startswith('Ph_')}
for node in g.nodes:
 if not node.name.startswith('Door'):continue
 origin=np.array(node.translation or [0,0,0]);source=node_mesh[node.name]
 direction=-1 if '_L_' in node.name else 1
 for angle in [15,30,45,60,75,90]:
  rot=Rotation.from_euler('y',direction*angle,degrees=True).as_matrix()
  mesh=trimesh.Trimesh((source.vertices-origin)@rot.T+origin,source.faces,process=False)
  moving=manifold(mesh);volume=(shellman^moving).volume()
  if volume>1e-6:issues.append((node.name,angle,'architecture',round(volume,6)))
  for name,other in phs.items():
   b=node_mesh[name].bounds
   if np.any(mesh.bounds[1]<b[0]) or np.any(mesh.bounds[0]>b[1]):continue
   volume=(moving^other).volume()
   if volume>1e-6:issues.append((node.name,angle,name,round(volume,6)))
print('Door swing intersections:',issues)
json.dump(issues,open('/workspace/church_work/swing.json','w'),indent=2)
