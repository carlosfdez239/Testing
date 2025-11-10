from rich import print_json
import json
from pprint import pprint

with open("brother_drivers.json", "r", encoding="utf-8") as f:
    json_str = f.read()

print_json(json_str)





#with open("brother_drivers.json", "r", encoding="utf-8") as f:
#    data = json.load(f)

#pprint(data)