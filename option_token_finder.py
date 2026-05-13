import json

with open(
    "OpenAPIScripMaster.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)

count = 0

for item in data:

    symbol = str(item.get("symbol", ""))

    if (
        "NIFTY" in symbol
        and "23800" in symbol
        and "CE" in symbol
    ):

        print("\nFOUND")

        print("SYMBOL :", symbol)

        print("TOKEN  :", item.get("token"))

        print("EXCHANGE:", item.get("exch_seg"))

        count += 1

        if count >= 20:

            break

print("\nTOTAL FOUND:", count)