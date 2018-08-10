import logging
import os
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

x = {"21": "Backfire", "22": "Breakout", "23": "Octane", "24": "Paladin", "25": "Road Hog", "26": "Gizmo",
     "28": "X-Devil",
     "29": "Hotshot", "30": "Merc", "31": "Venom", "402": "Takumi", "403": "Dominus", "404": "Scarab", "523": "Zippy",
     "597": "DeLorean Time Machine", "600": "Ripper", "607": "Grog", "803": "Batmobile", "1018": "Dominus GT",
     "1159": "X-Devil Mk2", "1171": "Masamune", "1172": "Marauder", "1286": "Aftershock", "1295": "Takumi RX-T",
     "1300": "Road Hog XL", "1317": "Esper", "1416": "Breakout Type-S", "1475": "Proteus", "1478": "Triton",
     "1533": "Vulcan", "1568": "Octane ZSR", "1603": "Twin Mill III", "1623": "Bone Shaker", "1624": "Endo",
     "1675": "Ice Charger", "1691": "Mantis", "1856": "J\u00e4ger 619 RS", "1919": "Centio V17", "1932": "Animus GP",
     "2268": "'70 Dodge Charger R/T", "2269": "'99 Nissan Skyline GT-R R34"}
y = {value: int(key) for key, value in x.items()}

excel_file_name = [i for i in os.listdir(os.path.dirname(os.path.realpath(__file__))) if i.endswith('xlsx')][0]
excel_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), excel_file_name)
xl = pd.read_excel(excel_file_path)

indices = []
for row_number, row_data in xl.iterrows():
    car = row_data['Car']
    car_index = y.get(car, row_number)
    indices.append(car_index)
xl['Item ID'] = indices

xl.set_index('Item ID', inplace=True)


def get_hitbox(car_item_id):
    try:
        car_hitbox = xl.loc[car_item_id, ['Length', 'Width', 'Height', 'Offset', 'Elevation']].values
    except KeyError:
        logger.debug("Cannot find car body id: %s. Falling back onto Octane." % car_item_id)
        car_hitbox = xl.loc[23, ['Length', 'Width', 'Height', 'Offset', 'Elevation']].values
    car_length, car_width, car_height, car_offset, car_elevation = car_hitbox
    car_x_lims = (-car_length / 2 + car_offset, car_length / 2 + car_offset)
    car_y_lims = (-car_width / 2, car_width / 2)
    car_z_lims = (-car_height / 2 + car_elevation, car_height / 2 + car_elevation)
    return car_x_lims, car_y_lims, car_z_lims


def get_distance(position, hit_box):
    """

    :param position: location of the ball in the local coordinates of the car
    :param hit_box: hitbox returned by get_hitbox
    :return:
    """
    car_x_lims, car_y_lims, car_z_lims = hit_box
    pos_x, pos_y, pos_z = position
    # x axis
    if car_x_lims[0] <= pos_x <= car_x_lims[1]:
        x_dist = 0
    elif pos_x < car_x_lims[0]:
        x_dist = abs(car_x_lims[0] - pos_x)
    elif pos_x > car_x_lims[1]:
        x_dist = abs(car_x_lims[1] - pos_x)
    # y axis
    if car_y_lims[0] <= pos_y <= car_y_lims[1]:
        y_dist = 0
    elif pos_y < car_y_lims[0]:
        y_dist = abs(car_y_lims[0] - pos_y)
    elif pos_y > car_y_lims[1]:
        y_dist = abs(car_y_lims[1] - pos_y)
    # z azis
    if car_z_lims[0] <= pos_z <= car_z_lims[1]:
        z_dist = 0
    elif pos_z < car_z_lims[0]:
        z_dist = abs(car_z_lims[0] - pos_z)
    elif pos_z > car_z_lims[1]:
        z_dist = abs(car_z_lims[1] - pos_z)

    return np.sqrt(x_dist ** 2 + y_dist ** 2 + z_dist ** 2)


# hitbox = get_hitbox(403)
# print(get_distance([0, 0, 155], hitbox))
