import json
import pandas as pd
import numpy as np
from .process_gain import process_gain
from .process_set import process_set

def read_json(file):
    # if file is a string load json from path
    if isinstance(file, str):
        with open(file, "r") as f:
            return json.load(f)
    return file

def build_df(blocks, json_path):
    components = read_json(json_path)

    rows = []  # list of rows to build DF

    for id in blocks:
        value = blocks[id]["value"]

        if value not in components:
            if value != "":
                print(f"Component '{value}' (id: {id}) not found in components.json")
            continue

        ports = components[value]["ports"]

        # assign connections to ports
        for pt in ports:  # for each port type
            pc = ports[pt]  # port count / expected labels

            if not isinstance(pc, list):
                pc = [pc, []]

            actual_count = len(blocks[id][pt])
            if actual_count != pc[0]:
                raise ValueError(
                    f"Component '{value}' (id: {id}) port '{pt}' expects {pc[0]} connections, found {actual_count}"
                )

            n = 0  # port instance counter
            for con in blocks[id][pt]:
                blabels = con[2]  # labels from the blocks
                clabels = pc[1]   # expected labels from the components.json

                match = [exp for exp in blabels if exp in clabels]
                match_count = len(match)

                if match_count > 1:
                    raise ValueError(
                        f"Component '{value}' (id: {id}) port '{pt}' has multiple matching labels {match} in connection {con}"
                    )
                elif match_count == 1:
                    port_name = match[0]
                elif match_count == 0:
                    # if there is only 1 expected port, use the base name
                    port_name = pt if pc[0] == 1 else f"{pt}_{n}"
                    n += 1

                # add DF row
                rows.append({
                    "block_id"  : id,
                    "component" : value,
                    "port_name" : port_name,
                    "edge_id"   : con[0],
                    "connected_block": con[1],
                    "power"     : con[3],
                    "frequency" : None,
                    "max" : components[value].get("max", {}).get(port_name, None),
                    "min" : components[value].get("min", {}).get(port_name, None),
                    "price": components[value].get("price", {}),
                    "current": components[value].get("current", 0),
                    "voltage": components[value].get("voltage", 0),
                })


    df_circuit = pd.DataFrame(rows)

    for param in ["power", "frequency"]:
        #df_circuit[param] = df_circuit[param].astype(object)
        df_circuit = process_set(df_circuit, components, param=param)
        df_circuit = process_gain(df_circuit, components, param=param)

    return df_circuit
