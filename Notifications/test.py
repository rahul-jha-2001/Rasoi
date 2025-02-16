from collections import defaultdict

def _destructure_variables(variables: dict):
    variable = defaultdict(list)

    for k, v in variables.items():
        if k.startswith("BODY"):
            variable["BODY"].append((k.split("_")[1], v))
        elif k.startswith("HEADER"):
            variable["HEADER"].append((k.split("_")[1], v))
        elif k.startswith("BUTTON"):
            variable["BUTTON"].append((k.split("_")[1], v))

    for i in variable:
        variable[i] = [v for _, v in sorted(variable[i], key=lambda x: x[0])]
    
    return variable

print(destructure_variables({"BODY_3": "BODY_3",
                        "BODY_2": "BODY_2",
                        "BUTTON_0": "BUTTON_0",
                        "BUTTON_1": "BUTTON_1",
                        "HEADER_1": "HEADER_1"}))

