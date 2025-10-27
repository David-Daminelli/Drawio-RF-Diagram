import numpy as np

def process_gain(df_circuit, components, param, it_lim = 500):
    it_count = 0
    df_circuit = df_circuit.copy()
    while df_circuit[param].isna().any():
        if it_count > it_lim:
            print("Exceeded maximum iterations while calculating powers. Possible open port.")
            break
        else:
            it_count += 1

        for block_id in df_circuit['block_id'].unique():
            # Get the component type of this block
            comp = df_circuit.loc[df_circuit['block_id'] == block_id, 'component'].iloc[0]
            gains = components[comp].get(f'gain_{param}', {})

            if (param == 'frequency') and (gains == {}):
                #print(f'{comp} has no frequency gain')
                gains = components[comp].get(f'gain_power', {}) # get the same power gains
                gains = {k: 1 for k in gains} # Set all frequency gains to 1

            # Iterate over all gain definitions for this component
            for gain_port, gain_value in gains.items():
                inp, out = gain_port.split('-')

                # Find input power
                inp_rows = df_circuit[
                    (df_circuit['block_id'] == block_id) &
                    (df_circuit['port_name'].str.contains(inp))
                ]
                if inp_rows.empty:
                    continue  # no input port found
                inp_power = inp_rows[param].iloc[0]
                if inp_power is None:
                    continue  # ignore if input power not defined

                # Find all output edges for this block
                out_rows = df_circuit[
                    (df_circuit['block_id'] == block_id) &
                    (df_circuit['port_name'].str.contains(out))
                ]

                # Update all output powers
                if param == 'power':
                    calc = (inp_power + gain_value)
                elif param == 'frequency':
                    calc = (inp_power*gain_value)
                df_circuit.loc[df_circuit['edge_id'].isin(out_rows['edge_id']), param] = calc

    if param == 'power':
        df_circuit['out_of_range'] = np.where(
            (df_circuit[param] > df_circuit['max']) | (df_circuit[param] < df_circuit['min']),
            True,
            False
        )
        edge_out_of_range = df_circuit.groupby('edge_id')['out_of_range'].any()
        df_circuit['out_of_range'] = df_circuit['edge_id'].map(edge_out_of_range)

    return df_circuit