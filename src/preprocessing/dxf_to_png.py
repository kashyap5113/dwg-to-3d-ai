import ezdxf
import matplotlib.pyplot as plt
from pathlib import Path


def dxf_to_png(dxf_path, output_png):
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    fig, ax = plt.subplots()

    for entity in msp:
        etype = entity.dxftype()

        if etype == "LINE":
            x = [entity.dxf.start[0], entity.dxf.end[0]]
            y = [entity.dxf.start[1], entity.dxf.end[1]]
            ax.plot(x, y, color="black")

        elif etype == "CIRCLE":
            center = entity.dxf.center
            radius = entity.dxf.radius
            circle = plt.Circle((center[0], center[1]), radius, fill=False)
            ax.add_patch(circle)

        elif etype == "LWPOLYLINE":
            points = entity.get_points()
            x = [p[0] for p in points]
            y = [p[1] for p in points]
            ax.plot(x, y, color="black")

    ax.set_aspect("equal")
    ax.axis("off")

    Path(output_png).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, bbox_inches="tight", pad_inches=0)
    plt.close()

    print(f"Saved PNG: {output_png}")


if __name__ == "__main__":
    input_dxf = "data/input_dwg/sample.dxf"
    output_png = "data/processed/sample_2d.png"
    dxf_to_png(input_dxf, output_png)
