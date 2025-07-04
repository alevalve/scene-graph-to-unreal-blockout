# Scene Graph -> Unreal BlockOut

Turn a natural-language scene description into a grey-box Unreal level in two steps:  
1. **Parse** your prompt into a sanitized scene-graph JSON.  
2. **Build** a BlockOut `.umap` in Unreal Engine from that JSON.

## Unreal Engine 

For this task, Unreal Engine 5.6.0 was used as our 3D computer graphics engine.

## 📂 Repository Layout

scene-graph-to-unreal-blockout/

├── parser.py # CLI: prompt → scene.json

├── BuildScene.py # Unreal Python: scene.json → BlockOut.umap

├── run_demo.sh # End-to-end shell: deps, parser, Unreal build

├── requirements.txt # Python dependencies

└── scene.json # Json file from parser.py

---

## 🔧 Prerequisites

- **Python 3.8+** (install via `pip install -r requirements.txt`)  
- **OpenAI API key** in your environment (`export OPENAI_API_KEY="sk-…"`)  
- **Unreal Engine 5.6+** with the **Python plugin** enabled  
- Access to **UnrealEditor** (or `UnrealEditor-Cmd` on Windows)  
- A valid Unreal **`.uproject`** file

---

## 1. Generate Scene-Graph JSON

If you only need a JSON representation of your scene, run:

```bash
export OPENAI_API_KEY="sk-…"

python3 parser.py \
  "A cosy loft with skylight and rocket-shaped lamp on the bedside table." \
  --model gpt-4.1 \
  --output scene.json
```

Positional prompt: scene description
--model, -m: OpenAI model (default: gpt-4.1)
--output, -o: output file path (default: scene.json)
This writes a sanitized scene.json to the current directory.

---

## 2. Generate Scene-Graph JSON

Use run_demo.sh to install dependencies, create the JSON and build the BlockOut map.

```bash
  chmod +x run_demo.sh
  ./run_demo.sh
  
  # Or override prompt and model:
  ./run_demo.sh \
    "A rustic cabin with a round table and a vase on top" \
    gpt-4o
```

Before run the sh file you should:

1. UE_BIN: path to your UnrealEditor binary
2. Include your GPT Key in parser.py
3. UPROJECT: full path to your .uproject
4. SCRIPTS_DIR: directory containing parser.py & BuildScene.py

--- 

## 3. Expected Output 

After running ```./run_demo.sh```, you should find the respective BlockOut file at the following path:

```swift
<Your-Unreal-Project-Directory>/Content/Maps/BlockOut.umap
```

For example:
```swift
./Unreal Projects/MyProject/Content/Maps/BlockOut.umap
```

<img width="520" alt="Screenshot 2025-06-30 at 10 01 56 AM" src="https://github.com/user-attachments/assets/4649306e-a24e-437e-a2d6-959d7488386e" />

## 4. Improvements  

Future enhancements will focus on three key areas:

**Geometry**: Add wall thickness and a full ceiling to transform the room from a simple block-out into a solid enclosure.

**Openings**: Extend the JSON schema to define doors and windows—complete with dimensions and positions—so you can automatically spawn frames and cut-outs.

**Material**s & Aesthetics: Apply default surface materials (e.g., drywall, concrete, wood) to walls, floor, and ceiling, instantly lending realism and visual polish to the generated space.





