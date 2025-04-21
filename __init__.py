bl_info = {
    "name": "Rock Generator",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "Auto Applies to Cubes",
    "description": "Automatically applies procedural rock geometry node to cubes.",
    "category": "Object",
}

import bpy
import os

def load_node_group():
    addon_dir = os.path.dirname(__file__)
    blend_path = os.path.join(addon_dir, "rock_generator.blend")

    if "RockGenerator" not in bpy.data.node_groups:
        with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
            if "RockGenerator" in data_from.node_groups:
                data_to.node_groups = ["RockGenerator"]

def apply_node_to_cube(obj):
    if obj.type == 'MESH' and obj.name.lower().startswith("cube"):
        if not any(mod.type == 'NODES' for mod in obj.modifiers):
            mod = obj.modifiers.new(name="RockModifier", type='NODES')
            mod.node_group = bpy.data.node_groups.get("RockGenerator")

def depsgraph_handler(scene):
    # Check all objects; if new cube exists without the modifier, apply it
    for obj in scene.objects:
        if obj.name.lower().startswith("cube") and obj.type == 'MESH':
            if not any(mod.type == 'NODES' and mod.node_group == bpy.data.node_groups.get("RockGenerator") for mod in obj.modifiers):
                apply_node_to_cube(obj)

# Register/unregister
def register():
    load_node_group()
    if depsgraph_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(depsgraph_handler)

def unregister():
    if depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_handler)

if __name__ == "__main__":
    register()
