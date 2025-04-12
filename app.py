from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html

import os
import tempfile

from ui.drawer import create_drawer
from ui.viewer import create_viewer
from visualizers.ball_and_stick import BallAndStickVisualizer
from visualizers.protein_ribbon import ProteinRibbonVisualizer
from colormappers.atom import AtomColorMapper
from colormappers.bfactor import BFactorColorMapper
from colormappers.residue import ResidueColorMapper

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

# Initialize server with Vue 2 for compatibility with trame-vuetify
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# Initial state
state.trame__title = "Molecule Visualizer"
state.visualization_style = "ball_and_stick"
state.color_mapping = "atom"
state.file_content = None
state.hover_info = ""
state.active_pdb_file = None
state.view_ball_and_stick = "<div>Ball and Stick view will appear here</div>"
state.view_protein_ribbon = "<div>Protein Ribbon view will appear here</div>"

# Available visualization styles and color mappers
visualization_styles = {
    "ball_and_stick": BallAndStickVisualizer(),
    "protein_ribbon": ProteinRibbonVisualizer(),
}

color_mappers = {
    "atom": AtomColorMapper(),
    "bfactor": BFactorColorMapper(),
    "residue": ResidueColorMapper(),
}

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

@ctrl.add("on_file_upload")
def on_file_upload(file_content=None, **kwargs):
    """Handle file upload and create visualization"""
    if not file_content:
        return
    
    # Create temporary file
    fd, filename = tempfile.mkstemp(suffix=".pdb")
    os.write(fd, file_content.encode())
    os.close(fd)
    
    state.active_pdb_file = filename
    update_visualization()

@ctrl.add("update_visualization_style")
def update_visualization_style(style=None):
    """Update visualization style"""
    if style:
        state.visualization_style = style
        update_visualization()

@ctrl.add("update_color_mapping")
def update_color_mapping(mapping=None):
    """Update color mapping"""
    if mapping:
        state.color_mapping = mapping
        update_visualization()

def update_visualization():
    """Update the visualization based on current state"""
    if not state.active_pdb_file:
        return
    
    # Get the current visualizer and color mapper
    visualizer = visualization_styles[state.visualization_style]
    color_mapper = color_mappers[state.color_mapping]
    
    # Create the visualization
    visualizer.create_visualization(
        state.active_pdb_file, 
        color_mapper=color_mapper,
        state=state,
        ctrl=ctrl
    )

# Load default PDB file if no file is uploaded
@ctrl.add("load_example")
def load_example():
    """Load example PDB file"""
    example_path = os.path.join(os.path.dirname(__file__), "static/examples/1cbs.pdb")
    if os.path.exists(example_path):
        state.active_pdb_file = example_path
        update_visualization()

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
        # Create drawer with controls
        create_drawer(
            None,
            visualization_styles=list(visualization_styles.keys()),
            color_mappings=list(color_mappers.keys()),
            state=state,
            ctrl=ctrl,
        )
    
    # Create main content
    with vuetify.VMain():
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            create_viewer(state, ctrl)
    
    # Add footer
    with vuetify.VFooter(app=True, height=36, color="grey lighten-4"):
        with html.Div(
            style="width: 100%; text-align: center; color: gray; font-size: 0.8em;"
        ):
            html.Span("Molecule Visualizer - Powered by Trame and VTK")
            html.Span("Hover Info: {{ hover_info }}", style="margin-left: 20px;")

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Start the server on port 5000 and listen on all interfaces (0.0.0.0)
    # for Replit compatibility
    server.start(port=5000, host="0.0.0.0")
