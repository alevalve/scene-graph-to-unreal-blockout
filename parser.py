import openai, json, argparse, sys, os

openai.api_key = ""

# Build JSON schema for the parser

scene_schema = {
    "name": "parse_scene_graph",
    "description": "Parse a natural-language scene prompt into a structured scene-graph JSON.",
    "parameters": {
        "type": "object",
        "properties": {
            "rooms": {
                "type": "array",
                "description": "List of rooms in the scene",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Unique room name"}
                    },
                    "required": ["name"]
                }
            },
            "objects": {
                "type": "array",
                "description": "List of all objects (furniture, props, etc.)",
                "items": {
                    "type": "object",
                    "properties": {
                        "id":     {"type": "string", "description": "Unique object identifier"},
                        "type":   {"type": "string", "description": "Object category, e.g., 'table', 'lamp'"},
                        "parent": {"type": "string", "description": "Either a room name or another object id"},
                        "position": {
                            "type": "object",
                            "description": "Absolute position in cm",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"},
                                "z": {"type": "number"}
                            },
                            "required": ["x","y","z"]
                        }
                    },
                    "required": ["id","type","parent","position"]
                }
            }
        },
        "required": ["rooms","objects"]
    }
}

def parse_scene_graph(prompt:str, model:str) -> dict: 
    """
    Send a prompt to OpenAI's API to parse a scene graph as a dict"""

    # Call the API with the scene schema
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role":"user","content":prompt}],
        functions=[scene_schema],
        function_call={"name": scene_schema['name']}
    )
    
    msg = resp.choices[0].message
    if not (hasattr(msg, 'function_call') and msg.function_call):
        raise ValueError("No function call in response")

    # Convert the JSON in a python dict
    try:
        scene = json.loads(msg.function_call.arguments)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in response: {e}")
    return scene

def sanitizer(scene: dict, room_dims, table_dims, positions) -> dict:
    """
    Sanitize the scene graph by adding specific values to empty fields
    """
    # Rooms
    for room in scene.get('rooms', []):
        for key, val in room_dims.items():
            room.setdefault(key, val)
    
    # Objects and Tables
    for obj in scene.get("objects", []):
        
        pos = obj.setdefault("position", {})
        for axis, default_val in positions.items():
            pos.setdefault(axis, default_val)

        if obj.get("type", "").lower() in ("table", "bedside_table", "desk"):
            dims = obj.setdefault("dimensions", {})
            for key, val in table_dims.items():
                dims.setdefault(key, val)

    return scene


if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Parse a prompt into a scene-graph JSON."
    )
    p.add_argument("prompt",
                   help="Textual description of the scene to build.")
    p.add_argument("--model", "-m",
                   default="gpt-4.1",
                   help="OpenAI model (default: gpt-4.1)")
    
    p.add_argument("-o","--output",
                    default="scene.json",
                    help="Where to write the output JSON")
    args = p.parse_args()

    # parse
    scene = parse_scene_graph(args.prompt, args.model)

    # sanitize 
    clean = sanitizer(
        scene,
        room_dims  = {"width":400, "length":500},
        table_dims = {"height":75},
        positions  = {"x":0, "y":0, "z":0}
    )

    # save json
    out_path = os.path.abspath(args.output)
    with open(out_path, "w") as f:
        json.dump(clean, f, indent=2)

    
