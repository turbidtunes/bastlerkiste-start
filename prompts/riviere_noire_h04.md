You are building one building as a production game asset for Unreal Engine 5 (LOD0 only). Work in two steps.

STEP 1 – PLAN
- Footprint and storeys with dimensions in metres, storey height, roof form.
- Furniture style of the building – exactly one of: creole_poor (a traditional, modest Creole household), creole_noble
  (a wealthy Creole / colonial house), spanish_trad (a traditional Spanish house), spanish_modern (modern Spanish: hotel,
  offices, cafés, modern flats), authority (public service: police, town hall, post, clinic, school, port office).
- Use: what the building is and who uses it – take it from the reference or invent a plausible one for the place
  (family home, flats, shop with the owner's flat above, rum shop / bar, workshop, boathouse, warehouse, school,
  clinic, police post, chapel, office …). Not every building is a home. The use decides the room programme and the
  furniture.
- Room programme per storey (each room with its use) and how the player moves through the building: entrances, stairs, corridors, which
  balconies / terraces / roof areas are reachable and how.
- Materials: EVERY surface of the building with its material name from the MATERIAL LIST below; a surface that fits
  no name on the list: new_<what> with a one-line description (we make a photo texture for it). No surface without
  a named or declared texture.
- Deviations: wherever a functional, walkable building needs something the reference picture does not show or shows
  differently (stair position, door width, wall thickness, missing access, a roof that cannot be built that way), say
  what you change and why. Function wins; keep the look – proportions, style, colours, materials, characteristic
  details – as close to the reference as possible.

STEP 2 – MODEL (after "go")

SCOPE
- Only the building itself: no vegetation (no trees, plants, planters with plants, climbing plants), no people or
  animals, no garden or boundary walls, fences, gates, hedges, no terrain, ground plane, paving or road beyond the
  building's own entrance steps / landing, no vehicles, no loose props outside (the rooms are furnished – see FURNITURE).
  Fixed parts of the building's outside belong to it: stairs, railings, shutters, awnings, empty sign boards,
  wall lamps, gutters and downpipes.
- Lettering: signs, shop names, posters and painted lettering are welcome where the building's use calls for them –
  fictional names only (no real brands, company logos, real phone numbers or addresses). They stay in the game as you
  deliver them.
- Detail level: LOD0 only (full detail). No LODs, no collision meshes, no proxy or impostor meshes.

FUNCTION – walkable wherever it makes sense
- Every exterior door is a real opening (at least 1.0 m x 2.1 m) into modelled rooms; interior doors 0.9 x 2.1 m;
  corridors at least 1.1 m wide.
- DOORS MUST WORK IN THE GAME: every door leaf is its own separate node (mesh), modelled CLOSED in its opening (never
  open, never ajar), with the frame / lining staying part of the building. Name each leaf node
  DoorLeaf_<nn>_<L|R>_<in|out> – nn = running number, L / R = hinge side seen from the side it opens towards, in / out
  = opens into the room or outwards (exterior doors open inwards, interior doors into the room they lead to); a double
  door = two leaves DoorLeaf_<nn>a_L_in + DoorLeaf_<nn>b_R_in; a sliding door DoorSlide_<nn>_<L|R> (slides to that
  side; an automatic shop entrance door that opens by itself adds _auto: DoorSlide_<nn>_<L|R>_auto), a roller shutter /
  garage door DoorRoll_<nn>. The leaf is a closed solid with real thickness (40–60 mm), its
  materials from the MATERIAL LIST, 5–10 mm gap to the frame all round. Window sashes and shutters stay part of the
  building (closed).
- Floors are real slabs 20–25 cm thick at consistent storey heights (about 3.0 m floor to floor); the ceiling is the
  underside of the slab above. Exterior walls 25–35 cm thick, interior walls 10–15 cm, so reveals show the depth.
- Every storey, balcony, loggia and roof terrace is reachable: stairs with risers at most 18 cm, treads at least
  28 cm, flight width at least 1.0 m, landings; a hatch + ladder for a flat roof that is meant to be used. Balconies
  are entered through a door. Railings and balustrades 1.0 m high and continuous.
- Plausible room layout for the building's use (e.g. shop + back room + WC; workshop + store + WC; flats with living
  room, kitchen, bathroom, bedrooms; stairwell). No fake rooms: no dark planes behind windows – the room behind a window exists. If the
  building is or contains a home: every home, however small, has a kitchen, a bathroom (shower + WC + basin, at least 1.6 x 2.2 m) and at least one bedroom of its
  own – a one-room cabin is not a home.
- Windows on every facade, at least one in every room people stay in (living, bedroom, kitchen, shop, office …); no blind side or back walls on a
  house (a tropical house has cross ventilation).
- Rooms generous enough that two people pass each other everywhere: corridors and landings at least 1.4 m wide,
  stair flights at least 1.2 m, no room narrower than 2.4 m (bathroom / WC 1.6 m), clear height at least 2.6 m,
  nothing that narrows a path below 1.2 m.
- FURNITURE AS PLACEHOLDERS – ALWAYS: plan every room completely furnished for the use you chose in STEP 1 (a home
  like a home, a shop like a shop, a workshop like a workshop) – but do NOT model the furniture: put one placeholder
  per piece, our game puts its own furniture in its place. A placeholder is a plain closed box with the real outer
  size of the piece (footprint x height), material "placeholder", named Ph_<room>_<role>_<nn>:
  <room> = the room's use (living | kitchen | dining | bedroom | bathroom | hall | store | office | shop | bar |
  workshop | garage | boatshed | classroom | clinic | waiting | chapel | guardroom | lobby | hotelroom, plus a number
  for a second room of that use, e.g. Ph_bedroom2_wardrobe_01); <role> = one of these exactly:
    living: sofa, armchair, coffee_table, tv_unit, display_cabinet, sideboard, bookcase, side_table, floor_lamp, rug
    dining: dining_table, dining_chair · kitchen: kitchen_run (counter run with sink), cooker, fridge, kitchen_table,
    kitchen_chair, wall_shelf, pantry · bedroom: bed_double, bed_single, bunk_bed, bedside, wardrobe, dresser, desk,
    chair, gun_cabinet · bathroom: wc, basin, shower, bathtub, mirror, towel_rail, bath_cabinet, washing_machine, laundry_basket ·
    hall: coat_rack, shoe_cabinet, bench, console · any room: ceiling_lamp, ceiling_fan, wall_lamp, curtains, picture
    office / public: office_desk, office_chair, visitor_chair, filing_cabinet, file_shelf, public_counter,
    waiting_bench, locker, safe, gun_cabinet, gun_rack, meeting_table, interview_table, notice_board, water_cooler, cell_bench, school_desk,
    teacher_desk, blackboard · hotel: reception_counter, lobby_sofa, lounge_chair, luggage_rack, minibar ·
    shop / bar: shop_counter, shop_shelf, drinks_cooler, chest_freezer, bar_counter, bar_stool, cafe_table ·
    workshop: workbench, tool_wall, storage_rack, drill_press, parts_crates, sewing_table, cloth_rack ·
    clinic: exam_couch, med_cabinet, screen · chapel: pew, altar, lectern
  (a piece none of these fits: a plain English role name – we build it). Placement: the box origin on the floor at the
  centre of its footprint (wall-hung pieces – mirror, wall_shelf, picture, wall_lamp, tool_wall, notice_board – on the
  wall face at their hanging height; ceiling_lamp / ceiling_fan at the ceiling), the box's local -Y axis = the piece's
  front (the side you sit on / open / use), turned only about the vertical. Direction goes into the node ROTATION,
  never into the box size: every box is modelled in its own local frame (width along local X, depth along local Y, a
  shelf on an east wall is the same box as on a north wall, only turned by its node), and its vertices sit around the
  node origin – the node translation is the only place the position is stored, never baked into the vertices too. The same rules as real furniture: standing
  on the floor, never in a wall or in a door's swing, 0.9 m paths from every door to every room and in front of beds,
  cupboards, counters, cooker, WC. No small objects (cups, books, tools – our game adds them). Minimum per room use:
  bedroom – bed, bedside, wardrobe; living – sofa / armchairs, coffee_table, a cabinet; kitchen – kitchen_run, cooker,
  fridge, kitchen_table + chairs, wall_shelf; bathroom – wc, basin, mirror, shower (in a home); shop – shop_counter,
  shop_shelf, fridge / chest_freezer; bar – bar_counter, bar_stool, cafe_table + chairs; office – office_desk,
  office_chair, filing_cabinet; workshop / garage – workbench, tool_wall, storage_rack; classroom – school_desk + chair,
  teacher_desk, blackboard; clinic – exam_couch, med_cabinet, office_desk; chapel – pew, altar, lectern; plus the
  ceiling_lamp or ceiling_fan of every room.
- Downpipes run down the wall (clipped to it every 1.5–2 m), fed from the gutter by a swan-neck under the eaves –
  never free-standing in front of the facade. Mirrors, cabinets and shelves never hang in front of a window.
- Nothing floats, nothing intersects: every part rests on what carries it – a column, pier or post stands with its whole
  base on its plinth / landing / floor (never half over an edge), steps and landings reach down into the ground. The building stands on z = 0; its plinth /
  foundation goes 20 cm below ground.

CLOSED GEOMETRY – no open roof or wall surfaces
- Every wall, slab, roof, parapet, eave, balcony slab, step and frame is a closed solid with real thickness – never a
  single surface. A roof is a slab with its top, its underside / soffit and closed edges (eaves, verges, ridge); you
  must not be able to look through or into any part from any side, also from below and from inside.
- The building shell has no holes except real openings (doors, windows, vents), and every opening shows its reveal.
- Glass panes are thin closed boxes (6–10 mm) set into their frames.

DETAIL AS GEOMETRY, NOT PAINTED ON
- Model in 3D everything that changes the silhouette or casts a shadow at 1–20 m: window frames, sashes and glazing
  bars, sills and lintels, shutters with real slats, door leaves with panels, cornices, string courses, pilasters,
  columns with base and capital, balusters, railings and their posts, gutters and downpipes, roof tiles (real tile
  rows on the visible slopes, ridge and hip tiles), chimneys, eaves with rafter ends, steps with nosings, quoins and
  plinth stones with recessed joints, signs as boards with thickness and raised letters, wall lamps, AC units.
- Textures carry only what is smaller than about 1 cm (grain, pores, stains, dirt, paint wear). Never paint windows,
  doors, mouldings, tiles, joints or shadows into a texture.
- Small bevels (5–20 mm) on exposed corners, sills, steps and columns. Real-world realism: construction, proportions
  and materials of a real building of this type and region, slightly weathered and lived in. No real brand names or
  logos.

TECHNICAL
- Units metres. glTF is Y-up: convert before export, the building must stand upright in any glTF viewer. Origin at
  the centre of the footprint on the ground; main facade facing -Y (in Z-up terms, i.e. +Z in glTF).
- Clean mesh: welded vertices, consistent outward winding (counter-clockwise seen from outside; inside the building
  every ceiling, wall and floor faces into the room it bounds – a ceiling's normal points down), vertex normals
  exported (smooth inside curved parts, hard edges above 30°). No duplicate faces, no faces of two parts lying in
  the same plane (do not stack boxes flush – merge them or keep 5 mm apart), no second parallel skin closer than
  5 mm, no faces hidden inside other parts (no tile undersides lying on the roof plane, no box bottoms on box tops),
  no zero-area triangles.
- Budget: about 60k triangles for a house, up to 150k for a large multi-storey building. Spend them on silhouette
  and on what the player sees up close; repeated elements (balusters, tiles, columns) simple, but round where round.
- One mesh / primitive per material, named exactly like its material – door leaves and placeholders are the only
  exceptions (their own nodes, see DOORS and FURNITURE AS PLACEHOLDERS).
- A list name means exactly the surface it names (our photo of it replaces yours): never use one for a different look –
  a honey-oak table is not wood_weathered (silver-grey driftwood), a sofa fabric is not canvas_fabric, a leather chair
  is not rubber_black. Every surface the list does not describe exactly is a new_<what> with its own tile.
- TEXTURE FOR EVERY SURFACE – absolutely binding (placeholders excepted: material "placeholder", no texture): every single surface carries a material that is either a name from
  the MATERIAL LIST or a newly declared new_<what> with a one-line description of the real surface (e.g.
  "new_window_frame_alu – grey-blue powder-coated aluminium, slightly chalky"). No plain colour materials, no
  unnamed or default materials, no "black" / "white" / "dark" placeholders – a window frame, a lamp housing, a
  gutter, a railing each get a real surface name. Glass is "glass".
- UVs: UV channel 0 in metres (1 UV unit = 1 m, real-world scale, no stretching) on every surface that uses a
  material from the MATERIAL LIST – our engine applies its own photo textures by material name. Only unique surfaces
  (signs, posters, painted lettering) get their own texture: name the material sign_<what> / poster_<what>, embed
  the texture (at least 1024 px, readable, no brand names) and give it a 0–1 UV layout.
- Glass: material "glass" (no texture). Emissive parts (lamp covers): material "lamp_glass".
- NEW TEXTURES IN THE ZIP: for every new_<what> material make a photo-real seamless tile texture (seamless by its
  content: no blurred or darker cross-fade band along the edges, no mirrored halves – 2 x 2 copies side by side must
  show no cross), straight-on, even
  daylight, no shadows, no perspective, no lettering, at least 1024 x 1024 px (2048 preferred), file name exactly
  new_<what>.png, and state its real-world size (e.g. "new_plaster_ochre_faded.png = 2 m x 2 m").
- DELIVERY – only what we need: the GLB (named after the building) + one new_<what>.png per new material + a short
  note.txt, nothing else (no previews, renders, reports, validation or checksum files, no inventories, no copies of
  textures for list materials – our photos replace them; the GLB embeds no textures except those of sign_ / poster_
  materials). Deliver it ONE of these two ways, whichever this session can do:
  (a) GITHUB (preferred, when this chat or Codex has access to the repository turbidtunes/bastlerkiste-start): commit
      the files into the folder inbox/<building_name>/ of that repository – <building_name> in lower_snake_case, e.g.
      inbox/creole_bakery/ with creole_bakery.glb, new_<what>.png …, note.txt – and push to main (or open a pull request).
      Single files at most 100 MB, no ZIP needed. Touch nothing else in that repository.
  (b) ZIP: pack the same files as normal, independent ZIP files of at most 20 MB each (every ZIP opens on its own – no
      split / multi-volume archive; the GLB in the first one, the tiles spread over the others) and give them to me as
      downloads.
  note.txt and your answer list: the building's use and furniture style, the doors (name, room it leads from / to,
  width), the rooms with their placeholders (roles per room), the triangle count, the materials used, every new_<what>
  material with its description and real-world tile size, and your deviations from the reference.

MATERIAL LIST (use these names exactly for the surface they describe – our photo replaces yours; a surface none of
them describes is a new_<what> with its own tile)
walls / stone: plaster_white (white render), plaster_cream_warm (warm cream render), render_spalled_old (old render with
spalls), limewash, blockwork_raw (bare concrete blocks), concrete_cast, basalt_masonry (rough basalt), basalt_dressed
(dressed basalt blocks), sandstone_ashlar, brick_old, rubble_pointing, mixed_fieldstone (fieldstone plinth),
pebble_mosaic
timber cladding / paint: weatherboard_cream (cream painted weatherboard), white_peeling_timber (white boards, peeling),
painted_timber_warmgrey, wood_weathered (silver-grey weathered timber), wood_mahogany_varnished, oak_honey (honey oak),
shutter_paint, paint_clean
roof: roof_terracotta, terracotta (ridge / hip tiles, pots), roof_slate_grey, roof_steel_bluegrey (coated steel sheet),
corrugated_rust, galvanized_steel, thatch_palm
metal: steel_painted_worn, steel_bare_rusty, aluminium_weathered, stainless_brushed, copper_patina, brass_tarnished
floors / steps: floor_tiles, ceramic_glazed_white (white glazed tiles), pavers_concrete, flagstone, limestone_flag
fittings: ceramic_glazed (sanitary ceramic), mirror_silver, stone_counter_light (stone worktop)
fabric / other: canvas_fabric (awnings), textile_cotton, rubber_black, plastic_weathered, glass, lamp_glass
(placeholders: material "placeholder")

BUILDING: the attached reference picture.
PLOT (only when a PLOT block follows): the building stands on the plot given there – its footprint must fit within the
buildable area (plot minus the stated setbacks), with at most the stated storeys; the main entrance faces the street side
given; use and furniture style as stated there.

PLOT: slot riviere_noire_H04 in Rivière-Noire (Mauritian / Creole). Plot 17 m wide (street frontage) x 21 m deep, level (terraced where the ground slopes). Keep 3 m to the street, 3 m at the back and 1.5 m to each neighbour: the footprint must fit within 14.0 x 15.0 m (smaller is fine), at most 2 storeys.
The main entrance faces the street on the -Y side.
Use: Creole timber house with lambrequins and a front veranda, family home. Furniture style: creole_poor. It is a home: put one Ph_bedroom_gun_cabinet_01 in the main bedroom (or Ph_hall_gun_cabinet_01).
