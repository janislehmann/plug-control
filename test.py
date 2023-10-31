
with open("state.txt", "r") as file:
    print(file.read())
    file.close()

with open("state.txt", "w") as file:
    file.write("test")
    file.close()

with open("state.txt", "r") as file:
    print(file.read())
    file.close()