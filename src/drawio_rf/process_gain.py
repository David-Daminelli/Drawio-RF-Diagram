import numpy as np
from .functions import Functions
funcs = Functions()

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
                ports = gain_port.split('-') # All ports passed. Last one is always output

                rows = []
                for p in ports:
                    rows += [df_circuit[
                    (df_circuit['block_id'] == block_id) &
                    (df_circuit['port_name'].str.contains(p))]]

                out_rows = rows[-1]

                powers = []
                for r in rows[:-1]:
                    if r.empty:
                        powers += [None]
                        continue
                    ipwr = r[param].iloc[0]
                    powers += [ipwr]

                if any(x is None for x in powers):
                    continue

                # Update all output powers
                if param == 'power':
                    sorted_power = np.sort(np.atleast_1d(np.array(powers[0])))
                    sorted_gain = np.sort(np.atleast_1d(np.array(gain_value)))
                    calc = (sorted_power + sorted_gain) + funcs.cable(components)
                elif param == 'frequency':
                    if isinstance(gain_value, list): # if value is list, so call the related function
                        calc = getattr(funcs, gain_value[0])(powers, gain_value[1])
                    else:
                        calc = (powers[0]*gain_value)

                mask = df_circuit['edge_id'].isin(out_rows['edge_id'])
                for idx in df_circuit[mask].index:
                    df_circuit.at[idx, param] = np.array(calc)

    if param == 'power':
        df_circuit['out_of_range'] = df_circuit.apply(
            lambda r: funcs.out_of_range(r[param], r['min'], r['max']),
            axis=1
        )

        edge_out_of_range = df_circuit.groupby('edge_id')['out_of_range'].any()
        df_circuit['out_of_range'] = df_circuit['edge_id'].map(edge_out_of_range)

    return df_circuit