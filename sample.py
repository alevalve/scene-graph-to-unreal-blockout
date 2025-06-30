import unreal

def main():
    unreal.log("Starting simple test...")
    
    # Get editor subsystem
    editor_actor = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    
    # Just spawn a simple cube
    unreal.log("Spawning test cube...")
    try:
        # Create a StaticMeshActor directly
        cube_actor = editor_actor.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 100))
        cube_actor.set_actor_label("TEST_CUBE")
        unreal.log("Test cube spawned successfully!")
        
        # Add a simple light
        light_actor = editor_actor.spawn_actor_from_class(unreal.PointLight, unreal.Vector(0, 0, 200))
        light_actor.set_actor_label("TEST_LIGHT")
        unreal.log("Test light spawned successfully!")
        
    except Exception as e:
        unreal.log_error(f"Error spawning actors: {e}")
    
    unreal.log("Test completed!")

# Main execution
if __name__ == "__main__":
    main()