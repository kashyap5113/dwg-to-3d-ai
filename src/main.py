from dwg_parser.parse_dwg import parse_dwg, save_json
from preprocessing.extract_geometry import geometry_to_3d
from renderer.render_obj import save_obj
from renderer.render_png import render_png
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DWG =  "data/input_dwg/sample.dxf"
JSON_OUT =  "data/processed/geometry.json"
OBJ_OUT =  "data/output_3d/model.obj"
PNG_OUT =  "data/output_3d/model.png"


def main():
    print("Parsing DWG...")
    entities = parse_dwg(str(INPUT_DWG))
    save_json(entities, JSON_OUT)

    print("Extracting geometry...")
    vertices = geometry_to_3d(JSON_OUT)

    print("Saving OBJ...")
    save_obj(vertices, OBJ_OUT)

    print("Rendering PNG...")
    render_png(OBJ_OUT, PNG_OUT)

    print("Pipeline complete!")


if __name__ == "__main__":
    main()
