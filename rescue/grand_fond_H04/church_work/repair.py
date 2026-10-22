import bpy,bmesh,math,json,numpy as np
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath='/workspace/inbox/grand_fond_parish_church/grand_fond_parish_church.glb')
arch=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith(('Door','Ph_'))]
bpy.ops.object.select_all(action='DESELECT')
for o in arch:o.select_set(True)
bpy.context.view_layer.objects.active=arch[0];bpy.ops.object.join();o=bpy.context.object
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001)
bmesh.ops.dissolve_limit(bm,angle_limit=.00001,use_dissolve_boundaries=True,verts=list(bm.verts),edges=list(bm.edges),delimit={'MATERIAL'})
boundary=[e for e in bm.edges if e.is_boundary]
print('Repair boundary before',len(boundary),flush=True)
if boundary:
 result=bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
 print('Repair faces added',len(result.get('faces',[])),flush=True)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
print('Repair boundary after',sum(e.is_boundary for e in bm.edges),'nonmanifold',sum(not e.is_manifold for e in bm.edges),flush=True)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00003)
for iteration in range(5):
 bmesh.ops.triangulate(bm,faces=list(bm.faces))
 tiny=[]
 for f in bm.faces:
  if len(f.verts)==3:
   a,b,c=[np.array(v.co,dtype=np.float64) for v in f.verts]
   if np.linalg.norm(np.cross(b-a,c-a))<2e-10:tiny.append(f)
 print('Tiny triangles',iteration,len(tiny),flush=True)
 if not tiny:break
 verts=set()
 for f in tiny:
  edge=max(f.edges,key=lambda e:e.calc_length())
  verts.update(v for v in f.verts if v not in edge.verts)
 if verts:bmesh.ops.dissolve_verts(bm,verts=list(verts),use_face_split=False,use_boundary_tear=False)
bmesh.ops.triangulate(bm,faces=list(bm.faces))
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(o.data);bm.free()
# Reproject each face in an orthonormal metric frame after topological repair.
mesh=o.data;uv=mesh.uv_layers.active or mesh.uv_layers.new(name='UVMap')
if mesh.has_custom_normals:mesh.normals_split_custom_set([(0,0,0)]*len(mesh.loops))
for f in mesh.polygons:
 n=f.normal;ref=Vector((0,0,1)) if abs(n.z)<.95 else Vector((0,1,0));u=ref.cross(n).normalized();v=n.cross(u)
 for li in f.loop_indices:
  p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.dot(u),p.dot(v))
 f.use_smooth=True
mesh.set_sharp_from_angle(angle=math.radians(30))
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
for obj in bpy.context.scene.objects:
 if obj.type!='MESH':continue
 if not obj.name.startswith(('Door','Ph_')):
  used={p.material_index for p in obj.data.polygons};mat=obj.data.materials[next(iter(used))];obj.name=mat.name;obj.data.name=mat.name
 else:
  for p in obj.data.polygons:p.use_smooth=False
bpy.ops.export_scene.gltf(filepath='/workspace/church_work/clean.glb',export_format='GLB',export_yup=True,export_normals=True,export_texcoords=True,export_materials='EXPORT',export_extras=True,export_cameras=False,export_lights=False)
