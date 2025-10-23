import xml.etree.ElementTree as ET

def read_drawio(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    blocks = {}
    edges_list = []
    labels_dict = {}  # map from edge_id to list of labels

    for cell in root.iter('mxCell'):
        cell_id = cell.get('id')
        value = cell.get('value', None)
        style = cell.get('style', '')

        # Edge label: vertex=1 but style contains "edgeLabel" and has parent
        if cell.get('vertex') == '1' and "edgeLabel" in style and cell.get('parent'):
            parent_edge_id = cell.get('parent')
            labels_dict.setdefault(parent_edge_id, []).append(value)

        # Block (vertex, not an edge label)
        elif cell.get('vertex') == '1':
            blocks[cell_id] = {
                "value": value,
                "in": [],
                "out": []
            }

        # Edge / connection
        elif cell.get('edge') == '1':
            source = cell.get('source')
            target = cell.get('target')
            if source or target:
                edges_list.append({
                    "edge_id": cell_id,
                    "source": source,
                    "target": target
                })
                labels_dict.setdefault(cell_id, [])  # initialize empty label list

    # Populate "in" and "out" with labels
    for e in edges_list:
        edge_id = e["edge_id"]
        source_id = e["source"]
        target_id = e["target"]
        edge_labels = tuple(labels_dict.get(edge_id, []))

        if source_id in blocks:
            blocks[source_id]["out"].append([edge_id, target_id, edge_labels, None])
        if target_id in blocks:
            blocks[target_id]["in"].append([edge_id, source_id, edge_labels, None])

    return blocks
