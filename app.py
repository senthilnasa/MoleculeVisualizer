#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import vtk
import numpy as np
from pathlib import Path
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk as vtk_widgets, html

from utils.molecule_data import extract_molecule_data
from utils.visualization import (
    create_ball_stick_visualization,
    create_ribbon_visualization,
    apply_color_mapping
)

# -----------------------------------------------------------------------------
# Create server and initialize state
# -----------------------------------------------------------------------------
server = get_server()
state, ctrl = server.state, server.controller

# Initialize state variables
state.trame__title = "Molecular Visualization Tool"
state.view_style = "ball_stick"  # "ball_stick" or "ribbon"
state.color_mapping = "atom"     # "atom", "bfactor", or "residue"
state.molecule_info = {}
state.hover_info = "Hover over atoms to see details"
state.drawer = True
state.pdb_files = []
state.active_file = None
state.default_pdb = "https://files.rcsb.org/download/1CRN.pdb"  # Default PDB file

# VTK pipeline
state.default_opacity = 1.0
state.background_color = [0.1, 0.1, 0.1]

# -----------------------------------------------------------------------------
# VTK setup
# -----------------------------------------------------------------------------

# VTK rendering components
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# VTK pipeline elements
pdb_reader = vtk.vtkPDBReader()
picker = vtk.vtkCellPicker()
picker.SetTolerance(0.005)

# Setup view and callbacks
view = vtk_widgets.VtkLocalView(render_window)
ctrl.on_server_ready.add(view.update)
ctrl.view_update = view.update
ctrl.view_reset_camera = view.reset_camera

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def update_visualization():
    """Update visualization based on the current state"""
    if not state.active_file:
        return
    
    # Clean up the renderer
    renderer.RemoveAllViewProps()
    
    try:
        # Load PDB file
        pdb_reader.SetFileName(state.active_file)
        pdb_reader.Update()
        
        # Create visualization based on selected style
        if state.view_style == "ball_stick":
            actor = create_ball_stick_visualization(pdb_reader)
        else:  # ribbon
            actor = create_ribbon_visualization(pdb_reader)
        
        # Apply color mapping
        apply_color_mapping(actor, pdb_reader, state.color_mapping)
        
        # Add actor to renderer
        renderer.AddActor(actor)
        
        # Extract molecule data for display
        state.molecule_info = extract_molecule_data(pdb_reader)
        
        # Reset camera to see the whole molecule
        renderer.ResetCamera()
        ctrl.view_update()
    except Exception as e:
        print(f"Error loading PDB: {str(e)}")
        state.hover_info = f"Error: {str(e)}"

def load_default_pdb():
    """Load the default PDB file"""
    import urllib.request
    
    # Create a temp directory if it doesn't exist
    temp_dir = Path("./temp")
    temp_dir.mkdir(exist_ok=True)
    
    # Download the default PDB file
    default_pdb_path = temp_dir / "default.pdb"
    urllib.request.urlretrieve(state.default_pdb, default_pdb_path)
    
    # Set it as the active file and update visualization
    state.active_file = str(default_pdb_path)
    state.pdb_files.append({"name": "Default (1CRN)", "path": str(default_pdb_path)})
    update_visualization()

def handle_pick(picker, event):
    """Handle atom picking on hover"""
    cell_id = picker.GetCellId()
    if cell_id != -1:
        # Get information about the picked cell/atom
        dataset = picker.GetDataSet()
        point_id = dataset.GetCell(cell_id).GetPointId(0)
        atom_type = dataset.GetPointData().GetArray("atom_types").GetValue(point_id)
        atom_index = dataset.GetPointData().GetArray("atom_index").GetValue(point_id)
        residue = dataset.GetPointData().GetArray("residue").GetValue(point_id)
        bfactor = dataset.GetPointData().GetArray("bfactor").GetValue(point_id)
        
        # Update hover info
        info = (
            f"Atom: {atom_type} (ID: {int(atom_index)}), "
            f"Residue: {int(residue)}, B-Factor: {bfactor:.2f}"
        )
        state.hover_info = info
    else:
        state.hover_info = "Hover over atoms to see details"
    
    ctrl.view_update()

# -----------------------------------------------------------------------------
# UI state change callbacks
# -----------------------------------------------------------------------------

@state.change("view_style")
def update_view_style(view_style, **kwargs):
    update_visualization()

@state.change("color_mapping")
def update_color_style(color_mapping, **kwargs):
    update_visualization()

@state.change("active_file")
def update_active_file(active_file, **kwargs):
    update_visualization()

# -----------------------------------------------------------------------------
# File upload handling
# -----------------------------------------------------------------------------

def handle_file_upload(event):
    """Handle PDB file upload"""
    files = event.files
    if not files:
        return
    
    for file in files:
        # Create a temp directory if it doesn't exist
        temp_dir = Path("./temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Save the file
        filepath = temp_dir / file.name
        with open(filepath, "wb") as f:
            f.write(file.content)
        
        # Add to the list of PDB files
        file_info = {"name": file.name, "path": str(filepath)}
        state.pdb_files.append(file_info)
        
        # Automatically set as active file
        state.active_file = str(filepath)

# -----------------------------------------------------------------------------
# Web UI Definition
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    # Customize the toolbar
    layout.title.set_text("Molecular Visualization Tool")
    
    # Define drawer content
    with layout.drawer as drawer:
        drawer.width = 300
        with vuetify.VCard(elevation=0):
            with vuetify.VCardTitle():
                html.Div("Visualization Controls")
        
            with vuetify.VCardText():
                # Visualization style selector
                with vuetify.VSelect(
                    v_model=("view_style", "ball_stick"),
                    items=("style_options", [
                        {"text": "Ball and Stick", "value": "ball_stick"},
                        {"text": "Protein Ribbon", "value": "ribbon"},
                    ]),
                    label="Visualization Style",
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="mb-2",
                ):
                    pass
                
                # Color mapping selector
                with vuetify.VSelect(
                    v_model=("color_mapping", "atom"),
                    items=("color_options", [
                        {"text": "Atom", "value": "atom"},
                        {"text": "B-Factor", "value": "bfactor"},
                        {"text": "Residue", "value": "residue"},
                    ]),
                    label="Color Mapping",
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="mb-4",
                ):
                    pass
                
                # File upload
                with vuetify.VFileInput(
                    label="Upload PDB File",
                    outlined=True,
                    dense=True,
                    accept=".pdb",
                    hide_details=True,
                    classes="mb-4",
                    prepend_icon="mdi-file-upload",
                    on_change=handle_file_upload,
                ):
                    pass
                
                # PDB file selector (if multiple files uploaded)
                with vuetify.VSelect(
                    v_model=("active_file", None),
                    items=("pdb_files", []),
                    item_text="name",
                    item_value="path",
                    label="Select PDB File",
                    hide_details=True,
                    dense=True,
                    outlined=True,
                    classes="mb-4",
                ):
                    pass
                
                # Molecule info section
                with vuetify.VCard(
                    outlined=True,
                    classes="mb-4",
                ):
                    with vuetify.VCardTitle(classes="subtitle-2"):
                        html.Div("Molecule Information")
                    
                    with vuetify.VCardText():
                        html.Div("{{ hover_info }}", classes="body-2")
                
    # Main content
    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # 3D Visualization View
            html_view = vtk_widgets.VtkLocalView(
                view,
                picker=picker,
                picking_modes=["hover"],
                on_hover_pick=handle_pick,
            )
    
    # Footer
    with layout.footer:
        with vuetify.VFooter(app=True, color="#f5f5f5", height="36"):
            with vuetify.VContainer(classes="py-0"):
                html.Div(
                    "Molecular Visualization Tool - Powered by Trame & VTK",
                    classes="text-center grey--text text--darken-1",
                )

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    # Load the default PDB file when the app starts
    server.controller.on_server_ready.add(load_default_pdb)
    
    # Start the server
    server.start()
