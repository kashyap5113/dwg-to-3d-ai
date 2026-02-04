# import numpy as np


# def extract_wall_features(poly, wall_height, layer):
#     minx, miny, maxx, maxy = poly.bounds
#     width = maxx - minx
#     height = maxy - miny

#     return {
#         "area": poly.area,
#         "perimeter": poly.length,
#         "wall_height": wall_height,
#         "aspect_ratio": max(width, height) / max(0.01, min(width, height)),
#         "layer": layer
#     }


# def extract_window_features(poly, window_height):
#     return {
#         "area": poly.area,
#         "perimeter": poly.length,
#         "window_height": window_height,
#         "layer": "window"
#     }


# def extract_floor_features(poly):
#     return {
#         "area": poly.area,
#         "perimeter": poly.length,
#         "layer": "floor"
#     }
from shapely.geometry import Polygon


def extract_wall_features(polygon: Polygon, wall_height: float, layer: str):
    """
    Extract features for ML material prediction
    """

    area = polygon.area

    minx, miny, maxx, maxy = polygon.bounds
    width = maxx - minx
    height = maxy - miny

    wall_thickness = min(width, height)

    features = {
        "wall_thickness": wall_thickness,
        "wall_height": wall_height,
        "area": area,
        "layer": layer.lower()
    }

    return features
