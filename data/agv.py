values = []
with open("/home/pi/code/plug-control/data/data.csv", "r") as file:
    for line in file.readlines():
        values.append(float(line.split(";")[2]))


inter = 0.0
agv_values = []

pointer = 0

for value in values:
    if pointer < 30:
        inter += value
        pointer += 1
    elif pointer == 30:
        agv_values.append(round(inter/30, 2))
        inter = value
        pointer = 1

for val in agv_values:
    with open("/home/pi/code/plug-control/data/data2.csv", "a") as file: 
        file.write(f"{val}\n")

print(agv_values)


