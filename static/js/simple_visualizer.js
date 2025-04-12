/**
 * A simpler 2D PDB Visualizer for the molecular structures
 * 
 * Features:
 * - Renders atoms with proper colors
 * - Shows bonds between nearby atoms
 * - Provides top view (X-Y) and side view (X-Z) projections
 * - Handles window resizing for responsive display
 */

// Global variables for responsive visualization
let currentTopAtoms = [];
let currentSideAtoms = [];
let currentBondsTop = [];
let currentBondsSide = [];
let canResize = false;

// Responsive visualization - redraw when window is resized
window.addEventListener('resize', function() {
    if (canResize && currentTopAtoms.length > 0) {
        drawMoleculeTopView('topViewCanvas', currentTopAtoms, currentBondsTop);
        drawMoleculeSideView('sideViewCanvas', currentSideAtoms, currentBondsSide);
    }
});

// Function to create a static top view of the molecule
function createTopView(pdbData, canvasId) {
    // Parse the PDB data to extract coordinates
    const atoms = parsePdbAtoms(pdbData);
    console.log(`Parsed ${atoms.length} atoms for static rendering`);
    
    // Store for responsive redrawing
    currentTopAtoms = atoms;
    
    // Calculate bonds between atoms
    const bonds = calculateBonds(atoms, 3.0); // 3Å threshold for bonds
    currentBondsTop = bonds;
    
    // Draw the molecule
    drawMoleculeTopView(canvasId, atoms, bonds);
    
    // Enable responsive redrawing
    canResize = true;
}

// Function to draw the molecule in top view (separating calculation from drawing)
function drawMoleculeTopView(canvasId, atoms, bonds) {
    // Get the canvas and drawing context
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Could not get canvas context');
        return;
    }
    
    // Clear canvas and set background
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw title
    ctx.fillStyle = '#000000';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Top View (X-Y Projection)', canvas.width / 2, 20);
    
    // Calculate the bounds of the molecule
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    
    for (const atom of atoms) {
        minX = Math.min(minX, atom.x);
        maxX = Math.max(maxX, atom.x);
        minY = Math.min(minY, atom.y);
        maxY = Math.max(maxY, atom.y);
    }
    
    // Calculate scale to fit canvas (with some padding)
    const padding = 40;
    const scaleX = (canvas.width - padding * 2) / (maxX - minX);
    const scaleY = (canvas.height - padding * 2) / (maxY - minY);
    const scale = Math.min(scaleX, scaleY) * 0.8;
    
    // Store transformed coordinates for bonds
    const transformedCoords = {};
    
    // First: Draw bonds
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#cccccc';
    
    for (const bond of bonds) {
        const atom1 = atoms[bond.atom1];
        const atom2 = atoms[bond.atom2];
        
        const x1 = (atom1.x - minX) * scale + padding;
        const y1 = (atom1.y - minY) * scale + padding;
        const x2 = (atom2.x - minX) * scale + padding;
        const y2 = (atom2.y - minY) * scale + padding;
        
        // Store coords for atom drawing
        transformedCoords[bond.atom1] = {x: x1, y: y1};
        transformedCoords[bond.atom2] = {x: x2, y: y2};
        
        // Draw the bond
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
    }
    
    // Second: Draw atoms on top of bonds
    for (let i = 0; i < atoms.length; i++) {
        const atom = atoms[i];
        
        // Use precomputed coordinates if available (from bond drawing)
        let x, y;
        if (transformedCoords[i]) {
            x = transformedCoords[i].x;
            y = transformedCoords[i].y;
        } else {
            x = (atom.x - minX) * scale + padding;
            y = (atom.y - minY) * scale + padding;
        }
        
        // Set circle size based on atom type
        let radius = 4;  // Increased base size
        if (atom.element === 'C') radius = 4;
        else if (atom.element === 'N') radius = 4.5;
        else if (atom.element === 'O') radius = 4.5;
        else if (atom.element === 'S') radius = 5;
        else if (atom.element === 'P') radius = 5;
        else radius = 4;
        
        // Set color based on atom type
        ctx.fillStyle = getAtomColor(atom.element);
        
        // Draw the atom
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        
        // Add a slight outline for better visibility
        ctx.strokeStyle = 'rgba(0,0,0,0.3)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
    }
}

// Function to create a static side view of the molecule
function createSideView(pdbData, canvasId) {
    // Parse the PDB data to extract coordinates
    const atoms = parsePdbAtoms(pdbData);
    console.log(`Parsed ${atoms.length} atoms for side view rendering`);
    
    // Store for responsive redrawing
    currentSideAtoms = atoms;
    
    // Calculate bonds between atoms
    const bonds = calculateBonds(atoms, 3.0); // 3Å threshold for bonds
    currentBondsSide = bonds;
    
    // Draw the molecule
    drawMoleculeSideView(canvasId, atoms, bonds);
}

// Function to draw the molecule in side view (separating calculation from drawing)
function drawMoleculeSideView(canvasId, atoms, bonds) {
    // Get the canvas and drawing context
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Could not get canvas context');
        return;
    }
    
    // Clear canvas and set background
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw title
    ctx.fillStyle = '#000000';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Side View (X-Z Projection)', canvas.width / 2, 20);
    
    // Calculate the bounds of the molecule
    let minX = Infinity, maxX = -Infinity;
    let minZ = Infinity, maxZ = -Infinity;
    
    for (const atom of atoms) {
        minX = Math.min(minX, atom.x);
        maxX = Math.max(maxX, atom.x);
        minZ = Math.min(minZ, atom.z);
        maxZ = Math.max(maxZ, atom.z);
    }
    
    // Calculate scale to fit canvas (with some padding)
    const padding = 40;
    const scaleX = (canvas.width - padding * 2) / (maxX - minX);
    const scaleZ = (canvas.height - padding * 2) / (maxZ - minZ);
    const scale = Math.min(scaleX, scaleZ) * 0.8;
    
    // Store transformed coordinates for bonds
    const transformedCoords = {};
    
    // First: Draw bonds
    ctx.lineWidth = 1;
    ctx.strokeStyle = '#cccccc';
    
    for (const bond of bonds) {
        const atom1 = atoms[bond.atom1];
        const atom2 = atoms[bond.atom2];
        
        const x1 = (atom1.x - minX) * scale + padding;
        const y1 = (atom1.z - minZ) * scale + padding;
        const x2 = (atom2.x - minX) * scale + padding;
        const y2 = (atom2.z - minZ) * scale + padding;
        
        // Store coords for atom drawing
        transformedCoords[bond.atom1] = {x: x1, y: y1};
        transformedCoords[bond.atom2] = {x: x2, y: y2};
        
        // Draw the bond
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();
    }
    
    // Second: Draw atoms on top of bonds
    for (let i = 0; i < atoms.length; i++) {
        const atom = atoms[i];
        
        // Use precomputed coordinates if available (from bond drawing)
        let x, y;
        if (transformedCoords[i]) {
            x = transformedCoords[i].x;
            y = transformedCoords[i].y;
        } else {
            x = (atom.x - minX) * scale + padding;
            y = (atom.z - minZ) * scale + padding;
        }
        
        // Set circle size based on atom type
        let radius = 4;  // Increased base size
        if (atom.element === 'C') radius = 4;
        else if (atom.element === 'N') radius = 4.5;
        else if (atom.element === 'O') radius = 4.5;
        else if (atom.element === 'S') radius = 5;
        else if (atom.element === 'P') radius = 5;
        else radius = 4;
        
        // Add small adjustment for depth effect (based on Y position)
        const depthFactor = 0.5 + 0.5 * (atom.y - Math.min(...atoms.map(a => a.y))) / 
                              (Math.max(...atoms.map(a => a.y)) - Math.min(...atoms.map(a => a.y)));
        radius *= depthFactor;
        
        // Set color based on atom type
        ctx.fillStyle = getAtomColor(atom.element);
        
        // Draw the atom
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        
        // Add a slight outline for better visibility
        ctx.strokeStyle = 'rgba(0,0,0,0.3)';
        ctx.lineWidth = 0.5;
        ctx.stroke();
    }
}

// Function to calculate bonds between atoms based on distance
function calculateBonds(atoms, threshold) {
    const bonds = [];
    
    // Calculate bonds (simple distance-based approach)
    for (let i = 0; i < atoms.length; i++) {
        for (let j = i + 1; j < atoms.length; j++) {
            const atom1 = atoms[i];
            const atom2 = atoms[j];
            
            // Calculate 3D distance
            const dx = atom1.x - atom2.x;
            const dy = atom1.y - atom2.y;
            const dz = atom1.z - atom2.z;
            const distance = Math.sqrt(dx*dx + dy*dy + dz*dz);
            
            // If atoms are close enough, they're bonded
            if (distance < threshold) {
                bonds.push({
                    atom1: i,
                    atom2: j,
                    distance: distance
                });
            }
        }
    }
    
    return bonds;
}

// Helper function to parse PDB data
function parsePdbAtoms(pdbData) {
    const atoms = [];
    const lines = pdbData.split('\n');
    
    for (const line of lines) {
        if (line.startsWith('ATOM') || line.startsWith('HETATM')) {
            try {
                const x = parseFloat(line.substring(30, 38));
                const y = parseFloat(line.substring(38, 46));
                const z = parseFloat(line.substring(46, 54));
                const atomName = line.substring(12, 16).trim();
                const element = line.substring(76, 78).trim() || atomName.charAt(0);
                
                atoms.push({
                    x: x,
                    y: y,
                    z: z,
                    element: element
                });
            } catch (e) {
                console.error('Error parsing PDB line:', e);
            }
        }
    }
    
    return atoms;
}

// Helper function to get color for an atom
function getAtomColor(element) {
    const atomColors = {
        'C': '#909090', // Carbon - gray
        'N': '#3050F8', // Nitrogen - blue
        'O': '#FF0D0D', // Oxygen - red
        'S': '#FFFF30', // Sulfur - yellow
        'P': '#FF8000', // Phosphorus - orange
        'H': '#FFFFFF', // Hydrogen - white
        'F': '#90E050', // Fluorine - light green
        'CL': '#1FF01F', // Chlorine - green
        'BR': '#A62929', // Bromine - brown
        'I': '#940094',  // Iodine - purple
        'CA': '#00FF00', // Calcium - bright green
        'MG': '#00FFFF', // Magnesium - cyan
        'NA': '#0000FF', // Sodium - blue
        'K': '#8000FF',  // Potassium - purple
        'ZN': '#808080', // Zinc - gray
        'FE': '#FFA500'  // Iron - orange
    };
    
    return atomColors[element] || '#808080'; // Default to gray
}