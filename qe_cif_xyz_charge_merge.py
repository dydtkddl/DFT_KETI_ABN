import sys
import numpy as np
from ase import Atoms
from ase.io import read, write
from ase.io.cif import write_cif
import os

def read_cif_with_symbols(cif_path):
    """Read CIF and return Atoms object and element labels."""
    atoms = read(cif_path)
    return atoms, atoms.get_chemical_symbols()

def read_chargemol_xyz_with_charge(xyz_path):
    """Read a Chargemol-style .xyz file with net charges in the 5th column."""
    with open(xyz_path, "r") as f:
        lines = f.readlines()

    try:
        natoms = int(lines[0].strip())
    except ValueError:
        raise ValueError("첫 줄에 원자 수가 명시되어야 합니다.")

    # 두 번째 줄 무시 (Jmol script)
    atom_lines = lines[2:2 + natoms]

    symbols = []
    positions = []
    charges = []

    for line in atom_lines:
        parts = line.strip().split()
        if len(parts) < 5:
            raise ValueError(f"Charge가 누락된 원자 라인: {line}")
        symbols.append(parts[0])
        positions.append([float(x) for x in parts[1:4]])
        charges.append(float(parts[4]))

    atoms = Atoms(symbols=symbols, positions=positions, pbc=True)
    return atoms, symbols, charges

def save_cif_with_charges(atoms, symbols, charges, out_path):
    """Save CIF file and add _atom_site_charge column."""
    write(out_path, atoms)
    with open(out_path, "r") as f:
        cif_lines = f.readlines()

    new_lines = []
    atom_index = 0
    in_loop = False
    for line in cif_lines:
        new_lines.append(line)
        if line.strip() == "_atom_site_occupancy":
            in_loop = True
            new_lines.append("_atom_site_charge\n")
        elif in_loop and atom_index < len(charges) and len(line.strip()) > 0 and not line.startswith("loop_") and not line.startswith("_"):
            charge = charges[atom_index]
            parts = line.strip().split()
            parts.append(f"{charge:.6f}")
            new_line = "  ".join(parts) + "\n"
            new_lines[-1] = new_line  # replace line
            atom_index += 1

    with open(out_path, "w") as f:
        f.writelines(new_lines)

def main():
    if len(sys.argv) != 3:
        print("사용법: python script.py input.cif charge_xyz")
        return

    cif_path = sys.argv[1]
    xyz_path = sys.argv[2]
    out_cif = os.path.splitext(cif_path)[0] + "_with_charge.cif"

    atoms, _ = read_cif_with_symbols(cif_path)
    charge_atoms, symbols, charges = read_chargemol_xyz_with_charge(xyz_path)

    if len(atoms) != len(charges):
        raise ValueError(f"CIF 원자 수({len(atoms)})와 XYZ charge 원자 수({len(charges)})가 다릅니다.")

    save_cif_with_charges(atoms, symbols, charges, out_cif)
    print(f" 저장 완료: {out_cif}")

main()