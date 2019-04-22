"""
Writers
"""
import csv
from typing import Mapping, List, Optional


class CSV:
    @staticmethod
    def write_map(f, map: Mapping[str, str], keys: Optional[List[str]] = None, default: Optional[str] = None):
        if keys is None:
            header = sorted(map.keys())
        else:
            header = keys
        out = csv.DictWriter(f, fieldnames=header, extrasaction='ignore', restval=default)
        out.writeheader()
        out.writerow(map)
