# this script is used to generate an ICEM model with user defined dimensions and mesh parameters
# geometry type: 2D, smooth reactor wall
# the files rpl_gen_fnc.py and rpl_gen_obj.py are required to run this file


# specify part names (retaining default names recommended)
name_fluid = "FLUID"
name_finlet = "FILMINLET"
name_fwall = "FILMWALL"
name_foutlet = "FILMOUTLET"
name_gwall = "GASWALL"
name_gtop = "GASTOP"
name_distr = "DISTRIBUTOR"


# global mesh parameters, default meshing
size_film = 1.2e-5          # maximum x cell size in film [m]
size_distr = 2.4e-5         # maximum x cell size at distributor [m]
size_xmax = 1e-4            # maximum x cell size [m]
size_ymax = 1e-4            # maximum y cell size [m]


############################################################### DO NOT EDIT BELOW ###############################################################
# dependencies
import rpl_gen_fnc as fnc                       # function source file
import rpl_gen_obj as obj                       # class source file
import os                                       # operating system operations
from colorama import Fore, Style, init          # console output formatting (validated to run on a windows system)


# numerical precision (specify in obj!)
geomprec = obj.geomprec             # numerical precision for geometry operations
meshprec = obj.meshprec             # numerical precision for mesh calculations


################################################################# PROGRAM START #################################################################
# initialize console formatting
init(autoreset=True)


# change to directory containing the script
sourcedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(sourcedir)


# print script intoduction messages
print(f"{Style.BRIGHT}#################################################################### WELCOME ####################################################################{Style.RESET_ALL}")
print("\n\nThis is a script for the automatic generation of a 2D smooth mesh in ICEM.")
print("Different variants of this geometry can be created, which differ in minor features.")
print("For information on how to use this script, please refer to the documentation provided.")
print("\nIf not already present, it will create a project folder containing:\n\t> .rpl file to be read into ICEM\n\t> .conf file containing the parameters specified")
print("The created folder will be located in a folder corresponding to the geometry variant.")
print("\nSteps to generate the mesh in ICEM:\n\t1) Load the .rpl file (File > Replay Scripts > Load script file)\n\t2) Execute all commands (do all)")
input("\nPress any key to continue...")


# input geometry type
print(f"{Style.BRIGHT}\n\n############################################################### GEOMETRY VARIANTS ###############################################################{Style.RESET_ALL}")
print("\n\nDifferent variants are available for the film inlet region of the geometry.\nSee documentation for the differences between the variants.")


geomtype = "2D-smooth-"
xgeom = []
ygeom = []

# film inlet variants
while True:
    print("\nAvailable film inlet variants:")
    print("\t- 1: Domain with simple film inlet region\n\t\t- suitable for periodic boundaries")
    print("\t- 2: Domain with additional gas space above film inlet")
    q_inlettype = input("Choose inlet variant to be created:\n>>> ")

    if q_inlettype == "1" or q_inlettype == "2": 
        break
    else:
        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter the number corresponding to the variant.")

# film outlet variants
q_outlettype = "1"

# geometric variants
if q_inlettype == "1" and q_outlettype == "1":
    # type 1
    # simple film inlet
    # simple film outlet
    geomtype += "1"
    geomnum = 1

elif q_inlettype == "2" and q_outlettype == "1":
    # type 2
    # additional gas space above film inlet
    # simple film outlet
    geomtype += "2"
    geomnum = 2

# periodic boundaries for type 1
if geomnum == 1:
    while True:
        q_periodic = input("\nUse periodic boundaries? (y/n)\n>>> ").lower()

        if q_periodic == "y":
            periodic = True
            break
        elif q_periodic == "n":
            periodic = False
            break
        else:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.")
else:
    periodic = False

print(f"\nGeometry variant: {Fore.GREEN}'{geomtype}'{Style.RESET_ALL}") 

# add xgeom objects
xgeom.append(obj.Geometry(obj.ht_geomname, obj.ht_geomdescr))
xgeom.append(obj.Geometry(obj.hi_geomname, obj.hi_geomdescr))
xgeom.append(obj.Geometry(obj.hd_geomname, obj.hd_geomdescr))

# add ygeom objects
ygeom.append(obj.Geometry(obj.lt_geomname, obj.lt_geomdescr))
if q_inlettype == "2":
    ygeom.append(obj.Geometry(obj.lag_geomname, obj.lag_geomdescr))         # inlet type 2

# create and change to variant folder 
folderdir = os.path.join(sourcedir, geomtype)
if not os.path.exists(folderdir):
    os.makedirs(folderdir)
    print(f"\nCreated new folder {Fore.GREEN}~\{geomtype}{Style.RESET_ALL} for current variant.")
os.chdir(folderdir)


# project name input
print(f"{Style.BRIGHT}\n\n############################################################### PROJECT DEFINITION ##############################################################{Style.RESET_ALL}")
while True:    
    projname = input("Choose ICEM project name:\n>>> ")
    
    if fnc.checkname(folderdir, projname):
        break

# filename definition
print(f"\nCreating ICEM project {Fore.GREEN}'{projname}'.{Style.RESET_ALL}")
rplfile = projname + ".rpl"
conffile = projname + ".conf"
projdir = os.path.join(folderdir, projname)


# read from existing config file
print(f"{Style.BRIGHT}\n\n############################################################# REFERENCE FILE INPUT ##############################################################{Style.RESET_ALL}")
while True:
    # query to read from .conf file
    q_conf = input("Use an existing config file for input parameters? (y/n)\n>>> ").lower()
    
    if q_conf == "y":
        # get reference config file
        refconffile = fnc.getconf(sourcedir, geomtype)
        break
    elif q_conf == "n":
        break
    else:
        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.\n")    
 
    
################################################################ PARAMETER INPUT ################################################################
print(f"{Style.BRIGHT}\n\n################################################################ PARAMETER INPUT ################################################################{Style.RESET_ALL}")


# geometric parameters
print("\n\n############################################################## GEOMETRIC PARAMETERS #############################################################")
while True:
    # reference data only available if reference file has been defined
    if q_conf == "y":
        while True:
            # query whether geometry data from config file should be used
            q_confgeom = input("Use config file data for geometric parameters? (y/n)\n>>> ").lower()
            if q_confgeom == "y":
                break               
            elif q_confgeom == "n":
                print()
                print()
                break
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.")
    else:
        q_confgeom = "n"

    # using file input for geometric parameters
    if q_confgeom == "y":
        # extract and assign xgeom
        confxgeom = fnc.getconfgeom(refconffile, "xgeom")
        fnc.assignconfgeom(xgeom, confxgeom)
        
        # check xgeom for nonzero values and valid dimensions
        if not fnc.checkgeom(xgeom) or not fnc.checkxgeom(xgeom):
            # manual geometry input
            fnc.setxgeom(xgeom)
            
            # reference meshing not available if geometry allocation failed
            q_confgeom = "n"


        # extract and assign ygeom
        confygeom = fnc.getconfgeom(refconffile, "ygeom")
        fnc.assignconfgeom(ygeom, confygeom)
        
        # check ygeom for nonzero values and valid dimensions
        if not fnc.checkgeom(ygeom):
            # manual geometry input
            fnc.setygeom_smooth(ygeom)

            # reference meshing not available if geometry allocation failed
            q_confgeom = "n"

        
    # user defined input of geometric features
    if q_conf == "n" or q_confgeom == "n":
        # parameter definition in x
        print(f"{Style.BRIGHT}Parameters for x-dimension:{Style.RESET_ALL}")
        fnc.setxgeom(xgeom)

        # parameter definition in y
        print(f"{Style.BRIGHT}\n\nParameters for y-dimension:{Style.RESET_ALL}")
        fnc.setygeom_smooth(ygeom)
        

    # print summary of geometric parameters
    print(f"{Style.BRIGHT}\n\nSummary of geometric parameters:{Style.RESET_ALL}")
    print("x-dimension:")
    for geom in xgeom:
        geom.printinfo()
    print("y-dimension:")
    for geom in ygeom:
        geom.printinfo()
   
    # query to proceed with geometric values
    while True:
        q_proc1 = input("\nProceed with the above values? (y/n)\n>>> ").lower()
        if q_proc1 == "y":
            break
        elif q_proc1 == "n":
            if q_conf == "y":
                q_conf = "n"
            print()
            print()
            break
        else:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.")
    if q_proc1 == "y":
        break


# final values of geometric parameters
# x geometry parameters
ht_geom = fnc.getobj(obj.ht_geomname, xgeom).getval()           # total domain size
hi_geom = fnc.getobj(obj.hi_geomname, xgeom).getval()           # film inlet
hd_geom = fnc.getobj(obj.hd_geomname, xgeom).getval()           # distributor
hg_geom = ht_geom - (hi_geom + hd_geom)                         # gas space

# y geometry parameters
lt_geom = fnc.getobj(obj.lt_geomname, ygeom).getval()           # film wall
if q_inlettype == "2":
    lag_geom = fnc.getobj(obj.lag_geomname, ygeom).getval()     # inlet: additional gas space


# creating meshing sections based on final geometric parameters provided
xsects = []
ysects = []

# x-dimension 
xsects.append(obj.Section(obj.hi_sectname, hi_geom))            # film inlet
xsects.append(obj.Section(obj.hd_sectname, hd_geom))            # distributor
xsects.append(obj.Section(obj.hg_sectname, hg_geom))            # gas space

# y-dimension
ysects.append(obj.Section(obj.lt_sectname, lt_geom))            # structures
if q_inlettype == "2":
    ysects.append(obj.Section(obj.lag_sectname, lag_geom))      # inlet: additional gas space     


# meshing parameters
print("\n\n############################################################### MESHING PARAMETERS ##############################################################")
while True:
    # read meshing from config file if geometry parameters are identical
    if q_confgeom == "y":
        while True:
            q_confmesh = input("Use config file data for meshing parameters? (y/n)\n>>> ").lower()
            if q_confmesh == "y":
                break               
            elif q_confmesh == "n":
                print()
                print()
                break
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.")
    else:
        q_confmesh = "n"
    
    # using config file input for meshing parameters
    if q_confmesh == "y":
        # refinement factor definition
        factor = fnc.confmeshing_factor()

        # meshing with specified refinement factor
        # x-dimension
        fnc.confmeshing(refconffile, xsects, factor)
        
        # y-dimension
        fnc.confmeshing(refconffile, ysects, factor)
    

    # user defined input of geometric features
    if q_conf == "n" or q_confmesh == "n":
        while True:
            print(f"{Style.BRIGHT}Default meshing:{Style.RESET_ALL}")
            print("x-dimension:")
            print(f"\t- Within film section (h_nu): Uniform distribution of cells with maximum size of {round(size_film*1000000.0, meshprec)} µm.")
            print(f"\t- Within distributor section (h_d): Geometric1 distribution of cells, growth from {round(size_film*1000000.0, meshprec)} µm to {round(size_distr*1000000.0, meshprec)} µm.")
            print(f"\t- Within gas section (h_g): Geometric1 distribution of cells, growth from {round(size_distr*1000000.0, meshprec)} µm to {round(size_xmax*1000000.0, meshprec)} µm.")
            print("y-dimension:")
            print(f"\t- For all sections: Uniform distribution of cells with maximum size of {round(size_ymax*1000000.0, meshprec)} µm")
            
            # use default meshing parameters
            q_defmsh = input("Do you want to use default meshing parameters? (y/n)\n>>> ").lower()

            # default meshing
            if q_defmsh == "y":
                # x-dimension
                fnc.uniform(fnc.getobj(obj.hi_sectname, xsects), size_film)                 # film inlet
                fnc.geo1(fnc.getobj(obj.hd_sectname, xsects), size_film, size_distr)        # distributor
                fnc.geo1(fnc.getobj(obj.hg_sectname, xsects), size_distr, size_xmax)        # gas space

                # y-dimension
                fnc.uniform(fnc.getobj(obj.lt_sectname, ysects), size_ymax)                 # total domain
                if q_inlettype == "2":
                    fnc.uniform(fnc.getobj(obj.lag_sectname, ysects), size_ymax)            # inlet: additional gas space
                break
            
            # custom meshing
            elif q_defmsh == "n":
                # print custom meshing messages
                fnc.custommeshing_info()
                
                # parameter definition in x
                print(f"{Style.BRIGHT}\n\nMesh definition in x-dimension:{Style.RESET_ALL}")
                for sect in xsects:
                    fnc.custommeshing(sect)

                # parameter definition in y
                print(f"{Style.BRIGHT}\n\nMesh definition in y-dimension:{Style.RESET_ALL}")
                for sect in ysects:
                    fnc.custommeshing(sect)      
                break
            
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.")

    # print summary of meshing parameters
    print(f"{Style.BRIGHT}\n\nSummary of meshing parameters:{Style.RESET_ALL}")
    print("x-dimension:")
    for sect in xsects:
        sect.printinfo()
    print("y-dimension:")
    for sect in ysects:
        sect.printinfo()
    
    # query to proceed with meshing parameters
    while True:
        q_proc2 = input("\nProceed with the above values? (y/n)\n>>> ").lower()
        if q_proc2 == "y":
            break
        elif q_proc2 == "n":
            print()
            print()
            break
        else:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.")
    if q_proc2 == "y":
        break


# final values of meshing parameters
# x meshing parameters
hi_mesh = fnc.getobj(obj.hi_sectname, xsects).getmesh()         # film inlet
hd_mesh = fnc.getobj(obj.hd_sectname, xsects).getmesh()         # distributor
hg_mesh = fnc.getobj(obj.hg_sectname, xsects).getmesh()         # gas space

# y meshing parameters
lt_mesh = fnc.getobj(obj.lt_sectname, ysects).getmesh()         # film wall
if q_inlettype == "2":
    lag_mesh = fnc.getobj(obj.lag_sectname, ysects).getmesh()   # additional gas space


############################################################### SCRIPT GENERATION ###############################################################
print(f"{Style.BRIGHT}\n\n############################################################### SCRIPT GENERATION ###############################################################{Style.RESET_ALL}")

############################################################## GEOMETRY GENERATION ##############################################################
print("Generating geometry...")
# geometry object lists
prts = []       # parts
pnts = []       # points
crvs = []       # curves


# part creation
# body parts 
prts.append(obj.Body(name_fluid, ht_geom/2.0, lt_geom/2.0, 0.0))    # fluid

# boundary parts
prts.append(obj.Part(name_finlet))      # inlet
prts.append(obj.Part(name_fwall))       # film wall
prts.append(obj.Part(name_foutlet))     # film outlet
prts.append(obj.Part(name_gwall))       # gas wall
if not periodic:
    prts.append(obj.Part(name_gtop))        # gas top
    prts.append(obj.Part(name_distr))       # distributor
print("\t- done part setup")

 
# film inlet region
# inlet variant 1: simple film inlet
if q_inlettype == "1":
    # point definition
    # points at lt_geom
    pnts.append(obj.Point(ht_geom, lt_geom, 0.0))
    pnts.append(obj.Point((hi_geom + hd_geom), lt_geom, 0.0))
    pnts.append(obj.Point(hi_geom, lt_geom, 0.0))
    pnts.append(obj.Point(0.0, lt_geom, 0.0))


    # curve definition
    # curves in x direction
    crvs.append(obj.Curve(pnts[-4], pnts[-3]))
    if periodic:
        fnc.getobj(name_finlet, prts).addgeom(crvs[-1])
    else:
        fnc.getobj(name_gtop, prts).addgeom(crvs[-1])
    crvs.append(obj.Curve(pnts[-3], pnts[-2]))
    if periodic:
        fnc.getobj(name_finlet, prts).addgeom(crvs[-1])
    else:
        fnc.getobj(name_distr, prts).addgeom(crvs[-1])
    crvs.append(obj.Curve(pnts[-2], pnts[-1]))
    fnc.getobj(name_finlet, prts).addgeom(crvs[-1])


# inlet variant 2: additional gas space
elif q_inlettype == "2":
    # point definition
    # points at (lt_geom + lag_geom)
    pnts.append(obj.Point(ht_geom, (lt_geom + lag_geom), 0.0))
    pnts.append(obj.Point((hi_geom + hd_geom), (lt_geom + lag_geom), 0.0))
    
    # points at lt_geom
    pnts.append(obj.Point(ht_geom, lt_geom, 0.0))
    pnts.append(obj.Point((hi_geom + hd_geom), lt_geom, 0.0))
    pnts.append(obj.Point(hi_geom, lt_geom, 0.0))
    pnts.append(obj.Point(0.0, lt_geom, 0.0))


    # curve definition
    # curves in y direction
    crvs.append(obj.Curve(pnts[-6], pnts[-4]))
    fnc.getobj(name_gwall, prts).addgeom(crvs[-1])
    crvs.append(obj.Curve(pnts[-5], pnts[-3]))
    fnc.getobj(name_distr, prts).addgeom(crvs[-1])

    # curves in x direction
    crvs.append(obj.Curve(pnts[-6], pnts[-5]))
    fnc.getobj(name_gtop, prts).addgeom(crvs[-1])
    crvs.append(obj.Curve(pnts[-3], pnts[-2]))
    fnc.getobj(name_distr, prts).addgeom(crvs[-1])
    crvs.append(obj.Curve(pnts[-2], pnts[-1]))
    fnc.getobj(name_finlet, prts).addgeom(crvs[-1])
print("\t- done film inlet region")



# film outlet region
# outlet variant 1: simple film outlet
if q_outlettype == "1":
    # point definition
    # points at lt_geom
    pnts.append(obj.Point(ht_geom, 0.0, 0.0))
    pnts.append(obj.Point((hi_geom + hd_geom), 0.0, 0.0))
    pnts.append(obj.Point(hi_geom, 0.0, 0.0))
    pnts.append(obj.Point(0.0, 0.0, 0.0))

    # number of points of film outlet region
    numpnts_foutlet = 4

    # curve definition
    # curves in y direction
    crvs.append(obj.Curve(pnts[-numpnts_foutlet-4], pnts[-4]))
    fnc.getobj(name_gwall, prts).addgeom(crvs[-1])
    crvs.append(obj.Curve(pnts[-numpnts_foutlet-1], pnts[-1]))
    fnc.getobj(name_fwall, prts).addgeom(crvs[-1])

    # curves in x direction
    crvs.append(obj.Curve(pnts[-4], pnts[-3]))
    fnc.getobj(name_foutlet, prts).addgeom(crvs[-1])
    crvs.append(obj.Curve(pnts[-3], pnts[-2]))
    fnc.getobj(name_foutlet, prts).addgeom(crvs[-1])
    crvs.append(obj.Curve(pnts[-2], pnts[-1]))
    fnc.getobj(name_foutlet, prts).addgeom(crvs[-1])
print("\t- done film outlet region")



################################################################### BLOCKING ####################################################################
print("\nGenerating blocking...")
blkg = []        # blocking operations (split, deletion)
edges = []       # edge-curve associations


# block modification
# geometry type 1
if geomnum == 1:
    # block splits
    # film inlet region
    # x splits
    blkg.append(obj.Split(pnts[2], 13, 21, prts))       # hi_geom
    blkg.append(obj.Split(pnts[1], 34, 21, prts))       # (hi_geom + hd_geom)
    print("\t- done x splits")


# geometry type 2
elif geomnum == 2:
    # block splits
    # film inlet region
    # x splits
    blkg.append(obj.Split(pnts[4], 13, 21, prts))       # hi_geom
    blkg.append(obj.Split(pnts[3], 34, 21, prts))       # (hi_geom + hd_geom)
    print("\t- done x splits")

    # y splits
    blkg.append(obj.Split(pnts[5], 11, 13, prts))       # lt_geom
    print("\t- done y splits")


    # block deletion
    # film inlet region
    blkg.append(obj.Delete(16))                         # delete block above inlet
    blkg.append(obj.Delete(17))                         # delete block above inlet


# edge-curve associations
print("\nAssociating edges to curves...")


# geometry type 1
if geomnum == 1:
    # film inlet region
    # x direction
    edges.append(obj.Edge(38, 21, crvs[0]))
    edges.append(obj.Edge(34, 38, crvs[1]))
    edges.append(obj.Edge(13, 34, crvs[2]))
    print("\t- done film inlet region")


    # film outlet region
    # y direction
    edges.append(obj.Edge(19, 21, crvs[-5]))
    edges.append(obj.Edge(11, 13, crvs[-4]))
    
    # x direction
    edges.append(obj.Edge(37, 19, crvs[-3]))
    edges.append(obj.Edge(33, 37, crvs[-2]))
    edges.append(obj.Edge(11, 33, crvs[-1]))
    print("\t- done film outlet region")


# geometry type 2
elif geomnum == 2:
    # film inlet region
    # y direction
    edges.append(obj.Edge(44, 21, crvs[0]))
    edges.append(obj.Edge(43, 38, crvs[1]))
    
    # x direction
    edges.append(obj.Edge(38, 21, crvs[2]))
    edges.append(obj.Edge(42, 43, crvs[3]))
    edges.append(obj.Edge(41, 42, crvs[4]))
    print("\t- done film inlet region")


    # film outlet region
    # y direction
    edges.append(obj.Edge(19, 44, crvs[-5]))
    edges.append(obj.Edge(11, 41, crvs[-4]))
    
    # x direction
    edges.append(obj.Edge(37, 19, crvs[-3]))
    edges.append(obj.Edge(33, 37, crvs[-2]))
    edges.append(obj.Edge(11, 33, crvs[-1]))
    print("\t- done film outlet region")


#################################################################### MESHING ####################################################################
print("\nMeshing...")
mshg = []        # meshing operations


# geometry type 1
if geomnum == 1:
    # x direction
    mshg.append(obj.Mesh(13, 34, hi_mesh))      # film
    mshg.append(obj.Mesh(34, 38, hd_mesh))      # distributor
    mshg.append(obj.Mesh(38, 21, hg_mesh))      # gas space
    print("\t- done x direction")


    # y direction
    mshg.append(obj.Mesh(11, 13, lt_mesh))     # total domain
    print("\t- done y direction")


# geometry type 2
elif geomnum == 2:
    # x direction
    mshg.append(obj.Mesh(41, 42, hi_mesh))      # film
    mshg.append(obj.Mesh(42, 43, hd_mesh))      # distributor
    mshg.append(obj.Mesh(43, 44, hg_mesh))      # gas space
    print("\t- done x direction")


    # y direction
    mshg.append(obj.Mesh(43, 38, lag_mesh))     # additional gas space
    mshg.append(obj.Mesh(11, 41, lt_mesh))      # total domain
    print("\t- done y direction")



################################################################# WRITE TO FILE #################################################################
print(f"{Style.BRIGHT}\n\n################################################################# WRITE TO FILE #################################################################{Style.RESET_ALL}")
# create project folder
if not os.path.exists(projdir):
    os.makedirs(projdir)                    # create project folder if not present
os.chdir(projdir)                           # change to project folder

# write to .rpl file
print("Writing to file " + rplfile + "...")
rpllines = []                               # list containing all lines of .rpl file

# add lines at the start of script
rpllines = fnc.rpl_start(rpllines)


# add lines for point definition (geometry)
rpllines = fnc.rpl_obj(rpllines, pnts)

# add lines for curve definition (geometry)
rpllines = fnc.rpl_obj(rpllines, crvs)

# add lines for part association (geometry)
rpllines = fnc.rpl_obj(rpllines, prts)

# add lines for blocking creation (blocking)
rpllines = fnc.rpl_2Dblocking(rpllines, fnc.getobj(name_fluid, prts))

# add lines for block modifications (blocking)
rpllines = fnc.rpl_obj(rpllines, blkg)

# add lines for blocking associations (blocking)
rpllines = fnc.rpl_obj(rpllines, edges)

# add lines for meshing (meshing)
rpllines = fnc.rpl_obj(rpllines, mshg)

# add lines at the end of script
rpllines = fnc.rpl_end(rpllines)

# write lines to new .rpl file, overwrite old one if it exists
try:
    with open(rplfile, 'x') as file:
        print(f" - {Fore.GREEN}writing new .rpl file{Style.RESET_ALL}")
        file.writelines(rpllines)
    file.close()
except FileExistsError:
    with open(rplfile, 'w') as file:
        print(f" - {Fore.RED}overwriting existing .rpl file{Style.RESET_ALL}")
        file.writelines(rpllines)
    file.close()
print(" - done write to file")


# write to .conf file
print("\nWriting to file " + conffile + "...")
conflines = []                                   # list containing all lines of .conf file

# project name
conflines = fnc.conf_start(conflines, projname)

# geometry configuration (user)
conflines = fnc.conf_geom2D(conflines, xgeom, ygeom)

# mesh configuration (user)
conflines = fnc.conf_mesh2D(conflines, xsects, ysects)

# mesh type
conflines = fnc.conf_type(conflines, geomtype)

# geometry configuration (script)
conflines = fnc.conf_geomdata(conflines, "xgeom", xgeom)
conflines = fnc.conf_geomdata(conflines, "ygeom", ygeom)

# mesh configuration (script)
conflines = fnc.conf_meshdata(conflines, xsects)
conflines = fnc.conf_meshdata(conflines, ysects)

# write lines to new .conf file, overwrite old one if it exists
try:
    with open(conffile, 'x') as file:
        print(f" - {Fore.GREEN}writing new .conf file{Style.RESET_ALL}")
        file.writelines(conflines)
    file.close()
except FileExistsError:
    with open(conffile, 'w') as file:
        print(f" - {Fore.RED}overwriting existing .conf file{Style.RESET_ALL}")
        file.writelines(conflines)
    file.close()
print(" - done write to file")

print(f"{Style.BRIGHT}{Fore.GREEN}\n\n##################################################################### DONE ######################################################################{Style.RESET_ALL}")