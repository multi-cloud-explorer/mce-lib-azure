from typing import List
import os
import argparse
import json

from decouple import config

CURRENT = os.path.abspath(os.path.dirname(__file__))

REGIONS_FILEPATH = config(
    'MCE_REGIONS_FILEPATH', default=os.path.join(CURRENT, 'azure-regions.json')
)

def get_regions(filepath=REGIONS_FILEPATH) -> List:

    if not os.path.exists(filepath):
        raise RuntimeError(f"{filepath} not found")

    with open(filepath) as fp:
        return json.load(fp)['value']

