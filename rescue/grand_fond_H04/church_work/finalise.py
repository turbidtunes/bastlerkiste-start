import sys,json,collections,os
sys.path.insert(0,'/workspace/build_libs')
from pygltflib import GLTF2
out='/workspace/inbox/grand_fond_parish_church'
g=GLTF2().load('/workspace/church_work/clean.glb')
for n in g.nodes:
 if n.mesh is not None:g.meshes[n.mesh].name=n.name
g.asset.generator='Grand Fond parish church | LOD0 | metres | geometry checked in Blender 4.3'
g.save_binary(out+'/grand_fond_parish_church.glb')
s=json.load(open('/workspace/church_work/stats.json'))
tri=sum(g.accessors[p.indices].count//3 for m in g.meshes for p in m.primitives)
s['triangles']=tri
json.dump(s,open('/workspace/church_work/stats.json','w'),indent=2)
lines=['GRAND-FOND PARISH CHURCH — grand_fond_parish_church',
'Use: Catholic parish church serving the bourg; worship, choir, sacristy, parish administration, bell room and lookout.',
'Furniture style: authority.',
f'LOD0 only. {tri:,} triangles. 12 separate door leaves; 73 furniture placeholders. No collisions, LODs, proxies, terrain or loose exterior props.',
'Dimensions: overall building including attached steps and projections 20.80 x 33.18 m; main body 17.60 x 23.00 m; tower 6.80 x 7.20 m; maximum height 18.25 m.',
'Plot: Grand-Fond H04, 30 x 42 m; fits 27 x 36 m buildable area. Place the frontmost step 3 m behind the street boundary. Main facade faces -Y in Z-up / +Z in glTF.',
'Metres. Ground datum z=0, foundation z=-0.20 m. Finished floor levels +0.60, +6.60, +12.60 m. Origin at envelope centre on ground. glTF Y-up.',
'Walls 0.30 m externally, 0.10-0.12 m internally; floors 0.25 m. Tower: eight flights, nine 0.1667 m risers per flight, 0.28 m treads; at least 1.20 m clear between wall and handrail. Landings at least 1.40 m clear. Continuous 1.0 m lookout parapet.',
'The nave is a tall single-storey volume. Bell room is level 2; stair exit and front/right lookout terrace form level 3. Sloping roofs and the cupola roof are not player terraces.',
'Main parvis: four 0.15 m risers, 0.32 m treads and a 1.54 m deep landing. Side and sacristy stairs turn along the facade to retain proper landings.',
'', 'DOORS — closed, 50 mm bodies, 7 mm frame gaps; separate hinge-origin nodes. Widths below are clear openings, not leaf sizes.',
'Hinge L/R is seen from the side the leaf opens towards. All doors open into their destination. Rotate about the node vertical axis; opening_rotation_degrees is stored in node extras. No animation or collision is included.']
for d in s['doors']:lines.append(f"{d['name']}: {d['from_to']}; opening {d['opening_width_m']:.2f} m; leaf {d['leaf_width_m']:.3f} m.")
lines+=['Main double opening 2.40 x 2.80 m; other exterior openings 1.10 x 2.20 m; interior openings 0.90 x 2.10 m.', '', 'ROOMS / PLACEHOLDERS']
descs={'hall':'Tower vestibule, approximately 3.2 x 5.8 m beside the stair; main entrance to nave.', 'chapel':'Nave and connected side aisles; 1.8 m central aisle, 1.2 m clear between pew rows.', 'chapel2':'Choir and faceted apse; level access from nave.', 'store':'Sacristy, approximately 3.84 x 4.64 m; choir door and rear exterior door.', 'office':'Parish office, approximately 3.84 x 3.58 m; door from east aisle.', 'store2':'Equipment store, 2.40 x 2.40 m; door from rear passage.', 'bathroom':'WC, approximately 2.40 x 2.22 m; door from rear passage. No dwelling is included.', 'hall2':'Rear service passage, at least 1.4 m clear around recessed rear piers.', 'hall3':'Enclosed tower stair, all flights and intermediate landings; upper enclosure exits to lookout.', 'hall4':'Bell room, approximately 3.28 x 6.60 m; bell assembly placed against east side to leave a clear route.'}
for room,items in s['rooms'].items():
 c=collections.Counter(i['role'] for i in items)
 lines.append(room+': '+descs.get(room,'')+' Placeholders: '+', '.join(f'{r} x{n}' for r,n in c.items())+'.')
lines+=['Custom roles: vestment_cabinet, preparation_table, church_bell (complete floor-supported bell-and-yoke assembly).',
'Every placeholder is an independent closed box. Dimensions use local X width, local Y depth; local -Y is its front. Standing origins are floor-centred; wall-hung origins are on their wall face; ceiling origins are at the ceiling with boxes hanging down. Placement and direction reside in node translation/rotation.',
'Lookout: no loose furnishings. Architecture includes fixed exterior lamps, shutters/louvres, downpipes and gutters.', '', 'MATERIALS', ', '.join(s['materials'])+'.',
'All architecture has metre-scaled UV0 and named surface materials. Each architectural material has one mesh/primitive; doors and placeholders are separate nodes. Curved parts use normals with a 30-degree sharp-edge threshold.',
'List-material photos are supplied by the game and are not included. GLB has no embedded images. Bind new PNGs externally by exact material name. The GLB material extras record their physical tile sizes. Glass has vertex-coloured panes and no texture; retain COLOR_0 in its UE material.',
'', 'NEW TEXTURES — all native 1254 x 1254 PNG, no upscaling',
'new_limestone_pale_aged.png = 2 x 2 m: pale grey-cream aged limestone, fine pores and restrained mottling; no joints or mouldings.',
'new_roof_metal_oxblood.png = 2 x 2 m: faded deep red painted metal, fine chalking and small wear speckles; no corrugations or seams.',
'new_zinc_dome_aged.png = 1 x 1 m: dull medium-grey aged zinc with subtle oxidation; no panel seams.',
'new_clock_enamel_ivory.png = 1 x 1 m: aged ivory enamel with fine crazing; no numerals or lettering.',
'new_lookout_waterproofing.png = 2 x 2 m: grey mineral-granule roof coating with fine aggregate; no seams or shadows.',
'', 'DEVIATIONS FROM REFERENCE / APPROVED PLAN',
'Reference has no measured interior. Footprint, rooms, floor levels, structure and service access are inferred. The tower is enlarged to contain a real stair; tall 6 m intervals retain three occupied levels.',
'The cupola is enlarged and slightly offset over the stair headroom. Reachable lookout occupies front and right sides, with continuous protective parapets, rather than a full ring around a small central cupola.',
'Rear sacristy, office, store, WC, their partitions and windows are introduced. Rear east piers are recessed into the choir side to retain passage width. Room sizes have been adjusted to the as-built layout.',
'Nave seating reduced from 20 to 14 pew placeholders to provide 1.2 m between rows. Four choir pews remain. Vestibule has one bench to keep the entrance route open. The bell placeholder includes its support/yoke.',
'Choir stays level with nave. Side and rear exterior steps turn along their landings, rather than projecting straight outward; all entrance doors have adequate landing depth.',
'Portal height is increased around the 2.8 m double doors. Clock uses raised hour indices and hands. Stained glass uses simplified coloured diamond panes, geometric leadwork and Gothic tracery. Roof vents use simple triangular louvred housings.',
'Statue niche remains empty; vegetation, forecourt paving, boundary structures, people and loose exterior objects are excluded. Only the building and its attached entrance steps/landings are delivered.',
'Photo tiles are native 1254 px rather than the preferred 2048 px, exceeding the required 1024 px minimum.',
'', 'VALIDATION',
'GLB imported and inspected in Blender; topology, outward normals, UV presence, node names, dimensions, door/furniture intersections and door swings checked programmatically. No Unreal Engine runtime session was available; the game must assign its named photo materials and door interactions.']
open(out+'/note.txt','w').write('\n'.join(lines)+'\n')
print('Final files prepared;',tri,'triangles')
