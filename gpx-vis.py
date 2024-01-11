#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import math
import requests
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw


IMAGE_SIZE = (1000, 1000)
IMAGE_MODE = "RGB"
IMAGE_BG_COLOR = (0, 0, 0)
IMAGE_FG_COLOR = (0, 255, 0)
IMAGE_TYPE = "PNG"
LINE_WIDTH = 1



def get_points(gpx_file):
    tree = ET.parse(gpx_file)
    root = tree.getroot()
    points = []

    for item in root.iter():
        if "trkpt" in item.tag:
            attr = item.attrib
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


def scale_to_img(point, h_w, bbox):
    old = (bbox[2], bbox[0])
    new = (0, h_w[1])
    y = ((point[0] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]
    old = (bbox[1], bbox[3])
    new = (0, h_w[0])
    x = ((point[1] - old[0]) * (new[1] - new[0]) / (old[1] - old[0])) + new[0]

    return int(x), h_w[1] - int(y)




if len(sys.argv) < 2:
    print(f"usage: {os.path.basename(sys.argv[0])} <gpx-dir> [<img-file>]", file=sys.stderr)
    sys.exit(1)

gpx_dir = sys.argv[1].strip()
if not os.path.isdir(gpx_dir):
    print(f"{gpx_dir} is not a directory", file=sys.stderr)
    sys.exit(1)

gpx_files = [f for f in glob.iglob(gpx_dir + "/*.gpx", recursive=False) if os.path.isfile(f)]
if len(gpx_files) == 0:
    print("no GPX files", file=sys.stderr)
    sys.exit(1)

#gpx_files.sort()

points = []
for gpx_file in gpx_files:
    points += get_points(gpx_file)

if len(points) == 0:
    print("no points", file=sys.stderr)
    sys.exit(1)

bbox = get_bbox(points)
img_size = get_img_size(bbox)

img_points = []
for point in points:
    img_point = scale_to_img(point, img_size, bbox)
    img_points.append(img_point)

image = Image.new(IMAGE_MODE, img_size, IMAGE_BG_COLOR)
draw = ImageDraw.Draw(image)
draw.line(img_points, fill=IMAGE_FG_COLOR, width=LINE_WIDTH)

if len(sys.argv) > 2:
    img_file = sys.argv[2].strip() + "." + IMAGE_TYPE.lower()
    image.save(img_file, IMAGE_TYPE)
else:
    image.show()

sys.exit(0)

