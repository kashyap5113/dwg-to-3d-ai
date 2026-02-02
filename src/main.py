from dwg_parser.parse_dwg import parse_dwg, save_json
from preprocessing.extract_geometry import geometry_to_3d
from renderer.render_obj import save_obj

INPUT_DWG = "data/input_dwg/sample.dxf"
JSON_OUT = "data/processed/geometry.json"
OBJ_OUT = "data/output_3d/model.obj"


def main():
    print("Parsing DWG...")
    entities = parse_dwg(INPUT_DWG)
    save_json(entities, JSON_OUT)

    print("Extracting geometry...")
    vertices = geometry_to_3d(JSON_OUT)

    print("Saving OBJ...")
    save_obj(vertices, OBJ_OUT)

    print("Pipeline complete!")


if __name__ == "__main__":
    main()
