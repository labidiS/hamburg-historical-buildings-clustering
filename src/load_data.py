import pandas as pd
from lxml import etree
from pyproj import Transformer
import re

def load_data(xml_path):
    tree = etree.parse(xml_path)
    root = tree.getroot()

    rows = []

    # Transformer from EPSG:25832 → WGS84 (lat/lon)
    transformer = Transformer.from_crs("EPSG:25832", "EPSG:4326", always_xy=True)

    for monument in root.findall(".//Denkmal"):
        name = monument.findtext("Bezeichnung")
        description = monument.findtext("Typ")

        x = monument.findtext("XCenter_EPSG25832")
        y = monument.findtext("YCenter_EPSG25832")

        datierung = monument.findtext("Datierung")

        # Extract first year from text like "1874; 1893"
        year = None
        if datierung:
            match = re.search(r"\d{4}", datierung)
            if match:
                year = int(match.group())

        if x and y:
            x = float(x)
            y = float(y)

            lon, lat = transformer.transform(x, y)

            rows.append({
                "name": name,
                "description": description,
                "latitude": lat,
                "longitude": lon,
                "year": year
            })

    return pd.DataFrame(rows)

