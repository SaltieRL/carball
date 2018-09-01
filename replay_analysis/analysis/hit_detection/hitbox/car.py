import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


def read_xl() -> pd.DataFrame:
    car_item_dict = {
        "21": "Backfire", "22": "Breakout", "23": "Octane", "24": "Paladin", "25": "Road Hog", "26": "Gizmo",
        "28": "X-Devil", "29": "Hotshot", "30": "Merc", "31": "Venom", "402": "Takumi", "403": "Dominus",
        "404": "Scarab", "523": "Zippy", "597": "DeLorean Time Machine", "600": "Ripper", "607": "Grog",
        "803": "Batmobile", "1018": "Dominus GT", "1159": "X-Devil Mk2", "1171": "Masamune", "1172": "Marauder",
        "1286": "Aftershock", "1295": "Takumi RX-T", "1300": "Road Hog XL", "1317": "Esper", "1416": "Breakout Type-S",
        "1475": "Proteus", "1478": "Triton", "1533": "Vulcan", "1568": "Octane ZSR", "1603": "Twin Mill III",
        "1623": "Bone Shaker", "1624": "Endo", "1675": "Ice Charger", "1691": "Mantis", "1856": "J\u00e4ger 619 RS",
        "1919": "Centio V17", "1932": "Animus GP", "2268": "'70 Dodge Charger R/T",
        "2269": "'99 Nissan Skyline GT-R R34"
    }
    car_name_to_item = {value: int(key) for key, value in car_item_dict.items()}

    excel_file_name = [i for i in os.listdir(os.path.dirname(os.path.realpath(__file__))) if i.endswith('xlsx')][0]
    excel_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), excel_file_name)
    xl = pd.read_excel(excel_file_path)

    indices = []
    for row_number, row_data in xl.iterrows():
        car = row_data['Car']
        car_index = car_name_to_item.get(car, row_number)
        indices.append(car_index)
    xl['Item ID'] = indices
    xl.set_index('Item ID', inplace=True)
    return xl
