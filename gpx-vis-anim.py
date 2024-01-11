#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import math
import time
from lxml import etree
import numpy as np
import cv2



IMAGE_SIZE = (1000, 1000)
IMAGE_MODE = "RGB"
IMAGE_BG_COLOR = (0, 0, 0)
IMAGE_FG_COLOR = (0, 255, 0)
LINE_WIDTH = 1




def get_points(gpx_file):
    points = []

    try:
        tree = etree.parse(gpx_file)
    except Exception as error:
        print(error, file=sys.stderr)
        return points

    root = tree.getroot()
    """
    tps = tree.xpath("//*[local-name() = 'trkpt']")
    for tp in tps:
        print(tp.attrib)
        print(tp.getchildren())
    """

    for item in root.iter():
        if "trkpt" in item.tag:
            attr = item.attrib
            """
            for i in item.iter():
                if "time" in i.tag:
                    t = i.text
            """
            points.append((float(attr["lat"]), float(attr["lon"])))

    return points


def get_bbox(points):
    min_lat, min_lon = points[0]
    max_lat, max_lon = points[0]
 
    for point in points:
        if min_lat > point[0]:
            min_lat = point[0]
        if min_lon > point[1]:
            min_lon = point[1]
        if max_lat < point[0]:
            max_lat = point[0]
        if max_lon < point[1]:
            max_lon = point[1]

    return (max_lat, min_lon, min_lat, max_lon)


def get_img_size(bbox):
    w = bbox[3] - bbox[1]
    h = bbox[0] - bbox[2]
    width, height = IMAGE_SIZE

    if w > h:
        width /= w / h
    else:
        height /= h / w

    return (int(math.ceil(width)), int(math.ceil(height)))


def scale_to_img(lat_lon, h_w, bbox):
    old = (bbox[2], bbox[0])
    new = (0, h_w[1])
    y = ((lat_lon[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
    old = (bbox[1], bbox[3])
    new = (0, h_w[0])
    x = ((lat_lon[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]

    return int(x), h_w[1] - int(y)




if len(sys.argv) == 1:
    print(f"usage: {os.path.basename(sys.argv[0])} <gpx-file(s)>", file=sys.stderr)
    sys.exit(1)

gpx_files = sys.argv[1:]
gpx_files.sort()

points = []
for gpx_file in gpx_files:
    points += get_points(gpx_file)

if len(points) == 0:
    print("no points", file=sys.stderr)
    sys.exit(1)

bbox = get_bbox(points)
img_size = get_img_size(bbox)
img = np.zeros((img_size[1], img_size[0], 3), np.uint8)
delay = 0.05
delay_coef = 1.5

for idx, point in enumerate(points):
    img_point = scale_to_img(point, img_size, bbox)
    img = cv2.circle(img, img_point, radius=0, color=IMAGE_FG_COLOR, thickness=-1)

    time.sleep(delay)

    cv2.imshow('GPX view', img)
    #cv2.putText(img, '%d/%d ' % (idx, len(points)), (img_size[0] - 100, 30), cv2.FONT_HERSHEY_DUPLEX, .5, (0, 255, 255), 1)

    k = cv2.waitKey(1) & 0xff
    if k == 27 or k == ord('q'): break
    if k == 82: delay /= delay_coef
    if k == 84: delay *= delay_coef

cv2.destroyAllWindows()

sys.exit(0)

