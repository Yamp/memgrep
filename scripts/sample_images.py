import sys
sys.path.extend([".", "..", "../.."])

import argparse
import os
import tqdm

from data.data_storage import get_default_storage
from data.s3_db import S3DB


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output_dir', required=True)
    parser.add_argument('-n', '--n_images', type=int, default=20)
    pargs = parser.parse_args()

    if not os.path.exists(pargs.output_dir):
        os.makedirs(pargs.output_dir)

    storage = get_default_storage()
    images_dict = storage.get_all_images(pargs.n_images)
    for image in tqdm.tqdm(images_dict.values()):
        path = os.path.join(pargs.output_dir, image.url())
        with open(path, 'wb') as bout:
            bout.write(image.data)
    