# Molecular Visualizer - 3D Interactive Structure Viewer

**Muskan Aneja's Capstone Project**

## Project Overview

Molecular Visualizer is an interactive web-based platform for visualizing protein structures from Protein Data Bank (PDB) files. This tool allows researchers, students, and molecular biology enthusiasts to explore molecular structures in both 2D and 3D representations with various visualization styles and color mapping options.

## Key Features

- **3D Interactive Visualization**: Rotate, zoom, and pan to explore molecular structures from any angle
- **Multiple Visualization Styles**: 
  - Ball and Stick model 
  - Protein Ribbon model
- **Diverse Color Mapping Options**:
  - Element-based coloring (CPK coloring)
  - B-factor (temperature) coloring
  - Residue-based coloring
- **Interactive Atom Information**: Hover over atoms to view detailed information (element, residue, chain, B-factor, coordinates)
- **2D Projections**: Top view (X-Y plane) and side view (X-Z plane) for complementary visualization
- **File Upload**: Upload and visualize your own PDB files
- **Responsive Design**: Works on desktop and mobile devices

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: 
  - Three.js for 3D rendering
  - Vue.js and Vuetify for UI components
  - HTML5 Canvas for 2D visualization
- **Data Processing**: Custom PDB file parsing algorithms

## How to Use

1. Start the application with `python static_pdb_viewer.py`
2. Open http://localhost:5000 in your browser
3. Click "Load Example Structure" or upload your own PDB file
4. Use mouse controls to interact with the 3D view:
   - Left-click + drag: Rotate the molecule
   - Right-click + drag: Pan the view
   - Scroll wheel: Zoom in/out
5. Try different visualization styles and color mappings using the dropdown options
6. Hover over atoms to see detailed information
7. Click the fullscreen button for a more immersive experience

## Future Enhancements

- Support for more visualization styles (Space-filling, Wireframe)
- Molecular surface visualization
- Distance and angle measurement tools
- Ligand highlighting
- Animation capabilities for dynamics visualization
- Export options for images and 3D models

## License

Open source for educational and research purposes.

## Project Structure

```
/ (root)
├── static/                  # Static assets
│   ├── css/                 # CSS stylesheets
│   ├── js/                  # JavaScript files
│   │   ├── 3d_visualizer.js # Three.js based 3D visualization
│   │   └── simple_visualizer.js # 2D canvas visualization
│   ├── lib/                 # Third-party libraries
│   └── examples/            # Example PDB files
├── templates/               # HTML templates
│   └── index.html           # Main application page
└── static_pdb_viewer.py     # Flask application
```