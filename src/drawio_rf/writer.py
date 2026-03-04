import xml.etree.ElementTree as ET
from engineering_notation import EngNumber as eng
import numpy as np

def write_drawio(df_circuit, og_path, output_path=None):
    if output_path is None:
        output_path = og_path

    tree = ET.parse(og_path)
    root = tree.getroot()

    # Create a lookup dictionary for edges
    df_edges = (
        df_circuit
        .drop_duplicates(subset=['edge_id'])
        .set_index('edge_id')
        [['power', 'unit', 'out_of_range', 'frequency']]
    )

    for cell in root.iter('mxCell'):
        if cell.get('edge') == '1':
            edge_id = cell.get('id')
            if edge_id in df_edges.index:
                row = df_edges.loc[edge_id]

                power_value = row.get('power')
                power_unit = row.get('unit', 'dBm')
                is_out_of_range = row.get('out_of_range', False)
                freq_value = row.get('frequency')

                # Define power color
                color = '#FF0000' if is_out_of_range else '#00AA00'  # vermelho ou verde


                power_value = np.atleast_1d(power_value)
                try:
                    power_str = "".join(f"{p:.2f} " for p in power_value)
                    if power_value.size > 1:
                        power_str = f'[{power_str.strip()}]{power_unit}' #if power_str != "" else "NaN"
                    else:
                        power_str = f'{power_str.strip()}{power_unit}'
                except:
                    power_str = "NaN"

                freq_value = np.atleast_1d(freq_value)
                try:
                    freq_str = "".join(f"{eng(f, precision=3)}Hz\n" if not np.isnan(f) else "NaN" for f in freq_value)
                except:
                    freq_str = "NaN"

                # Final text using HTML
                cell.set('value',
                         f"<span style='color:{color}'>{power_str}</span>"
                         + (f"<br><span style='color:#0000FF'>{freq_str}</span>" if freq_str else "")
                        )

                # Update style
                style = cell.get('style', '')
                style_parts = [s for s in style.split(';') if not s.startswith(('fontColor=', 'fontStyle='))]
                style_parts.append(f'fontColor={color}')
                style_parts.append('fontStyle=1')
                cell.set('style', ';'.join(style_parts))

    tree.write(output_path)
    return df_circuit
