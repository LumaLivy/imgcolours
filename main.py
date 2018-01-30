# Main code adapted from http://charlesleifer.com/blog/using-python-and-k-means-to-find-the-dominant-colors-in-images/

from collections import namedtuple
import math
import random
from PIL import Image

#SET THESE VALUES FOR YOUR OWN SYSTEM!!!

#depending on your system, you might only have to change the spot that says 'hydro' with your name. This will create a new colour scheme called "dynamic"
terminal_path = "/home/hydro/.local/share/xfce4/terminal/colorschemes/dynamic.txt"

scale = 64; #this is how big each square is in the colour palette image output

#don't touch anything below this line unless you know what you're doing

#This is the beginning of the borrowed colour script:

Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))

def get_points(img):
    points = []
    w, h = img.size
    for count, color in img.getcolors(w * h):
        points.append(Point(color, 3, count))
    return points

rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))

def colorz(filename, n):
    img = Image.open(filename)
    img.thumbnail((200, 200))
    w, h = img.size

    points = get_points(img)
    clusters = kmeans(points, n, 1)
    rgbs = [map(int, c.center.coords) for c in clusters]
    return map(rtoh, rgbs)

def euclidean(p1, p2):
    return (sum([
        (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
    ]))

def calculate_center(points, n):
    vals = [0.0 for i in range(n)]
    plen = 0
    for p in points:
        plen += p.ct
        for i in range(n):
            vals[i] += (p.coords[i] * p.ct)
    return Point([(v / plen) for v in vals], n, 1)

def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]

    while True:
        plists = [[] for i in range(k)]

        for p in points:
            smallest_distance = float('Inf')
            for i in range(k):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i
            plists[idx].append(p)

        diff = 0
        for i in range(k):
            old = clusters[i]
            center = calculate_center(plists[i], old.n)
            new = Cluster(plists[i], center, old.n)
            clusters[i] = new
            diff = max(diff, euclidean(old.center, new.center))

        if diff < min_diff:
            break

    return clusters

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

#now to adapt the data to xfce4

#main program

filename = input("File Path: ")
num_colours = int(input("How Many Colours? "))
show_palette = bool(input("Show palette? ")) #I know this doesn't work

list_colours_hex = list(colorz(filename, num_colours))
list_colours_rgb = list_colours_hex

palette = list_colours_hex

for i in range(len(list_colours_hex)):

    rgb = hex_to_rgb(list_colours_hex[i])

    r = str(rgb[0])
    g = str(rgb[1])
    b = str(rgb[2])

    string = "rgb(" + r + "," + g + "," + b + ");"

    palette[i] = [rgb, list_colours_hex[i], string]

palette.sort(key=lambda i: sum(i[0])/3)

image_palette = []

# the list for the actual pixels
for i in range(len(palette)):
    for j in range(scale * scale):
        image_palette.append(palette[i][0])

for colour in palette:
    print(colour[0],"Hex:", colour[1])

# Show the image
if show_palette:
    out_image = Image.new("RGB", (scale, num_colours * scale), "#FFFFFF")
    out_image.putdata(list(image_palette[i] for i in range(len(image_palette))))
    out_image.show()

#change terminal colours

with open(terminal_path, 'r') as file:
    term_data = file.readlines()

print(palette)

#foreground
term_data[2] = "ColorForeground=" + palette[len(palette) - 1][1] + "\n"

#background
term_data[3] = "ColorBackground=" + palette[0][1] + "\n"

#palette

#works but slow and colours might blend in with each other

term_data[4] = "ColorPalette=" + "".join(palette[i + math.ceil(num_colours / 2)][2] for i in range(num_colours - math.ceil(num_colours / 2)) for j in range(math.ceil(32 / num_colours)))


#idea: sort colours into closest match to each default terminal colour and add a custom ordered string that way

with open(terminal_path, 'w') as file:
    for line in term_data:
        file.write("%s" % line)
