# import joblib
import numpy as np
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from pathlib import Path


# ======================
# TRAINING DATA (dummy MVP data)
# ======================

data = [
    ["wall", 0.25, 3.0, 10.0, "concrete"],
    ["wall", 0.10, 2.5, 8.0, "gypsum"],
    ["floor", 0.20, 0.2, 50.0, "tile"],
    ["floor", 0.20, 0.2, 60.0, "marble"],
    ["window", 0.05, 1.2, 2.0, "glass"],
    ["door", 0.10, 2.2, 2.0, "wood"],
]

df = pd.DataFrame(data, columns=["layer", "thickness", "height", "area", "material"])


# ======================
# ENCODERS
# ======================

layer_encoder = LabelEncoder()
material_encoder = LabelEncoder()

df["layer_enc"] = layer_encoder.fit_transform(df["layer"])
df["material_enc"] = material_encoder.fit_transform(df["material"])

X = df[["thickness", "height", "area", "layer_enc"]].values
y = df["material_enc"].values


# ======================
# TRAIN MODEL
# ======================

model = XGBClassifier(
    n_estimators=50,
    max_depth=3,
    learning_rate=0.1,
    use_label_encoder=False,
    eval_metric="mlogloss"
)

model.fit(X, y)


# ======================
# SAVE FILES USING JOBLIB
# ======================

Path("ml").mkdir(exist_ok=True)

joblib.dump(model, "ml/material_model.pkl")
joblib.dump(layer_encoder, "ml/layer_encoder.pkl")
joblib.dump(material_encoder, "ml/material_encoder.pkl")

print("✅ Model and encoders saved successfully.")
