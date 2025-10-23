import xml.etree.ElementTree as ET

def write_drawio(df_circuit, og_path, output_path=None):
    # Load existing draw.io XML structure
    if output_path is None:
        output_path = og_path

    tree = ET.parse(og_path)
    root = tree.getroot()

    # Map edge_id → power e out_of_range
    edge_power_dict = dict(zip(df_circuit['edge_id'], df_circuit['power']))
    edge_status_dict = dict(zip(df_circuit['edge_id'], df_circuit['out_of_range']))

    for cell in root.iter('mxCell'):
        if cell.get('edge') == '1':
            edge_id = cell.get('id')
            if edge_id in edge_power_dict:
                power_value = edge_power_dict[edge_id]
                is_out_of_range = edge_status_dict[edge_id]

                # Set label as power with "dBm"
                cell.set('value', f"{power_value} dBm")

                # Determine font color: red if out of range, green otherwise
                color = '#FF0000' if is_out_of_range else '#00AA00'

                # Update style: remove old fontColor/fontStyle and add new
                style = cell.get('style', '')
                style_parts = [s for s in style.split(';') if not s.startswith(('fontColor=', 'fontStyle='))]
                style_parts.append(f'fontColor={color}')
                style_parts.append('fontStyle=1')  # 1 = bold
                cell.set('style', ';'.join(style_parts))

    # Write the updated XML back to file
    tree.write(output_path)
    return df_circuit