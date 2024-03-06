import festim as F
from fenics import *

def tag_mesh(filename='test.xdmf'):
    mesh = Mesh()
    XDMFFile(filename).read(mesh)

    # marking physical groups (volumes and surfaces)
    volume_markers = MeshFunction("size_t", mesh, mesh.topology().dim())
    volume_markers.set_all(1)

    tol = 1e-14


    inlet_surface = CompiledSubDomain(
        "on_boundary && near(x[0], 32, tol)",
        tol=tol,
    )
    outlet_surface = CompiledSubDomain(
        "on_boundary && near(x[0], -2, tol)",
        tol=tol,
    )

    inlet_id = 1
    outlet_id =2
    walls_id = 3
    surface_markers = MeshFunction("size_t", mesh, mesh.topology().dim() - 1)
    surface_markers.set_all(walls_id)

    inlet_surface.mark(surface_markers, inlet_id)
    outlet_surface.mark(surface_markers, outlet_id)

    output_file = XDMFFile("surface_markers.xdmf")
    output_file.write(surface_markers)

    output_file2 = XDMFFile("volume_markers.xdmf")
    output_file2.write(volume_markers)


def run_simple_sim():
    tag_mesh()
    my_sim = F.Simulation()

    my_sim.mesh = F.MeshFromXDMF(volume_file='volume_markers.xdmf', boundary_file='surface_markers.xdmf')

    my_sim.materials = F.Material(id=1, D_0=1, E_D=0)

    inlet_BC = F.DirichletBC(surfaces=1, value=1, field="solute")
    outlet_BC = F.DirichletBC(surfaces=2, value=0, field="solute")
    my_sim.boundary_conditions = [
        inlet_BC, outlet_BC
    ]

    my_sim.T = F.Temperature(500)

    my_sim.settings = F.Settings(1e-10, 1e-10, transient=False)

    my_sim.exports = [F.XDMFExport(field="solute")]

    my_sim.initialise()
    my_sim.run()

if __name__=="__main__":
    run_simple_sim()