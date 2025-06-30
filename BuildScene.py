import unreal
import json
import os

# Load the scene JSON file from disk
def load_scene_json() -> dict:
    scene_path = os.path.join(os.path.dirname(__file__), "scene.json")
    if not os.path.isfile(scene_path):
        unreal.log_error(f"Scene JSON not found at: {scene_path}")
        return {}
    try:
        with open(scene_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        unreal.log_error(f"Failed to parse {scene_path}: {e}")
        return {}

# Attach a child actor to its parent actor
def attach_child(child: unreal.Actor, parent: unreal.Actor):
    if child and parent:
        child.attach_to_actor(parent, "", unreal.AttachmentRule.KEEP_WORLD,
                               unreal.AttachmentRule.KEEP_WORLD,
                               unreal.AttachmentRule.KEEP_WORLD)

# Helper to spawn a static mesh actor from a mesh asset path
def spawn_static_mesh(asset_path: str, location: unreal.Vector, rotation: unreal.Rotator, scale: unreal.Vector, editor_actor: unreal.EditorActorSubsystem) -> unreal.Actor:
    mesh = unreal.load_asset(asset_path)
    if not mesh:
        unreal.log_error(f"Could not load StaticMesh: {asset_path}")
        return None
    actor = editor_actor.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
    if not actor:
        unreal.log_error(f"Failed to spawn StaticMeshActor for: {asset_path}")
        return None
    # Assign the mesh to the actor's component
    sm_comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if not sm_comp:
        unreal.log_error(f"StaticMeshComponent not found on actor: {actor.get_name()}")
        return actor
    sm_comp.set_static_mesh(mesh)
    actor.set_actor_scale3d(scale)
    actor.set_mobility(unreal.ComponentMobility.MOVABLE)
    return actor

# Main scene-building function
def build_scene(scene: dict):
    # Obtain editor subsystems
    editor_level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor_actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    # Define and create/overwrite the level
    MAP_PATH = '/Game/Maps/BlockOut'
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        unreal.log_warning(f"Level {MAP_PATH} exists; overwriting.")
        unreal.EditorAssetLibrary.delete_asset(MAP_PATH)
    try:
        unreal.log_warning("Creating new level")
        editor_level.new_level(MAP_PATH)
    except Exception as e:
        unreal.log_error(f"Failed to create level: {e}")
        return

    # Clean up any existing actors
    for actor in editor_actor.get_all_level_actors():
        if not isinstance(actor, (unreal.WorldSettings, unreal.LevelBounds)):
            editor_actor.destroy_actor(actor)

    # Spawn lighting
    dir_light = editor_actor.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,500))
    if dir_light:
        dir_light.set_actor_rotation(unreal.Rotator(-45,45,0), False)
        comp = dir_light.get_component_by_class(unreal.DirectionalLightComponent)
        if comp:
            comp.set_intensity(10)
            comp.set_use_temperature(True)
            comp.set_temperature(6500)
    sky_light = editor_actor.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,0))
    if sky_light:
        comp = sky_light.get_component_by_class(unreal.SkyLightComponent)
        if comp:
            comp.set_intensity(3.0)
            comp.set_mobility(unreal.ComponentMobility.STATIONARY)


    PLANE = '/Engine/BasicShapes/Plane'

    ROOM_HEIGHT = 300  # Z dimension for all rooms

    for room in data['rooms']:
        w = room['width']
        l = room['length']
        h = ROOM_HEIGHT

        half_w = w  / 2.0
        half_l = l  / 2.0

        # Unreal’s Plane mesh is 100×100 units by default, so scale factors:
        floor_scale = unreal.Vector(w/100.0,   l/100.0,   1.0)
        ns_wall_scale = unreal.Vector(w/100.0,   h/100.0,   1.0)  # North/South walls
        ew_wall_scale = unreal.Vector(l/100.0,   h/100.0,   1.0)  # East/West walls

        # Floor – centered at origin
        spawn_static_mesh(PLANE,
            unreal.Vector(0, 0, 0),               
            unreal.Rotator(0, 0, 0),              
            floor_scale,
            editor_actor)

        # North wall (+Y)
        spawn_static_mesh(PLANE,
            unreal.Vector(0,  half_l,  h/2.0),    # pos
            unreal.Rotator(90, 0, 0),             # rot: plane vertical facing +Y
            ns_wall_scale,
            editor_actor)

        # South wall (–Y)
        spawn_static_mesh(PLANE,
            unreal.Vector(0, -half_l,  h/2.0),
            unreal.Rotator(90, 0, 0),             # same rotation works both sides
            ns_wall_scale,
            editor_actor)

        # East wall (+X)
        spawn_static_mesh(PLANE,
            unreal.Vector( half_w, 0,  h/2.0),
            unreal.Rotator(0, 0, 90),             # plane vertical facing +X
            ew_wall_scale,
            editor_actor)

        # West wall (–X)
        spawn_static_mesh(PLANE,
            unreal.Vector(-half_w, 0,  h/2.0),
            unreal.Rotator(0, 0, 90),
            ew_wall_scale,
            editor_actor)

    # Spawn placeholder actors for rooms
    room_actors = {}
    for room in scene.get('rooms', []):
        name = room.get('name')
        width = room.get('width',0)
        length = room.get('length',0)
        loc = unreal.Vector(width/2.0,length/2.0,0)
        ra = editor_actor.spawn_actor_from_class(unreal.Actor,loc)
        if ra:
            ra.set_actor_label(name)
            room_actors[name] = ra

    # Spawn object cubes
    actors = {}
    CUBE = '/Engine/BasicShapes/Cube'
    for obj in scene.get('objects', []):
        pos = obj.get('position',{})
        loc = unreal.Vector(pos.get('x',0),pos.get('y',0),pos.get('z',0))
        a = spawn_static_mesh(CUBE, loc, unreal.Rotator(0,0,0), unreal.Vector(1,1,1), editor_actor)
        if a:
            a.set_actor_label(obj.get('id',''))
            actors[obj.get('id','')] = a

    # Attach children to their parents
    unreal.log_warning("Attaching children to parents")
    for obj in scene.get('objects', []):
        child = actors.get(obj.get('id'))
        parent = actors.get(obj.get('parent')) or room_actors.get(obj.get('parent'))
        attach_child(child, parent)

    # Save level and finish
    unreal.log_warning("Saving level")
    editor_level.save_current_level()
    unreal.log("BlockOut level built and saved.")

if __name__ == "__main__":
    data = load_scene_json()
    if data:
        build_scene(data)
    else:
        unreal.log_error("No scene data found")
