# import joblib
# import pandas as pd

# model = joblib.load("ml/material_model.pkl")
# layer_encoder = joblib.load("ml/layer_encoder.pkl")
# material_encoder = joblib.load("ml/material_encoder.pkl")


# def predict_material(feature_dict):
#     df = pd.DataFrame([feature_dict])

#     df["layer"] = layer_encoder.transform(df["layer"])

#     y_pred = model.predict(df)[0]
#     material = material_encoder.inverse_transform([y_pred])[0]

#     return material
import joblib
import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(BASE_DIR / "material_model.pkl")
layer_encoder = joblib.load(BASE_DIR / "layer_encoder.pkl")
material_encoder = joblib.load(BASE_DIR / "material_encoder.pkl")


def predict_material(features: dict):
    """
    features = {
        wall_thickness,
        wall_height,
        area,
        layer
    }
    """

    layer = features["layer"]

    # Handle unseen layers safely
    if layer not in layer_encoder.classes_:
        layer_encoded = 0
    else:
        layer_encoded = layer_encoder.transform([layer])[0]

    X = np.array([[
        features["wall_thickness"],
        features["wall_height"],
        features["area"],
        layer_encoded
    ]])

    pred = model.predict(X)[0]
    material = material_encoder.inverse_transform([pred])[0]

    return material
