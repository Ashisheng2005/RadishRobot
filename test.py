with open("./requirements.txt", "r", encoding="utf-8") as f:
    data = f.read()
    for i in data.split("\n"):
        print(f"\"{i}\",")