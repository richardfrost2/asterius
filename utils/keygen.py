"""
"Keygen-ish" GIF Maker
by frost
"""
from PIL import Image
from utils.colorme import shift_hue
from io import BytesIO

def keygen(input_img: Image) -> BytesIO:
    """docs here"""
    frames = []
    output_file = BytesIO()
    for shift_amt in range(0, 360, 12):
        img = shift_hue(input_img, shift_amt)
        frames.append(img)
    frames[0].save(fp=output_file, 
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=33, # 30 fps, 1 loop per second
        loop=0, # forever
        )
    output_file.seek(0)
    return output_file
    

