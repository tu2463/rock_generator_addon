bl_info = {
    "name": "Auto Rock Generator",
    "author": "Cheyu Tu",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "Auto Applies to Cubes",
    "description": "Automatically applies procedural rock geometry node to cubes.",
    "category": "Object",
}

import bpy
import os

"""
Rock Mesh Type
"""

class AddRockOperator(bpy.types.Operator):
    bl_idname = "mesh.primitive_rock_add"
    bl_label = "Rock"
    bl_description = "Add a Rock with RockGenerator and RockMaterial"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add()
        obj = context.active_object
        if obj:
            apply_geometry_nodes_modifier(obj)
        return {'FINISHED'}

def add_rock_to_mesh_menu(self, context):
    self.layout.operator(AddRockOperator.bl_idname, text="Rock", icon='MESH_CUBE')


"""
Rock Generator, Rock Material
"""

ROCK_GROUP_NAME = "RockGenerator"
ROCK_MATERIAL_NAME = "RockMaterial"
ROCK_BLEND_FILE = "rock_generator.blend"
tracked_objects = set()


def get_addon_dir():
    return os.path.dirname(__file__)


def append_node_group():
    if ROCK_GROUP_NAME in bpy.data.node_groups and ROCK_MATERIAL_NAME in bpy.data.materials:
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
            print(f"[RockGen] Node group '{ROCK_GROUP_NAME}' not found.")

        if ROCK_MATERIAL_NAME in data_from.materials:
            data_to.materials = [ROCK_MATERIAL_NAME]
            print(f"[RockGen] Material '{ROCK_MATERIAL_NAME}' appended.")
        else:
            print(f"[RockGen] Material '{ROCK_MATERIAL_NAME}' not found.")

def apply_geometry_nodes_modifier(obj):
    if obj is None or obj.type != 'MESH':
        return

    node_group = bpy.data.node_groups.get(ROCK_GROUP_NAME)
    rock_mat = bpy.data.materials.get(ROCK_MATERIAL_NAME)

    if node_group is None:
        print("[RockGen] Node group not yet available.")
        return

    # Apply Geometry Nodes modifier if not already there
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group == node_group:
            break
    else:
        mod = obj.modifiers.new(name="RockModifier", type='NODES')
        mod.node_group = node_group
        print(f"[RockGen] Modifier applied to {obj.name}.")

    # Apply material if not already assigned
    if rock_mat and rock_mat.name not in [m.name for m in obj.data.materials]:
        obj.data.materials.append(rock_mat)
        print(f"[RockGen] Material applied to {obj.name}.")



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

    bpy.utils.register_class(AddRockOperator)
    bpy.types.VIEW3D_MT_mesh_add.append(add_rock_to_mesh_menu)
    print("[RockGen] Add-on registered.")

def unregister():
    if on_file_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_file_load)
    if on_scene_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(on_scene_update)
    print("[RockGen] Add-on unregistered.")