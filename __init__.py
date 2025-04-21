bl_info = {
    "name": "Auto Rock Generator",
    "author": "cheyut",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "Auto Applies to Cubes",
    "description": "Automatically applies procedural rock geometry node to cubes.",
    "category": "Object",
}

import bpy
import os

# Globals
NODE_GROUP_NAME = "RockGenerator"

loaded_node = False
known_objects = set()

def load_node_group():
    if NODE_GROUP_NAME in bpy.data.node_groups:
        return True  # already loaded

    addon_dir = os.path.dirname(__file__)
    blend_path = os.path.join(addon_dir, "rock_generator.blend")
    if not os.path.exists(blend_path):
        print(f"[RockGen] Missing file: {blend_path}")
        return False

    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        if NODE_GROUP_NAME in data_from.node_groups:
            data_to.node_groups = [NODE_GROUP_NAME]
            print(f"[RockGen] Node group '{NODE_GROUP_NAME}' appended.")
            return True
        else:
            print(f"[RockGen] Node group '{NODE_GROUP_NAME}' not found in .blend.")
            return False

def apply_rock_modifier(obj):
    if obj and obj.type == 'MESH':
        if not any(mod.type == 'NODES' and mod.node_group and mod.node_group.name == NODE_GROUP_NAME for mod in obj.modifiers):
            mod = obj.modifiers.new(name="Rockify", type='NODES')
            mod.node_group = bpy.data.node_groups.get(NODE_GROUP_NAME)
            print(f"[RockGen] Applied RockGenerator to {obj.name}")

def handle_new_objects(scene):
    global known_objects
    new_objs = {obj.name for obj in bpy.data.objects} - known_objects
    for name in new_objs:
        obj = bpy.data.objects.get(name)
        if obj and obj.type == 'MESH' and "cube" in obj.name.lower():
            apply_rock_modifier(obj)
    known_objects = {obj.name for obj in bpy.data.objects}

def init_on_load(dummy=None):
    global known_objects
    if load_node_group():
        known_objects = {obj.name for obj in bpy.data.objects}
        print(f"[RockGen] Initialized. Tracking {len(known_objects)} objects.")

def register():
    bpy.app.handlers.load_post.append(init_on_load)
    bpy.app.handlers.depsgraph_update_post.append(handle_new_objects)
    print("[RockGen] Add-on enabled.")

def unregister():
    if init_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(init_on_load)
    if handle_new_objects in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(handle_new_objects)
    print("[RockGen] Add-on disabled.")