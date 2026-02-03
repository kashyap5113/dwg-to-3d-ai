# src/backend/app.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import shutil

from src.dwg_parser.parse_dwg import parse_dwg
from src.preprocessing.extract_geometry import extract_walls_floors_doors_windows
from src.renderer.mesh_reconstruction import build_mesh

app = FastAPI(title="DWG to 3D Backend API")

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"message": "DWG to 3D Backend API running 🚀"}


@app.post("/upload-dwg/")
async def upload_dwg(file: UploadFile = File(...)):
    try:
        # =========================
        # 1. Save uploaded file
        # =========================
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"File saved: {file_path}")

        # =========================
        # 2. Parse DXF
        # =========================
        entities = parse_dwg(file_path)
        print("Parsed entities:", len(entities))

        if not entities:
            raise HTTPException(status_code=400, detail="No entities found in DXF")

        # =========================
        # 3. Extract geometry
        # =========================
        geometry = extract_walls_floors_doors_windows(entities)

        print("Walls:", len(geometry["walls"]))
        print("Floors:", len(geometry["floors"]))
        print("Doors:", len(geometry["doors"]))
        print("Windows:", len(geometry["windows"]))

        if not geometry["walls"] and not geometry["floors"]:
            raise HTTPException(status_code=400, detail="No walls or floors found")

        # =========================
        # 4. Build mesh (GLB)
        # =========================
        mesh_path = OUTPUT_DIR / file.filename
        build_mesh(geometry, mesh_path)

        glb_path = mesh_path.with_suffix(".glb")

        if not glb_path.exists():
            raise HTTPException(status_code=500, detail="Mesh generation failed")

        print("GLB created:", glb_path)

        # =========================
        # 5. Return GLB file
        # =========================
        return FileResponse(
            path=glb_path,
            filename=glb_path.name,
            media_type="model/gltf-binary"
        )

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
