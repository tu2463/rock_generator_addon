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
    global loaded_node
    if loaded_node or NODE_GROUP_NAME in bpy.data.node_groups:
        return

    addon_dir = os.path.dirname(__file__)
    blend_path = os.path.join(addon_dir, "rock_generator.blend")
    if not os.path.exists(blend_path):
        print(f"[RockGen] Missing: {blend_path}")
        return

    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        if NODE_GROUP_NAME in data_from.node_groups:
            data_to.node_groups = [NODE_GROUP_NAME]
            print(f"[RockGen] Node group '{NODE_GROUP_NAME}' loaded!")
            loaded_node = True
        else:
            print(f"[RockGen] Node group not found in file.")

def apply_rock_to_cube(obj):
    if obj and obj.type == 'MESH' and NODE_GROUP_NAME in bpy.data.node_groups:
        if not any(mod.type == 'NODES' and mod.node_group and mod.node_group.name == NODE_GROUP_NAME for mod in obj.modifiers):
            mod = obj.modifiers.new(name="Rockify", type='NODES')
            mod.node_group = bpy.data.node_groups[NODE_GROUP_NAME]

def object_add_handler(scene):
    global known_objects
    current_names = {obj.name for obj in bpy.data.objects}
    new_names = current_names - known_objects
    for name in new_names:
        obj = bpy.data.objects.get(name)
        if obj and obj.type == 'MESH' and "cube" in obj.name.lower():
            apply_rock_to_cube(obj)
    known_objects = current_names

def track_existing_objects(dummy=None):
    global known_objects
    load_node_group()
    known_objects = {obj.name for obj in bpy.data.objects}

def register():
    bpy.app.handlers.load_post.append(track_existing_objects)
    bpy.app.handlers.depsgraph_update_post.append(object_add_handler)

def unregister():
    if track_existing_objects in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(track_existing_objects)
    if object_add_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(object_add_handler)