import os, sys, math, json, struct, collections, time
sys.path.insert(0,'/workspace/build_libs')
import numpy as np
import manifold3d as mf
from shapely.geometry import Polygon, box as rect, LineString
from shapely.ops import unary_union
import trimesh
from math import sin,cos,pi,sqrt

OUT='/workspace/inbox/grand_fond_parish_church'
WORK='/workspace/church_work'
M=mf.Manifold; C=mf.CrossSection
parts=[]; nodes=[]; ids={}; rooms=collections.defaultdict(list); doors=[]
palette={
'basalt_masonry':(.19,.205,.19),'basalt_dressed':(.23,.25,.24),'rubble_pointing':(.37,.36,.30),
'new_limestone_pale_aged':(.68,.65,.53),'limewash':(.78,.77,.67),'limestone_flag':(.46,.44,.36),
'floor_tiles':(.50,.45,.36),'concrete_cast':(.42,.43,.40),'plaster_white':(.83,.82,.76),
'new_roof_metal_oxblood':(.35,.065,.065),'new_zinc_dome_aged':(.31,.33,.33),
'white_peeling_timber':(.77,.75,.65),'wood_mahogany_varnished':(.23,.085,.045),
'painted_timber_warmgrey':(.22,.23,.20),'galvanized_steel':(.48,.52,.53),
'steel_painted_worn':(.075,.085,.075),'new_clock_enamel_ivory':(.86,.83,.70),
'new_lookout_waterproofing':(.31,.32,.30),'glass':(.5,.65,.7),'lamp_glass':(.95,.79,.43),
'placeholder':(.30,.47,.59)}

def tag(m,mat,col=None):
 values=[list(palette).index(mat),*(col if col else (1.,1.,1.))]
 m=m.set_properties(4,lambda p,q:values).as_original(); ids[m.original_id()]=(mat,col); return m
def put(m,mat,col=None):
 if not m.is_empty(): parts.append(tag(m,mat,col))
 return m
def cube(x0,x1,y0,y1,z0,z1):
 if min(x1-x0,y1-y0,z1-z0)<=0: return M()
 return M.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def bevelcube(x0,x1,y0,y1,z0,z1,b=.008):
 import itertools
 lo=np.array([x0,y0,z0]);hi=np.array([x1,y1,z1]);pts=[]
 for signs in itertools.product([0,1],repeat=3):
  for axis in range(3):
   p=np.where(signs,hi-b,lo+b);p[axis]=hi[axis] if signs[axis] else lo[axis];pts.append(p)
 return M.hull_points(pts)
def box(c,s,mat):
 x,y,z=c; a,b,d=np.array(s)/2; return put(cube(x-a,x+a,y-b,y+b,z-d,z+d),mat)
def union(a): return M.batch_boolean(a,mf.OpType.Add) if a else M()
def poly(p,h):
 if p.is_empty:return M()
 if p.geom_type=='MultiPolygon':return union([poly(q,h) for q in p.geoms])
 contours=[np.array(p.exterior.coords[:-1],dtype=float)]+[np.array(r.coords[:-1],dtype=float) for r in p.interiors]
 return M.extrude(C(contours,mf.FillRule.EvenOdd),h)
def local(p,depth,u=0,v=0,z=0,axis='y'):
 # polygon coordinates horizontal, height; extrude along outward depth
 a=poly(p,depth)
 if axis=='y':return a.transform(((1,0,0,u),(0,0,-1,v+depth/2),(0,1,0,z)))
 return a.transform(((0,0,1,v-depth/2),(1,0,0,u),(0,1,0,z)))
def arch(w,h,base=0):
 spring=h-sqrt(3)*w/2
 q=[(-w/2,base),(w/2,base)]
 q += [(-w/2+w*cos(t),base+spring+w*sin(t)) for t in np.linspace(0,pi/3,9)]
 q += [(w/2+w*cos(t),base+spring+w*sin(t)) for t in np.linspace(2*pi/3,pi,9)]
 return Polygon(q).buffer(0)
def tube(a,b,r,mat,n=8):
 a=np.array(a); b=np.array(b); d=b-a; L=np.linalg.norm(d)
 if L<1e-5:return
 w=d/L; ref=np.array([0,0,1.]) if abs(w[2])<.9 else np.array([0,1.,0])
 u=np.cross(ref,w);u/=np.linalg.norm(u);v=np.cross(w,u)
 t=np.column_stack((u,v,w,a));put(M.cylinder(L,r,r,n).transform(t),mat)
def ring(p,thick,depth,u,v,z,axis,mat='new_limestone_pale_aged'):
 put(local(p.buffer(thick,join_style=2).difference(p),depth,u,v,z,axis),mat)

def wall(u0,u1,v,z0,z1,axis='y',holes=(),stone=True,th=.30):
 if abs(z0-.6)<1e-6:z0=.59
 if abs(z0-12.6)<1e-6:z0=12.59
 shape=rect(u0,z0,u1,z1)
 for u,z,w,h,typ in holes:
  p=arch(w,h) if typ!='rect' else rect(-w/2,0,w/2,h)
  from shapely.affinity import translate
  shape=shape.difference(translate(p,u,z))
 mat='basalt_masonry' if stone else 'limewash'
 a=tag(local(shape,th,0,v,0,axis),mat)
 if stone:
  # shallow real masonry joints on both faces; recesses expose mortar
  cuts=[]
  faces=[-1 if v<0 else 1]
  for face in faces:
   vv=v+face*(th/2-.006)
   for i,zz in enumerate(np.arange(z0+.43,z1,.47)):
    cuts.append(local(rect(u0-.02,zz-.008,u1+.02,zz+.008),.025,0,vv,0,axis))
    for xx in np.arange(u0+(.46 if i%2 else .88),u1,.94):
     cuts.append(local(rect(xx-.007,max(zz-.46,z0+.05),xx+.007,zz-.008),.025,0,vv,0,axis))
  a=a-tag(union(cuts),'rubble_pointing')
 parts.append(a)
 return shape

glasscols=[(.16,.28,.60),(.62,.12,.09),(.17,.41,.28),(.74,.53,.14),(.35,.18,.46),(.40,.62,.65)]
def window(u,v,z,w=1.15,h=3.0,axis='y',stained=True):
 p=arch(w,h)
 ring(p,.17,.48,u,v,z,axis)
 ring(p,.055,.53,u,v,z,axis)
 sill=rect(-w/2-.24,-.14,w/2+.24,-.025)
 put(local(sill,.56,u,v,z,axis),'new_limestone_pale_aged')
 inner=p.buffer(-.045)
 if stained:
  from shapely.affinity import rotate,translate
  cells=[]
  pitch=.36
  for i,x in enumerate(np.arange(-w-1,w+1,pitch)):
   for j,y in enumerate(np.arange(-1,h+1,pitch)):
    q=rotate(rect(-pitch/2,-pitch/2,pitch/2,pitch/2),45,origin=(0,0))
    q=translate(q,x+(j%2)*pitch/2,y)
    # square grid rotated independently would overlap; use diamond tiling below
  cells=[]
  d=.27
  for j in range(-1,int(h/d)+2):
   for i in range(-int(w/d)-2,int(w/d)+3):
    x=i*2*d+(j%2)*d;y=j*d
    q=Polygon([(x-d,y),(x,y-d),(x+d,y),(x,y+d)]).buffer(-.008).intersection(inner)
    if not q.is_empty and q.area>.0002:
     cells.append(q);put(local(q,.008,u,v,z,axis),'glass',glasscols[(i+2*j)%len(glasscols)])
  lead=inner.difference(unary_union([q.buffer(.002,join_style=2) for q in cells]))
  put(local(lead,.018,u,v,z,axis),'steel_painted_worn')
 else:put(local(inner,.008,u,v,z,axis),'glass',(.58,.70,.72))
 ring(inner,.035,.075,u,v,z,axis,'steel_painted_worn')

def door(num,u,v,z,w,h=2.2,axis='y',double=False,hinge='L',frm=True,fromto='',inward=None):
 # local opening horizontal X, inside +Y for y wall, -X for x wall
 if frm:
  p=rect(-w/2,0,w/2,h); outer=rect(-w/2-.10,0,w/2+.10,h+.12)
  put(local(outer.difference(p),.34,u,v,z,axis),'wood_mahogany_varnished')
 if inward is None:inward=1 if axis=='y' else -1
 angle=(0 if inward==1 else pi) if axis=='y' else (-pi/2 if inward==1 else pi/2)
 hsign=(1 if inward==1 else -1) if axis=='y' else (-1 if inward==1 else 1)
 specs=[('a','L',0,w/2),('b','R',0,w/2)] if double else [('',hinge,0,w)]
 for suffix,side,left,width in specs:
  leafw=width-.014
  # local mesh centered horizontally at hinge, thickness centred on its own axis
  sgn=-1 if side=='L' else 1
  originu=u+hsign*(w/2-.007 if side=='L' else -w/2+.007)
  lo,hi=sorted([0,sgn*leafw]); a=tag(cube(lo,hi,-.05,0,0,h-.014),'wood_mahogany_varnished')
  for yy in [-.051,.001]:
   for zz0,zz1 in [(.22,.95),(1.10,h-.20)]:
    cut=cube(lo+.12,hi-.12,yy-.004,yy+.004,zz0,zz1)
    a=a-tag(cut,'wood_mahogany_varnished')
  # attached iron straps and handle, all one leaf node
  dec=[]
  for zz in [.30,h-.35]:dec.append(tag(cube(lo+.035,hi-.035,-.060,-.05,zz,zz+.04),'steel_painted_worn'))
  handle=hi-.13 if side=='L' else lo+.13
  dec.append(tag(cube(handle-.02,handle+.02,-.085,-.05,1.05,1.20),'steel_painted_worn'))
  a=union([a]+dec)
  pos=[originu,v+inward*.175,z+.007] if axis=='y' else [v+inward*.175,originu,z+.007]
  name=f'DoorLeaf_{num:02d}{suffix}_{side}_in'
  nodes.append((name,a,pos,angle,{'kind':'door','opening_width_m':w,'from_to':fromto,'hinge_side':side,'opens':'in','opening_rotation_degrees':-90 if side=='L' else 90}))
  doors.append({'name':name,'from_to':fromto,'opening_width_m':w,'leaf_width_m':round(leafw,3)})

counts=collections.Counter()
def ph(room,role,x,y,w,d,h,z=.6,angle=0):
 counts[room,role]+=1;name=f'Ph_{room}_{role}_{counts[room,role]:02d}'
 hung=role in ['mirror','wall_shelf','picture','wall_lamp','tool_wall','notice_board','towel_rail']
 overhead=role in ['ceiling_lamp','ceiling_fan']
 a=tag(cube(-w/2,w/2,-d if hung else -d/2,0 if hung else d/2,-h if overhead else 0,0 if overhead else h),'placeholder')
 nodes.append((name,a,[x,y,z],angle,{'kind':'placeholder','room':room,'role':role,'size_m':[w,d,h],'front_local':'-Y'}))
 rooms[room].append({'name':name,'role':role,'size_m':[w,d,h]})
def ceiling(room,x,y,z,fan=False):ph(room,'ceiling_fan' if fan else 'ceiling_lamp',x,y,1.3 if fan else .4,1.3 if fan else .4,.15,z)

print('Building shell',flush=True)
# Combined footprint and real foundation/slab; tower enters the front nave.
foot=unary_union([rect(-8.8,-10,8.8,13),rect(-3.4,-13.4,3.4,-6.2),Polygon([(-4.5,12.7),(4.5,12.7),(4.5,15),(2.5,17),(-2.5,17),(-4.5,15)])])
put(poly(foot,.55).translate((0,0,-.2)),'basalt_dressed')
put(poly(foot,.25).translate((0,0,.35)),'limestone_flag')
# service tiles replace top 12 mm of the slab locally by union with floor surface
for x0,x1,y0,y1 in [(-8.5,-4.6,8.15,12.7),(4.6,8.5,4.35,7.8),(6.1,8.5,8,12.7)]:
 put(cube(x0,x1,y0,y1,.588,.6),'floor_tiles')
# lower side walls, openings
sideys=[-7.8,-4.7,-1.6,2.0,5.5,9.8]
for side in [-1,1]:
 ys=sideys if side==-1 else [-7.8,-4.7,-1.6,2.,5.5,9.0,11.6]
 holes=[(y,1.65,1.15,(1.7 if side==1 and y>4 else 2.0 if side==-1 and y>8 else 3.0),'arch') for y in ys]
 holes += [(0,.6,1.1,2.2,'rect')]
 wall(-10,13,side*8.65,.6,5.25,'x',holes)
 for u,z,w,h,typ in holes[:-1]:window(u,side*8.65,z,w,h,axis='x')
 door(2 if side==-1 else 3,0,side*8.65,.6,1.1,axis='x',hinge='L' if side==-1 else 'R',inward=-side,fromto=('west' if side==-1 else 'east')+' landing -> side aisle')
# front aisle walls, lean-to gable upper slopes
for side in [-1,1]:
 a,b=(-8.8,-3.4) if side==-1 else (3.4,8.8)
 wall(a,b,-9.85,.6,5.25,'y',[(side*6.2,1.6,1.3,3.1,'arch')])
 window(side*6.2,-9.85,1.6,1.3,3.1)
 p=Polygon([(a,5.25),(b,5.25),(b,7.1 if side==-1 else 5.25),(a,5.25 if side==-1 else 7.1)])
 put(local(p,.30,0,-9.85,0),'basalt_masonry')
# nave upper walls and actual open arcades below
for side in [-1,1]:
 wall(-9.85,13,side*4.5,6.3,8.65,'x',[(y,6.85,.72,1.45,'arch') for y in [-7.4,-3.9,-.4,3.1,6.6,10.1]])
 for y in [-7.4,-3.9,-.4,3.1,6.6,10.1]:window(y,side*4.5,6.85,.72,1.45,'x',False)
 for y in [-7.0,-3.1,.8,4.7,8.6,12.5]:
  # octagonal pier, base and capital
  for z,h,r in [(.59,.21,.47),(.79,3.57,.30),(4.35,.18,.43)]:
   xx=side*4.5;rr=r
   if side==1 and y>8:
    xx=4.15;rr=.60 if z>4 else .30
   put(M.cylinder(h,rr,rr,8).translate((xx,y,z)),'new_limestone_pale_aged')
 for y in [-5.05,-1.15,2.75,6.65,10.55]:
  from shapely.affinity import translate,scale
  p=scale(arch(3.3,3.0),xfact=1,yfact=1.8/3.0,origin=(0,0))
  p=translate(p,y,4.5).buffer(0).union(rect(y-1.65,.6,y+1.65,4.51)).buffer(0)
  sp=rect(y-1.95,4.50,y+1.95,6.65).difference(p)
  put(local(sp,.42,0,side*4.5,0,'x'),'new_limestone_pale_aged')
# rear apse facets with genuine windows
apse=[(-4.5,13),(-4.5,15),(-2.5,17),(2.5,17),(4.5,15),(4.5,13)]
for a,b in zip(apse[:-1],apse[1:]):
 a=np.array(a);b=np.array(b);mid=(a+b)/2;length=np.linalg.norm(b-a);d=(b-a)/length
 # construct in y-plane, then rotate/translate into facet
 old=len(parts)
 wall(-length/2,length/2,0,.6,8.4,'y',[(0,2.0,min(1.25,length-.8),4.6,'arch')])
 window(0,0,2.0,min(1.25,length-.8),4.6)
 angle=math.degrees(math.atan2(d[1],d[0]))
 for i in range(old,len(parts)):parts[i]=parts[i].rotate((0,0,angle)).translate((mid[0],mid[1],0))
# back aisle walls and rooms
for side in [-1,1]:
 a,b=(-8.8,-4.5) if side==-1 else (4.5,8.8)
 hh=1.5 if side==-1 else 1.1
 wall(a,b,12.85,.6,5.25,'y',[(side*7.2,2.1,1.0,hh,'arch')])
 window(side*7.2,12.85,2.1,1,hh)
# partition around sacristy, office, passage/store/WC
wall(-8.5,-4.6,8.0,.6,4.0,stone=False,th=.12)
wall(8.0,12.7,-4.6,.6,4.0,'x',[(10.4,.6,.9,2.1,'rect')],False,.12)
door(5,10.4,-4.6,.6,.9,2.1,'x',hinge='R',fromto='choir -> sacristy')
# extra exterior sacristy door in rear wall, cut later
rearcut=local(rect(-.55,0,.55,2.2),1,-5.45,12.85,.6)
parts=[p-rearcut if not p.is_empty() else p for p in parts]
door(4,-5.45,12.85,.6,1.1,inward=-1,fromto='rear landing -> sacristy')
wall(4.6,8.5,4.2,.6,3.6,holes=[(5.5,.6,.9,2.1,'rect')],stone=False,th=.12)
wall(4.6,8.5,7.9,.6,3.6,stone=False,th=.12)
wall(4.2,7.9,4.6,.6,3.6,'x',stone=False,th=.12)
door(6,5.5,4.2,.6,.9,2.1,fromto='east aisle -> parish office')
wall(7.9,12.7,6.04,.6,3.6,'x',[(9.0,.6,.9,2.1,'rect'),(11.5,.6,.9,2.1,'rect')],False,.12)
wall(6.1,8.5,10.42,.6,3.6,stone=False,th=.12)
door(7,9.0,6.04,.6,.9,2.1,'x',hinge='R',inward=1,fromto='rear passage -> store')
door(8,11.5,6.04,.6,.9,2.1,'x',inward=1,fromto='rear passage -> WC')
for a,b,c,d,z in [(-8.5,-4.55,8,12.7,4),(4.55,8.5,4.2,12.7,3.6)]:put(cube(a,b,c,d,z,z+.25),'plaster_white')

print('Tower and stair',flush=True)
# Tower external shell, street portal and paired louvres
front_holes=[(0,.6,2.4,4.9,'arch')]+[(x,8.0,1.45,3.7,'arch') for x in [-.9,.9]]
wall(-3.4,3.4,-13.25,.6,12.6,'y',front_holes)
window(0,-13.25,3.40,2.4,1.10) if False else None
# fixed pointed transom over rectangular main doors
p=arch(2.4,4.9).difference(rect(-2,0,2,2.94))
ring(arch(2.4,4.9),.23,.55,0,-13.25,.6,'y')
ring(arch(2.4,4.9),.40,.40,0,-13.25,.6,'y')
put(local(p,.008,0,-13.25,.6),'glass',(.24,.39,.55))
ring(p,.025,.065,0,-13.25,.6,'y','new_limestone_pale_aged')
# radial tracery in tympanum, clipped to its outline
for xx in [-.52,0,.52]:
 q=arch(.70,1.2).boundary.buffer(.045).intersection(p)
 from shapely.affinity import translate
 q=translate(arch(.70,1.2).boundary.buffer(.04),xx,2.75).intersection(p)
 put(local(q,.09,0,-13.25,.6),'new_limestone_pale_aged')
door(1,0,-13.25,.6,2.4,2.8,double=True,fromto='main landing -> vestibule')
for side in [-1,1]:
 hs=[(-9.8,8.,1.4,3.7,'arch'),(-11.9,2.6,.55,1.6,'arch'),(-8.,4.5,.55,1.6,'arch')]
 wall(-13.1,-6.2,side*3.25,.6,12.6,'x',hs)
 for y,z,w,h,t in hs[1:]:window(y,side*3.25,z,w,h,'x',False)
wall(-3.4,3.4,-6.35,.6,12.6,'y',[(1.4,.6,2.6,4.1,'arch'),(.9,8,1.6,3.7,'arch')])
def louvre(u,v,z,w,h,axis):
 p=arch(w,h);ring(p,.15,.42,u,v,z,axis)
 for zz in np.arange(.05,h,.19):
  q=rect(-w/2,zz,w/2,zz+.065).intersection(p.buffer(-.04))
  put(local(q,.18,u,v,z,axis),'painted_timber_warmgrey')
for x in [-.9,.9]:louvre(x,-13.25,8,1.45,3.7,'y')
for side in [-1,1]:louvre(-9.8,side*3.25,8,1.4,3.7,'x')
louvre(.9,-6.35,8,1.6,3.7,'y')
# stair bay / room partition and bell floor
wall(-11.65,-6.5,-.24,.6,12.6,'x',[(-10.90,.6,.9,2.1,'rect'),(-10.9,6.6,.9,2.1,'rect')],False,.12)
wall(-3.1,-.29,-11.64,.6,12.6,'y',stone=False,th=.10)
door(9,-10.9,-.24,.6,.9,2.1,'x',hinge='R',fromto='vestibule -> tower stair')
door(10,-10.9,-.24,6.6,.9,2.1,'x',inward=1,fromto='tower landing -> bell room')
put(cube(-.18,3.1,-13.1,-6.5,6.35,6.6),'concrete_cast')
# 8 flights: 9 risers per flight, 1.5 m rise, 8 x .28 m going
for f in range(8):
 z=.6+1.5*f; forward=f%2==0
 x0,x1=(-3.1,-1.84) if forward else (-1.56,-.3)
 q=[(-10.2,z-.20)]
 # form one continuous closed sawtooth flight, use length coordinate
 profile=[(0,z-.40),(2.24,z+1.5-.40),(2.24,z+1.5)]
 for k in range(8,-1,-1):
  xx=min(k*.28,2.24);zz=z+(k+1)/6
  if k<8:profile += [(xx+.28,zz),(xx,zz)]
 profile += [(0,z-.40)]
 flight=local(Polygon(profile).buffer(0),x1-x0,0,(x0+x1)/2,0,'x')
 if forward:flight=flight.translate((0,-10.18,0))
 else:flight=flight.mirror((0,1,0)).translate((0,-7.94,0))
 put(flight,'concrete_cast')
 # landings connect both flights; exactly one slab at each height
 endz=z+1.5
 ya,yb=(-7.94,-6.5) if forward else (-11.59,-10.18)
 put(cube(-3.1,-.3,ya,yb,endz-.25,endz),'concrete_cast')
 # guard on open inner stair edge, 1 m above nosing
 xx=x1-.025 if forward else x0+.025
 ys=[-10.18,-9.06,-7.94] if forward else [-7.94,-9.06,-10.18]
 for j,yy in enumerate(ys):
  zz=z+1/6+j*(1.5-1/6)/2
  tube((xx,yy,zz),(xx,yy,zz+1),.025,'steel_painted_worn')
 tube((xx,ys[0],z+1+1/6),(xx,ys[-1],z+2.5),.03,'steel_painted_worn')
 if forward:tube((-1.865,-7.94,endz+1),(-1.535,-7.94,endz+1+1/6),.03,'steel_painted_worn')
 elif f<7:tube((-1.535,-10.18,endz+1),(-1.865,-10.18,endz+1+1/6),.03,'steel_painted_worn')
# lookout slab with true stair aperture (no roof blocking headroom)
top=rect(-3.4,-13.4,3.4,-6.2).difference(rect(-3.09,-11.58,-.31,-6.51))
put(poly(top,.235).translate((0,0,12.35)),'concrete_cast')
put(poly(top,.015).translate((0,0,12.585)),'new_lookout_waterproofing')
# enlarged cupola headhouse over stair; eastern exit to usable terrace
for v in [-11.66,-6.40]:wall(-3.3,1.55,v,12.6,15.35,'y',[(.1,13.1,.70,1.7,'arch')],False,.16)
wall(-11.72,-6.4,-3.22,12.6,15.35,'x',stone=False,th=.16)
wall(-11.72,-6.4,1.47,12.6,15.35,'x',[(-10.7,12.6,1.1,2.2,'rect'),(-8.4,13.1,.75,1.7,'arch')],False,.16)
door(11,-10.7,1.47,12.6,1.1,axis='x',hinge='R',fromto='lookout -> tower stair enclosure')
window(-8.4,1.47,13.1,.75,1.7,'x',False)
for v in [-11.66,-6.4]:window(.1,v,13.1,.70,1.7,'y',False)
for yy in [-10.18,-8.4,-6.5]:tube((-.27,yy,12.6),(-.27,yy,13.6),.025,'steel_painted_worn')
tube((-.27,-10.18,13.6),(-.27,-6.5,13.6),.03,'steel_painted_worn')
# continuous lookout parapet, slightly inset from footprint edges
for x in [-3.28,3.28]:put(cube(x-.12,x+.12,-13.4,-6.2,12.6,13.60),'new_limestone_pale_aged')
for y in [-13.28,-6.32]:put(cube(-3.4,3.4,y-.12,y+.12,12.6,13.60),'new_limestone_pale_aged')
# ellipsoidal closed dome atop stair headhouse
outer=M.sphere(1,24).scale((2.48,2.76,1.5)).translate((-.82,-9.06,15.35))
inner=M.sphere(1,24).scale((2.36,2.64,1.38)).translate((-.82,-9.06,15.35))
dome=(outer-inner)^cube(-5,5,-15,-3,15.35,18)
put(dome,'new_zinc_dome_aged')
from shapely.affinity import scale,translate
from shapely.geometry import Point
dome_hole=translate(scale(Point(0,0).buffer(1,resolution=24),2.36,2.64),-.82,-9.06)
put(poly(rect(-3.3,-11.8,1.65,-6.3).difference(dome_hole),.15).translate((0,0,15.20)),'new_zinc_dome_aged')
for dx,dy in [(0,0)]:
 tube((-.82,-9.06,16.82),(-.82,-9.06,18.25),.045,'steel_painted_worn')
 tube((-1.18,-9.06,17.83),(-.46,-9.06,17.83),.04,'steel_painted_worn')

print('Roofs and architectural detail',flush=True)
def roof_plane(x0,x1,y0,y1,z0,z1,mat='new_roof_metal_oxblood'):
 # corrugated closed slab: actual folded profile, continuous underside
 n=max(2,int(abs(x1-x0)/.07));xs=np.linspace(x0,x1,n+1)
 tops=[z0+(z1-z0)*(x-x0)/(x1-x0)+(.018 if i%2 else -.018) for i,x in enumerate(xs)]
 p=Polygon(list(zip(xs,tops))+[(x1,z1-.20),(x0,z0-.20)])
 put(local(p,y1-y0,0,(y0+y1)/2,0)-cube(-3.56,3.56,-13.6,-6.20,0,20),'new_roof_metal_oxblood')
 # internal timber purlins with endpoints on load bearing walls
 for y in np.arange(y0+.8,y1,3.8):
  old=len(parts);tube((x0,y,z0-.23),(x1,y,z1-.23),.10,'wood_mahogany_varnished',6)
  for k in range(old,len(parts)):parts[k]=parts[k]-cube(-3.56,3.56,-13.6,-6.20,0,20)
roof_plane(-4.75,0,-9.9,13.3,8.7,11.5)
roof_plane(0,4.75,-9.9,13.3,11.5,8.7)
roof_plane(-9.08,-4.45,-10.25,13.2,5.3,7.15)
roof_plane(4.45,9.08,-10.25,13.2,7.15,5.3)
# Small Gothic triangular louvred roof vents seen in the reference.
for side in [-1,1]:
 for yy in [-3.1,1.0,5.1,9.2]:
  p=Polygon([(-.45,9.48),(.45,9.48),(0,10.6)])
  inner=Polygon([(-.35,9.58),(.35,9.58),(0,10.42)])
  put(local(p,.82,yy,side*2.9,0,'x')-local(inner,1.0,yy,side*2.9,0,'x'),'new_roof_metal_oxblood')
  ring(inner,.045,.10,yy,side*3.32,0,'x','white_peeling_timber')
  for zz in np.arange(9.64,10.40,.14):
   slat=rect(-.35,zz,.35,zz+.045).intersection(inner)
   put(local(slat,.08,yy,side*3.32,0,'x'),'painted_timber_warmgrey')
# real boarded ceiling over nave and choir; no floating ceiling placeholders
put(cube(-4.5,4.5,-6.2,9.4,8.5,8.65),'wood_mahogany_varnished')
choirfoot=unary_union([rect(-4.5,9.4,4.5,13),Polygon([(-4.5,13),(4.5,13),(4.5,15),(2.5,17),(-2.5,17),(-4.5,15)])])
put(poly(choirfoot,.2).translate((0,0,8.35)),'wood_mahogany_varnished')
# gable closure at rear/front central nave
for y in [-9.85,13.0]:
 p=Polygon([(-4.5,8.55),(4.5,8.55),(0,11.35)])
 if y<0:p=p.difference(rect(-3.4,0,3.4,14))
 put(local(p,.25,0,y,0),'limewash')
# faceted apse hip; solid roof wedges share boundaries and are unioned
ap=Polygon([(-4.75,12.6),(4.75,12.6),(4.75,15.1),(2.6,17.25),(-2.6,17.25),(-4.75,15.1)])
pts=list(ap.exterior.coords)[:-1]; apex=np.array([0,13.5,11.35])
for a,b in zip(pts,pts[1:]+pts[:1]):
 aa=np.array([a[0],a[1],8.65]);bb=np.array([b[0],b[1],8.65])
 verts=np.array([aa,bb,apex,aa-[0,0,.2],bb-[0,0,.2],apex-[0,0,.2]])
 faces=np.array([[0,1,2],[3,5,4],[0,3,4],[0,4,1],[1,4,5],[1,5,2],[2,5,3],[2,3,0]],dtype=np.uint32)
 t=trimesh.Trimesh(verts,faces,process=False);t.fix_normals()
 put(M(mf.Mesh(np.float32(t.vertices),np.uint32(t.faces))),'new_roof_metal_oxblood')
 # real narrow radial ribs, join roof skin
 for t in np.linspace(.05,.95,max(2,int(np.linalg.norm(bb-aa)/.23))):
  low=aa*(1-t)+bb*t; tube(low,apex,.025,'new_roof_metal_oxblood',6)
for a in pts:tube((a[0],a[1],8.66),apex,.045,'new_roof_metal_oxblood',8)
tube((0,-9.9,11.5),(0,13.3,11.5),.08,'new_roof_metal_oxblood')
# cornices / string courses / projecting quoins / buttresses
for z in [5.8,7.78,12.1,12.45]:
 for x in [-3.4,3.4]:put(cube(x-.12,x+.12,-13.4,-6.2,z,z+.16),'new_limestone_pale_aged')
 for y in [-13.4,-6.2]:put(cube(-3.5,3.5,y-.1,y+.1,z,z+.16),'new_limestone_pale_aged')
for x in [-3.25,3.25]:
 for y in [-13.25,-6.35]:
  for k,z in enumerate(np.arange(.62,12.1,.47)):
   sx=.56 if k%2 else .72;sy=.72 if k%2 else .56
   put(bevelcube(x-sx/2,x+sx/2,y-sy/2,y+sy/2,z,z+.445),'new_limestone_pale_aged')
for side in [-1,1]:
 for y in [-9.5,-6.3,-3.2,3.65,7.2,12.55]:
  x=side*8.9
  put(cube(x-.48,x+.48,y-.47,y+.47,-.20,.83),'basalt_dressed')
  # tapered buttress closed extruded side profile
  pp=Polygon([(0,.8),(.75,.8),(.60,3.3),(.35,4.9),(0,5.2)])
  a=local(pp,.65,0,y,0)
  if side==-1:a=a.mirror((1,0,0))
  put(a.translate((side*8.65,0,0)),'basalt_masonry')
  for z,ext in [(1.0,.72),(3.2,.56),(4.7,.38)]:
   put(cube(min(side*8.6,side*(8.65+ext)),max(side*8.6,side*(8.65+ext)),y-.37,y+.37,z,z+.12),'new_limestone_pale_aged')
 # cornice at aisle and clerestory
 for x,z in [(side*8.8,5.18),(side*4.52,8.54)]:
  put(cube(x-.13,x+.13,-10.1,13.15,z,z+.14),'new_limestone_pale_aged')
 # scalloped white eave board, not painted silhouette
 for y in np.arange(-9.9,13,.42):
  p=Polygon([(y-.20,5.17),(y+.20,5.17),(y+.20,5.02),(y+.09,5.02),(y,4.90),(y-.09,5.02),(y-.20,5.02)])
  put(local(p,.065,0,side*9.00,0,'x'),'white_peeling_timber')
 # hollow gutter trough and wall hugging pipes
 gouter=M.cylinder(23.4,.10,.10,10).rotate((90,0,0)).translate((side*9.0,13.2,5.25))
 ginner=M.cylinder(23.45,.078,.078,10).rotate((90,0,0)).translate((side*9.0,13.22,5.25))
 trough=(gouter-ginner)^cube(-10,10,-11,14,5.1,5.29)
 put(trough,'galvanized_steel')
 for y in [-8.8,6.8,11.8]:
  x=side*8.88
  tube((side*9.,y,5.20),(side*9.,y,4.9),.055,'galvanized_steel')
  tube((side*9.,y,4.9),(x,y,4.65),.055,'galvanized_steel')
  tube((x,y,4.65),(x,y,.22),.055,'galvanized_steel')
  for z in [.7,2.3,3.9]:
   put(cube(min(side*8.8,x),max(side*8.8,x)+.01,y-.085,y+.085,z-.03,z+.03),'galvanized_steel')
# front clock: disc, separate raised tick indices and hands
put(M.cylinder(.07,.58,.58,48).rotate((90,0,0)).translate((0,-13.41,7.1)),'new_clock_enamel_ivory')
for i in range(12):
 t=i*pi/6;x=.49*sin(t);z=7.1+.49*cos(t)
 tube((x,-13.49,z),(x*.88,-13.49,7.1+(z-7.1)*.88),.018,'steel_painted_worn',6)
tube((0,-13.5,7.1),(-.21,-13.5,7.37),.022,'steel_painted_worn')
tube((0,-13.5,7.1),(.35,-13.5,7.30),.015,'steel_painted_worn')
# empty niche above portal, shallow stone surround attached to wall
ring(arch(.48,.70),.08,.22,0,-13.48,5.72,'y')
# attached steps, solid to -0.20 m
def steps(x0,x1,y0,y1,axis='y',reverse=False):
 for k in range(4):
  a=y0+k*.32;b=y1
  if axis=='y':put(bevelcube(x0,x1,a,b,-.2,.15*(k+1)),'basalt_dressed')
  else:put(bevelcube(a,b,x0,x1,-.2,.15*(k+1)),'basalt_dressed')
steps(-4.1,4.1,-15.9,-13.4)
for side in [-1,1]:
 a=union([cube(8.8,10.4,-1.1,1.1,-.2,.6)]+[cube(8.8,10.4,1.1,2.06-k*.32,-.2,.15*(k+1)) for k in range(3)])
 if side==-1:a=a.mirror((1,0,0))
 put(a,'basalt_dressed')
put(cube(-6.3,-4.6,13,14.4,-.2,.6),'basalt_dressed')
for k in range(3):put(cube(-7.26+k*.32,-6.3,13,14.4,-.2,.15*(k+1)),'basalt_dressed')
# fixed entry wall lamps with closed housings and luminous panes
for x in [-2.1,2.1]:
 tube((x,-13.39,3),(x,-13.72,3),.025,'steel_painted_worn')
 put(cube(x-.13,x+.13,-13.87,-13.61,2.7,3.03),'steel_painted_worn')
 put(cube(x-.105,x+.105,-13.88,-13.87,2.73,2.98),'lamp_glass')

print('Furniture placeholders',flush=True)
ph('hall','bench',2.75,-11.8,1.7,.50,.85,angle=-pi/2)
ph('hall','notice_board',3.1,-12.1,.8,.05,.6,z=1.6,angle=-pi/2)
ceiling('hall',1.6,-9.5,6.35)
for x in [-2.5,2.5]:
 for y in np.linspace(-4.5,6.6,7):ph('chapel','pew',x,y,2.7,.65,.95,angle=pi)
for y in [-4,1.4,6.8]:
 for x in [-2.2,2.2]:ceiling('chapel',x,y,8.5)
for y in [-2.7,4.2]:
 for x in [-2.4,2.4]:ceiling('chapel',x,y,8.5,True)
ph('chapel2','altar',0,14.0,2.4,1,1)
ph('chapel2','lectern',-2.8,13.2,.65,.60,1.3)
for x in [-2.6,2.6]:
 for y in [9.8,11.65]:ph('chapel2','pew',x,y,1.8,.65,.95,angle=pi)
ceiling('chapel2',0,10.5,8.35);ceiling('chapel2',0,15,8.35)
ph('store','vestment_cabinet',-7.6,8.42,1.5,.55,2.1,angle=pi)
ph('store','vestment_cabinet',-5.73,8.42,1.4,.55,2.1,angle=pi)
ph('store','preparation_table',-7.8,10.5,1.5,.7,.85,angle=pi/2)
ph('store','chair',-6.95,9.9,.45,.5,.9,angle=-pi/2)
ph('store','chair',-6.95,11.0,.45,.5,.9,angle=-pi/2)
ph('store','basin',-8.15,12.1,.60,.45,.85,angle=pi/2)
ph('store','mirror',-8.5,12.1,.6,.025,.70,z=1.65,angle=pi/2)
ph('store','wall_shelf',-6.7,8.06,1.0,.30,.25,z=2.5,angle=pi)
ceiling('store',-6.5,10.7,4)
ph('office','office_desk',7.7,6.5,1.4,.70,.75,angle=-pi/2)
ph('office','office_chair',6.80,6.5,.55,.60,1.05,angle=-pi/2)
ph('office','visitor_chair',5.8,7.1,.5,.5,.9,angle=pi/2)
ph('office','visitor_chair',5.8,6.3,.5,.5,.9,angle=pi/2)
ph('office','filing_cabinet',7.85,4.65,.9,.55,1.35,angle=pi)
ph('office','file_shelf',7.6,7.65,1.2,.35,1.9)
ceiling('office',6.6,6,3.6);ceiling('office',6.5,7,3.6,True)
ph('store2','storage_rack',7.6,8.20,1.4,.45,2,angle=pi)
ph('store2','storage_rack',7.6,10.06,1.4,.45,2)
ceiling('store2',7.3,9.2,3.6)
ph('bathroom','wc',7.95,12.30,.55,.75,.80)
ph('bathroom','basin',7.95,10.75,.6,.45,.85,angle=pi)
ph('bathroom','mirror',7.95,10.48,.6,.025,.70,z=1.6,angle=pi)
ph('bathroom','towel_rail',7.15,10.48,.6,.08,.10,z=1.6,angle=pi)
ceiling('bathroom',7.3,11.6,3.6)
for y in [8.8,11.8]:ceiling('hall2',5.3,y,3.6)
for i in range(9):ph('hall3','wall_lamp',-3.14 if i>=7 else -3.10,-7.1 if i%2 else -11.05,.18,.10,.25,z=.6+i*1.5+1.9,angle=pi/2)
ph('hall4','church_bell',2.3,-8.1,1.4,1.2,2.8,z=6.6)
ph('hall4','wall_lamp',3.1,-11,.18,.10,.25,z=8.5,angle=-pi/2)
# The church_bell box represents the complete floor-supported bell and yoke assembly.

print('Union solids',len(parts),flush=True)
# Resolve all architectural intersections, remove buried faces and retain materials.
t=time.time();building=union(parts).as_original().simplify(.001);print('Union complete',time.time()-t,building.num_tri(),building.status(),flush=True)
assert building.status()==mf.Error.NoError
bb=building.bounding_box(); centre_y=(bb[1]+bb[4])/2

def extract(m):
 mesh=m.calculate_normals(4,30).to_mesh64(4);v0=np.asarray(mesh.vert_properties);f=np.asarray(mesh.tri_verts)
 v=np.concatenate([v0[:,:3],v0[:,7:10]],axis=1)
 groups=collections.defaultdict(list)
 keys=v0[f[:,0],3:7];uni,inv=np.unique(np.round(keys,5),axis=0,return_inverse=True)
 for i,key in enumerate(uni):
  mat=list(palette)[int(round(key[0]))];col=key[1:4].tolist()
  groups[mat].append((f[inv==i],col))
 return v,groups

gltf={'asset':{'version':'2.0','generator':'Grand Fond church procedural solid modeller'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'buffers':[{}],'bufferViews':[],'accessors':[]}
binary=bytearray();matidx={}
for name,col in palette.items():
 matidx[name]=len(gltf['materials']);d={'name':name,'pbrMetallicRoughness':{'baseColorFactor':[*col,1],'roughnessFactor':.82,'metallicFactor':.35 if name in ['galvanized_steel','steel_painted_worn','new_zinc_dome_aged'] else 0},'extras':{'surface_name':name,'uv_unit_metres':1,'engine_texture_by_material_name':name!='placeholder'}}
 if name=='glass':d['pbrMetallicRoughness']['baseColorFactor']=[1,1,1,.57];d['alphaMode']='BLEND';d['pbrMetallicRoughness']['roughnessFactor']=.18;d['doubleSided']=False
 if name=='lamp_glass':d['emissiveFactor']=[.7,.4,.12]
 if name.startswith('new_'):d['extras']['texture_file']=name+'.png';d['extras']['tile_metres']=1 if name in ['new_zinc_dome_aged','new_clock_enamel_ivory'] else 2
 gltf['materials'].append(d)
def access(a,typ,component=5126):
 a=np.asarray(a,dtype=np.float32 if component==5126 else np.uint32)
 while len(binary)%4:binary.append(0)
 off=len(binary);binary.extend(a.tobytes());vi=len(gltf['bufferViews']);gltf['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':a.nbytes})
 d={'bufferView':vi,'componentType':component,'count':len(a),'type':typ}
 if typ=='VEC3':d.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 i=len(gltf['accessors']);gltf['accessors'].append(d);return i
R=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
totaltri=0
def exportmesh(name,m,pos=None,angle=0,extras=None,split=False):
 global totaltri
 v,groups=extract(m);prims=[]
 for mat,chunks in groups.items():
  fs=np.concatenate([a for a,c in chunks]);co=np.concatenate([np.tile(c if c else (1,1,1),(len(a)*3,1)) for a,c in chunks])
  test=v[fs,:3];areas=np.linalg.norm(np.cross(test[:,1]-test[:,0],test[:,2]-test[:,0]),axis=1)
  good=areas>1e-9;fs=fs[good];co=co.reshape(-1,3,3)[good].reshape(-1,3)
  xyz=v[fs.reshape(-1),:3].copy();norm=v[fs.reshape(-1),3:6]
  if split:xyz[:,1]-=centre_y
  # triangle-local orthonormal UV projection: one unit equals one metre
  tri=xyz.reshape(-1,3,3);n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
  ref=np.tile([0,0,1.],(len(n),1));ref[np.abs(n[:,2])>.95]=[0,1,0]
  u=np.cross(ref,n);u/=np.linalg.norm(u,axis=1)[:,None];vv=np.cross(n,u)
  uv=np.stack([np.einsum('tij,tj->ti',tri,u),np.einsum('tij,tj->ti',tri,vv)],axis=-1).reshape(-1,2)
  arr=np.concatenate([xyz@R.T,norm@R.T,uv,co],axis=1).astype(np.float32)
  # weld vertices with matching position, normal, UV and colour; preserve hard edges
  unique,inv=np.unique(arr,axis=0,return_inverse=True)
  attrs={'POSITION':access(unique[:,:3],'VEC3'),'NORMAL':access(unique[:,3:6],'VEC3'),'TEXCOORD_0':access(unique[:,6:8],'VEC2')}
  if mat=='glass':attrs['COLOR_0']=access(unique[:,8:11],'VEC3')
  prim={'attributes':attrs,'indices':access(inv,'SCALAR',5125),'material':matidx[mat],'mode':4}
  totaltri+=len(fs)
  if split:
   mi=len(gltf['meshes']);gltf['meshes'].append({'name':mat,'primitives':[prim]});ni=len(gltf['nodes']);gltf['nodes'].append({'name':mat,'mesh':mi});gltf['scenes'][0]['nodes'].append(ni)
  else:prims.append(prim)
 if not split:
  mi=len(gltf['meshes']);gltf['meshes'].append({'name':name,'primitives':prims});ni=len(gltf['nodes'])
  position=np.array(pos,float);position[1]-=centre_y
  node={'name':name,'mesh':mi,'translation':(R@position).tolist(),'rotation':[0,sin(angle/2),0,cos(angle/2)],'extras':extras or {}}
  gltf['nodes'].append(node);gltf['scenes'][0]['nodes'].append(ni)
exportmesh('building',building,split=True)
for name,m,pos,angle,extras in nodes:exportmesh(name,m,pos,angle,extras)
gltf['buffers'][0]['byteLength']=len(binary)
raw=json.dumps(gltf,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4);binary+=b'\0'*((-len(binary))%4)
path=OUT+'/grand_fond_parish_church.glb'
with open(path,'wb') as f:
 f.write(struct.pack('<4sII',b'glTF',2,12+8+len(raw)+8+len(binary)));f.write(struct.pack('<I4s',len(raw),b'JSON'));f.write(raw);f.write(struct.pack('<I4s',len(binary),b'BIN\0'));f.write(binary)
stats={'triangles':totaltri,'shell_triangles':building.num_tri(),'materials':[gltf['materials'][i]['name'] for i in sorted({p['material'] for m in gltf['meshes'] for p in m['primitives']})],'doors':doors,'rooms':rooms,'bounds':building.bounding_box(),'nodes':len(gltf['nodes']),'bytes':os.path.getsize(path)}
json.dump(stats,open(WORK+'/stats.json','w'),indent=2)
print(json.dumps({k:v for k,v in stats.items() if k not in ['rooms','doors']},indent=2),flush=True)
