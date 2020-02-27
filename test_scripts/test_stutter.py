def destutter_coords(new_coords):
    while len(last_coords) > 6:
        last_coords.pop()
    last_coords.insert(0, "{}:{}".format(new_coords[0], new_coords[1]))
    print(last_coords)
    sums = {}
    for coords in last_coords:
        if sums.get(coords) is None:
            sums[coords] = 1
        else:
            sums[coords] = sums[coords] + 1
            if sums[coords] >= 4:
                spl = coords.split(":")
                c = (int(spl[0]), int(spl[1]))
                print("winner: {}".format(c))
    print("winner: {}".format(new_coords))
    return new_coords

last_coords = []
src = [
    (10, 10), 
    (10, 11),
    (10, 10),
    (10, 10),
    (11, 11),
    (12, 12),
    (13, 13),
    (13, 13),
    (18,12),
    (13, 13),
    (18,12),
    (13, 13),
    (13, 13),
    (13, 13),
    (18,12),
    (13, 13),
    (13, 13)
]
for c in src:
    destutter_coords(c)