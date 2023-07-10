import os.path as osp
from datetime import datetime
from random import randint

import gdown


async def drive_download(url, output, callback=None):
    output = osp.join(
        output, datetime.now().strftime(f"%Y%M%d_%H%m%s{randint(10000, 99999)}")
    )
    gdown.download(url=url, output=output, quiet=False, fuzzy=True, resume=True)

    if callback is not None:
        return await callback(output)
