import os
import glob
import numpy as np
from ase import Atoms
from ase.io import write


def extract_cell_parameters(lines, ref_index):
    """Extract CELL_PARAMETERS block found above a reference index (like ATOMIC_POSITIONS)."""
    for i in range(ref_index, 0, -1):
        if "CELL_PARAMETERS" in lines[i]:
            # Collect next 3 lines as cell vectors
            cell = []
            for j in range(i + 1, i + 4):
                cell.append([float(x) for x in lines[j].strip().split()])
            return np.array(cell)
    return None


def extract_atomic_positions(lines):
    """Extract the last ATOMIC_POSITIONS block and return symbols and positions."""
    atom_indices = [i for i, line in enumerate(lines) if "ATOMIC_POSITIONS" in line]
    if not atom_indices:
        return None, None, None

    idx = atom_indices[-1]
    symbols = []
    positions = []

    for line in lines[idx + 1:]:
        if line.strip() == "":
            break
        parts = line.strip().split()
        if len(parts) >= 4:
            symbols.append(parts[0])
            positions.append([float(x) for x in parts[1:4]])

    return symbols, np.array(positions), idx


def parse_cell_from_input_in(input_in_path):
    """Parse CELL_PARAMETERS from input.in if available."""
    if not os.path.exists(input_in_path):
        return None
    with open(input_in_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "CELL_PARAMETERS" in line:
            cell = []
            for j in range(i + 1, i + 4):
                cell.append([float(x) for x in lines[j].strip().split()])
            return np.array(cell)
    return None


def process_input_out(out_path):
    """Process a single input.out file and convert to CIF."""
    with open(out_path, "r") as f:
        lines = f.readlines()

    symbols, positions, atomic_idx = extract_atomic_positions(lines)
    if symbols is None or positions is None:
        print(f" No ATOMIC_POSITIONS found in {out_path}")
        return

    # Try to get CELL_PARAMETERS from input.out
    cell = extract_cell_parameters(lines, atomic_idx)

    # If not found, try input.in
    if cell is None:
        dir_path = os.path.dirname(out_path)
        input_in_path = os.path.join(dir_path, "input.in")
        cell = parse_cell_from_input_in(input_in_path)

    if cell is None:
        print(f" No CELL_PARAMETERS found for {out_path}")
        return

    atoms = Atoms(symbols=symbols, positions=positions, cell=cell, pbc=True)
    output_path = os.path.join(os.path.dirname(out_path), "input.out.cif")
    write(output_path, atoms)
    print(f" Saved: {output_path}")


def main():
    out_files = glob.glob("**/input.out", recursive=True)
    print(f" Found {len(out_files)} input.out files.")
    for out_file in out_files:
        process_input_out(out_file)


main()
