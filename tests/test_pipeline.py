import os

def test_outputs_exist():
    assert os.path.exists("data/processed/geometry.json")
    assert os.path.exists("data/output_3d/model.obj")
    assert os.path.exists("data/output_3d/model.png")
