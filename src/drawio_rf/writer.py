import xml.etree.ElementTree as ET
from engineering_notation import EngNumber as eng
import numpy as np

def write_drawio(df_circuit, og_path, output_path=None):
    if output_path is None:
        output_path = og_path

    tree = ET.parse(og_path)
    root = tree.getroot()

    # Map edge_id → power, out_of_range e frequency
    edge_power_dict = dict(zip(df_circuit['edge_id'], df_circuit['power']))
    edge_status_dict = dict(zip(df_circuit['edge_id'], df_circuit['out_of_range']))
    edge_freq_dict = dict(zip(df_circuit['edge_id'], df_circuit['frequency']))

    for cell in root.iter('mxCell'):
        if cell.get('edge') == '1':
            edge_id = cell.get('id')
            if edge_id in edge_power_dict:
                power_value = edge_power_dict[edge_id]
                is_out_of_range = edge_status_dict.get(edge_id, False)
                freq_value = edge_freq_dict.get(edge_id, None)

                # Define power color
                color = '#FF0000' if is_out_of_range else '#00AA00'  # vermelho ou verde

                # Set values to Nan in case of errors
                try:
                    power_str = f"{power_value:.2f}dBm"
                except:
                    power_str = "NaN"

                freq_value = np.atleast_1d(freq_value)
                freq_str = "".join(f"{eng(f, precision=3)}Hz\n" for f in freq_value)

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
