import json

from modules.get_path import load_file


def get_targets():
    json_data = json.loads(open(load_file("resources//targets.json")).read())
    targets_list = []
    for v in json_data:
        for t in json_data[v]:
            if t != "name":
                for m in json_data[v][t]:
                    current_target = f"{v}.{t}.{m}"
                    if "tx" not in current_target:
                        targets_list.append(current_target)
    return targets_list
