"""roles.py – ChatGPT placeholder roles -> our kit pieces per furniture style (AUFTRAG_MOEBEL_STILE.md, user 19.10.).

ChatGPT (prompt v6) sets Ph_<room>_<role>_<nn> boxes; dress.py --placeholders puts our piece of that role in the
building's style there. Older furnished deliveries (Furn_<room>_<what>_<nn>) are mapped to roles with LEGACY.

STYLES: creole_poor (default household), creole_noble (was "colonial"), spanish_trad (was "med"), spanish_modern,
authority. pieces(role, style) -> candidate pieces: the style's list, else the creole_poor list, else any style's list;
an empty result is a GAP (a piece we still have to build, AUFTRAG_MOEBEL_STILE.md §4)."""

STYLES = ("creole_poor", "creole_noble", "spanish_trad", "spanish_modern", "authority")
OLD_STYLE = {"colonial": "creole_noble", "med": "spanish_trad", None: "creole_poor", "": "creole_poor"}

P, N, T, M, A = STYLES
ROLES = {
    # living
    "sofa": {P: ["sofa_3", "sofa_2"], N: ["rattan_sofa"], T: ["sofa_3", "sofa_2"], A: ["waiting_bench"]},
    "armchair": {P: ["armchair"], N: ["wicker_chair", "planters_chair"], T: ["wicker_chair"]},
    "coffee_table": {P: ["coffee_table"]},
    "tv_unit": {P: ["tv_cabinet"]},
    "display_cabinet": {P: ["display_cabinet"]},
    "sideboard": {P: ["display_cabinet", "dresser"], N: ["sideboard", "display_cabinet"], T: ["sideboard", "display_cabinet", "dresser"]},
    "bookcase": {P: ["bookcase"]}, "side_table": {P: ["side_table"]},
    "floor_lamp": {N: ["standing_lamp"], T: ["standing_lamp"], M: ["standing_lamp"]},
    "rug": {P: ["mat_natte", "rug"], N: ["rug"], T: ["rug"]},
    # dining
    "dining_table": {P: ["dining_table"], N: ["colonial_table"], T: ["farm_table"]},
    "dining_chair": {P: ["dining_chair", "monobloc"], N: ["colonial_chair"], T: ["rush_chair"]},
    # kitchen
    "kitchen_run": {P: ["sink_unit", "hob_counter"], T: ["tiled_counter"]},
    "cooker": {P: ["cooker", "hob2"], N: ["cooker"], T: ["cooker"], M: ["cooker"], A: ["cooker"]},
    "extractor_hood": {P: ["extractor_hood"]}, "grill_station": {P: ["grill_station"]},
    "fridge": {P: ["fridge"]},
    "kitchen_table": {P: ["kitchen_table"], N: ["kitchen_table", "dining_table", "colonial_table"], T: ["kitchen_table", "farm_table"]},
    "kitchen_chair": {P: ["monobloc", "dining_chair"], N: ["colonial_chair"], T: ["rush_chair"]},
    "wall_shelf": {P: ["shelves"], T: ["plate_rack"]},
    "pantry": {P: ["pantry"]},
    "stool": {P: ["plastic_stool"], T: ["plastic_stool"]},
    # bedroom
    "bed_double": {P: ["bed_double"], N: ["four_poster", "bed_double"], T: ["bed_double"]},
    "bed_single": {P: ["bed_single"]},
    "bunk_bed": {},
    "bedside": {P: ["bedside"]},
    "wardrobe": {P: ["wardrobe"], N: ["armoire"], T: ["wardrobe"]},
    "dresser": {P: ["dresser"]},
    "desk": {P: ["desk"]},
    "chair": {P: ["monobloc"], N: ["colonial_chair"], T: ["rush_chair"], M: ["office_chair"], A: ["office_chair"]},
    # bathroom
    "wc": {P: ["wc"]}, "basin": {P: ["basin"]}, "shower": {P: ["shower"]}, "bathtub": {}, "mirror": {P: ["mirror"]},
    "towel_rail": {P: ["towel_rail"]}, "bath_cabinet": {P: ["bath_shelf"]}, "washing_machine": {P: ["washing_machine"]},
    "laundry_basket": {P: ["laundry_basket"]},
    # hall
    "coat_rack": {P: ["coat_rack"]}, "shoe_cabinet": {P: ["shoe_cabinet"]}, "bench": {P: ["hall_bench"], A: ["waiting_bench"]}, "console": {P: ["console"]},
    # any room
    "ceiling_lamp": {P: ["ceiling_lamp"]}, "ceiling_fan": {P: ["ceiling_fan"]}, "wall_lamp": {P: ["wall_lamp"]}, "curtains": {P: ["curtains"]},
    "picture": {P: ["pictures"]},
    # office / public
    "office_desk": {P: ["desk"]}, "office_chair": {P: ["office_chair"]}, "visitor_chair": {P: ["dining_chair"], N: ["colonial_chair"]},
    "filing_cabinet": {P: ["filing_cabinet"]}, "file_shelf": {P: ["steel_rack"]}, "public_counter": {P: ["reception_desk"]}, "rug_large": {P: ["area_rug"]}, "waiting_bench": {P: ["waiting_bench"]},
    "locker": {P: ["locker"]}, "safe": {P: ["safe"]}, "gun_cabinet": {P: ["gun_cabinet"]}, "gun_rack": {P: ["gun_rack"]},
    "guard_locker": {P: ["guard_locker_locked"]}, "meeting_table": {}, "interview_table": {}, "notice_board": {P: ["notice_board"]},
    "water_cooler": {P: ["water_cooler"]}, "cell_bench": {}, "school_desk": {}, "teacher_desk": {P: ["desk"]}, "blackboard": {},
    # hotel
    "reception_counter": {}, "lobby_sofa": {P: ["sofa_3"]}, "lounge_chair": {N: ["planters_chair"], T: ["wicker_chair"]},
    "luggage_rack": {}, "minibar": {},
    # shop / bar
    "shop_counter": {P: ["shop_counter"]}, "shop_shelf": {P: ["shop_shelf", "shelf_goods"]}, "drinks_cooler": {P: ["drinks_cooler"]},
    "chest_freezer": {P: ["chest_freezer"]}, "bar_counter": {P: ["bar_counter"]}, "bar_stool": {P: ["bar_stool"]}, "cafe_table": {P: ["cafe_table"]}, "surfboard_rack": {P: ["surfboard_rack"]}, "bistro": {P: ["bistro_set"]},
    # workshop
    "workbench": {P: ["workbench"]}, "tool_wall": {P: ["tool_wall"]}, "storage_rack": {P: ["steel_rack"]}, "drill_press": {P: ["drill_press"]},
    "parts_crates": {}, "sewing_table": {}, "cloth_rack": {},
    # clinic, chapel
    "exam_couch": {P: ["exam_couch"]}, "med_cabinet": {P: ["med_cabinet"]}, "screen": {P: ["screen_folding"]},
    "pew": {P: ["pew"]}, "altar": {P: ["altar"]}, "lectern": {P: ["lectern"]},
}

# Furn_<room>_<what> of the deliveries before prompt v6 -> role (None = a small thing / part of another piece: dropped,
# dress.py adds its own small things); "table" / "chair" / "cabinet" / "bed" are decided by room + size in role_of()
LEGACY = {
    "sofa": "sofa", "armchair": "armchair", "coffee_table": "coffee_table", "lowtable": "coffee_table",
    "dining_chair": "dining_chair", "office_chair": "office_chair", "desk": "desk", "reception": "public_counter",
    "kitchen": "kitchen_run", "counter": "kitchen_run", "cooker": "cooker", "fridge": "fridge", "refrigerator": "fridge",
    "wall_shelf": "wall_shelf", "wallshelf": "wall_shelf", "wardrobe": "wardrobe", "bedside": "bedside", "nightstand": "bedside",
    "toilet": "wc", "wc": "wc", "vanity": "basin", "basin": "basin", "shower": "shower", "showertray": "shower",
    "mirror": "mirror", "towelrail": "towel_rail", "towel_rail": "towel_rail", "washing_machine": "washing_machine",
    "washingmachine": "washing_machine", "laundry_hamper": "laundry_basket", "linencabinet": "bath_cabinet",
    "ceilinglamp": "ceiling_lamp", "ceiling_light": "ceiling_lamp", "light": "ceiling_lamp", "ceilingfan": "ceiling_fan",
    "fan": "ceiling_fan", "curtain_pair": "curtains", "pair": "curtains", "shelving": "file_shelf", "storagerack": "storage_rack",
    "workbench": "workbench", "toolwall": "tool_wall", "drillpress": "drill_press", "partscrate": "parts_crates",
    "sewing_machine": "sewing_table", "cloth_rack": "cloth_rack", "shoecabinet": "shoe_cabinet", "coathooks": "coat_rack",
    "coat_rack": "coat_rack", "bench": "bench", "sideboard": "sideboard", "stool": "stool", "sink": None,
    "lamp": "ceiling_lamp", "bedsidetable": "bedside", "laundrybasket": "laundry_basket", "diningtable": "dining_table",
    "filingcabinet": "filing_cabinet", "partsrack": "storage_rack", "toolboard": "tool_wall", "toolcabinet": "storage_rack",
    "rack": "storage_rack", "packingtable": "workbench", "sidetable": "side_table", "lowtable": "coffee_table",
    **{k: None for k in ("crate", "radio", "papers", "bottle", "crockery", "timberstock", "plant", "vase")},
    # small things and parts of other pieces
    **{k: None for k in ("cup", "mug", "pot", "saucepan", "place_setting", "setting", "book", "scissors", "thread_spool",
                         "binder", "keyboard", "monitor", "mouse", "mouse_pad", "pen_holder", "cushion", "pillow", "duvet",
                         "mattress", "folded_cloth", "cloth_roll", "bedside_lamp", "bedsidelamp", "waste_bin", "bin",
                         "servingbowl", "bowl", "vice", "key_shelf", "showerscreen", "showerfittings", "hamper", "machine")},
}


def role_of(what, room, size):
    """Furn_ <what> (+ room token, box size w, d, h in m) -> role or None"""
    w = what.lower().strip("_")
    if w in ROLES: return w                                     # already a role name (Furn_kitchen_chair -> kitchen_chair)
    for k in sorted(LEGACY, key=len, reverse=True):
        if w == k: return LEGACY[k]
    big = max(size[0], size[1])
    if w.startswith("bed"): return "bed_double" if min(size[0], size[1]) >= 1.25 else "bed_single"
    if w.startswith("table"):
        if size[2] < .55: return "coffee_table"
        return "kitchen_table" if room.startswith("kitchen") else "meeting_table" if room.startswith("office") else \
            "sewing_table" if room.startswith("workshop") and big < 1.4 else "workbench" if room.startswith("workshop") else "dining_table"
    if w.startswith("chair"):
        return "kitchen_chair" if room.startswith("kitchen") else "dining_chair" if room.startswith("dining") else \
            "visitor_chair" if room.startswith("office") else "chair"
    if w.startswith("cabinet"):
        return "bath_cabinet" if room.startswith("bath") else "filing_cabinet" if room.startswith("office") else \
            "bedside" if big < .6 and room.startswith("bed") else "sideboard"
    for k in sorted(LEGACY, key=len, reverse=True):
        if w.startswith(k) or w.endswith(k): return LEGACY[k]
    return w                                                    # unknown: a role we do not have (GAP)


# a long kitchen_run box (> 1.7 m) is filled end to end with these pieces (one each, in this order, while they fit)
RUNS = {P: ["sink_unit", "hob2", "kitchen_table"], N: ["sink_unit", "cooker"], T: ["tiled_counter", "sink_unit"],
        M: ["sink_unit", "cooker"], A: ["sink_unit"]}


def run_pieces(style, lib):
    st = OLD_STYLE.get(style, style)
    return [p for p in RUNS.get(st, RUNS[P]) if p in lib]


def pieces(role, style, lib):
    """candidate pieces for a role in a style (only pieces that exist in pieces.json)"""
    st = OLD_STYLE.get(style, style)
    r = ROLES.get(role, {})
    for s in (st, P):
        c = [p for p in r.get(s, []) if p == "curtains" or p in lib]
        if c: return c
    for s in STYLES:
        c = [p for p in r.get(s, []) if p == "curtains" or p in lib]
        if c: return c
    return []
