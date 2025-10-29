import drawio_rf
import os

BASE_DIR =  os.path.dirname(os.path.abspath(__file__))

file = os.path.join(BASE_DIR, "..", 'example', 'example.xml')
components = os.path.join(BASE_DIR, "..", 'db', 'example.json')

drawio_rf.reset_drawio(file)
circuit_df = drawio_rf.compute_drawio(file,json=components)
