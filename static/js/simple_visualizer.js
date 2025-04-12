/**
 * A simpler 2D PDB Visualizer for the molecular structures
 */

// Function to create a static top view of the molecule
function createTopView(pdbData, canvasId) {
    // Parse the PDB data to extract coordinates
    const atoms = parsePdbAtoms(pdbData);
    console.log(`Parsed ${atoms.length} atoms for static rendering`);
    
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
    
    // Draw atoms as circles
    for (const atom of atoms) {
        const x = (atom.x - minX) * scale + padding;
        const y = (atom.y - minY) * scale + padding;
        
        // Set circle size based on atom type
        let radius = 2;
        if (atom.element === 'C') radius = 2;
        else if (atom.element === 'N') radius = 2.5;
        else if (atom.element === 'O') radius = 2.5;
        else if (atom.element === 'S') radius = 3;
        else if (atom.element === 'P') radius = 3;
        else radius = 2;
        
        // Set color based on atom type
        ctx.fillStyle = getAtomColor(atom.element);
        
        // Draw the atom
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Function to create a static side view of the molecule
function createSideView(pdbData, canvasId) {
    // Parse the PDB data to extract coordinates
    const atoms = parsePdbAtoms(pdbData);
    console.log(`Parsed ${atoms.length} atoms for static rendering`);
    
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
    
    // Draw atoms as circles
    for (const atom of atoms) {
        const x = (atom.x - minX) * scale + padding;
        const y = (atom.z - minZ) * scale + padding;
        
        // Set circle size based on atom type
        let radius = 2;
        if (atom.element === 'C') radius = 2;
        else if (atom.element === 'N') radius = 2.5;
        else if (atom.element === 'O') radius = 2.5;
        else if (atom.element === 'S') radius = 3;
        else if (atom.element === 'P') radius = 3;
        else radius = 2;
        
        // Set color based on atom type
        ctx.fillStyle = getAtomColor(atom.element);
        
        // Draw the atom
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
    }
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