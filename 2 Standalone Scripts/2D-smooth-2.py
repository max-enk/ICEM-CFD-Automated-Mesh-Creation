# this script is used to generate an ICEM model with user defined dimensions
# it allows the creation of a smooth (unstructured) domain with variable dimensions

# specify part names
name_fluid = "FLUID"
name_finlet = "FILMINLET"
name_fwall = "FILMWALL"
name_foutlet = "FILMOUTLET"
name_gwall = "GASWALL"
name_gtop = "GASTOP"
name_distr = "DISTRIBUTOR"

geomprec = 6                    # specify numerical precision of point locations
meshprec = 6                    # specify numerical precision for mesh calculations (potentially higher runtime with higher values)

meshtype = "2D-smooth-1"        # 2D smooth mesh without structures

############################################################### DO NOT EDIT BELOW ###############################################################
# dependencies
import os               # operating system operations
import re               # regular expressions
import numpy as np      # numerical python


######################################################### CLASS AND FUNCTION DEFINITION #########################################################
# definition of geom1/2 rule
def geomrule(n_i, n_max, r_t):
    # sum term in geom formula
    if n_i >= 3:
        sumrange = np.arange(2, n_i)
        sum = np.sum(r_t**(sumrange - 2))
    else:
        sum = 1.0

    # calculate S_i using the geom1 formula
    val = (r_t - 1)/(r_t**(n_max - 1) - 1)*sum
    return val


# definition of geom1/2 growth rate calculation
def geomrmax(r_t, r_12, r_step, max_n, h_1):
    # incrementing ratio r_t until growth rate between first and second cell r_12 is smaller than 1
    while r_12 > 1.0:
            r_t = round(r_t + r_step, meshprec)
            r_12 = geomrule(2, max_n, r_t)/h_1
    return r_t


# definition of geom1/2 calculation
def geom12(geom, h_1, h_n):
    # meshing array containing:
        # 0: mesh distribution rule
        # 1: number of nodes (n)
        # 2: relative spacing 1 (h1rel)
        # 3: relative spacing 2 (h2rel)
        # 4: growth rate at spacing 1
        # 5: growth rate at spacing 2
        # 6: maximum allowed cell size
        # 7: print line
    geo = [None]*8
    
    # geom1 parameters
    if h_1 < h_n:
        h1rel = round(h_1/geom.getval(), meshprec)  # set relative length of first cell
        h2rel = round(h_n/geom.getval(), meshprec)  # maximum relative length of last cell
        n = int(np.ceil(1/h1rel))                   # initial maximum number of nodes (as for uniform distribution with size h1rel)
    # geom2 parameters
    else:
        h1rel = round(h_n/geom.getval(), meshprec)  # set relative length of last cell
        h2rel = round(h_1/geom.getval(), meshprec)  # maximum relative length of first cell
        n = int(np.ceil(1/h1rel))                   # initial maximum number of nodes (as for uniform distribution with size h1rel)
    
    rstep = 10**(-meshprec)                         # increment size of growth rate
    rmin = round(1.0 + rstep, meshprec)             # minimum (starting growth rate)
    
    # geom1/2 calculation
    r = rmin
    h2calc = 1 - geomrule(n, n, r)                  # initial calculation for h2rel
    r12 = geomrule(2, n, r)/h1rel     	            # initial calculation for r12 (growth rate between first and second cell)
    
    # starting from maximum n, find highest possible n to fit h2calc < h2rel and r12 > 1
    while h2calc < h2rel:
        # getting maximum r value for current n 
        r = rmin
        r12 = geomrule(2, n, r)/h1rel
        r = geomrmax(r, r12, rstep, n, h1rel)
        
        # calculating size of last cell
        h2calc = 1 - geomrule(n, n, r)
        
        if h2calc < h2rel:
            n -= 1 
    
    # calculate final values
    n += 1
    r = rmin
    r12 = geomrule(2, n, r)/h1rel
    r = round(geomrmax(r, r12, rstep, n, h1rel) - rstep, meshprec)
    h2calc = 1 - geomrule(n, n, r)
    
    # meshing list definition    
    # geom1
    if h_1 < h_n:
        geo[0] = "geo1"
        geo[1] = n
        geo[2] = h1rel
        geo[3] = h2rel
        geo[4] = r
        geo[5] = 1
        geo[6] = h_n
        geo[7] = "geom1 distribution with minimum cell size " + str(round(h_1*1000.0, meshprec)) + " mm, maximum cell size " + str(round(h2calc*geom.getval()*1000.0, meshprec)) + " mm and growth factor " + str(round(r, meshprec))
    # geom2 - value associations flipped
    else:
        geo[0] = "geo2"
        geo[1] = n
        geo[2] = h2rel
        geo[3] = h1rel
        geo[4] = 1
        geo[5] = r
        geo[6] = h_1
        geo[7] = "geom2 distribution with minimum cell size " + str(round(h_n*1000.0, meshprec)) + " mm, maximum cell size " + str(round(h2calc*geom.getval()*1000.0, meshprec)) + " mm and growth factor " + str(round(r, meshprec))
    return geo


# definition of uniform calculation
def uniform(geom, h_u):
    # meshing array containing:
        # 0: mesh distribution rule
        # 1: number of nodes (n)
        # 2: relative spacing 1 (h1rel)
        # 3: relative spacing 2 (h2rel)
        # 4: growth rate at spacing 1
        # 5: growth rate at spacing 2
        # 6: maximum allowed cell size
        # 7: print line
    uni = [None]*8

    # meshing list definition    
    uni[0] = "uniform"
    uni[1] = int(np.ceil(geom.getval()/h_u)) + 1
    uni[2] = round(h_u/geom.getval(), meshprec)
    uni[3] = round(h_u/geom.getval(), meshprec)
    uni[4] = 1
    uni[5] = 1
    uni[6] = 0
    uni[7] = "uniform distribution with cell size " + str(round(geom.getval()/(uni[1] - 1)*1000.0, meshprec)) + " mm"
    return uni


# message to be displayed when custom meshing is selected
def custommeshingmessage():
    print("\nCustom meshing:")
    print("    - In every coordinate direction, the domain is split into sections, which are referenced by their corresponding geometric parameter(s).")
    print("    - Meshing parameters have to be defined for every section according to the blocking structure automatically generated.")
    print("    - See references for more information.")
    print("\nNote the following:")            
    print("    - Meshing parameters are set once for every zone and will be automatically copied to all related (parallel) edges.")
    print("    - Currently, only 'geometric1', 'geometric2' and 'uniform' node distributions can be selected. To use other distributions, manually edit the mesh in ICEM afterwards.")
    print("    - There is currently no guarantee, that the meshing can be applied as specified. Validate the mesh settings after generation.")
    input("\nPress any key to continue...")


# definition of input function for custom meshing
def custommeshing(geom):
    while True:
        # meshing array containing:
        # 0: mesh distribution rule
        # 1: number of nodes (n)
        # 2: relative spacing 1 (h1rel)
        # 3: relative spacing 2 (h2rel)
        # 4: growth rate at spacing 1
        # 5: growth rate at spacing 2
        # 6: maximum allowed cell size
        # 7: print line
        meshing = [None]*8

        # query for meshing rule to be used
        rule = input("Enter node distribution: (geom1, geom2, uni)\n - geom1: increasing cell size in line with positive coordinate direction (normal vector)\n - geom2: decreasing cell size in line with positive coordinate direction (normal vector)\n - uni: uniform cell distribution\n>>> ").lower()

        if rule == "geom1":
            while True:
                # query for minimum and maximum cell sizes
                while True:
                    cell_1 = input("Enter minimum cell size (where coordinate is smallest on edge) [mm].\nShould be distinctly smaller than the respective edge length (" + str(round(geom.getval()*1000.0, geomprec)) + " mm).\n>>> ")
                    try:
                        c_1 = round(float(cell_1)/1000.0, meshprec)
                        break
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")
                while True:
                    cell_n =input("Enter maximum cell size (where coordinate is largest on edge) [mm].\nShould be smaller than the respective edge length (" + str(round(geom.getval()*1000.0, geomprec)) + " mm) and larger than the minimum cell size.\n>>> ")
                    try:
                        c_n = round(float(cell_n)/1000.0, meshprec)
                        break
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")
                if c_1 >= c_n or c_1 >= geom.getval()*1000.0 or c_n >= geom.getval():
                    print("Invalid input.")
                else:
                    break
            # calculate mesh
            geom.setmesh(geom12(geom, c_1, c_n))

            print(str(geom.getmesh()[1]-1) + " cells with smallest size " + str(round(c_1*1000.0, meshprec)) + " mm, largest size " + str(round(geom.getval()*geom.getmesh()[3]*1000.0, meshprec)) + " mm and growth rate " + str(geom.getmesh()[4]))
            break

        elif rule == "geom2":
            while True:
                # query for minimum and maximum cell sizes
                while True:
                    cell_n = input("Enter minimum cell size (where coordinate is largest on edge) [mm].\nShould be distinctly smaller than the respective edge length (" + str(round(geom.getval()*1000.0, geomprec)) + " mm).\n>>> ")
                    try:
                        c_n = round(float(cell_n)/1000.0, meshprec)
                        break
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")    
                while True:
                    cell_1 =input("Enter maximum cell size (where coordinate is smallest on edge) [mm].\nShould be smaller than the respective edge length (" + str(round(geom.getval()*1000.0, geomprec)) + " mm) and larger than the minimum cell size.\n>>> ")
                    try:
                        c_1 = round(float(cell_1)/1000.0, meshprec)
                        break
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")
                if c_1 <= c_n or c_1 >= geom.getval()*1000.0 or c_n >= geom.getval():
                    print("Invalid input.")
                else:
                    break
            # calculate mesh
            geom.setmesh(geom12(geom, c_1, c_n))

            print(str(geom.getmesh()[1]-1) + " cells with smallest size " + str(round(c_n*1000.0, meshprec)) + " mm, largest size " + str(round(geom.getval()*geom.getmesh()[2]*1000.0, meshprec)) + " mm and growth rate " + str(geom.getmesh()[5]))
            break

        elif rule == "uni":
            while True:
                # query for maximum uniform cell size
                while True:
                    cell_u = input("Enter maximum uniform cell size [mm].\nMust be smaller than or equal to the respective edge length (" + str(round(geom.getval()*1000.0, geomprec)) + " mm).\n>>> ")
                    try:
                        c_u = round(float(cell_u)/1000.0, meshprec)
                        break
                    except ValueError:
                        print("Invalid input. Please enter a valid number.")                
                if geom.getval() < c_u:
                    print("Invalid input.")
                else:
                    break
            # calculate mesh
            geom.setmesh(uniform(geom, c_u))

            print(str(geom.getmesh()[1]-1) + " uniform cells with size " + str(round(geom.getval()/(geom.getmesh()[1]-1)*1000.0, meshprec)) + " mm")
            break
        
        else:
            print("Invalid input. Please enter one of the provided options.")


# definition of function for meshing with reference
def refmeshing(geom, rref, conf):
    if conf[0] == "uniform":
        geom.setmesh(uniform(geom, round(rref*float(conf[2])*geom.getval(), meshprec)))
    elif conf[0] == "geo1" or conf[0] == "geo2":
        geom.setmesh(geom12(geom, round(rref*float(conf[2])*geom.getval(), meshprec), round(rref*float(conf[3])*geom.getval(), meshprec)))


# geometry class definition (contains geometric and meshing parameters)
class Geom:
    # geometry constructor
    def __init__(self, val):
        self.val = round(val, geomprec)     # value of variable in [m]
        self.mesh = [None]*8                # list of meshing parameters 

    # geometry destructor
    def __del__(self):
        pass

    # getter functions
    def getval(self):                       # size of geometry
        return self.val
    def getmesh(self):                      # meshing list
        return self.mesh
    
    #setter functions
    def setval(self, val):
        self.val = val
    def setmesh(self, mesh):
        self.mesh = mesh

   
# point class definition (geometry)
class Point:
    count = 0
    
    # point constructor
    def __init__(self, x, y, z):
        # set coordinates 
        self.x = round(x, geomprec)             # x coordinate of point
        self.y = round(y, geomprec)             # y coordinate of point
        self.z = round(z, geomprec)             # z coordinate of point
        
        # set point name and number. expecting maximum of 9999 points. 
        if Point.count >= 0 and Point.count <= 9:
            self.name = "pnt.000" + str(Point.count)
        elif Point.count >= 10 and Point.count <= 99:
            self.name = "pnt.00" + str(Point.count)
        elif Point.count >= 100 and Point.count <= 999:
            self.name = "pnt.0" + str(Point.count)
        else:
            self.name = "pnt." + str(Point.count)
        self.num = Point.count

        # increase point count everytime a point gets created
        Point.count += 1

    # point destructor
    def __del__(self):
        pass

    # getter functions
    def getx(self):
        return self.x
    def gety(self):
        return self.y
    def getz(self):
        return self.z
    def getname(self):
        return self.name
    def getnum(self):
        return self.num


# curve class definition (geometry)
class Curve:
    count = 0

    # curve constructor
    def __init__(self, pnt1, pnt2):
        # set point association
        self.pnt1 = pnt1                    # first point
        self.pnt2 = pnt2                    # second point
        
        # set curve name and number. expecting maximum of 9999 curves. 
        if Curve.count >= 0 and Curve.count <= 9:
            self.name = "crv.000" + str(Curve.count)
        elif Curve.count >= 10 and Curve.count <= 99:
            self.name = "crv.00" + str(Curve.count)
        elif Curve.count >= 100 and Curve.count <= 999:
            self.name = "crv.0" + str(Curve.count)
        else:
            self.name = "crv." + str(Curve.count)
        self.num = Curve.count
        
        # increase curve count everytime a curve gets created
        Curve.count += 1

    # curve destructor
    def __del__(self):
        pass

    # getter functions
    def getpnt1(self):
        return self.pnt1
    def getpnt2(self):
        return self.pnt2
    def getname(self):
        return self.name
    def getnum(self):
        return self.num


# surface class definition (geometry)
class Surf:
    count = 0

    # surface constructor
    def __init__(self, mode, curves):
        self.mode = str(mode)               # surface generation mode
        self.curves = curves                # list of curves
        
        # set surface name and number. expecting maximum of 9999 surfaces. 
        if Surf.count >= 0 and Surf.count <= 9:
            self.name = "srf.000" + str(Surf.count)
        elif Surf.count >= 10 and Surf.count <= 99:
            self.name = "srf.00" + str(Surf.count)
        elif Surf.count >= 100 and Surf.count <= 999:
            self.name = "srf.0" + str(Surf.count)
        else:
            self.name = "srf." + str(Surf.count)
        self.num = Surf.count
        
        # increase surface count everytime a surface gets created
        Surf.count += 1

    # surface destructor
    def __del__(self):
        pass

    # getter functions
    def getmode(self):
        return self.mode
    def getcrvs(self):                      # list of curves
        return self.curves
    def getcrvlist(self):                   # list of curves in one string
        # make list in case of multiple entries
        if len(self.curves) > 1:
            crvlist = "{"
            for crv in self.curves[:-1]:
                crvlist += crv.getname() + " "
            crvlist += self.curves[-1].getname() + "}"
        # just print single entry
        else:
            crvlist = "{" + self.curves[0].getname() + "}"
        return crvlist
    def getname(self):
        return self.name
    def getnum(self):
        return self.num


# body part class definition (geometry)
class Body:
    # body constructor
    def __init__(self, name, loc):
        self.name = name                    # name of part as set at the top of script
        self.loc = loc                      # x, y, z location of body point

    # body destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):
        return self.name
    def getloc(self):
        return self.loc
  

# boundary part class definition (geometry)
class Part:
    # part constructor
    def __init__(self, name, geom):
        self.name = name                    # name of part as set at the top of script
        self.geom = geom                    # list of geometry associated with this part

    # part destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):
        return self.name
    def getgeom(self):
        return self.geom
    def getpartlist(self):                  # has string of associated geometry as return value
        # make list in case of multiple entries
        if len(self.geom) > 1:
            prtlist = "{"
            for prt in self.geom[:-1]:
                prtlist += prt.getname() + " "
            prtlist += self.geom[-1].getname() + "}"
        # just print single entry
        else:            
            prtlist = self.geom[0].getname()
        return prtlist


# split block operation class definition (blocking)
class Split:
    # split constructor
    def __init__(self, pnt, vert1, vert2):
        # set point and vertice associations
        self.pnt = pnt	                    # point closest to edge(vert1,vert2), at which edge will be cut
        self.vert1 = vert1                  # first vertex of edge to be cut
        self.vert2 = vert2                  # second vertex of edge to be cut

    # split destructor
    def __del__(self):
        pass

    # getter functions
    def getpnt(self):
        return self.pnt
    def getvert1(self):
        return self.vert1
    def getvert2(self):
        return self.vert2
    

# delete block operation class definition (blocking)
class Delete:
    # delete constructor
    def __init__(self, blk):
        # set point and vertice associations
        self.blk = blk 	                   # block to delete

    # split destructor
    def __del__(self):
        pass

    # getter functions
    def getblk(self):
        return self.blk


# vertex association operation class definition (blocking)
class Vert:
    # vertex constructor
    def __init__(self, num, pnt):
        self.num = num                      # number of vertex
        self.pnt = pnt                      # vertex associated point

    # vertex destructor
    def __del__(self):
        pass

    # getter functions
    def getnum(self):
        return self.num
    def getpnt(self):
        return self.pnt


# edge association operation class definition (blocking)
class Edge:
    # edge constructor
    def __init__(self, vert1, vert2, crv):
        self.vert1 = vert1                  # first vertex of edge
        self.vert2 = vert2                  # second vertex of edge
        self.crv = crv                      # edge associated curve

    # edge destructor
    def __del__(self):
        pass

    # getter functions
    def getvert1(self):
        return self.vert1
    def getvert2(self):
        return self.vert2
    def getcrv(self):
        return self.crv


# mesh class definition (meshing)
class Mesh:
    # mesh constructor
    def __init__(self, vert1, vert2, meshing):
        self.vert1 = vert1                  # first vertex of edge to be meshed
        self.vert2 = vert2                  # second vertex of edge to be meshed
        self.distr = meshing[0]             # node distribution rule
        self.nodes = meshing[1]             # number of nodes on edge
        self.h1rel = meshing[2]             # relative length of first node spacing
        self.h2rel = meshing[3]             # relative length of last node spacing
        self.r1 = meshing[4]                # growth ratio of first node spacing
        self.r2 = meshing[5]                # growth ratio of last node spacing
        self.lmax = meshing[6]              # maximum node spacing

    # mesh destructor
    def __del__(self):
        pass

    # getter functions
    def getvert1(self):
        return self.vert1
    def getvert2(self):
        return self.vert2
    def getdistr(self):
        return self.distr
    def getnodes(self):
        return self.nodes
    def geth1rel(self):
        return self.h1rel
    def geth2rel(self):
        return self.h2rel
    def getr1(self):
        return self.r1
    def getr2(self):
        return self.r2
    def getlmax(self):
        return self.lmax


################################################################# PROGRAM HEAD ##################################################################
# change to directory containing the script
sourcedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourcedir)


# print script intoduction messages
print("#################################################################### WELCOME ####################################################################\n")
print("This is a script for the automatic generation of a 2D smooth mesh in ICEM. Features:\n    - additional gas space above film inlet\n    - shared outlet for gas and liquid phases")
print("If not already present, it will create a project folder containing:\n    > .rpl file to be read into ICEM\n    > .conf file containing the parameters specified\n")
print("Steps to generate the mesh in ICEM:\n    1) Load the .rpl file (File > Replay Scripts > Load script file)\n    2) Execute all commands (do all)\n")


# project name input
while True:
    projname = input("Enter ICEM project name:\n>>> ")
    
    # check if project name meets requirements
    if re.match(r'^[a-zA-Z0-9_+\-]+$', projname):       # only letters, numbers and '_', '+', '-' are allowed
        projdir = os.path.join(sourcedir, projname)     # project directory

        # check if project directory already exists
        if os.path.exists(projdir):
            while True:
                # prompt to continue with existing folder
                q_folder = input("A folder with the specified project name already exists.\nExisting files in this folder with the project name will be overwritten.\nUse this folder anyway? (y/n)\n>>> ").lower()                
                if q_folder == "y":
                    break               
                elif q_folder == "n":
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

            if q_folder == "y":
                break
        else:
            break
    
    # project name does not meet requirements
    else:
        print("Invalid project name. Only letters, numbers and '_', '+', '-' are allowed.")


# filename definition
print("\nCreating ICEM project " + projname + ".\n")
rplfile = projname + ".rpl"
conffile = projname + ".conf"

# read from existing config file
while True:
    # query whether an existing config file should be used
    q_conf = input("Use an existing config file for input parameters? (y/n)\n>>> ").lower()
    if q_conf == "y":
        while True:
            # input reference config file
            refconffile = input("Enter filename of .conf file to be read:\n>>> ")
            # append .conf in case not specified
            if not refconffile.endswith(".conf"):
                refconffile += ".conf"
            # check if file exists
            if os.path.exists(refconffile):
                with open(refconffile, 'r') as file:
                    dimmode = False
                    # check if file contains "2D smooth" specification
                    for line in file:
                        line = line.strip()
                        if line == meshtype:
                            dimmode = True
                            break
                file.close()
                if dimmode == True:
                    print("\nReading from reference file " + refconffile + ".\n")
                    break
                else:
                    print("The config file specified is not suited for 2D smooth mesh creation.")
            else:
                refconffile	= refconffile.split(".conf")[0]
                refconffile = refconffile + "/" + refconffile + ".conf"
                if os.path.exists(refconffile):
                    with open(refconffile, 'r') as file:
                        dimmode = False
                        # check if file contains "2D smooth" specification
                        for line in file:
                            line = line.strip()
                            if line == meshtype:
                                dimmode = True
                    file.close()
                    if dimmode == True:
                        print("\nReading from reference file /" + refconffile + ".\n")
                        break
                    else:
                        print("The config file specified is not suited for 2D smooth mesh creation.")
                else:
                    print("The specified file " + refconffile.split("/")[1] + " does not exist in the current directory or in a respective subfolder.")
        break
    elif q_conf == "n":
        print("")
        break
    else:
        print("Invalid input. Please enter 'y' or 'n'.")


################################################################ PARAMETER INPUT ################################################################
print("################################################################ PARAMETER INPUT ################################################################\n")
# geometric parameters
while True:
    print("############################################################## GEOMETRIC PARAMETERS #############################################################\n")

    if q_conf == "y":
        while True:
            # query whether geometry data from config file should be used
            q_confgeom = input("Use config file data for geometric parameters? (y/n)\n>>> ").lower()
            if q_confgeom == "y":
                break               
            elif q_confgeom == "n":
                print("")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    else:
        q_confgeom = "n"

    # using file input for geometric parameters
    if q_confgeom == "y":
        xgeom = []
        ygeom = []

        # Read the config file
        with open(refconffile, 'r') as file:
            for line in file:
                line = line.strip()             # Remove leading/trailing whitespaces
                if line.startswith("xgeom"):
                    xgeom = line.split()[1:]    # Extract xgeom parameters
                elif line.startswith("ygeom"):
                    ygeom = line.split()[1:]    # Extract ygeom parameters
        file.close()

        # assigning geometric values
        # x-values
        h = float(xgeom[0])
        hnu = float(xgeom[1])
        hd = float(xgeom[2])
        # y-values
        l = float(ygeom[0])
        lg = float(ygeom[1])
        
    # user defined input of geometric features
    if q_conf == "n" or q_confgeom == "n":
        # parameter definition in x
        print("Parameters for x-dimension:\n")
        # total domain size
        while True:
            h_inp = input("Enter total domain size in x-direction (H) [mm]:\n>>> ")                 
            try:
                h = abs(float(h_inp)/1000.0)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        # film inlet
        while True:  
            hnu_inp = input("Enter thickness of film inlet (Nusselt-Height) (h_nu) [mm]:\n>>> ")    
            try:
                hnu = abs(float(hnu_inp)/1000.0)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        # distributor
        while True:
            hd_inp = input("Enter distributor thickness (h_d) [mm]:\n>>> ")                         
            try:
                hd = abs(float(hd_inp)/1000.0)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # parameter definition in y
        print("\nParameters for y-dimension:\n")
        # total domain size (not including additional gas space)
        while True:
            l_inp = input("Enter total domain size in y-direction (L) [mm]:\n>>> ")
            try:
                l = abs(float(l_inp)/1000.0)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")       
        # additional gas space
        while True:
            lg_inp = input("Enter size of additional gas space (l_g) [mm]:\n>>> ")                  
            try:
                lg = abs(float(lg_inp)/1000.0)
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")                                                                            

    # print summary of geometric parameters
    print("\nSummary of geometric parameters:")
    print("    > x-dimension:")
    print("        > Total domain height (H): " + str(h*1000.0) + " mm")
    print("        > Thickness of film inlet (h_nu): " + str(hnu*1000.0) + " mm")
    print("        > Thickness of distributor (h_d): " + str(hd*1000.0) + " mm")
    print("    > y-dimension:")
    print("        > Total domain length (L): " + str(l*1000.0) + " mm")
    print("        > Length of additional gas space (l_g): " + str(lg*1000.0) + " mm")
   
    # query to proceed with geometric values
    while True:
        q_proc1 = input("\nProceed with the above values? (y/n)\n>>> ").lower()
        if q_proc1 == "y":
            print("")
            break
        elif q_proc1 == "n":
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
    if q_proc1 == "y":
        break

# creating geometry objects based on geometric parameters provided
# x-dimension 
h_t = Geom(h)                   # total domain size (not to be meshed)
h_nu = Geom(hnu)                # film inlet
h_d = Geom(hd)                  # distributor
h_g = Geom((h - (hnu + hd)))    # gas space between x = (h_nu + h_d) .. H
# y-dimension
l_t = Geom(l)                   # total domain size
l_g =Geom(lg)                   # additional gas space


# meshing parameters
while True:
    print("############################################################### MESHING PARAMETERS ##############################################################\n")

    if q_conf == "y":
        while True:
            # query whether geometry data from config file should be used
            q_confmesh = input("Use config file data for meshing parameters? (y/n)\n>>> ").lower()
            if q_confmesh == "y":
                while True:
                    #definition of refinement factor
                    while True:
                        inp_r_ref = input("Specify factor for mesh refinement/coarsening.\nIt will be applied to all specified absolute cell sizes, respective growth factors and node counts will be calculated.\nThe default is '1.0'. Larger values will coarsen the mesh, smaller values refine it. Values can be given in decimal or fraction representation.\n>>> (1.0) ")
                        try:
                            r_ref = float(eval(inp_r_ref))
                            break
                        except ValueError:
                            print("Invalid input. Please enter a valid number.")
                        except NameError:
                            print("Invalid input. Please enter a valid number.")
                        except SyntaxError:
                            if inp_r_ref == "":
                                r_ref = 1.0
                                break
                            else:
                                print("Invalid input. Please enter a valid number.")
                    if r_ref <= 0:
                        print("Invalid input. Refinement factor must be larger than zero.")
                    else:
                        break          
                break               
            elif q_confmesh == "n":
                print("")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    else:
        q_confmesh = "n"
    
    # using file input for meshing parameters
    if q_confmesh == "y":
        # extract parameters from file
        with open(refconffile, 'r') as file:
            for line in file:
                line = line.strip()                     # remove leading/trailing whitespaces
                
                if line.startswith("h_nu "):
                    h_nu_conf = line.split()[1:]        # extract h_nu mesh data                
                elif line.startswith("h_d "):
                    h_d_conf = line.split()[1:]         # extract h_d mesh data                
                elif line.startswith("h_g "):
                    h_g_conf = line.split()[1:]         # extract h_g mesh data               
                elif line.startswith("l_t "):
                    l_t_conf = line.split()[1:]         # extract l_t mesh data
                elif line.startswith("l_g "):
                    l_g_conf = line.split()[1:]         # extract l_g mesh data
        file.close()

        # meshing with specified refinement factor
        # x-dimension
        refmeshing(h_nu, r_ref, h_nu_conf)
        refmeshing(h_d, r_ref, h_d_conf)
        refmeshing(h_g, r_ref, h_g_conf)
        # y-dimension
        refmeshing(l_t, r_ref, l_t_conf)
        refmeshing(l_g, r_ref, l_g_conf)
    
    # user defined input of geometric features
    if q_conf == "n" or q_confmesh == "n":
        while True:
            print("Default meshing:")
            print("    > x-dimension:")
            print("        > Within film section (h_nu): Uniform distribution of cells with maximum size of 12 µm")
            print("        > Within distributor section (h_d): Geometric1 distribution of cells, growth from 12 µm to 24 µm with maximum growth rate of 1.1")
            print("        > Within gas section (h_g): Geometric1 distribution of cells, growth from 24 µm to 100 µm with maximum growth rate of 1.1")
            print("    > y-dimension:")
            print("        > For all sections: Uniform distribution of cells with maximum size of 100 µm\n")
            
            # query to use default meshing parameters
            q_defmsh = input("Do you want to use default meshing parameters? (y/n)\n>>> ").lower()

            # default meshing
            if q_defmsh == "y":
                # global mesh parameters
                size_film = 1.2e-5
                size_distr = 2.4e-5
                size_max = 1e-4

                # x-dimension
                h_nu.setmesh(uniform(h_nu, size_film))
                h_d.setmesh(geom12(h_d, size_film, size_distr))
                h_g.setmesh(geom12(h_g, size_distr, size_max))
                # y-dimension
                l_t.setmesh(uniform(l_t, size_max))
                l_g.setmesh(uniform(l_g, size_max))
                break
            
            # custom meshing
            elif q_defmsh == "n":
                # print custom meshing messages
                custommeshingmessage()

                # parameter definition in x
                print("\nMesh definition in x-dimension:")                
                print("\nMeshing for film section (h_nu):")
                custommeshing(h_nu)
                print("\nMeshing for distributor section (h_d):")
                custommeshing(h_d)
                print("\nMeshing for gas section (h_g):")
                custommeshing(h_g)

                # parameter definition in y
                print("\nMesh definition in y-dimension:")
                print("\nMeshing for total domain (L):")
                custommeshing(l_t)
                print("\nMeshing for additional gas section (l_g):")
                custommeshing(l_g)
                break
            
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    # print summary of meshing parameters
    print("\nSummary of meshing parameters:")
    print("    > x-dimension:")
    print("        > h_nu: " + h_nu.getmesh()[-1])
    print("        > h_d: " + h_d.getmesh()[-1])
    print("        > h_g: " + h_g.getmesh()[-1])
    print("    > y-dimension:")
    print("        > l_t: " + l_t.getmesh()[-1])
    print("        > l_g: " + l_g.getmesh()[-1])
    
    # query to proceed with meshing parameters
    while True:
        q_proc2 = input("\nProceed with the above values? (y/n)\n>>> ").lower()
        if q_proc2 == "y":
            print("")
            break
        elif q_proc2 == "n":
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
    if q_proc2 == "y":
        break


############################################################### SCRIPT GENERATION ###############################################################
print("############################################################### SCRIPT GENERATION ###############################################################")

############################################################## GEOMETRY GENERATION ##############################################################
print("Generating geometry...")
pnts = []                                   # list containing all points
crvs = []                                   # list containing all curves
prts = []                                   # list of all boundary parts
geom_fluid = None                           # string of fluid body location
geom_finlet = []                            # list of surfaces included in inlet
geom_fwall = []                             # list of surfaces included in film wall
geom_foutlet = []                           # list of surfaces included in outlet
geom_gwall = []                             # list of surfaces included in gaswall
geom_gtop = []                              # list of surfaces included in gastop
geom_distr = []                             # list of surfaces included in distributor 
geom_sides = []                             # list of surfaces included in sides

# points
pnts.append(Point(0.0, l_t.getval(), 0.0))
pnts.append(Point(h_nu.getval(), l_t.getval(), 0.0))
pnts.append(Point((h_nu.getval() + h_d.getval()), l_t.getval(), 0.0))
pnts.append(Point((h_nu.getval() + h_d.getval()), (l_t.getval() + l_g.getval()), 0.0))
pnts.append(Point(h_t.getval(), (l_t.getval() + l_g.getval()), 0.0))
pnts.append(Point(h_t.getval(), l_t.getval(), 0.0))
pnts.append(Point(h_t.getval(), 0.0, 0.0))
pnts.append(Point((h_nu.getval() + h_d.getval()), 0.0, 0.0))
pnts.append(Point(h_nu.getval(), 0.0, 0.0))
pnts.append(Point(0.0, 0.0, 0.0))
print(" - done points")

# curves
crvs.append(Curve(pnts[0], pnts[1]))
geom_finlet.append(crvs[-1])
crvs.append(Curve(pnts[1], pnts[2]))
geom_distr.append(crvs[-1])
crvs.append(Curve(pnts[2], pnts[3]))
geom_distr.append(crvs[-1])
crvs.append(Curve(pnts[3], pnts[4]))
geom_gtop.append(crvs[-1])
crvs.append(Curve(pnts[4], pnts[5]))
geom_gwall.append(crvs[-1])
crvs.append(Curve(pnts[5], pnts[6]))
geom_gwall.append(crvs[-1])
crvs.append(Curve(pnts[6], pnts[7]))
geom_foutlet.append(crvs[-1])
crvs.append(Curve(pnts[7], pnts[8]))
geom_foutlet.append(crvs[-1])
crvs.append(Curve(pnts[8], pnts[9]))
geom_foutlet.append(crvs[-1])
crvs.append(Curve(pnts[9], pnts[0]))
geom_fwall.append(crvs[-1])
print(" - done curves\n")

# part association
print("Associating parts...")

# body parts
geom_fluid = "{" + str(h_t.getval()/2.0) + " " + str(l_t.getval()/2.0) + " " + str(0.0) + "}"    # x, y, z coordinate of fluid body point
fluid = Body(name_fluid, geom_fluid)

# boundary parts
prts.append(Part(name_fwall, geom_fwall))
prts.append(Part(name_finlet, geom_finlet))
prts.append(Part(name_foutlet, geom_foutlet))
prts.append(Part(name_distr , geom_distr))
prts.append(Part(name_gtop, geom_gtop))
prts.append(Part(name_gwall, geom_gwall))
print(" - done\n")


################################################################### BLOCKING ####################################################################
print("Generating blocking...")
blkg = []                                   # list containing blocking operations (split, deletion)
edges = []                                  # list containing edge curve associations

# block modification operations
blkg.append(Split(pnts[0], 11, 13))
blkg.append(Split(pnts[3], 13, 21))
blkg.append(Delete(10))
blkg.append(Split(pnts[1], 33, 38))
print(" - done\n")

# edge-curve associations
print("Associating edges to curves...")
edges.append(Edge(33, 43, crvs[0]))
edges.append(Edge(43, 38, crvs[1]))
edges.append(Edge(38, 39, crvs[2]))
edges.append(Edge(39, 21, crvs[3]))
edges.append(Edge(34, 21, crvs[4]))
edges.append(Edge(19, 34, crvs[5]))
edges.append(Edge(37, 19, crvs[6]))
edges.append(Edge(42, 37, crvs[7]))
edges.append(Edge(11, 42, crvs[8]))
edges.append(Edge(11, 33, crvs[9]))
print(" - done\n")


#################################################################### MESHING ####################################################################
print("Meshing...")
mshg = []                                   # list containing all meshing operations

# x-coordinate
mshg.append(Mesh(33, 43, h_nu.getmesh()))  # film inlet
mshg.append(Mesh(43, 38, h_d.getmesh()))   # distributor
mshg.append(Mesh(38, 34, h_g.getmesh()))    # gas space
# y-coordinate
mshg.append(Mesh(33, 11, l_t.getmesh()))    # total domain size 
mshg.append(Mesh(38, 39, l_g.getmesh()))    # additional gas space
print(" - done\n")


################################################################# WRITE TO FILE #################################################################
# create project folder
if not os.path.exists(projdir):
    os.makedirs(projdir)                    # create project folder if not present
os.chdir(projdir)                           # change to project folder

# write to .rpl file
print("Writing to file " + rplfile + "...")
lines = []                                  # list containing all lines of .rpl file

# add lines at the start of script
lines.append("ic_set_global geo_cad 0 toptol_userset\n")
lines.append("ic_set_global geo_cad 0.0 toler\n")
lines.append("ic_undo_group_begin\n")
lines.append("ic_geo_new_family GEOM\n")
lines.append("ic_boco_set_part_color GEOM\n")
lines.append("ic_empty_tetin\n")
lines.append("\n")


# add lines for point definition (geometry)
for pnt in pnts:
    lines.append("ic_point {} GEOM " + pnt.getname() + " " + str(pnt.getx()) + "," + str(pnt.gety()) + "," + str(pnt.getz()) + "\n")
lines.append("\n")

# add lines for curve definition (geometry)
lines.append("ic_set_global geo_cad 0 toptol_userset\n")
lines.append("ic_set_global geo_cad 4e-005 toler\n")
for crv in crvs:
    lines.append("ic_delete_geometry curve names " + crv.getname() + " 0\n")
    lines.append("ic_curve point GEOM " + crv.getname() + " {" + crv.getpnt1().getname() + " " + crv.getpnt2().getname() + "}\n")
lines.append("\n")

# add lines for part association
# fluid body part
lines.append("ic_geo_new_family " + fluid.getname() + "\n")
lines.append("ic_boco_set_part_color " + fluid.getname() + "\n")
lines.append("ic_geo_create_volume " + fluid.getloc() + " {} " + fluid.getname() + "\n")
lines.append("\n")
# boundary parts
for prt in prts:
    lines.append("ic_geo_set_part curve " + prt.getpartlist() + " " + prt.getname() + " 0\n")
lines.append("ic_delete_empty_parts\n")
lines.append("\n")

# add lines for blocking creation
lines.append("ic_hex_unload_blocking\n")
lines.append("ic_hex_initialize_mesh 2d new_numbering new_blocking " + fluid.getname() + "\n")
lines.append("ic_hex_unblank_blocks\n")
lines.append("ic_hex_multi_grid_level 0\n")
lines.append("ic_hex_projection_limit 0\n")
lines.append("ic_hex_default_bunching_law default 2.0\n")
lines.append("ic_hex_floating_grid off\n")
lines.append("ic_hex_transfinite_degree 1\n")
lines.append("ic_hex_unstruct_face_type one_tri\n")
lines.append("ic_hex_set_unstruct_face_method uniform_quad\n")
lines.append("ic_hex_set_n_tetra_smoothing_steps 20\n")
lines.append("ic_hex_error_messages off_minor\n")
lines.append("ic_hex_set_piercing 0\n")
lines.append("\n")

# add lines for block modifications
prtlist = fluid.getname()
for prt in prts:
    prtlist += " " + prt.getname()

for blk in blkg:
    # split block
    if isinstance(blk, Split):
        lines.append("ic_hex_undo_major_start split_grid\n")
        lines.append("ic_hex_split_grid " + str(blk.getvert1()) + " " + str(blk.getvert2()) + " " + blk.getpnt().getname() + " m GEOM " + prtlist + " VORFN\n")
        lines.append("ic_hex_undo_major_end split_grid\n")
    
    # delete block
    elif isinstance(blk, Delete):
        lines.append("ic_hex_mark_blocks unmark\n")
        lines.append("ic_hex_mark_blocks superblock " + str(blk.getblk()) + "\n")
        lines.append("ic_hex_change_element_id VORFN\n")

    # undefined
    else:
        lines.append("\n")
lines.append("\n")

# add lines for edge associations
for edge in edges:
    lines.append("ic_hex_undo_major_start set_edge_projection\n")
    lines.append("ic_hex_set_edge_projection " + str(edge.getvert1()) + " " + str(edge.getvert2()) + " 0 1 " + edge.getcrv().getname() + "\n")
    lines.append("ic_hex_undo_major_end set_edge_projection\n")
lines.append("\n")

# add lines for meshing
for mesh in mshg:
    lines.append("ic_hex_set_mesh " + str(mesh.getvert1()) + " " + str(mesh.getvert2()) + " n " + str(mesh.getnodes()) + " h1rel " + str(mesh.geth1rel()) + " h2rel " + str(mesh.geth2rel()) + " r1 " + str(mesh.getr1()) + " r2 " + str(mesh.getr2()) + " lmax " + str(mesh.getlmax()) + " " + mesh.getdistr() + " copy_to_parallel unlocked\n")
lines.append("\n")

# add lines at the end of script
lines.append("ic_undo_group_end\n")

# write lines to new .rpl file, overwrite old one if it exists
try:
    with open(rplfile, 'x') as file:
        print(" - writing new .rpl file")
        file.writelines(lines)
    file.close()
except FileExistsError:
    with open(rplfile, 'w') as file:
        print(" - overwriting existing .rpl file")
        file.writelines(lines)
    file.close()
print(" - done write to file\n")

# write to .conf file
print("Writing to file " + conffile + "...")
conf = []                                   # list containing all lines of .conf file

# project name
conf.append("Configuration file for " + projname + "\n")
conf.append("\n")

# geometry configuration
conf.append("Summary of geometric parameters:\n")
conf.append("x-dimension:\n")
conf.append("    Total domain height (H): " + str(h_t.getval()*1000.0) + " mm\n")
conf.append("    Thickness of film inlet (h_nu): " + str(h_nu.getval()*1000.0) + " mm\n")
conf.append("    Thickness of distributor (h_d): " + str(h_d.getval()*1000.0) + " mm\n")
conf.append("y-dimension:\n")
conf.append("    Total domain length (L): " + str(l_t.getval()*1000.0) + " mm\n")
conf.append("    Length of additional gas space (l_g): " + str(l_g.getval()*1000.0) + " mm\n")
conf.append("\n")

# mesh configuration
conf.append("Summary of meshing parameters:\n")
conf.append("x-dimension:\n")
conf.append("    h_nu: " + h_nu.getmesh()[-1] + "\n")
conf.append("    h_d: " + h_d.getmesh()[-1] + "\n")
conf.append("    h_g: " + h_g.getmesh()[-1] + "\n")
conf.append("y-dimension:\n")
conf.append("    l_t: " + l_t.getmesh()[-1] + "\n")
conf.append("    l_g: " + l_g.getmesh()[-1] + "\n")
conf.append("\n")

conf.append("\n######################################################################################################################################################################\n\n")
# geometry configuration to be read by this script
conf.append(meshtype + "\n")
conf.append("xgeom " + str(h_t.getval()) + " " + str(h_nu.getval()) + " " + str(h_d.getval()) + "\n")
conf.append("ygeom " + str(l_t.getval()) + " " + str(l_g.getval()) + "\n")
conf.append("\n")

# mesh configuration to be read by this script
conf.append("h_nu " + str(h_nu.getmesh()[:7]).replace("[", "").replace("]", "").replace("'", "").replace(",", "") + "\n")
conf.append("h_d " + str(h_d.getmesh()[:7]).replace("[", "").replace("]", "").replace("'", "").replace(",", "") + "\n")
conf.append("h_g " + str(h_g.getmesh()[:7]).replace("[", "").replace("]", "").replace("'", "").replace(",", "") + "\n")
conf.append("l_t " + str(l_t.getmesh()[:7]).replace("[", "").replace("]", "").replace("'", "").replace(",", "") + "\n")
conf.append("l_g " + str(l_g.getmesh()[:7]).replace("[", "").replace("]", "").replace("'", "").replace(",", "") + "\n")
conf.append("\n")

# write lines to new .conf file, overwrite old one if it exists
try:
    with open(conffile, 'x') as file:
        print(" - writing new .conf file")
        file.writelines(conf)
    file.close()
except FileExistsError:
    with open(conffile, 'w') as file:
        print(" - overwriting existing .conf file")
        file.writelines(conf)
    file.close()
print(" - done write to file\n")

print("##################################################################### DONE ######################################################################")
