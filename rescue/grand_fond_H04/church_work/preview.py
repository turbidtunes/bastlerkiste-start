import bpy, math, os
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath='/workspace/inbox/grand_fond_parish_church/grand_fond_parish_church.glb')
for o in bpy.data.objects:
 if o.name.startswith('Ph_'):o.hide_render=True
for mat in bpy.data.materials:
 if mat.name.startswith('new_'):
  p='/workspace/inbox/grand_fond_parish_church/'+mat.name+'.png'
  if os.path.exists(p):
   nd=mat.node_tree.nodes;links=mat.node_tree.links;pr=next((n for n in nd if n.type=='BSDF_PRINCIPLED'),None)
   im=nd.new('ShaderNodeTexImage');im.image=bpy.data.images.load(p);tc=nd.new('ShaderNodeTexCoord');mp=nd.new('ShaderNodeVectorMath');mp.operation='SCALE';mp.inputs[3].default_value=1 if 'zinc' in mat.name or 'enamel' in mat.name else .5
   links.new(tc.outputs['UV'],mp.inputs[0]);links.new(mp.outputs[0],im.inputs['Vector']);links.new(im.outputs['Color'],pr.inputs['Base Color'])
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=6
scene.cycles.use_denoising=False
scene.world.color=(.45,.45,.45)
bpy.ops.object.light_add(type='AREA',location=(-10,-20,28));bpy.context.object.data.energy=5000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=22
bpy.ops.object.light_add(type='SUN',location=(0,0,25));bpy.context.object.rotation_euler=(.5,-.5,-.5);bpy.context.object.data.energy=2.0;bpy.context.object.data.angle=.25
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam
def render(name,loc,target,ortho=None):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.type='ORTHO' if ortho else 'PERSP'
 if ortho:cam.data.ortho_scale=ortho
 else:cam.data.lens=22
 scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
 scene.render.filepath='/workspace/church_work/'+name+'.png';bpy.ops.render.render(write_still=True)
render('exterior',(-29,-39,24),(0,0,6.3),43)
render('rear',(30,36,22),(0,1,6),43)
for y in [-3,4,11]:
 bpy.ops.object.light_add(type='AREA',location=(0,y,7.8));bpy.context.object.data.energy=800;bpy.context.object.data.size=4
for o in bpy.data.objects:
 if o.name.startswith('Ph_'):o.hide_render=False
render('interior',(0,-5.9,2.4),(0,11,4.8))
bpy.ops.wm.save_as_mainfile(filepath='/workspace/church_work/review.blend')
