import os

def test_pipeline_output():
    assert os.path.exists("data/processed/geometry.json")
    assert os.path.exists("data/output_3d/model.obj")
