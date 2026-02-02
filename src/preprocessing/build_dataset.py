import sys
from pathlib import Path

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR / "src"))

from dwg_parser.parse_dwg import parse_dwg, save_json
from preprocessing.extract_geometry import geometry_to_3d
from renderer.render_obj import save_obj
from preprocessing.dxf_to_png import dxf_to_png


INPUT_DIR = Path("data/input_dwg")
DATASET_IMAGES = Path("dataset/images")
DATASET_MODELS = Path("dataset/models")


def build_dataset():
    DATASET_IMAGES.mkdir(parents=True, exist_ok=True)
    DATASET_MODELS.mkdir(parents=True, exist_ok=True)

    dxf_files = list(INPUT_DIR.glob("*.dxf"))

    if len(dxf_files) == 0:
        print("❌ No DXF files found in data/input_dwg/")
        return

    for i, dxf_file in enumerate(dxf_files, start=1):
        idx = f"{i:03d}"

        print(f"Processing {dxf_file.name}")

        png_path = DATASET_IMAGES / f"{idx}.png"
        obj_path = DATASET_MODELS / f"{idx}.obj"
        json_path = Path("data/processed") / f"{idx}.json"

        entities = parse_dwg(str(dxf_file))
        save_json(entities, json_path)

        vertices = geometry_to_3d(json_path)

        if vertices is None:
            print(f"⚠️ Skipping {dxf_file.name} (no geometry found)")
            continue

        save_obj(vertices, obj_path)
        dxf_to_png(str(dxf_file), png_path)


    print("✅ Dataset generation completed!")


if __name__ == "__main__":
    build_dataset()
