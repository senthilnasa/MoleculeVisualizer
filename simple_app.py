import os
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html

# Define server
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# State
state.trame__title = "Simple PDB Viewer"
state.pdb_content = ""
state.file_name = ""
state.molecule_info = {
    "atoms": 0,
    "residues": 0,
    "chains": 0,
}

# Functions
def load_example_pdb():
    """Load example PDB file"""
    print("Loading example PDB...")
    example_path = os.path.join(os.path.dirname(__file__), "static/examples/1cbs.pdb")
    if os.path.exists(example_path):
        with open(example_path, 'r') as f:
            pdb_content = f.read()
        
        state.file_name = "1cbs.pdb"
        state.pdb_content = pdb_content
        
        # Count basic info
        lines = pdb_content.splitlines()
        atoms = 0
        residues = set()
        chains = set()
        
        for line in lines:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                atoms += 1
                try:
                    residue_id = line[22:27].strip()
                    chain_id = line[21]
                    residues.add(residue_id + chain_id)
                    chains.add(chain_id)
                except:
                    pass
        
        state.molecule_info["atoms"] = atoms
        state.molecule_info["residues"] = len(residues)
        state.molecule_info["chains"] = len(chains)
        print(f"Loaded PDB with {atoms} atoms, {len(residues)} residues, {len(chains)} chains")
    else:
        print(f"Example file not found: {example_path}")

# Register function
ctrl.on_server_ready.add(lambda **_: print("Server is ready!"))
ctrl.add("load_example", load_example_pdb)

# GUI
with SinglePageLayout(server) as layout:
    layout.title.set_text("Simple PDB Viewer")
    
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VBtn("Load Example PDB", click=load_example_pdb)
        vuetify.VSpacer()
    
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-8"):
            with vuetify.VRow():
                with vuetify.VCol(cols=12):
                    with vuetify.VCard():
                        vuetify.VCardTitle("PDB Information")
                        with vuetify.VCardText():
                            with html.Div(v_if="file_name"):
                                html.H3("{{ file_name }}")
                                html.P("Atoms: {{ molecule_info.atoms }}")
                                html.P("Residues: {{ molecule_info.residues }}")
                                html.P("Chains: {{ molecule_info.chains }}")
                            with html.Div(v_else=True):
                                html.P("No PDB file loaded. Click 'Load Example PDB' to view a sample file.")
            
            with vuetify.VRow(v_if="pdb_content"):
                with vuetify.VCol(cols=12):
                    with vuetify.VCard():
                        vuetify.VCardTitle("PDB Content")
                        with vuetify.VCardText():
                            vuetify.VTextarea(
                                v_model=("pdb_content"),
                                readonly=True,
                                filled=True,
                                auto_grow=False,
                                rows=20,
                                style="font-family: monospace;"
                            )

if __name__ == "__main__":
    server.start(port=5000, host="0.0.0.0")