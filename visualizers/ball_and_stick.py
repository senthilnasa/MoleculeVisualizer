from trame.widgets import vtk as vtk_widgets
import vtk

# Use vtk directly instead of vtkmodules
vtkDataObject = vtk.vtkDataObject
vtkPDBReader = vtk.vtkPDBReader
vtkActor = vtk.vtkActor
vtkRenderer = vtk.vtkRenderer
vtkRenderWindow = vtk.vtkRenderWindow
vtkRenderWindowInteractor = vtk.vtkRenderWindowInteractor
vtkPolyDataMapper = vtk.vtkPolyDataMapper
vtkCellPicker = vtk.vtkCellPicker
vtkCommand = vtk.vtkCommand
vtkTransform = vtk.vtkTransform
vtkSphereSource = vtk.vtkSphereSource
vtkCylinderSource = vtk.vtkCylinderSource
vtkGlyphSource2D = vtk.vtkGlyphSource2D

import numpy as np

from .base import BaseVisualizer
from utils import extract_data_arrays

class BallAndStickVisualizer(BaseVisualizer):
    """Ball and Stick visualization style for PDB files"""
    
    def create_visualization(self, pdb_file, color_mapper=None, state=None, ctrl=None):
        """Create a Ball and Stick visualization of the PDB file"""
        # Create renderer and window
        renderer = vtkRenderer()
        renderWindow = vtkRenderWindow()
        renderWindow.AddRenderer(renderer)
        
        # PDB reader
        reader = vtkPDBReader()
        reader.SetFileName(pdb_file)
        reader.Update()
        
        # Get data arrays
        data_arrays = extract_data_arrays(reader)
        
        # Apply color mapping if provided
        if color_mapper:
            actor = color_mapper.apply_to_ball_and_stick(reader, renderer)
        else:
            # Default visualization
            sphereSource = vtkSphereSource()
            sphereSource.SetRadius(0.2)
            sphereSource.SetThetaResolution(20)
            sphereSource.SetPhiResolution(20)
            
            stick = vtkCylinderSource()
            stick.SetRadius(0.07)
            stick.SetResolution(10)
            
            # Ball mapper
            ballMapper = vtkPolyDataMapper()
            ballMapper.SetInputConnection(reader.GetOutputPort(0))
            
            # Stick mapper
            stickMapper = vtkPolyDataMapper()
            stickMapper.SetInputConnection(reader.GetOutputPort(1))
            
            # Ball actor
            ballActor = vtkActor()
            ballActor.SetMapper(ballMapper)
            
            # Stick actor
            stickActor = vtkActor()
            stickActor.SetMapper(stickMapper)
            
            # Add actors to renderer
            renderer.AddActor(ballActor)
            renderer.AddActor(stickActor)
            
        # Setup picker for interaction
        picker = vtkCellPicker()
        picker.SetTolerance(0.005)
        
        # Setup callback for hover
        def handle_mouse_move(obj, event):
            global_point = obj.GetEventPosition()
            result = picker.Pick(global_point[0], global_point[1], 0, renderer)
            
            if result != 0:
                picked_position = picker.GetPickPosition()
                cell_id = picker.GetCellId()
                
                if cell_id >= 0:
                    # Get atom info from picked cell
                    output = reader.GetOutput()
                    atoms = reader.GetAtoms()
                    
                    if atoms and cell_id < atoms.GetNumberOfTuples():
                        atom_name = atoms.GetValue(cell_id)
                        residue = reader.GetResidues().GetValue(cell_id)
                        chain = reader.GetChains().GetValue(cell_id)
                        element = reader.GetAtomType().GetValue(cell_id) if reader.GetAtomType() else "Unknown"
                        
                        info = f"Atom: {atom_name}, Residue: {residue}, Chain: {chain}, Element: {element}"
                        state.hover_info = info
                    else:
                        state.hover_info = f"Cell ID: {cell_id}"
                else:
                    state.hover_info = ""
            else:
                state.hover_info = ""
        
        # Set up interaction
        renderWindow.GetInteractor().AddObserver(vtkCommand.MouseMoveEvent, handle_mouse_move)
        
        # Reset camera
        renderer.ResetCamera()
        
        # Create simple HTML view reference for our wrapper
        view_html = f'<div id="vtk-view-ball-and-stick"></div>'
        
        # Update state with the view
        state.view_ball_and_stick = view_html
        
        return view_html
