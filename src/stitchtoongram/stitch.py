import zipfile
from io import BytesIO

from stitchtoon.core.image_io import ImageIO
from stitchtoon.core.slices_detectors import SlicesDetector
from stitchtoon.core.stitcher import Stitcher


def unzip_stitch(path, quality, height, out):
    images = ImageIO.load_archive(path)

    slices = SlicesDetector.slice_points(
        images=images, height=height, smart=True, sensitivity=100, min_height=0.5
    )
    images = Stitcher.stitch(images, slices)
    max_size = 40
    compresslevel = 5
    too_big = True
    while too_big:
        zf = zipfile.ZipFile(
            out, "w", zipfile.ZIP_DEFLATED, compresslevel=compresslevel
        )

        for idx, image in enumerate(images, 1):
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format, quality=quality)
            img_byte_arr = img_byte_arr.getvalue()
            zf.writestr(
                ImageIO.filename_format_handler(f"{idx:03}", format), img_byte_arr
            )

        cmp_size = 0
        for info in zf.infolist():
            cmp_size += info.compress_size

        if cmp_size < max_size:
            too_big = False
        else:
            if compresslevel < 9:
                compresslevel += 1
            quality -= 7

    zf.close()

    return out
