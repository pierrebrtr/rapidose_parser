import glob, os
import json

os.chdir("data/")
count = 0
for file in glob.glob("*.json"):
    print(os.path.splitext(file)[0])
    f = open(file)
    json_array = json.load(f)
    if len(json_array) > 15:
        print("Had to split")
        count += 1
    chunkSize = 15

    for i in range(0, len(json_array), chunkSize):
        filename = f"{os.path.splitext(file)[0]}_{str(i // chunkSize)}"
        with open(
            f"./splitted/{filename}.json",
            "w",
        ) as f:
            json.dump(json_array[i : i + chunkSize], f)

print(count)