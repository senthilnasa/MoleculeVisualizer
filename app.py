import os
import tempfile
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

# Initialize server with Vue 2 for compatibility with trame-vuetify
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# Initial state
state.trame__title = "Molecule Visualizer"
state.visualization_style = "text_view"
state.file_content = None
state.pdb_content = ""
state.active_pdb_file = None
state.file_name = ""
state.molecule_info = {
    "atoms": 0,
    "residues": 0,
    "chains": 0
}

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

@ctrl.add("on_file_upload")
def on_file_upload(file_content=None, **kwargs):
    """Handle file upload and parse PDB content"""
    if not file_content:
        return
    
    # Create temporary file
    fd, filename = tempfile.mkstemp(suffix=".pdb")
    os.write(fd, file_content.encode())
    os.close(fd)
    
    state.active_pdb_file = filename
    state.file_name = os.path.basename(filename)
    
    # Read the PDB file
    with open(filename, 'r') as f:
        pdb_content = f.read()
    
    # Update state
    state.pdb_content = pdb_content
    
    # Parse basic PDB info
    parse_pdb_info(pdb_content)

def parse_pdb_info(pdb_content):
    """Parse basic information from PDB file"""
    lines = pdb_content.splitlines()
    
    # Count atoms, residues, and chains
    atoms = 0
    residues = set()
    chains = set()
    
    for line in lines:
        if line.startswith("ATOM") or line.startswith("HETATM"):
            atoms += 1
            residue_id = line[22:27].strip()  # residue sequence number and insertion code
            chain_id = line[21]  # chain identifier
            
            residues.add(residue_id + chain_id)
            chains.add(chain_id)
    
    # Update molecule info
    state.molecule_info = {
        "atoms": atoms,
        "residues": len(residues),
        "chains": len(chains)
    }

# Load default PDB file if no file is uploaded
@ctrl.add("load_example")
def load_example():
    """Load example PDB file"""
    example_path = os.path.join(os.path.dirname(__file__), "static/examples/1cbs.pdb")
    if os.path.exists(example_path):
        with open(example_path, 'r') as f:
            file_content = f.read()
        
        state.active_pdb_file = example_path
        state.file_name = "1cbs.pdb"
        state.pdb_content = file_content
        
        # Parse basic PDB info
        parse_pdb_info(file_content)

# -----------------------------------------------------------------------------
# UI setup
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    # Set page title
    layout.title.set_text("Molecule Visualizer")
    
    # Create a sidebar for controls
    with vuetify.VNavigationDrawer(
        app=True,
        clipped=True,
        width=300,
        v_model=("drawer_open", True),
    ):
        # Drawer controls
        with vuetify.VContainer(classes="fill-height"):
            with vuetify.VRow(classes="mb-4"):
                vuetify.VCard(
                    classes="mx-auto",
                    elevation=2,
                    outlined=True,
                    width="100%",
                    children=[
                        vuetify.VCardTitle("Upload PDB File"),
                        vuetify.VCardText(
                            children=[
                                vuetify.VFileInput(
                                    label="Select PDB file",
                                    prepend_icon="mdi-file-document",
                                    on_change=("on_file_upload", "(value) => value"),
                                ),
                                vuetify.VBtn(
                                    "Load Example (1cbs.pdb)",
                                    color="primary",
                                    classes="mt-2",
                                    block=True,
                                    on_click=load_example,
                                ),
                            ]
                        ),
                    ],
                )
            
            # Show molecule info
            if_template = "molecule_info.atoms > 0"
            with vuetify.VRow(classes="mb-4", v_if=(if_template)):
                vuetify.VCard(
                    classes="mx-auto",
                    elevation=2,
                    outlined=True,
                    width="100%",
                    children=[
                        vuetify.VCardTitle("Molecule Information"),
                        vuetify.VCardText(
                            children=[
                                html.Div(children=[
                                    html.P("File: {{ file_name }}"),
                                    html.P("Atoms: {{ molecule_info.atoms }}"),
                                    html.P("Residues: {{ molecule_info.residues }}"),
                                    html.P("Chains: {{ molecule_info.chains }}"),
                                ]),
                            ]
                        ),
                    ],
                )
    
    # Create main content
    with vuetify.VMain():
        with vuetify.VContainer(fluid=True, classes="pa-4 fill-height"):
            # Welcome message when no file is loaded
            with html.Div(
                v_if=("!active_pdb_file"),
                style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; width: 80%;"
            ):
                html.H3("Welcome to Molecule Visualizer")
                html.P("Upload a PDB file or load the example to get started")
                vuetify.VIcon("mdi-molecule", size="100", color="primary")
                
            # PDB content viewer
            with html.Div(v_if=("active_pdb_file"), style="height: 100%; width: 100%;"):
                with vuetify.VCard(height="100%", outlined=True):
                    vuetify.VCardTitle("{{ file_name }}")
                    with vuetify.VCardText(style="height: calc(100% - 60px);"):
                        vuetify.VTextarea(
                            v_model=("pdb_content", ""), 
                            readonly=True,
                            filled=True,
                            auto_grow=False,
                            rows=20,
                            style="font-family: monospace; height: 100%; width: 100%;"
                        )
    
    # Add footer
    with vuetify.VFooter(app=True, height=36, color="grey lighten-4"):
        with html.Div(
            style="width: 100%; text-align: center; color: gray; font-size: 0.8em;"
        ):
            html.Span("Molecule Visualizer - Powered by Trame")

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Start the server on port 5000 and listen on all interfaces (0.0.0.0)
    # for Replit compatibility
    server.start(port=5000, host="0.0.0.0")
