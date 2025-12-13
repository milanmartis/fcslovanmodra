# app/image_utils.py
from PIL import Image
import io

def process_logo_bytes(input_bytes: bytes, threshold: int = 240) -> bytes:
    """
    - odstráni (takmer) biele pozadie -> spraví ho priehľadné
    - automaticky oreže podľa alfa kanálu
    - vráti PNG bytes
    """
    img = Image.open(io.BytesIO(input_bytes)).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for r, g, b, a in datas:
        if r >= threshold and g >= threshold and b >= threshold:
            # biela = transparentná
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)

    # auto-crop podľa alfa kanálu (nepriehľadné pixely)
    alpha = img.split()[3]
    bbox = alpha.point(lambda x: 255 if x > 0 else 0).getbbox()
    if bbox:
        img = img.crop(bbox)

    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()
