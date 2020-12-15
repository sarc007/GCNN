import csv
import cv2
import math
import random
import sys

INPUT_CSV = "sld_25_consolidated.csv"
POLYLINE_CSV = "sld_25_polylines.csv"
INPUT_IMAGE = "sld_25.jpg"

print("Before setting limits ", sys.getrecursionlimit())
sys.setrecursionlimit(150000)
print("After setting limits ", sys.getrecursionlimit())

def read_csv(ifil):
    csv_data = []
    with open(ifil, "r") as input_csv:
        reader = csv.reader(input_csv)
        for data in reader:
            if data:
                csv_data.append(data)
    csv_data.remove(csv_data[0])
    return csv_data


def sort_polyline(data):
    rectl = []
    frst_t = True
    lstv = data[len(data) - 1]
    for i in data:
        if int(i[0]) == 1 and frst_t:
            rectl.append(i)
            frst_t = False
        elif int(i[0]) == 1 and not frst_t:
            rectl.append(pre)
            rectl.append(i)
        pre = i
    rectl.append(lstv)
    frctl = []
    for _ in range(len(rectl) // 2):
        frctl.append([rectl[0][1], rectl[0][2], rectl[1][1], rectl[1][2]])
        rectl.remove(rectl[0])
        rectl.remove(rectl[0])
    return frctl


def drarect(data, image):
    clrs = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255), (255, 255, 0)]
    clr = random.choice(clrs)
    for i in data:
        cv2.rectangle(image, (int(i[0]), int(i[1])), (int(i[2]), int(i[3])), clr, 2)
    return image


def drapnt(data, image):
    fpl = []
    for i in data:
        xmin, ymin, xmax, ymax = int(i[0]), int(i[1]), int(i[2]), int(i[3])
        cv2.circle(image, (xmin, ymin), 1, (0, 177, 0), 2)
        cv2.circle(image, (xmax, ymin), 1, (0, 177, 0), 2)
        cv2.circle(image, (xmin, ymax), 1, (0, 177, 0), 2)
        cv2.circle(image, (xmax, ymax), 1, (0, 177, 0), 2)

        x1_midpoint = ((xmin + xmax) // 2, (ymin + ymin) // 2)
        x2_midpoint = ((xmin + xmax) // 2, (ymax + ymax) // 2)
        y1_midpoint = ((xmin + xmin) // 2, (ymin + ymax) // 2)
        y2_midpoint = ((xmax + xmax) // 2, (ymin + ymax) // 2)

        image = cv2.circle(image, x1_midpoint, 1, (0, 255, 0), 2)
        image = cv2.circle(image, x2_midpoint, 1, (0, 255, 0), 2)
        image = cv2.circle(image, y1_midpoint, 1, (0, 255, 0), 2)
        image = cv2.circle(image, y2_midpoint, 1, (0, 255, 0), 2)

        center_coord = int((xmin + xmax) / 2), int((ymin + ymax) / 2)
        image = cv2.circle(image, center_coord, 1, (0, 255, 0), 2)

        templ = [(xmin, ymin), x1_midpoint, (xmax, ymin), y1_midpoint, (xmax, ymax), x2_midpoint, (xmin, ymax),
                 y2_midpoint, center_coord]
        fpl.append(templ)

    return image, fpl


def srup(rl, sl):
    for i in rl:
        xmin, ymin, xmax, ymax = int(i[0]), int(i[1]), int(i[2]), int(i[3])
        center_coord = int((xmin + xmax) / 2), int((ymin + ymax) / 2)
        for j in sl:
            xmin, ymin, xmax, ymax = int(j[0]), int(j[1]), int(j[2]), int(j[3])
            if xmin < center_coord[0] < xmax and ymin < center_coord[1] < ymax:
                rl.remove(i)
                break
    return rl


def rup(wpl, vil, txtl):
    twpl = srup(wpl, vil)
    twpl = srup(twpl, txtl)
    return twpl


def get_spnt(fndlst):
    tl = []
    for i in fndlst:
        tl.append(i[0])
    stmp_elmnt = min(tl)
    for i in fndlst:
        if stmp_elmnt == i[0]:
            frstv, scndv = i[1], i[2]
    return frstv, scndv


vt_data = read_csv(INPUT_CSV)
# p_data = read_csv(POLYLINE_CSV)

vi = True
txt = False
pllin = False

vil = []
txtl = []
pllinl = []

for d in vt_data:
    if vi:
        if d[1] == "Shape":
            vi = False
            txt = True
            continue
        vil.append([d[1], d[2], d[3], d[4], d[5]])

    elif txt:
        if d[0] == "Polyline":
            txt = False
            pllin = True
            continue
        txtl.append([d[3], d[4], d[5], d[6], d[7]])

    elif pllin:
        pllinl.append([d[0], d[1], d[2]])

# pllinl = read_csv(POLYLINE_CSV)
fpl = sort_polyline(pllinl)

fwpl = rup(fpl, vil, txtl)
# sys.exit()
# print(vil)
# sys.exit()

image = cv2.imread(INPUT_IMAGE)
image = drarect(vil, image)
image = drarect(txtl, image)
image = drarect(fwpl, image)

image, point_vil = drapnt(vil, image)
image, point_txtl = drapnt(txtl, image)
image, point_fwpl = drapnt(fwpl, image)

coordinates = point_vil + point_txtl + point_fwpl

id_ = 0
id_list = []

flist_index = -1
slist_index = -1


def get_min_euclidean(flist, slist):
    sml_ed_pnts = []
    tl = []
    tl_index = []
    for i in flist:
        x1 = i[0]
        y1 = i[1]
        for j in slist:
            x2 = j[0]
            y2 = j[1]
            tl_index.append(((x1, y1), (x2, y2)))
            e_dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            tl.append([e_dist])
    return (min(tl), tl_index[tl.index(min(tl))])


i = 0
box_to_box = []

def create_box_to_box_list(i):
    list_i = 0
    min_box_list = []
    current_box = []
    min_box_index = []
    print(i)
    # while list_i < len(coordinates):
    while True:
        if i == len(coordinates) - 1 and list_i == len(coordinates) - 1:
            break

        if i == len(coordinates) - 1 and list_i == len(coordinates) - 2:
            min_box = get_min_euclidean(coordinates[i], coordinates[list_i])
            min_box_list.append(min_box)
            current_box.append(min_box[0])
            box_to_box.append(min_box_list[current_box.index(min(current_box))])
            i += 1
            break
        if list_i != i:
            min_box = get_min_euclidean(coordinates[i], coordinates[list_i])
            min_box_list.append(min_box)
            current_box.append(min_box[0])
            # min_box_index.append(list_i)

        if list_i == len(coordinates) - 1:
            box_to_box.append(min_box_list[current_box.index(min(current_box))])
            i += 1

            return
        list_i += 1

for x in range(len(coordinates)):
    create_box_to_box_list(x)

# box_to_box = set(box_to_box)
# print(type(box_to_box))
# print(box_to_box)
unique_box_to_box = []
count_of_coord = 0
for coord in box_to_box:
    coord_inv = (coord[0], (coord[1][1], coord[1][0]))
    if coord not in unique_box_to_box and coord_inv not in unique_box_to_box:
        unique_box_to_box.append(coord)

print(unique_box_to_box)

image = INPUT_IMAGE
for i in coordinates:
    cv2.rectangle(image, (i[0]), (i[4]), (255, 0, 0), 2)
for i in unique_box_to_box:
    print(i[1][0], i[1][1])
    cv2.putText(image, str(i[0]), (i[1][0]), 1, 1, (0, 0, 255))
    cv2.line(image, (i[1][0]), (i[1][1]), (0, 255, 0), 2)

cv2.imwrite("testing_suhailsir.jpg", image)
