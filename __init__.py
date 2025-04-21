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

ROCK_GROUP_NAME = "RockGenerator"
ROCK_BLEND_FILE = "rock_generator.blend"
tracked_objects = set()


def get_addon_dir():
    return os.path.dirname(__file__)


def append_node_group():
    if ROCK_GROUP_NAME in bpy.data.node_groups:
        print("[RockGen] Node group already loaded.")
        return

    blend_path = os.path.join(get_addon_dir(), ROCK_BLEND_FILE)
    if not os.path.exists(blend_path):
        print(f"[RockGen] File not found: {blend_path}")
        return

    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        if ROCK_GROUP_NAME in data_from.node_groups:
            data_to.node_groups = [ROCK_GROUP_NAME]
            print(f"[RockGen] Node group '{ROCK_GROUP_NAME}' appended.")
        else:
            print(f"[RockGen] Node group '{ROCK_GROUP_NAME}' not found in {blend_path}.")


def apply_geometry_nodes_modifier(obj):
    if obj is None or obj.type != 'MESH':
        return

    node_group = bpy.data.node_groups.get(ROCK_GROUP_NAME)
    if node_group is None:
        print("[RockGen] Node group not yet available.")
        return

    # Check if already has this modifier
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group == node_group:
            return

    mod = obj.modifiers.new(name="RockModifier", type='NODES')
    mod.node_group = node_group
    print(f"[RockGen] Modifier applied to {obj.name}.")


def on_scene_update(scene):
    global tracked_objects
    current_names = {obj.name for obj in bpy.data.objects}
    new_objects = current_names - tracked_objects

    for obj_name in new_objects:
        obj = bpy.data.objects.get(obj_name)
        if obj and obj.type == 'MESH' and "cube" in obj.name.lower():
            print(f"[RockGen] New cube detected: {obj.name}")
            apply_geometry_nodes_modifier(obj)

    tracked_objects = current_names


def on_file_load(_):
    append_node_group()
    global tracked_objects
    tracked_objects = {obj.name for obj in bpy.data.objects}
    print(f"[RockGen] Tracked {len(tracked_objects)} existing objects.")


def register():
    bpy.app.timers.register(append_node_group, first_interval=0.1)
    bpy.app.handlers.load_post.append(on_file_load)
    bpy.app.handlers.depsgraph_update_post.append(on_scene_update)
    print("[RockGen] Add-on registered.")


def unregister():
    if on_file_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_file_load)
    if on_scene_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_scene_update)
    print("[RockGen] Add-on unregistered.")