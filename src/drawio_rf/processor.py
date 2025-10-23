import json
import pandas as pd
import numpy as np

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
            raise ValueError(f"Component '{value}' (id: {id}) not found in components.json")

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
                    "max" : components[value].get("max", {}).get(port_name, None),
                    "min" : components[value].get("min", {}).get(port_name, None),
                })


    df_circuit = pd.DataFrame(rows)

    circuit_comps = df_circuit['component'].unique()
    for c in circuit_comps:

        # set the power
        for s in components[c].get("set", {}).items():
            set_port  = s[0] # port that will be setted
            set_value = s[1] # value to set

            set_id = df_circuit.loc[(df_circuit['component'] == c) & (df_circuit['port_name'] == set_port), 'edge_id']
            df_circuit.loc[df_circuit['edge_id'].isin(set_id), 'power'] = set_value

        it_count = 0
        while df_circuit['power'].isna().any():
            for block_id in df_circuit['block_id'].unique():
                # Get the component type of this block
                comp = df_circuit.loc[df_circuit['block_id'] == block_id, 'component'].iloc[0]

                # Iterate over all gain definitions for this component
                for gain_port, gain_value in components[comp].get('gain', {}).items():
                    inp, out = gain_port.split('-')

                    # Find input power
                    inp_rows = df_circuit[
                        (df_circuit['block_id'] == block_id) &
                        (df_circuit['port_name'].str.contains(inp))
                    ]
                    if inp_rows.empty:
                        continue  # no input port found
                    inp_power = inp_rows['power'].iloc[0]
                    if inp_power is None:
                        continue  # ignore if input power not defined

                    # Find all output edges for this block
                    out_rows = df_circuit[
                        (df_circuit['block_id'] == block_id) &
                        (df_circuit['port_name'].str.contains(out))
                    ]

                    # Update all output powers
                    df_circuit.loc[df_circuit['edge_id'].isin(out_rows['edge_id']), 'power'] = inp_power + gain_value
                    it_count += 1
                    if it_count > 500:
                        raise RuntimeError("Exceeded maximum iterations while calculating powers. Possible open port.")
    df_circuit['out_of_range'] = np.where(
        (df_circuit['power'] > df_circuit['max']) | (df_circuit['power'] < df_circuit['min']),
        True,
        False
    )
    edge_out_of_range = df_circuit.groupby('edge_id')['out_of_range'].any()
    df_circuit['out_of_range'] = df_circuit['edge_id'].map(edge_out_of_range)

    return df_circuit
