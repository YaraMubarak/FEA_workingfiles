#Import libraries
import numpy as np
from dolfin import *

dt = 1. / 57. # s^-1, assumes cardiac cycle is 1 s
nu = 0.00000377 # m^2/s

first_filenum = 1
last_filenum = 57
root = '/home/ymubarak/Documents/FEA_workingfiles/c180/As4'
mesh_filename_root = root + '/Data/lv_mesh.'
velocity_filename_root = root + '/Data/lv_vel.'

# Load mesh and velocity from the last tstep to allow estimation of u_dot at
# first tstep.
mesh_filename = mesh_filename_root + str(last_filenum) + '.h5'
mesh = Mesh()
mesh_in = HDF5File(mpi_comm_world(), mesh_filename, 'r')
mesh_in.read(mesh, 'mesh', False)
mesh_in.close()
V = VectorFunctionSpace(mesh, 'CG', 1)
velocity_filename = velocity_filename_root + str(last_filenum) + '.h5'
velocity = Function(V)
vel_in = HDF5File(mpi_comm_world(), velocity_filename, 'r')
vel_in.read(velocity, 'velocity')
vel_in.close()

# Set up output file
fout = File('Results/pressure.pvd')

# Loop through the velocity fields and solve for pressure
for i in range(first_filenum, last_filenum+1):
    # Load new mesh
    mesh_filename = mesh_filename_root + str(i) + '.h5'
    mesh = Mesh()
    mesh_in = HDF5File(mpi_comm_world(), mesh_filename, 'r')
    mesh_in.read(mesh, 'mesh', False)
    mesh_in.close()

    # Define new function spaces Q, V, and T for scalars, vectors, and 
    # tensors, respectively
    Q = FunctionSpace(mesh,'CG',1)
    V = VectorFunctionSpace(mesh, 'CG', 1)	
    T = TensorFunctionSpace(mesh,'CG',1)

    # Project old velocity field to new mesh.
    # Need to allow extrapolation since domain is changing.
    velocity.set_allow_extrapolation(True)
    velocity_prev = project(velocity, V)

    # Load new velocity field
    velocity_filename = velocity_filename_root + str(i) + '.h5'
    velocity = Function(V)
    vel_in = HDF5File(mpi_comm_world(), velocity_filename, 'r')
    vel_in.read(velocity, 'velocity')
    vel_in.close()

    # Project gradient of velocity to CG1 tensor space so that 
    # div(grad_velocity) can be used to approximate laplacian of velocity
    grad_velocity = project(grad(velocity), T)

    # Approximate time derivative of velocity using backward difference
    udot = (velocity - velocity_prev) / dt

    # Define test, trial, and solution functions
    w = TestFunction(Q)
    p = Function(Q)
    pp = TrialFunction(Q)




    # Define zero Dirichlet BC at rightmost node in mesh.
    coords = mesh.coordinates()
    x_dirichlet = -1e8
    y_dirichlet = -1e8
    for j in range(coords.shape[0]):
        if coords[j, 0] > x_dirichlet:
            x_dirichlet = coords[j, 0]
            y_dirichlet = coords[j, 1]
    def dirichlet_node(x, on_boundary):
        return near(x[0], x_dirichlet) and near(x[1], y_dirichlet)
    bc = DirichletBC(Q, Constant(0.), dirichlet_node, method='pointwise')

    # Define b vector
    b = -udot - grad(velocity)*velocity + nu*div(grad_velocity)

    # Set up forms and solve
    L = dot(grad(w),b)*dx 
    a = dot(grad(w), grad(pp))*dx 

    solve(a == L , p, bc )

    # This line is needed so that fieldnames are consistent in vtu files
    p.rename('pressure', 'pressure')

    # Shift pressure such that all values are >= 0. This is done because PPE
    # only gives relative pressures anyway.
    p.vector().set_local(p.vector().get_local() - np.amin(p.vector().array()))

    # Save
    fout << p
