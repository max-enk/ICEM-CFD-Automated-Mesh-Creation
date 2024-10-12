# this script is used to generate an ICEM model with user defined dimensions and mesh parameters
# geometry type: 3D, horizontal structures
# the files rpl_gen_fnc.py and rpl_gen_obj.py are required to run this file


# specify part names (retaining default names recommended)
name_fluid = "FLUID"
name_finlet = "FILMINLET"
name_fwall = "FILMWALL"
name_foutlet = "FILMOUTLET"
name_gwall = "GASWALL"
name_gtop = "GASTOP"
name_distr = "DISTRIBUTOR"
name_sides = "SIDES"


# global mesh parameters, default meshing
size_film = 1.2e-5          # maximum x cell size in film and z cell size at walls [m]
size_distr = 1e-4           # maximum x cell size at distributor [m]
size_xmax = 4e-4            # maximum x cell size [m]
size_ymax = 4e-4            # maximum y cell size [m]
size_zmax = 4e-4            # maximum z cell size [m]


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
print("\n\nThis is a script for the automatic generation of a 3D mesh with horizontal structures in ICEM.")
print("Different variants of this geometry can be created, which differ in minor features.")
print("For information on how to use this script, please refer to the documentation provided.")
print("\nIf not already present, it will create a project folder containing:\n\t> .rpl file to be read into ICEM\n\t> .conf file containing the parameters specified")
print("The created folder will be located in a folder corresponding to the geometry variant.")
print("\nSteps to generate the mesh in ICEM:\n\t1) Load the .rpl file (File > Replay Scripts > Load script file)\n\t2) Execute all commands (do all)")
input("\nPress any key to continue...")


# input geometry type
print(f"{Style.BRIGHT}\n\n############################################################### GEOMETRY VARIANTS ###############################################################{Style.RESET_ALL}")
print("\n\nDifferent variants are available for the film inlet region of the geometry.\nSee documentation for the differences between the variants.")


geomtype = "3D-horizontal-"
xgeom = []
ygeom = []
zgeom = []

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
xgeom.append(obj.Geometry(obj.dgr_geomname, obj.dgr_geomdescr))

# add ygeom objects
ygeom.append(obj.Geometry(obj.lt_geomname, obj.lt_geomdescr))
if q_inlettype == "2":
    ygeom.append(obj.Geometry(obj.lag_geomname, obj.lag_geomdescr))         # inlet type 2
ygeom.append(obj.Geometry(obj.ls_geomname, obj.ls_geomdescr))
ygeom.append(obj.Geometry(obj.lgr_geomname, obj.lgr_geomdescr))
ygeom.append(obj.Geometry(obj.li_geomname, obj.li_geomdescr))
ygeom.append(obj.Geometry(obj.lo_geomname, obj.lo_geomdescr))
ygeom.append(obj.Geometry(obj.ns_geomname, obj.ns_geomdescr))

# add zgeom objects
zgeom.append(obj.Geometry(obj.wt_geomname, obj.wt_geomdescr))
zgeom.append(obj.Geometry(obj.wc_geomname, obj.wc_geomdescr))
zgeom.append(obj.Geometry(obj.ws_geomname, obj.ws_geomdescr))

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
        if not fnc.checkgeom(ygeom) or not fnc.checkygeom_hstruct(ygeom):
            # manual geometry input
            fnc.setygeom_hstruc(ygeom)

            # reference meshing not available if geometry allocation failed
            q_confgeom = "n"


        # extract and assign zgeom
        confzgeom = fnc.getconfgeom(refconffile, "zgeom")
        fnc.assignconfgeom(zgeom, confzgeom)
        
        # check zgeom for nonzero values and valid dimensions
        if not fnc.checkgeom(zgeom) or not fnc.checkzgeom(zgeom):
            # manual geometry input
            fnc.setzgeom(zgeom)

            # reference meshing not available if geometry allocation failed
            q_confgeom = "n"

        
    # user defined input of geometric features
    if q_conf == "n" or q_confgeom == "n":
        # parameter definition in x
        print(f"{Style.BRIGHT}Parameters for x-dimension:{Style.RESET_ALL}")
        fnc.setxgeom(xgeom)

        # parameter definition in y
        print(f"{Style.BRIGHT}\n\nParameters for y-dimension:{Style.RESET_ALL}")
        fnc.setygeom_hstruc(ygeom)
        
        # parameter definition in z
        print(f"{Style.BRIGHT}\n\nParameters for z-dimension:{Style.RESET_ALL}")
        fnc.setzgeom(zgeom)
        

    # print summary of geometric parameters
    print(f"{Style.BRIGHT}\n\nSummary of geometric parameters:{Style.RESET_ALL}")
    print("x-dimension:")
    for geom in xgeom:
        geom.printinfo()
    print("y-dimension:")
    for geom in ygeom:
        geom.printinfo()
    print("z-dimension:")
    for geom in zgeom:
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
dgr_geom = fnc.getobj(obj.dgr_geomname, xgeom).getval()         # grooves

# y geometry parameters
lt_geom = fnc.getobj(obj.lt_geomname, ygeom).getval()           # film wall
if q_inlettype == "2":
    lag_geom = fnc.getobj(obj.lag_geomname, ygeom).getval()     # inlet: additional gas space
ls_geom = fnc.getobj(obj.ls_geomname, ygeom).getval()           # structures
lgr_geom = fnc.getobj(obj.lgr_geomname, ygeom).getval()         # grooves
li_geom = fnc.getobj(obj.li_geomname, ygeom).getval()           # smooth wall at inlet
lo_geom = fnc.getobj(obj.lo_geomname, ygeom).getval()           # smooth wall at outlet
ns = fnc.getobj(obj.ns_geomname, ygeom).getval()                # number of structures

# z geometry parameters
wt_geom = fnc.getobj(obj.wt_geomname, zgeom).getval()           # total domain size
wc_geom = fnc.getobj(obj.wc_geomname, zgeom).getval()           # central section
ws_geom = fnc.getobj(obj.ws_geomname, zgeom).getval()           # side sections


# creating meshing sections based on final geometric parameters provided
xsects = []
ysects = []
zsects = []

# x-dimension 
xsects.append(obj.Section(obj.hi_sectname, hi_geom))            # film inlet
xsects.append(obj.Section(obj.hd_sectname, hd_geom))            # distributor
xsects.append(obj.Section(obj.hg_sectname, hg_geom))            # gas space
xsects.append(obj.Section(obj.dgr_sectname, dgr_geom))          # grooves

# y-dimension
if q_inlettype == "2":
    ysects.append(obj.Section(obj.lag_sectname, lag_geom))      # inlet: additional gas space
ysects.append(obj.Section(obj.ls_sectname, ls_geom))            # structures
ysects.append(obj.Section(obj.lgr_sectname, lgr_geom))          # grooves
ysects.append(obj.Section(obj.li_sectname, li_geom))            # smooth wall at inlet
ysects.append(obj.Section(obj.lo_sectname, lo_geom))            # smooth wall at outlet

# z-dimension
zsects.append(obj.Section(obj.ws1_sectname, ws_geom))           # side section 1
zsects.append(obj.Section(obj.wc_sectname, wc_geom))            # central section
zsects.append(obj.Section(obj.ws2_sectname, ws_geom))           # side section 2          


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

        # z-dimension
        fnc.confmeshing(refconffile, zsects, factor)
    

    # user defined input of geometric features
    if q_conf == "n" or q_confmesh == "n":
        while True:
            print(f"{Style.BRIGHT}Default meshing:{Style.RESET_ALL}")
            print("x-dimension:")
            print(f"\t- Within film and groove sections (d_gr, h_nu): Uniform distribution of cells with maximum size of {round(size_film*1000000.0, meshprec)} µm.")
            print(f"\t- Within distributor section (h_d): Geometric1 distribution of cells, growth from {round(size_film*1000000.0, meshprec)} µm to {round(size_distr*1000000.0, meshprec)} µm.")
            print(f"\t- Within gas section (h_g): Geometric1 distribution of cells, growth from {round(size_distr*1000000.0, meshprec)} µm to {round(size_xmax*1000000.0, meshprec)} µm.")
            print("y-dimension:")
            print(f"\t- For all sections: Uniform distribution of cells with maximum size of {round(size_ymax*1000000.0, meshprec)} µm")
            print("z-dimension:")
            print(f"\t- Within central section (w_c): Uniform distribution of cells with maximum size of {round(size_zmax*1000000.0, meshprec)} µm")
            print(f"\t- Within side sections (w_s1, w_s2): Geometric1/2 distribution of cells, growth from {round(size_film*1000000.0, meshprec)} µm (at side walls) to {round(size_zmax*1000000.0, meshprec)} µm\n")
            
            # use default meshing parameters
            q_defmsh = input("Do you want to use default meshing parameters? (y/n)\n>>> ").lower()

            # default meshing
            if q_defmsh == "y":
                # x-dimension
                fnc.uniform(fnc.getobj(obj.hi_sectname, xsects), size_film)                 # film inlet
                fnc.geo1(fnc.getobj(obj.hd_sectname, xsects), size_film, size_distr)        # distributor
                fnc.geo1(fnc.getobj(obj.hg_sectname, xsects), size_distr, size_xmax)        # gas space
                fnc.uniform(fnc.getobj(obj.dgr_sectname, xsects), size_film)                # grooves

                # y-dimension
                if q_inlettype == "2":
                    fnc.uniform(fnc.getobj(obj.lag_sectname, ysects), size_ymax)            # inlet: additional gas space
                fnc.uniform(fnc.getobj(obj.ls_sectname, ysects), size_ymax)                 # structures
                fnc.uniform(fnc.getobj(obj.lgr_sectname, ysects), size_ymax)                # grooves
                fnc.uniform(fnc.getobj(obj.li_sectname, ysects), size_ymax)                 # smooth wall at inlet
                fnc.uniform(fnc.getobj(obj.lo_sectname, ysects), size_ymax)                 # smooth wall at outlet

                # z-dimension
                fnc.uniform(fnc.getobj(obj.wc_sectname, zsects), size_zmax)                 # center
                fnc.geo1(fnc.getobj(obj.ws1_sectname, zsects), size_film, size_zmax)        # side section 1
                fnc.geo2(fnc.getobj(obj.ws2_sectname, zsects), size_film, size_zmax)        # side section 2
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

                # parameter definition in z
                print(f"{Style.BRIGHT}\n\nMesh definition in z-dimension:{Style.RESET_ALL}")
                for sect in zsects:
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
    print("z-dimension:")
    for sect in zsects:
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
dgr_mesh = fnc.getobj(obj.dgr_sectname, xsects).getmesh()       # grooves

# y meshing parameters
if q_inlettype == "2":
    lag_mesh = fnc.getobj(obj.lag_sectname, ysects).getmesh()   # additional gas space
ls_mesh = fnc.getobj(obj.ls_sectname, ysects).getmesh()         # structures
lgr_mesh = fnc.getobj(obj.lgr_sectname, ysects).getmesh()       # grooves
li_mesh = fnc.getobj(obj.li_sectname, ysects).getmesh()         # smooth wall at inlet
lo_mesh = fnc.getobj(obj.lo_sectname, ysects).getmesh()         # smooth wall at outlet

# z meshing parameters
wc_mesh = fnc.getobj(obj.wc_sectname, zsects).getmesh()         # central section
ws1_mesh = fnc.getobj(obj.ws1_sectname, zsects).getmesh()       # side section 1
ws2_mesh = fnc.getobj(obj.ws2_sectname, zsects).getmesh()       # side section 2


############################################################### SCRIPT GENERATION ###############################################################
print(f"{Style.BRIGHT}\n\n############################################################### SCRIPT GENERATION ###############################################################{Style.RESET_ALL}")

############################################################## GEOMETRY GENERATION ##############################################################
print("Generating geometry...")
# geometry object lists
prts = []       # parts
pnts = []       # points
crvs = []       # curves
srfs = []       # surfaces


# part creation
# body parts 
prts.append(obj.Body(name_fluid, ht_geom/2.0, lt_geom/2.0, wt_geom/2.0))    # fluid

# boundary parts
prts.append(obj.Part(name_finlet))      # inlet
prts.append(obj.Part(name_fwall))       # film wall
prts.append(obj.Part(name_foutlet))     # film outlet
prts.append(obj.Part(name_gwall))       # gas wall
if not periodic:
    prts.append(obj.Part(name_gtop))    # gas top
    prts.append(obj.Part(name_distr))   # distributor
prts.append(obj.Part(name_sides))       # sides
print("\t- done part setup")



# outer z coordinates
zbounds = [0.0, wt_geom]

 
# film inlet region
# inlet variant 1: simple film inlet
if q_inlettype == "1":
    for bound in zbounds:
        # point definition
        # points at lt_geom
        pnts.append(obj.Point(ht_geom, lt_geom, bound))
        pnts.append(obj.Point((hi_geom + hd_geom), lt_geom, bound))
        pnts.append(obj.Point(hi_geom, lt_geom, bound))
        pnts.append(obj.Point(0.0, lt_geom, bound))
        
        # points at (lt_geom - li_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom - li_geom), bound))
        pnts.append(obj.Point((hi_geom + hd_geom), (lt_geom - li_geom), bound))
        pnts.append(obj.Point(hi_geom, (lt_geom - li_geom), bound))
        pnts.append(obj.Point(0.0, (lt_geom - li_geom), bound))
        pnts.append(obj.Point(-1.0*dgr_geom, (lt_geom - li_geom), bound))

        # points at (lt_geom - li_geom - lgr_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom - li_geom - lgr_geom), bound))
        pnts.append(obj.Point((hi_geom + hd_geom), (lt_geom - li_geom - lgr_geom), bound))
        pnts.append(obj.Point(hi_geom, (lt_geom - li_geom - lgr_geom), bound))
        pnts.append(obj.Point(0.0, (lt_geom - li_geom - lgr_geom), bound))
        pnts.append(obj.Point(-1.0*dgr_geom, (lt_geom - li_geom - lgr_geom), bound))
        

        # curve definition
        # curves in y direction
        crvs.append(obj.Curve(pnts[-14], pnts[-10]))
        crvs.append(obj.Curve(pnts[-10], pnts[-5]))

        crvs.append(obj.Curve(pnts[-13], pnts[-9]))
        crvs.append(obj.Curve(pnts[-9], pnts[-4]))

        crvs.append(obj.Curve(pnts[-12], pnts[-8]))
        crvs.append(obj.Curve(pnts[-8], pnts[-3]))

        crvs.append(obj.Curve(pnts[-11], pnts[-7]))
        crvs.append(obj.Curve(pnts[-7], pnts[-2]))
        
        crvs.append(obj.Curve(pnts[-6], pnts[-1]))

        # curves in x direction
        crvs.append(obj.Curve(pnts[-14], pnts[-13]))
        crvs.append(obj.Curve(pnts[-13], pnts[-12]))
        crvs.append(obj.Curve(pnts[-12], pnts[-11]))

        crvs.append(obj.Curve(pnts[-10], pnts[-9]))
        crvs.append(obj.Curve(pnts[-9], pnts[-8]))
        crvs.append(obj.Curve(pnts[-8], pnts[-7]))
        crvs.append(obj.Curve(pnts[-7], pnts[-6]))

        crvs.append(obj.Curve(pnts[-5], pnts[-4]))
        crvs.append(obj.Curve(pnts[-4], pnts[-3]))
        crvs.append(obj.Curve(pnts[-3], pnts[-2]))
        crvs.append(obj.Curve(pnts[-2], pnts[-1]))


        # surface definition (sides)
        # surfaces at film inlet
        srfs.append(obj.Surface([crvs[-20], crvs[-11], crvs[-8], crvs[-18]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-18], crvs[-10], crvs[-7], crvs[-16]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-16], crvs[-9], crvs[-6], crvs[-14]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])

        # surfaces at first groove
        srfs.append(obj.Surface([crvs[-19], crvs[-8], crvs[-4], crvs[-17]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-17], crvs[-7], crvs[-3], crvs[-15]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-15], crvs[-6], crvs[-2], crvs[-13]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-13], crvs[-5], crvs[-1], crvs[-12]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])

    # number of points and curves of film inlet region
    numpnts_finlet_bounds = 14          # number of points per bound
    numcrvs_finlet_bounds = 20          # number of curves per bound
    
    # curves in z direction
    zpnts_finlet = [-14, -13, -12, -11, -10, -7, -6, -5, -2, -1]        # points for curves between zbounds of film inlet region 
    for pnt in zpnts_finlet:
        crvs.append(obj.Curve(pnts[pnt], pnts[pnt-numpnts_finlet_bounds]))
    numcrvs_finlet_vert = int(len(zpnts_finlet))        # number of curves between bounds

    # surfaces between zbounds
    # film wall 
    srfs.append(obj.Surface([crvs[-7], crvs[-5], crvs[-numcrvs_finlet_vert-14], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-14]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-5], crvs[-4], crvs[-numcrvs_finlet_vert-5], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-5]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-4], crvs[-1], crvs[-numcrvs_finlet_vert-12], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-12]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-1], crvs[-2], crvs[-numcrvs_finlet_vert-1], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-1]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])

    # film inlet
    srfs.append(obj.Surface([crvs[-7], crvs[-8], crvs[-numcrvs_finlet_vert-9], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-9]]))
    fnc.getobj(name_finlet, prts).addgeom(srfs[-1])

    # distributor
    srfs.append(obj.Surface([crvs[-8], crvs[-9], crvs[-numcrvs_finlet_vert-10], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-10]]))
    if periodic:
        fnc.getobj(name_finlet, prts).addgeom(srfs[-1])
    else:
        fnc.getobj(name_distr, prts).addgeom(srfs[-1])

    # gas top
    srfs.append(obj.Surface([crvs[-9], crvs[-10], crvs[-numcrvs_finlet_vert-11], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-11]]))
    if periodic:
        fnc.getobj(name_finlet, prts).addgeom(srfs[-1])
    else:    
        fnc.getobj(name_gtop, prts).addgeom(srfs[-1])

    # gas wall
    srfs.append(obj.Surface([crvs[-10], crvs[-6], crvs[-numcrvs_finlet_vert-20], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-20]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-6], crvs[-3], crvs[-numcrvs_finlet_vert-19], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-19]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])


# inlet variant 2: additional gas space
elif q_inlettype == "2":
    for bound in zbounds:
        # point definition
        # points at (lt_geom + lag_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom + lag_geom), bound))
        pnts.append(obj.Point((hi_geom + hd_geom), (lt_geom + lag_geom), bound))
        
        # points at lt_geom
        pnts.append(obj.Point(ht_geom, lt_geom, bound))
        pnts.append(obj.Point((hi_geom + hd_geom), lt_geom, bound))
        pnts.append(obj.Point(hi_geom, lt_geom, bound))
        pnts.append(obj.Point(0.0, lt_geom, bound))
        
        # points at (lt_geom - li_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom - li_geom), bound))
        pnts.append(obj.Point((hi_geom + hd_geom), (lt_geom - li_geom), bound))
        pnts.append(obj.Point(hi_geom, (lt_geom - li_geom), bound))
        pnts.append(obj.Point(0.0, (lt_geom - li_geom), bound))
        pnts.append(obj.Point(-1.0*dgr_geom, (lt_geom - li_geom), bound))

        # points at (lt_geom - li_geom - lgr_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom - li_geom - lgr_geom), bound))
        pnts.append(obj.Point((hi_geom + hd_geom), (lt_geom - li_geom - lgr_geom), bound))
        pnts.append(obj.Point(hi_geom, (lt_geom - li_geom - lgr_geom), bound))
        pnts.append(obj.Point(0.0, (lt_geom - li_geom - lgr_geom), bound))
        pnts.append(obj.Point(-1.0*dgr_geom, (lt_geom - li_geom - lgr_geom), bound))
        

        # curve definition
        # curves in y direction
        crvs.append(obj.Curve(pnts[-16], pnts[-14]))
        crvs.append(obj.Curve(pnts[-14], pnts[-10]))
        crvs.append(obj.Curve(pnts[-10], pnts[-5]))

        crvs.append(obj.Curve(pnts[-15], pnts[-13]))
        crvs.append(obj.Curve(pnts[-13], pnts[-9]))
        crvs.append(obj.Curve(pnts[-9], pnts[-4]))

        crvs.append(obj.Curve(pnts[-12], pnts[-8]))
        crvs.append(obj.Curve(pnts[-8], pnts[-3]))

        crvs.append(obj.Curve(pnts[-11], pnts[-7]))
        crvs.append(obj.Curve(pnts[-7], pnts[-2]))
        
        crvs.append(obj.Curve(pnts[-6], pnts[-1]))

        # curves in x direction
        crvs.append(obj.Curve(pnts[-16], pnts[-15]))
        crvs.append(obj.Curve(pnts[-14], pnts[-13]))
        crvs.append(obj.Curve(pnts[-13], pnts[-12]))
        crvs.append(obj.Curve(pnts[-12], pnts[-11]))

        crvs.append(obj.Curve(pnts[-10], pnts[-9]))
        crvs.append(obj.Curve(pnts[-9], pnts[-8]))
        crvs.append(obj.Curve(pnts[-8], pnts[-7]))
        crvs.append(obj.Curve(pnts[-7], pnts[-6]))

        crvs.append(obj.Curve(pnts[-5], pnts[-4]))
        crvs.append(obj.Curve(pnts[-4], pnts[-3]))
        crvs.append(obj.Curve(pnts[-3], pnts[-2]))
        crvs.append(obj.Curve(pnts[-2], pnts[-1]))


        # surface definition (sides)
        # surface of additional gas space
        srfs.append(obj.Surface([crvs[-23], crvs[-12], crvs[-11], crvs[-20]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])

        # surfaces at film inlet
        srfs.append(obj.Surface([crvs[-22], crvs[-11], crvs[-8], crvs[-19]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-19], crvs[-10], crvs[-7], crvs[-17]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-17], crvs[-9], crvs[-6], crvs[-15]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])

        # surfaces at first groove
        srfs.append(obj.Surface([crvs[-21], crvs[-8], crvs[-4], crvs[-18]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-18], crvs[-7], crvs[-3], crvs[-16]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-16], crvs[-6], crvs[-2], crvs[-14]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-14], crvs[-5], crvs[-1], crvs[-13]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])

    # number of points and curves of film inlet region
    numpnts_finlet_bounds = 16          # number of points per bound
    numcrvs_finlet_bounds = 23          # number of curves per bound
    
    # curves in z direction
    zpnts_finlet = [-16, -15, -14, -13, -12, -11, -10, -7, -6, -5, -2, -1]      # points for curves between zbounds of film inlet region 
    for pnt in zpnts_finlet:
        crvs.append(obj.Curve(pnts[pnt], pnts[pnt-numpnts_finlet_bounds]))
    numcrvs_finlet_vert = int(len(zpnts_finlet))        # number of curves between bounds

    # surfaces between zbounds
    # film wall 
    srfs.append(obj.Surface([crvs[-7], crvs[-5], crvs[-numcrvs_finlet_vert-15], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-15]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-5], crvs[-4], crvs[-numcrvs_finlet_vert-5], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-5]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-4], crvs[-1], crvs[-numcrvs_finlet_vert-13], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-13]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-1], crvs[-2], crvs[-numcrvs_finlet_vert-1], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-1]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])

    # film inlet
    srfs.append(obj.Surface([crvs[-7], crvs[-8], crvs[-numcrvs_finlet_vert-9], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-9]]))
    fnc.getobj(name_finlet, prts).addgeom(srfs[-1])

    # distributor
    srfs.append(obj.Surface([crvs[-8], crvs[-9], crvs[-numcrvs_finlet_vert-10], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-10]]))
    fnc.getobj(name_distr, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-9], crvs[-11], crvs[-numcrvs_finlet_vert-20], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-20]]))
    fnc.getobj(name_distr, prts).addgeom(srfs[-1])

    # gas top
    srfs.append(obj.Surface([crvs[-11], crvs[-12], crvs[-numcrvs_finlet_vert-12], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-12]]))   
    fnc.getobj(name_gtop, prts).addgeom(srfs[-1])

    # gas wall
    srfs.append(obj.Surface([crvs[-12], crvs[-10], crvs[-numcrvs_finlet_vert-23], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-23]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-10], crvs[-6], crvs[-numcrvs_finlet_vert-22], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-22]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-6], crvs[-3], crvs[-numcrvs_finlet_vert-21], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-21]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])
print("\t- done film inlet region")



# structures
for i in range(ns):
    # points for curves between zbounds of structures
    zpnts_struc = [-10, -7, -6, -5, -2, -1]
    numcrvs_struc_vert = len(zpnts_struc)
    

    for j in range(len(zbounds)):
        # point definition
        # first row of points, first structure, first zbound
        if i == 0 and j == 0:
            for k in range(5):
                pnts.append(obj.Point(pnts[-numpnts_finlet_bounds-5].getx(), (pnts[-numpnts_finlet_bounds-5].gety() - ls_geom), zbounds[j]))
        # first row of points, rest of structures
        else:
            for k in range(5):
                pnts.append(obj.Point(pnts[-15].getx(), (pnts[-15].gety() - ls_geom), zbounds[j]))    

        # second row of points
        for k in range(5):
            pnts.append(obj.Point(pnts[-5].getx(), (pnts[-5].gety() - lgr_geom), zbounds[j]))
        
        # number of points of structures
        numpnts_struc_bounds = 10          # number of points per bound
        
        # curve definition
        # first structure, first zbound
        if i == 0 and j == 0:
            pnt1 = -numpnts_struc_bounds-numpnts_finlet_bounds-5
            pnt2 = -numpnts_struc_bounds-numpnts_finlet_bounds-4
            pnt3 = -numpnts_struc_bounds-numpnts_finlet_bounds-3
            pnt4 = -numpnts_struc_bounds-numpnts_finlet_bounds-2
        # rest of structures
        else:
            pnt1 = -2*numpnts_struc_bounds-5
            pnt2 = -2*numpnts_struc_bounds-4
            pnt3 = -2*numpnts_struc_bounds-3
            pnt4 = -2*numpnts_struc_bounds-2
        
        # curves in y direction
        crvs.append(obj.Curve(pnts[pnt1], pnts[-10]))
        crvs.append(obj.Curve(pnts[-10], pnts[-5]))
        crvs.append(obj.Curve(pnts[pnt2], pnts[-9]))
        crvs.append(obj.Curve(pnts[-9], pnts[-4]))
        crvs.append(obj.Curve(pnts[pnt3], pnts[-8]))
        crvs.append(obj.Curve(pnts[-8], pnts[-3]))
        crvs.append(obj.Curve(pnts[pnt4], pnts[-7]))
        crvs.append(obj.Curve(pnts[-7], pnts[-2]))
        crvs.append(obj.Curve(pnts[-6], pnts[-1]))

        # curves in x direction
        crvs.append(obj.Curve(pnts[-10], pnts[-9]))
        crvs.append(obj.Curve(pnts[-9], pnts[-8]))
        crvs.append(obj.Curve(pnts[-8], pnts[-7]))
        crvs.append(obj.Curve(pnts[-7], pnts[-6]))

        crvs.append(obj.Curve(pnts[-5], pnts[-4]))
        crvs.append(obj.Curve(pnts[-4], pnts[-3]))
        crvs.append(obj.Curve(pnts[-3], pnts[-2]))
        crvs.append(obj.Curve(pnts[-2], pnts[-1]))
        
        # number of curves of structures
        numcrvs_struc_bounds = 17          # number of curves per bound


        # surface definition (sides)
        # first structure, first zbound
        if i == 0 and j == 0:
            crv1 = -numcrvs_struc_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-4
            crv2 = -numcrvs_struc_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-3
            crv3 = -numcrvs_struc_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-2
        # first structure, second zbound
        elif i == 0 and j == 1:
            crv1 = -2*numcrvs_struc_bounds-numcrvs_finlet_vert-4
            crv2 = -2*numcrvs_struc_bounds-numcrvs_finlet_vert-3
            crv3 = -2*numcrvs_struc_bounds-numcrvs_finlet_vert-2
        # rest of structures
        else:
            crv1 = -numcrvs_struc_vert-2*numcrvs_struc_bounds-4
            crv2 = -numcrvs_struc_vert-2*numcrvs_struc_bounds-3
            crv3 = -numcrvs_struc_vert-2*numcrvs_struc_bounds-2
        
        # surfaces at structure
        srfs.append(obj.Surface([crvs[crv1], crvs[-17], crvs[-8], crvs[-15]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[crv2], crvs[-15], crvs[-7], crvs[-13]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[crv3], crvs[-13], crvs[-6], crvs[-11]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])

        # surfaces at groove
        srfs.append(obj.Surface([crvs[-8], crvs[-16], crvs[-4], crvs[-14]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-7], crvs[-14], crvs[-3], crvs[-12]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-6], crvs[-12], crvs[-2], crvs[-10]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-5], crvs[-10], crvs[-1], crvs[-9]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])


    # curves in z direction
    for pnt in zpnts_struc:
        crvs.append(obj.Curve(pnts[pnt], pnts[pnt-10]))
    

    # surfaces between bounds  
    # gas wall
    srfs.append(obj.Surface([crvs[-numcrvs_struc_vert-2*numcrvs_struc_bounds-3], crvs[-6], crvs[-numcrvs_struc_vert-17], crvs[-numcrvs_struc_vert-numcrvs_struc_bounds-17]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-6], crvs[-3], crvs[-numcrvs_struc_vert-16], crvs[-numcrvs_struc_vert-numcrvs_struc_bounds-16]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])

    # film wall
    srfs.append(obj.Surface([crvs[-numcrvs_struc_vert-2*numcrvs_struc_bounds-2], crvs[-5], crvs[-numcrvs_struc_vert-11], crvs[-numcrvs_struc_vert-numcrvs_struc_bounds-11]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-5], crvs[-4], crvs[-numcrvs_struc_vert-5], crvs[-numcrvs_struc_vert-numcrvs_struc_bounds-5]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-4], crvs[-1], crvs[-numcrvs_struc_vert-9], crvs[-numcrvs_struc_vert-numcrvs_struc_bounds-9]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-1], crvs[-2], crvs[-numcrvs_struc_vert-1], crvs[-numcrvs_struc_vert-numcrvs_struc_bounds-1]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
print("\t- done structures")



# film outlet region
# outlet variant 1: simple film outlet
if q_outlettype == "1":
    # point definition
    for zbound in zbounds:
        pnts.append(obj.Point(ht_geom, 0.0, zbound))
        pnts.append(obj.Point((hi_geom + hd_geom), 0.0, zbound))
        pnts.append(obj.Point(hi_geom, 0.0, zbound))
        pnts.append(obj.Point(0.0, 0.0, zbound))

    # number of points of film outlet region
    numpnts_foutlet_bounds = 4          # number of points per bound

    # curve definition
    # lower zbound
    # curves in y direction
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-4], pnts[-2*numpnts_foutlet_bounds-numpnts_struc_bounds-5]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-3], pnts[-2*numpnts_foutlet_bounds-numpnts_struc_bounds-4]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-2], pnts[-2*numpnts_foutlet_bounds-numpnts_struc_bounds-3]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-1], pnts[-2*numpnts_foutlet_bounds-numpnts_struc_bounds-2]))
    # curves in x direction
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-4], pnts[-numpnts_foutlet_bounds-3]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-3], pnts[-numpnts_foutlet_bounds-2]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-2], pnts[-numpnts_foutlet_bounds-1]))

    # upper zbound
    # curves in y direction
    crvs.append(obj.Curve(pnts[-4], pnts[-2*numpnts_foutlet_bounds-5]))
    crvs.append(obj.Curve(pnts[-3], pnts[-2*numpnts_foutlet_bounds-4]))
    crvs.append(obj.Curve(pnts[-2], pnts[-2*numpnts_foutlet_bounds-3]))
    crvs.append(obj.Curve(pnts[-1], pnts[-2*numpnts_foutlet_bounds-2]))
    # curves in x direction
    crvs.append(obj.Curve(pnts[-4], pnts[-3]))
    crvs.append(obj.Curve(pnts[-3], pnts[-2]))
    crvs.append(obj.Curve(pnts[-2], pnts[-1]))

    # number of curves of film outlet region
    numcrvs_foutlet_bounds = 7          # number of curves per bound


    # surface definition (sides)
    # lower zbound
    srfs.append(obj.Surface([crvs[-2*numcrvs_foutlet_bounds-numcrvs_struc_vert-numcrvs_struc_bounds-4], crvs[-numcrvs_foutlet_bounds-7], crvs[-numcrvs_foutlet_bounds-3], crvs[-numcrvs_foutlet_bounds-6]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2*numcrvs_foutlet_bounds-numcrvs_struc_vert-numcrvs_struc_bounds-3], crvs[-numcrvs_foutlet_bounds-6], crvs[-numcrvs_foutlet_bounds-2], crvs[-numcrvs_foutlet_bounds-5]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2*numcrvs_foutlet_bounds-numcrvs_struc_vert-numcrvs_struc_bounds-2], crvs[-numcrvs_foutlet_bounds-5], crvs[-numcrvs_foutlet_bounds-1], crvs[-numcrvs_foutlet_bounds-4]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    # upper zbound
    srfs.append(obj.Surface([crvs[-2*numcrvs_foutlet_bounds-numcrvs_struc_vert-4], crvs[-7], crvs[-3], crvs[-6]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2*numcrvs_foutlet_bounds-numcrvs_struc_vert-3], crvs[-6], crvs[-2], crvs[-5]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2*numcrvs_foutlet_bounds-numcrvs_struc_vert-2], crvs[-5], crvs[-1], crvs[-4]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])


    # curves in z direction
    zpnts_foutlet = [-4, -3, -2, -1]
    for pnt in zpnts_foutlet:
        crvs.append(obj.Curve(pnts[pnt], pnts[pnt-4]))
    numcrvs_foutlet_vert = len(zpnts_foutlet)


    # surfaces between bounds
    # gaswall
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_bounds-3], crvs[-4], crvs[-numcrvs_foutlet_vert-7], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_bounds-7]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])

    # film outlet
    srfs.append(obj.Surface([crvs[-4], crvs[-3], crvs[-numcrvs_foutlet_vert-3], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_bounds-3]]))
    fnc.getobj(name_foutlet, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-3], crvs[-2], crvs[-numcrvs_foutlet_vert-2], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_bounds-2]]))
    fnc.getobj(name_foutlet, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2], crvs[-1], crvs[-numcrvs_foutlet_vert-1], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_bounds-1]]))
    fnc.getobj(name_foutlet, prts).addgeom(srfs[-1])

    # film wall
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_bounds-2], crvs[-1], crvs[-numcrvs_foutlet_vert-4], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_bounds-4]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])

numpnts_bounds = len(pnts)              # number of all points on bounds
print("\t- done film outlet region")



# inner z coordinates
zints = [ws_geom, ws_geom + wc_geom]


# definition of additional points of inner z coordinates
# film inlet region
# inlet variant 1: simple film inlet
if q_inlettype == "1":
    for zint in zints:
        # points at lt_geom
        pnts.append(obj.Point(ht_geom, lt_geom, zint))
        pnts.append(obj.Point((hi_geom + hd_geom), lt_geom, zint))
        pnts.append(obj.Point(hi_geom, lt_geom, zint))
        pnts.append(obj.Point(0.0, lt_geom, zint))

        # points at (lt_geom - li_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom - li_geom), zint))
        pnts.append(obj.Point(0.0, (lt_geom - li_geom), zint))
        pnts.append(obj.Point(-1.0*dgr_geom, (lt_geom - li_geom), zint))
        
        # points at (lt_geom - li_geom - lgr_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom - li_geom - lgr_geom), zint))
        pnts.append(obj.Point(0.0, (lt_geom - li_geom - lgr_geom), zint))
        pnts.append(obj.Point(-1.0*dgr_geom, (lt_geom - li_geom - lgr_geom), zint))

    # number of points of film inlet region
    numpnts_finlet_ints = 10            # number of points per int


# inlet variant 2: additional gas space
elif q_inlettype == "2":
    for zint in zints:
        # points at (lt_geom + lag_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom + lag_geom), zint))
        pnts.append(obj.Point((hi_geom + hd_geom), (lt_geom + lag_geom), zint))
        
        # points at lt_geom
        pnts.append(obj.Point(ht_geom, lt_geom, zint))
        pnts.append(obj.Point((hi_geom + hd_geom), lt_geom, zint))
        pnts.append(obj.Point(hi_geom, lt_geom, zint))
        pnts.append(obj.Point(0.0, lt_geom, zint))

        # points at (lt_geom - li_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom - li_geom), zint))
        pnts.append(obj.Point(0.0, (lt_geom - li_geom), zint))
        pnts.append(obj.Point(-1.0*dgr_geom, (lt_geom - li_geom), zint))
        
        # points at (lt_geom - li_geom - lgr_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom - li_geom - lgr_geom), zint))
        pnts.append(obj.Point(0.0, (lt_geom - li_geom - lgr_geom), zint))
        pnts.append(obj.Point(-1.0*dgr_geom, (lt_geom - li_geom - lgr_geom), zint))   
        
    # number of points of film inlet region
    numpnts_finlet_ints = 12            # number of points per int


# structures
for i in range(ns):
    for j in range(len(zints)):
        # first row of points, first structure, first zint
        if i == 0 and j == 0:
            for k in range(3):
                pnts.append(obj.Point(pnts[-numpnts_finlet_ints-3].getx(), (pnts[-numpnts_finlet_ints-3].gety() - ls_geom), zints[j]))
        # first row of points, rest of structures
        else:           
            for k in range(3):
                pnts.append(obj.Point(pnts[-9].getx(), (pnts[-9].gety() - ls_geom), zints[j]))
        
        # second row of points
        for k in range(3):
            pnts.append(obj.Point(pnts[-3].getx(), (pnts[-3].gety() - lgr_geom), zints[j]))


# film outlet region
# outlet variant 1: simple outlet
if q_outlettype == "1":
    for zint in zints:
        pnts.append(obj.Point(ht_geom, 0.0, zint))
        pnts.append(obj.Point((hi_geom + hd_geom), 0.0, zint))
        pnts.append(obj.Point(hi_geom, 0.0, zint))
        pnts.append(obj.Point(0.0, 0.0, zint))
print("\t- done internal points")



################################################################### BLOCKING ####################################################################
print("\nGenerating blocking...")
blkg = []        # blocking operations (split, deletion)
verts = []       # vertex-point associations


# block modification
# geometry type 1
if geomnum == 1:
    # block splits
    # film inlet region
    # x splits
    blkg.append(obj.Split(pnts[3], 25, 41, prts))       # 0.0
    blkg.append(obj.Split(pnts[2], 70, 41, prts))       # hi_geom
    blkg.append(obj.Split(pnts[1], 86, 41, prts))       # (hi_geom + hd_geom)

    # y splits
    blkg.append(obj.Split(pnts[8], 21, 25, prts))       # (lt_geom - li_geom)
    blkg.append(obj.Split(pnts[13], 21, 120, prts))     # (lt_geom - li_geom - lgr_geom)

    # structures
    for i in range(ns):
        blkg.append(obj.Split(pnts[2*numpnts_struc_bounds*i+4+2*numpnts_finlet_bounds], 21, blkg[-1].getvert2()+28, prts))      # y split (structures)
        blkg.append(obj.Split(pnts[blkg[-1].getpnt().getnum()+5], 21, blkg[-1].getvert2()+28, prts))                            # y split (grooves)
    print("\t- done xy block splits")


    # block deletion
    # film inlet region
    blkg.append(obj.Delete(61))                 # delete block below smooth wall at inlet

    # structures
    for i in range(ns):
        blkg.append(obj.Delete(97+i*36))        # delete block below structure

    # film outlet region
    blkg.append(obj.Delete(13))                 # delete block below smooth wall at outlet
    print("\t- done global block deletion")


    # remaining splits
    blkg.append(obj.Split(pnts[numpnts_bounds], 41, 42, prts))                                  # z split (ws_geom)
    blkg.append(obj.Split(pnts[numpnts_bounds+numpnts_finlet_ints], 201+70*ns, 42, prts))       # z split (ws_geom + wc_geom)
    print("\t- done z block splits")


# geometry type 2
elif geomnum == 2:
    
    # film inlet region# x splits
    blkg.append(obj.Split(pnts[5], 25, 41, prts))       # 0.0
    blkg.append(obj.Split(pnts[4], 70, 41, prts))       # hi_geom
    blkg.append(obj.Split(pnts[3], 86, 41, prts))       # (hi_geom + hd_geom)

    # y splits
    blkg.append(obj.Split(pnts[5], 21, 25, prts))       # lt_geom
    blkg.append(obj.Split(pnts[10], 21, 120, prts))     # (lt_geom - li_geom)
    blkg.append(obj.Split(pnts[15], 21, 148, prts))     # (lt_geom - li_geom - lgr_geom)


    # structures
    for i in range(ns):
        blkg.append(obj.Split(pnts[2*numpnts_struc_bounds*i+4+2*numpnts_finlet_bounds], 21, blkg[-1].getvert2()+28, prts))      # y split (structures)
        blkg.append(obj.Split(pnts[blkg[-1].getpnt().getnum()+5], 21, blkg[-1].getvert2()+28, prts))                            # y split (grooves)
    print("\t- done xy block splits")


    # block deletion
    # film inlet region
    blkg.append(obj.Delete(61))                 # delete block above inlet
    blkg.append(obj.Delete(62))                 # delete block above inlet
    blkg.append(obj.Delete(63))                 # delete block above inlet
    blkg.append(obj.Delete(79))                 # delete block below smooth wall at inlet

    # structures
    for i in range(ns):
        blkg.append(obj.Delete(115+i*36))       # delete block below structure

    # block deletions of film outlet region
    blkg.append(obj.Delete(13))                 # delete block below smooth wall at outlet
    print("\t- done global block deletion")


    # remaining splits
    blkg.append(obj.Split(pnts[numpnts_bounds], 41, 42, prts))                                  # z split (ws_geom)
    blkg.append(obj.Split(pnts[numpnts_bounds+numpnts_finlet_ints], 236+70*ns, 42, prts))       # z split (ws_geom + wc_geom)
    print("\t- done z block splits")




# vertex-point associations
print("\nAssociating vertices to points...")


# geometry type 1
if geomnum == 1:
    # film inlet region
    # lower zbound
    verts.append(obj.Vert(41, pnts[0]))
    verts.append(obj.Vert(102, pnts[1]))
    verts.append(obj.Vert(86, pnts[2]))
    verts.append(obj.Vert(70, pnts[3]))

    verts.append(obj.Vert(124, pnts[4]))
    verts.append(obj.Vert(123, pnts[5]))
    verts.append(obj.Vert(122, pnts[6]))
    verts.append(obj.Vert(121, pnts[7]))
    verts.append(obj.Vert(120, pnts[8]))

    verts.append(obj.Vert(152, pnts[9]))
    verts.append(obj.Vert(151, pnts[10]))
    verts.append(obj.Vert(150, pnts[11]))
    verts.append(obj.Vert(149, pnts[12]))
    verts.append(obj.Vert(148, pnts[13]))
    
    # upper zbound
    verts.append(obj.Vert(42, pnts[14]))
    verts.append(obj.Vert(106, pnts[15]))
    verts.append(obj.Vert(90, pnts[16]))
    verts.append(obj.Vert(74, pnts[17]))

    verts.append(obj.Vert(131, pnts[18]))
    verts.append(obj.Vert(130, pnts[19]))
    verts.append(obj.Vert(129, pnts[20]))
    verts.append(obj.Vert(128, pnts[21]))
    verts.append(obj.Vert(127, pnts[22]))

    verts.append(obj.Vert(159, pnts[23]))
    verts.append(obj.Vert(158, pnts[24]))
    verts.append(obj.Vert(157, pnts[25]))
    verts.append(obj.Vert(156, pnts[26]))
    verts.append(obj.Vert(155, pnts[27]))
    print("\t- done film inlet region")


    # structures
    for i in range(ns):
        # first row of points, lower zbound
        for k in range(5):
            verts.append(obj.Vert(180+56*i-k, pnts[verts[-1].getpnt().getnum()+1]))
        
        # second row of points, lower zbound
        for k in range(5):
            verts.append(obj.Vert(verts[-5].getnum()+28, pnts[verts[-1].getpnt().getnum() + 1]))

        # first row of points, upper zbound
        for k in range(5):
            verts.append(obj.Vert(187+56*i-k, pnts[verts[-1].getpnt().getnum()+1]))
        
        # second row of points, upper zbound
        for k in range(5):
            verts.append(obj.Vert(verts[-5].getnum()+28, pnts[verts[-1].getpnt().getnum()+1]))  
    print("\t- done structures")


    # film outlet region
    # lower zbound
    verts.append(obj.Vert(37, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(101, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(85, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(69, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(38, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(105, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(89, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(73, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done film outlet region")


    # film inlet region
    # lower zint 
    v0 = 201 + ns*70
    verts.append(obj.Vert(v0, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-1, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-2, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-3, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v0-7, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-10, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-11, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v0-14, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-17, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-18, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    v1 = 243 + ns*84
    verts.append(obj.Vert(v1, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-1, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-2, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-3, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v1-7, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-10, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-11, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v1-14, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-17, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-18, pnts[verts[-1].getpnt().getnum()+1]))


    # structures
    for i in range(ns):
        # first row of points, lower zint
        verts.append(obj.Vert(v0-21-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v0-24-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v0-25-i*14, pnts[verts[-1].getpnt().getnum()+1]))

        # second row of points, lower zint
        verts.append(obj.Vert(v0-21-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v0-24-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v0-25-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))

        # first row of points, upper zint
        verts.append(obj.Vert(v1-21-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v1-24-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v1-25-i*14, pnts[verts[-1].getpnt().getnum()+1]))

        # second row of points, upper zint
        verts.append(obj.Vert(v1-21-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v1-24-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v1-25-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))


    # bottom section at outlet
    # lower zint
    verts.append(obj.Vert(v0-21-ns*14, pnts[-8]))
    verts.append(obj.Vert(v0-22-ns*14, pnts[-7]))
    verts.append(obj.Vert(v0-23-ns*14, pnts[-6]))
    verts.append(obj.Vert(v0-24-ns*14, pnts[-5]))

    # upper zint
    verts.append(obj.Vert(v1-21-ns*14, pnts[-4]))
    verts.append(obj.Vert(v1-22-ns*14, pnts[-3]))
    verts.append(obj.Vert(v1-23-ns*14, pnts[-2]))
    verts.append(obj.Vert(v1-24-ns*14, pnts[-1]))
    print("\t- done internal associations")


# geometry type 2
elif geomnum == 2:
    # film inlet region
    # lower zbound
    verts.append(obj.Vert(41, pnts[0]))
    verts.append(obj.Vert(102, pnts[1]))

    verts.append(obj.Vert(124, pnts[2]))
    verts.append(obj.Vert(123, pnts[3]))
    verts.append(obj.Vert(122, pnts[4]))
    verts.append(obj.Vert(121, pnts[5]))

    verts.append(obj.Vert(152, pnts[6]))
    verts.append(obj.Vert(151, pnts[7]))
    verts.append(obj.Vert(150, pnts[8]))
    verts.append(obj.Vert(149, pnts[9]))
    verts.append(obj.Vert(148, pnts[10]))

    verts.append(obj.Vert(180, pnts[11]))
    verts.append(obj.Vert(179, pnts[12]))
    verts.append(obj.Vert(178, pnts[13]))
    verts.append(obj.Vert(177, pnts[14]))
    verts.append(obj.Vert(176, pnts[15]))

    # upper zbound
    verts.append(obj.Vert(42, pnts[16]))
    verts.append(obj.Vert(106, pnts[17]))

    verts.append(obj.Vert(131, pnts[18]))
    verts.append(obj.Vert(130, pnts[19]))
    verts.append(obj.Vert(129, pnts[20]))
    verts.append(obj.Vert(128, pnts[21]))

    verts.append(obj.Vert(159, pnts[22]))
    verts.append(obj.Vert(158, pnts[23]))
    verts.append(obj.Vert(157, pnts[24]))
    verts.append(obj.Vert(156, pnts[25]))
    verts.append(obj.Vert(155, pnts[26]))

    verts.append(obj.Vert(187, pnts[27]))
    verts.append(obj.Vert(186, pnts[28]))
    verts.append(obj.Vert(185, pnts[29]))
    verts.append(obj.Vert(184, pnts[30]))
    verts.append(obj.Vert(183, pnts[31]))
    print("\t- done film inlet region")


    # structures
    for i in range(ns):
        # first row of points, lower zbound
        for k in range(5):
            verts.append(obj.Vert(208+56*i-k, pnts[verts[-1].getpnt().getnum()+1]))
        
        # second row of points, lower zbound
        for k in range(5):
            verts.append(obj.Vert(verts[-5].getnum()+28, pnts[verts[-1].getpnt().getnum()+1]))

        # first row of points, upper zbound
        for k in range(5):
            verts.append(obj.Vert(215+56*i-k, pnts[verts[-1].getpnt().getnum()+1]))
        
        # second row of points, upper zbound
        for k in range(5):
            verts.append(obj.Vert(verts[-5].getnum()+28, pnts[verts[-1].getpnt().getnum()+1]))  
    print("\t- done structures")


    # film outlet region
    # lower zbound
    verts.append(obj.Vert(37, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(101, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(85, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(69, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(38, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(105, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(89, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(73, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done film outlet region")


    # film inlet region
    # lower zint 
    v0 = 236 + ns*70
    verts.append(obj.Vert(v0, pnts[numpnts_bounds]))
    verts.append(obj.Vert(v0-1, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v0-7, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-8, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-9, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-10, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v0-14, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-17, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-18, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v0-21, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-24, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v0-25, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    v1 = 285 + ns*84
    verts.append(obj.Vert(v1, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-1, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v1-7, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-8, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-9, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-10, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v1-14, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-17, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-18, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(v1-21, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-24, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(v1-25, pnts[verts[-1].getpnt().getnum()+1]))


    # structures
    for i in range(ns):
        # first row of points, lower zint
        verts.append(obj.Vert(v0-28-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v0-31-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v0-32-i*14, pnts[verts[-1].getpnt().getnum()+1]))

        # second row of points, lower zint
        verts.append(obj.Vert(v0-28-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v0-31-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v0-32-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))

        # first row of points, upper zint
        verts.append(obj.Vert(v1-28-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v1-31-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v1-32-i*14, pnts[verts[-1].getpnt().getnum()+1]))

        # second row of points, upper zint
        verts.append(obj.Vert(v1-28-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v1-31-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))
        verts.append(obj.Vert(v1-32-7-i*14, pnts[verts[-1].getpnt().getnum()+1]))

    # bottom section at outlet
    # lower zint
    verts.append(obj.Vert(v0-28-ns*14, pnts[-8]))
    verts.append(obj.Vert(v0-29-ns*14, pnts[-7]))
    verts.append(obj.Vert(v0-30-ns*14, pnts[-6]))
    verts.append(obj.Vert(v0-31-ns*14, pnts[-5]))

    # upper zint
    verts.append(obj.Vert(v1-28-ns*14, pnts[-4]))
    verts.append(obj.Vert(v1-29-ns*14, pnts[-3]))
    verts.append(obj.Vert(v1-30-ns*14, pnts[-2]))
    verts.append(obj.Vert(v1-31-ns*14, pnts[-1]))
    print("\t- done internal associations")


#################################################################### MESHING ####################################################################
print("\nMeshing...")
mshg = []        # meshing operations


# geometry type 1
if geomnum == 1:
    # x direction
    mshg.append(obj.Mesh(120, 121, dgr_mesh))       # grooves
    mshg.append(obj.Mesh(121, 122, hi_mesh))        # film
    mshg.append(obj.Mesh(122, 123, hd_mesh))        # distributor
    mshg.append(obj.Mesh(123, 124, hg_mesh))        # gas space
    print("\t- done x direction")


    # y direction
    # top section at inlet
    mshg.append(obj.Mesh(121, 70, li_mesh))         # smooth inlet
    mshg.append(obj.Mesh(149, 121, lgr_mesh))       # first groove
    
    # structures
    for i in range(ns):
        mshg.append(obj.Mesh(177+56*i, mshg[-1].getvert1(), ls_mesh))                   # structure
        mshg.append(obj.Mesh(mshg[-1].getvert1()+28, mshg[-1].getvert1(), lgr_mesh))    # groove
    
    # bottom section at outlet
    mshg.append(obj.Mesh(69, mshg[-1].getvert1(), lo_mesh))                             # smooth outlet
    print("\t- done y direction")


    # z direction
    mshg.append(obj.Mesh(41, v0, ws1_mesh))         # side section 1 (at lower zbound)
    mshg.append(obj.Mesh(v0, v1, wc_mesh))          # central section
    mshg.append(obj.Mesh(v1, 42, ws2_mesh))         # side section 2 (at upper zbound)
    print("\t- done z direction")



# geometry type 2
elif geomnum == 2:
    # x direction
    mshg.append(obj.Mesh(148, 149, dgr_mesh))       # grooves
    mshg.append(obj.Mesh(149, 150, hi_mesh))        # film
    mshg.append(obj.Mesh(150, 151, hd_mesh))        # distributor
    mshg.append(obj.Mesh(151, 152, hg_mesh))        # gas space
    print("\t- done x direction")


    # y direction
    # top section at inlet
    mshg.append(obj.Mesh(123, 102, lag_mesh))       # gas space
    mshg.append(obj.Mesh(149, 121, li_mesh))        # smooth inlet
    mshg.append(obj.Mesh(177, 149, lgr_mesh))       # first groove
    
    # structures
    for i in range(ns):
        mshg.append(obj.Mesh(205+56*i, mshg[-1].getvert1(), ls_mesh))                   # structure
        mshg.append(obj.Mesh(mshg[-1].getvert1()+28, mshg[-1].getvert1(), lgr_mesh))    # groove
    
    # bottom section at outlet
    mshg.append(obj.Mesh(69, mshg[-1].getvert1(), lo_mesh))                             # smooth outlet
    print("\t- done y direction")


    # z direction
    mshg.append(obj.Mesh(41, v0, ws1_mesh))         # side section 1 (at lower zbound)
    mshg.append(obj.Mesh(v0, v1, wc_mesh))          # central section
    mshg.append(obj.Mesh(v1, 42, ws2_mesh))         # side section 2 (at upper zbound)
    print("\t- done z direction")


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

# add lines for surface definition (geometry)
rpllines = fnc.rpl_obj(rpllines, srfs)

# add lines for part association (geometry)
rpllines = fnc.rpl_obj(rpllines, prts)

# add lines for blocking creation (blocking)
rpllines = fnc.rpl_3Dblocking(rpllines, fnc.getobj(name_fluid, prts))

# add lines for block modifications (blocking)
rpllines = fnc.rpl_obj(rpllines, blkg)

# add lines for blocking associations (blocking)
rpllines = fnc.rpl_obj(rpllines, verts)

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
conflines = fnc.conf_geom3D(conflines, xgeom, ygeom, zgeom)

# mesh configuration (user)
conflines = fnc.conf_mesh3D(conflines, xsects, ysects, zsects)

# mesh type
conflines = fnc.conf_type(conflines, geomtype)

# geometry configuration (script)
conflines = fnc.conf_geomdata(conflines, "xgeom", xgeom)
conflines = fnc.conf_geomdata(conflines, "ygeom", ygeom)
conflines = fnc.conf_geomdata(conflines, "zgeom", zgeom)

# mesh configuration (script)
conflines = fnc.conf_meshdata(conflines, xsects)
conflines = fnc.conf_meshdata(conflines, ysects)
conflines = fnc.conf_meshdata(conflines, zsects)

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