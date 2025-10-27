def process_set(df_circuit, components, param):
    df_circuit = df_circuit.copy()
    circuit_comps = df_circuit['component'].unique()
    for c in circuit_comps:

        sets = components[c].get(f"set_{param}", {})

        # set the power
        for s in sets.items():
            set_port  = s[0] # port that will be setted
            set_value = s[1] # value to set

            set_id = df_circuit.loc[(df_circuit['component'] == c) & (df_circuit['port_name'] == set_port), 'edge_id']
            df_circuit.loc[df_circuit['edge_id'].isin(set_id), param] = set_value

    return df_circuit