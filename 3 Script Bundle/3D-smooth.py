# this script is used to generate an ICEM model with user defined dimensions and mesh parameters
# geometry type: 3D, smooth reactor wall
# the files rpl_gen_fnc.py and rpl_gen_obj.py are required to run this file


# specify part names (retaining default names recommended)
name_fluid = "FLUID"
name_finlet = "FILMINLET"
name_fwall = "FILMWALL"
name_foutlet = "FILMOUTLET"
name_owall = "FILMOUTLETWALL"
name_gwall = "GASWALL"
name_gtop = "GASTOP"
name_gbottom = "GASBOTTOM"
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


geomtype = "3D-smooth-"
xgeom = []
ygeom = []
zgeom = []

# film inlet variants
while True:
    print("\nAvailable film inlet variants:")
    print("\t- 1: Domain with simple film inlet region\n\t\t- suitable for periodic boundaries in combination with simple film outlet")
    print("\t- 2: Domain with additional gas space above film inlet")
    q_inlettype = input("Choose inlet variant to be created:\n>>> ")

    if q_inlettype == "1" or q_inlettype == "2": 
        break
    else:
        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter the number corresponding to the variant.")

# film outlet variants
while True:
    print("\nAvailable film outlet variants:")
    print("\t- 1: Domain with simple film outlet region\n\t\t- suitable for periodic boundaries in combination with simple film inlet")
    print("\t- 2: Domain with recessed film outlet")
    q_outlettype = input("Choose outlet variant to be created:\n>>> ")

    # type 1
    if q_outlettype == "1" or q_outlettype == "2":
        break
    else:
        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter the number corresponding to the variant.")

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

elif q_inlettype == "1" and q_outlettype == "2":
    # type 3
    # simple film inlet
    # recessed film outlet
    geomtype += "3"
    geomnum = 3

elif q_inlettype == "2" and q_outlettype == "2":
    # type 4
    # additional gas space above film inlet
    # recessed film outlet
    geomtype += "4"
    geomnum = 4

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
if q_outlettype == "2":                                                     # outlet type 2
    xgeom.append(obj.Geometry(obj.heo_geomname, obj.heo_geomdescr))
    xgeom.append(obj.Geometry(obj.hro_geomname, obj.hro_geomdescr))

# add ygeom objects
ygeom.append(obj.Geometry(obj.lt_geomname, obj.lt_geomdescr))
if q_inlettype == "2":                                                      # inlet type 2
    ygeom.append(obj.Geometry(obj.lag_geomname, obj.lag_geomdescr))
if q_outlettype == "2":                                                     # outlet type 2
    ygeom.append(obj.Geometry(obj.lro_geomname, obj.lro_geomdescr))

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
        if not fnc.checkgeom(ygeom):
            # manual geometry input
            fnc.setygeom_smooth(ygeom)

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
        fnc.setygeom_smooth(ygeom)
        
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
if q_outlettype == "2":
    heo_geom = fnc.getobj(obj.heo_geomname, xgeom).getval()                 # outlet: edge region
    hro_geom = fnc.getobj(obj.hro_geomname, xgeom).getval() - heo_geom      # outlet: recessed outlet

# y geometry parameters
lt_geom = fnc.getobj(obj.lt_geomname, ygeom).getval()           # film wall
if q_inlettype == "2":
    lag_geom = fnc.getobj(obj.lag_geomname, ygeom).getval()     # inlet: additional gas space
if q_outlettype == "2":
    lro_geom = fnc.getobj(obj.lro_geomname, ygeom).getval()      # outlet: recessed outlet

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
if q_outlettype == "2":
    xsects.append(obj.Section(obj.heo_sectname, heo_geom))      # outlet: edge region
    xsects.append(obj.Section(obj.hro_sectname, hro_geom))      # outlet: remaining outlet

# y-dimension
ysects.append(obj.Section(obj.lt_sectname, lt_geom))            # film wall
if q_inlettype == "2":
    ysects.append(obj.Section(obj.lag_sectname, lag_geom))      # inlet: additional gas space
if q_outlettype == "2":
    ysects.append(obj.Section(obj.lro_sectname, lro_geom))      # outlet: recessed outlet

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
            print(f"\t- Within film section (h_nu): Uniform distribution of cells with maximum size of {round(size_film*1000000.0, meshprec)} µm.")
            print(f"\t- Within distributor section (h_d): Geometric1 distribution of cells, growth from {round(size_film*1000000.0, meshprec)} µm to {round(size_distr*1000000.0, meshprec)} µm.")
            print(f"\t- Within gas section (h_g): Geometric1 distribution of cells, growth from {round(size_distr*1000000.0, meshprec)} µm to {round(size_xmax*1000000.0, meshprec)} µm.")
            if q_outlettype == "2":
                print(f"\t- Within section at outlet edge (h_eo): Uniform distribution of cells with maximum size of {round(size_film*1000000.0, meshprec)} µm.")
                print(f"\t- Within recessed outlet section (h_ro): Geometric2 distribution of cells, growth from {round(size_film*1000000.0, meshprec)} µm to {round(size_xmax*1000000.0, meshprec)} µm.")
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
                if q_outlettype == "2":
                    fnc.uniform(fnc.getobj(obj.heo_sectname, xsects), size_film)            # outlet: edge region
                    fnc.geo2(fnc.getobj(obj.hro_sectname, xsects), size_film, size_xmax)    # outlet: remaining outlet

                # y-dimension
                fnc.uniform(fnc.getobj(obj.lt_sectname, ysects), size_ymax)                 # structures
                if q_inlettype == "2":
                    fnc.uniform(fnc.getobj(obj.lag_sectname, ysects), size_ymax)            # inlet: additional gas space
                if q_outlettype == "2":
                    fnc.uniform(fnc.getobj(obj.lro_sectname, ysects), size_ymax)            # outlet: recessed outlet


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
if q_outlettype == "2":
    heo_mesh = fnc.getobj(obj.heo_sectname, xsects).getmesh()   # outlet: edge region
    hro_mesh = fnc.getobj(obj.hro_sectname, xsects).getmesh()   # outlet: remaining outlet

# y meshing parameters
lt_mesh = fnc.getobj(obj.lt_sectname, ysects).getmesh()         # total domain
if q_inlettype == "2":
    lag_mesh = fnc.getobj(obj.lag_sectname, ysects).getmesh()   # inlet: additional gas space
if q_outlettype == "2":
    lro_mesh = fnc.getobj(obj.lro_sectname, ysects).getmesh()   # outlet: recessed outlet

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
prts.append(obj.Part(name_finlet))          # inlet
prts.append(obj.Part(name_fwall))           # film wall
prts.append(obj.Part(name_foutlet))         # film outlet
prts.append(obj.Part(name_gwall))           # gas wall
if not periodic:
    prts.append(obj.Part(name_gtop))        # gas top
    prts.append(obj.Part(name_distr))       # distributor
prts.append(obj.Part(name_sides))           # sides
if q_outlettype == "2":
    prts.append(obj.Part(name_owall))       # outlet wall
    prts.append(obj.Part(name_gbottom))     # gas bottom
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

    
        # curve definition
        # curves in x direction
        crvs.append(obj.Curve(pnts[-4], pnts[-3]))
        crvs.append(obj.Curve(pnts[-3], pnts[-2]))
        crvs.append(obj.Curve(pnts[-2], pnts[-1]))

    # number of points and curves of film inlet region
    numpnts_finlet_bounds = 4           # number of points per bound
    numcrvs_finlet_bounds = 3           # number of curves per bound

    # curves in z direction
    zpnts_finlet = [-4, -3, -2, -1]     # points for curves between zbounds of film inlet region 
    for pnt in zpnts_finlet:
        crvs.append(obj.Curve(pnts[pnt], pnts[pnt-numpnts_finlet_bounds]))
    numcrvs_finlet_vert = int(len(zpnts_finlet))        # number of curves between bounds

    # surfaces between zbounds
    # gas top
    srfs.append(obj.Surface([crvs[-4], crvs[-3], crvs[-numcrvs_finlet_vert-3], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-3]]))
    if periodic:
        fnc.getobj(name_finlet, prts).addgeom(srfs[-1])
    else:
        fnc.getobj(name_gtop, prts).addgeom(srfs[-1])

    # distributor
    srfs.append(obj.Surface([crvs[-3], crvs[-2], crvs[-numcrvs_finlet_vert-2], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-2]]))
    if periodic:
        fnc.getobj(name_finlet, prts).addgeom(srfs[-1])
    else:
        fnc.getobj(name_distr, prts).addgeom(srfs[-1])

    # film inlet
    srfs.append(obj.Surface([crvs[-2], crvs[-1], crvs[-numcrvs_finlet_vert-1], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-1]]))
    fnc.getobj(name_finlet, prts).addgeom(srfs[-1])


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

        
        # curve definition
        # curves in y direction
        crvs.append(obj.Curve(pnts[-6], pnts[-4]))
        crvs.append(obj.Curve(pnts[-5], pnts[-3]))

        # curves in x direction
        crvs.append(obj.Curve(pnts[-6], pnts[-5]))
        crvs.append(obj.Curve(pnts[-4], pnts[-3]))
        crvs.append(obj.Curve(pnts[-3], pnts[-2]))
        crvs.append(obj.Curve(pnts[-2], pnts[-1]))


        # surface definition (sides)
        # surface of additional gas space
        srfs.append(obj.Surface([crvs[-6], crvs[-4], crvs[-3], crvs[-5]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])

    # number of points and curves of film inlet region
    numpnts_finlet_bounds = 6           # number of points per bound
    numcrvs_finlet_bounds = 6           # number of curves per bound

    # curves in z direction
    zpnts_finlet = [-6, -5, -4, -3, -2, -1]     # points for curves between zbounds of film inlet region 
    for pnt in zpnts_finlet:
        crvs.append(obj.Curve(pnts[pnt], pnts[pnt-numpnts_finlet_bounds]))
    numcrvs_finlet_vert = int(len(zpnts_finlet))        # number of curves between bounds

    # surfaces between zbounds
    # gas wall
    srfs.append(obj.Surface([crvs[-6], crvs[-4], crvs[-numcrvs_finlet_vert-6], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-6]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])

    # gas top
    srfs.append(obj.Surface([crvs[-6], crvs[-5], crvs[-numcrvs_finlet_vert-4], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-4]]))
    fnc.getobj(name_gtop, prts).addgeom(srfs[-1])

    # distributor
    srfs.append(obj.Surface([crvs[-5], crvs[-3], crvs[-numcrvs_finlet_vert-5], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-5]]))
    fnc.getobj(name_distr, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-3], crvs[-2], crvs[-numcrvs_finlet_vert-2], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-2]]))
    fnc.getobj(name_distr, prts).addgeom(srfs[-1])

    # film inlet
    srfs.append(obj.Surface([crvs[-2], crvs[-1], crvs[-numcrvs_finlet_vert-1], crvs[-numcrvs_finlet_vert-numcrvs_finlet_bounds-1]]))
    fnc.getobj(name_finlet, prts).addgeom(srfs[-1])
print("\t- done film inlet region")



# film outlet region
# outlet variant 1: simple film outlet
if q_outlettype == "1":
    # point definition
    for zbound in zbounds:
        pnts.append(obj.Point(ht_geom, 0.0, zbound))
        pnts.append(obj.Point((hi_geom + hd_geom), 0.0, zbound))
        pnts.append(obj.Point(hi_geom, 0.0, zbound))
        pnts.append(obj.Point(0.0, 0.0, zbound))

        # curve definition
        # curves in x direction
        crvs.append(obj.Curve(pnts[-4], pnts[-3]))
        crvs.append(obj.Curve(pnts[-3], pnts[-2]))
        crvs.append(obj.Curve(pnts[-2], pnts[-1]))

    # number of points and curves of film outlet region
    numpnts_foutlet_bounds = 4          # number of points per bound
    numcrvs_foutlet_bounds = 3          # number of curves per bound

    # curve definition
    # curves in y direction, lower zbound
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-4], pnts[-2*numpnts_foutlet_bounds-numpnts_finlet_bounds-4]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-3], pnts[-2*numpnts_foutlet_bounds-numpnts_finlet_bounds-3]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-2], pnts[-2*numpnts_foutlet_bounds-numpnts_finlet_bounds-2]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-1], pnts[-2*numpnts_foutlet_bounds-numpnts_finlet_bounds-1]))

    # curves in y direction, upper zbound
    crvs.append(obj.Curve(pnts[-4], pnts[-2*numpnts_foutlet_bounds-4]))
    crvs.append(obj.Curve(pnts[-3], pnts[-2*numpnts_foutlet_bounds-3]))
    crvs.append(obj.Curve(pnts[-2], pnts[-2*numpnts_foutlet_bounds-2]))
    crvs.append(obj.Curve(pnts[-1], pnts[-2*numpnts_foutlet_bounds-1]))

    # number of remaining y curves of film outlet region
    numcrvs_foutlet_sides = 4          # number of curves per bound


    # surface definition (sides)
    # lower zbound
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_sides-4], crvs[-numcrvs_foutlet_sides-3], crvs[-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-3], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-3]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_sides-3], crvs[-numcrvs_foutlet_sides-2], crvs[-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-2], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-2]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_sides-2], crvs[-numcrvs_foutlet_sides-1], crvs[-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-1], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-1]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])

    # upper zbound
    srfs.append(obj.Surface([crvs[-4], crvs[-3], crvs[-2*numcrvs_foutlet_sides-3], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-3]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-3], crvs[-2], crvs[-2*numcrvs_foutlet_sides-2], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-2]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2], crvs[-1], crvs[-2*numcrvs_foutlet_sides-1], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-1]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])


    # curves in z direction
    zpnts_foutlet = [-4, -3, -2, -1]
    for pnt in zpnts_foutlet:
        crvs.append(obj.Curve(pnts[pnt], pnts[pnt-numpnts_foutlet_bounds]))
    numcrvs_foutlet_vert = len(zpnts_foutlet)

    # surfaces between bounds
    # gas wall
    srfs.append(obj.Surface([crvs[-4], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_sides-4], crvs[-numcrvs_foutlet_vert-4], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-4]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])

    # film outlet
    srfs.append(obj.Surface([crvs[-4], crvs[-3], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-3], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-3]]))
    fnc.getobj(name_foutlet, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-3], crvs[-2], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-2], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-2]]))
    fnc.getobj(name_foutlet, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2], crvs[-1], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-1], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-1]]))
    fnc.getobj(name_foutlet, prts).addgeom(srfs[-1])

    # film wall
    srfs.append(obj.Surface([crvs[-1], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_sides-1], crvs[-numcrvs_foutlet_vert-1], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-1]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])


# outlet variant 2: recessed film outlet
elif q_outlettype == "2":
    # point definition
    for zbound in zbounds:
        # points at the end of filmwall
        pnts.append(obj.Point(ht_geom, 0.0, zbound))
        pnts.append(obj.Point((hi_geom + hd_geom), 0.0, zbound))
        pnts.append(obj.Point(hi_geom, 0.0, zbound))
        pnts.append(obj.Point(0.0, 0.0, zbound))
        pnts.append(obj.Point(-1.0*heo_geom, 0.0, zbound))
        pnts.append(obj.Point(-1.0*(heo_geom + hro_geom), 0.0, zbound))

        # points at the end of domain
        pnts.append(obj.Point(ht_geom, -1.0*lro_geom, zbound))
        pnts.append(obj.Point((hi_geom + hd_geom), -1.0*lro_geom, zbound))
        pnts.append(obj.Point(hi_geom, -1.0*lro_geom, zbound))
        pnts.append(obj.Point(0.0, -1.0*lro_geom, zbound))
        pnts.append(obj.Point(-1.0*heo_geom, -1.0*lro_geom, zbound))
        pnts.append(obj.Point(-1.0*(heo_geom + hro_geom), -1.0*lro_geom, zbound))


        # curve definition
        # curves in y direction
        crvs.append(obj.Curve(pnts[-12], pnts[-6]))
        crvs.append(obj.Curve(pnts[-11], pnts[-5]))
        crvs.append(obj.Curve(pnts[-10], pnts[-4]))
        crvs.append(obj.Curve(pnts[-9], pnts[-3]))
        crvs.append(obj.Curve(pnts[-8], pnts[-2]))
        crvs.append(obj.Curve(pnts[-7], pnts[-1]))

        # curves in x direction
        crvs.append(obj.Curve(pnts[-12], pnts[-11]))
        crvs.append(obj.Curve(pnts[-11], pnts[-10]))
        crvs.append(obj.Curve(pnts[-10], pnts[-9]))
        crvs.append(obj.Curve(pnts[-9], pnts[-8]))
        crvs.append(obj.Curve(pnts[-8], pnts[-7]))

        crvs.append(obj.Curve(pnts[-6], pnts[-5]))
        crvs.append(obj.Curve(pnts[-5], pnts[-4]))
        crvs.append(obj.Curve(pnts[-4], pnts[-3]))
        crvs.append(obj.Curve(pnts[-3], pnts[-2]))
        crvs.append(obj.Curve(pnts[-2], pnts[-1]))


        # surface definition (sides)
        srfs.append(obj.Surface([crvs[-16], crvs[-10], crvs[-5], crvs[-15]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-15], crvs[-9], crvs[-4], crvs[-14]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-14], crvs[-8], crvs[-3], crvs[-13]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-13], crvs[-7], crvs[-2], crvs[-12]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])
        srfs.append(obj.Surface([crvs[-12], crvs[-6], crvs[-1], crvs[-11]]))
        fnc.getobj(name_sides, prts).addgeom(srfs[-1])

    # number of points and curves of film outlet region
    numpnts_foutlet_bounds = 12         # number of points per bound
    numcrvs_foutlet_bounds = 16         # number of curves per bound

    # curve definition
    # curves in y direction, lower zbound
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-12], pnts[-2*numpnts_foutlet_bounds-numpnts_finlet_bounds-4]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-11], pnts[-2*numpnts_foutlet_bounds-numpnts_finlet_bounds-3]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-10], pnts[-2*numpnts_foutlet_bounds-numpnts_finlet_bounds-2]))
    crvs.append(obj.Curve(pnts[-numpnts_foutlet_bounds-9], pnts[-2*numpnts_foutlet_bounds-numpnts_finlet_bounds-1]))

    # curves in y direction, upper zbound
    crvs.append(obj.Curve(pnts[-12], pnts[-2*numpnts_foutlet_bounds-4]))
    crvs.append(obj.Curve(pnts[-11], pnts[-2*numpnts_foutlet_bounds-3]))
    crvs.append(obj.Curve(pnts[-10], pnts[-2*numpnts_foutlet_bounds-2]))
    crvs.append(obj.Curve(pnts[-9], pnts[-2*numpnts_foutlet_bounds-1]))


    # number of remaining y curves of film outlet region
    numcrvs_foutlet_sides = 4          # number of curves per bound


    # surface definition (sides)
    # lower zbound
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_sides-4], crvs[-numcrvs_foutlet_sides-3], crvs[-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-10], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-3]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_sides-3], crvs[-numcrvs_foutlet_sides-2], crvs[-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-9], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-2]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_sides-2], crvs[-numcrvs_foutlet_sides-1], crvs[-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-8], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-numcrvs_finlet_bounds-1]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])

    # upper zbound
    srfs.append(obj.Surface([crvs[-4], crvs[-3], crvs[-2*numcrvs_foutlet_sides-10], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-3]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-3], crvs[-2], crvs[-2*numcrvs_foutlet_sides-9], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-2]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2], crvs[-1], crvs[-2*numcrvs_foutlet_sides-8], crvs[-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-numcrvs_finlet_vert-1]]))
    fnc.getobj(name_sides, prts).addgeom(srfs[-1])

    # curves in z direction
    zpnts_foutlet = [-12, -9, -8, -7, -6, -5, -4, -3, -2, -1]
    for pnt in zpnts_foutlet:
        crvs.append(obj.Curve(pnts[pnt], pnts[pnt-numpnts_foutlet_bounds]))
    numcrvs_foutlet_vert = len(zpnts_foutlet)


    # surfaces between bounds
    # gas wall
    srfs.append(obj.Surface([crvs[-10], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-4], crvs[-numcrvs_foutlet_vert-4], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_sides-4]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-10], crvs[-6], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-16], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-16]]))
    fnc.getobj(name_gwall, prts).addgeom(srfs[-1])

    # film outlet
    srfs.append(obj.Surface([crvs[-7], crvs[-1], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-11], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-11]]))
    fnc.getobj(name_foutlet, prts).addgeom(srfs[-1])

    # film wall
    srfs.append(obj.Surface([crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-2*numcrvs_foutlet_bounds-1], crvs[-9], crvs[-numcrvs_foutlet_vert-1], crvs[-numcrvs_foutlet_vert-numcrvs_foutlet_sides-1]]))
    fnc.getobj(name_fwall, prts).addgeom(srfs[-1])
    
    # gas bottom
    srfs.append(obj.Surface([crvs[-6], crvs[-5], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-5], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-5]]))
    fnc.getobj(name_gbottom, prts).addgeom(srfs[-1])
    
    # outlet wall
    srfs.append(obj.Surface([crvs[-9], crvs[-8], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-7], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-7]]))
    fnc.getobj(name_owall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-8], crvs[-7], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-6], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-6]]))
    fnc.getobj(name_owall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-5], crvs[-4], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-4], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-4]]))
    fnc.getobj(name_owall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-4], crvs[-3], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-3], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-3]]))
    fnc.getobj(name_owall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-3], crvs[-2], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-2], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-2]]))
    fnc.getobj(name_owall, prts).addgeom(srfs[-1])
    srfs.append(obj.Surface([crvs[-2], crvs[-1], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-1], crvs[-numcrvs_foutlet_vert-2*numcrvs_foutlet_sides-numcrvs_foutlet_bounds-1]]))
    fnc.getobj(name_owall, prts).addgeom(srfs[-1])

numpnts_bounds = len(pnts)              # number of all points on bounds
print("\t- done film outlet region")



# inner z coordinates
zints = [ws_geom, ws_geom + wc_geom]


# definition of additional points of inner z coordinates
# film inlet region
# inlet variant 1: simple film inlet
if q_inlettype == "1":
    for zint in zints:
        # point definition
        # points at lt_geom
        pnts.append(obj.Point(ht_geom, lt_geom, zint))
        pnts.append(obj.Point((hi_geom + hd_geom), lt_geom, zint))
        pnts.append(obj.Point(hi_geom, lt_geom, zint))
        pnts.append(obj.Point(0.0, lt_geom, zint))


# inlet variant 2: additional gas space
elif q_inlettype == "2":
    for zint in zints:
        # point definition
        # points at (lt_geom + lag_geom)
        pnts.append(obj.Point(ht_geom, (lt_geom + lag_geom), zint))
        pnts.append(obj.Point((hi_geom + hd_geom), (lt_geom + lag_geom), zint))
        
        # points at lt_geom
        pnts.append(obj.Point(ht_geom, lt_geom, zint))
        pnts.append(obj.Point((hi_geom + hd_geom), lt_geom, zint))
        pnts.append(obj.Point(hi_geom, lt_geom, zint))
        pnts.append(obj.Point(0.0, lt_geom, zint))



# film outlet region
# outlet variant 1: simple outlet
if q_outlettype == "1":
    for zint in zints:
        pnts.append(obj.Point(ht_geom, 0.0, zint))
        pnts.append(obj.Point((hi_geom + hd_geom), 0.0, zint))
        pnts.append(obj.Point(hi_geom, 0.0, zint))
        pnts.append(obj.Point(0.0, 0.0, zint))


# outlet variant 2: recessed outlet
elif q_outlettype == "2":
    for zint in zints:
        # points at the end of filmwall
        pnts.append(obj.Point(ht_geom, 0.0, zint))
        pnts.append(obj.Point(0.0, 0.0, zint))
        pnts.append(obj.Point(-1.0*heo_geom, 0.0, zint))
        pnts.append(obj.Point(-1.0*(heo_geom + hro_geom), 0.0, zint))

        # points at the end of domain
        pnts.append(obj.Point(ht_geom, -1.0*lro_geom, zint))
        pnts.append(obj.Point((hi_geom + hd_geom), -1.0*lro_geom, zint))
        pnts.append(obj.Point(hi_geom, -1.0*lro_geom, zint))
        pnts.append(obj.Point(0.0, -1.0*lro_geom, zint))
        pnts.append(obj.Point(-1.0*heo_geom, -1.0*lro_geom, zint))
        pnts.append(obj.Point(-1.0*(heo_geom + hro_geom), -1.0*lro_geom, zint))
print("\t- done internal points")



################################################################### BLOCKING ####################################################################
print("\nGenerating blocking...")
blkg = []        # blocking operations (split, deletion)
verts = []       # vertex-point associations


# block modification
# geometry type 1
if geomnum == 1:
    # x splits
    blkg.append(obj.Split(pnts[6], 26, 42, prts))       # hi_geom
    blkg.append(obj.Split(pnts[5], 74, 42, prts))       # (hi_geom + hd_geom)

    # z splits
    blkg.append(obj.Split(pnts[16], 41, 42, prts))      # ws_geom
    blkg.append(obj.Split(pnts[20], 112, 42, prts))     # (ws_geom + wc_geom)


# geometry type 2
elif geomnum == 2:
    # x split
    blkg.append(obj.Split(pnts[1], 25, 41, prts))       # (hi_geom + hd_geom)

    # y split
    blkg.append(obj.Split(pnts[5], 21, 25, prts))       # lt_geom

    # block deletion
    blkg.append(obj.Delete(41))                         # delete block above inlet

    # x split
    blkg.append(obj.Split(pnts[4], 86, 87, prts))       # hi_geom

    # z splits
    blkg.append(obj.Split(pnts[20], 41, 42, prts))      # ws_geom
    blkg.append(obj.Split(pnts[26], 142, 42, prts))     # (ws_geom + wc_geom)


# geometry type 3
elif geomnum == 3:
    # x split
    blkg.append(obj.Split(pnts[3], 25, 41, prts))       # 0.0

    # y split
    blkg.append(obj.Split(pnts[13], 21, 25, prts))      # 0.0

    # block deletion
    blkg.append(obj.Delete(41))                         # delete block below film wall

    # x splits
    blkg.append(obj.Split(pnts[12], 86, 87, prts))      # heo_geom
    blkg.append(obj.Split(pnts[10], 87, 88, prts))      # hi_geom
    blkg.append(obj.Split(pnts[9], 127, 88, prts))      # (hi_geom + hd_geom)

    # z splits
    blkg.append(obj.Split(pnts[32], 41, 42, prts))      # ws_geom
    blkg.append(obj.Split(pnts[36], 190, 42, prts))     # (ws_geom + wc_geom)


# geometry type 4
elif geomnum == 4:
    # x split
    blkg.append(obj.Split(pnts[5], 25, 41, prts))       # 0.0

    # y split
    blkg.append(obj.Split(pnts[17], 21, 25, prts))      # 0.0

    # block deletion
    blkg.append(obj.Delete(41))                         # delete block below film wall

    # y split
    blkg.append(obj.Split(pnts[5], 87, 70, prts))       # lt_geom

    # x split
    blkg.append(obj.Split(pnts[1], 70, 41, prts))       # (hi_geom + hd_geom)
    
    # block deletion
    blkg.append(obj.Delete(54))                         # delete block above film inlet
    
    # x split
    blkg.append(obj.Split(pnts[16], 86, 87, prts))      # hi_geom
    blkg.append(obj.Split(pnts[14], 87, 128, prts))     # (hi_geom + hd_geom)

    # z splits
    blkg.append(obj.Split(pnts[36], 41, 42, prts))      # ws_geom
    blkg.append(obj.Split(pnts[42], 230, 42, prts))     # (ws_geom + wc_geom)
print("\t- done blocking")




# vertex-point associations
print("\nAssociating vertices to points...")


# geometry type 1
if geomnum == 1:
    # film inlet region
    # lower zbound
    verts.append(obj.Vert(41, pnts[0]))
    verts.append(obj.Vert(86, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(70, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(25, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(42, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(90, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(74, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(26, pnts[verts[-1].getpnt().getnum()+1]))

    # film outlet region
    # lower zbound
    verts.append(obj.Vert(37, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(85, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(69, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(21, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(38, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(89, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(73, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(22, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done outer vertices")


    # film inlet region
    # lower zint
    verts.append(obj.Vert(112, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(111, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(110, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(109, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    verts.append(obj.Vert(136, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(135, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(134, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(133, pnts[verts[-1].getpnt().getnum()+1]))

    # film outlet region
    # lower zint
    verts.append(obj.Vert(106, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(105, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(104, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(103, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    verts.append(obj.Vert(130, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(129, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(128, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(127, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done inner vertices")


# geometry type 2
elif geomnum == 2:
    # film inlet region
    # lower zbound
    verts.append(obj.Vert(41, pnts[0]))
    verts.append(obj.Vert(70, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(88, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(87, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(107, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(86, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(42, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(74, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(93, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(92, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(112, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(91, pnts[verts[-1].getpnt().getnum()+1]))

    # film outlet region
    # lower zbound
    verts.append(obj.Vert(37, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(69, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(106, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(21, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(38, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(73, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(111, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(22, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done outer vertices")


    # film inlet region
    # lower zint
    verts.append(obj.Vert(142, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(141, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(136, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(135, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(134, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(133, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    verts.append(obj.Vert(172, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(171, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(166, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(165, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(164, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(163, pnts[verts[-1].getpnt().getnum()+1]))

    # film outlet region
    # lower zint
    verts.append(obj.Vert(130, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(129, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(128, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(127, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    verts.append(obj.Vert(160, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(159, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(158, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(157, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done inner vertices")
    

# geometry type 3
elif geomnum == 3:
    # film inlet region
    # lower zbound
    verts.append(obj.Vert(41, pnts[0]))
    verts.append(obj.Vert(148, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(128, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(70, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(42, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(153, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(133, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(74, pnts[verts[-1].getpnt().getnum()+1]))

    # film outlet region
    # lower zbound
    verts.append(obj.Vert(88, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(147, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(127, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(87, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(107, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(86, pnts[verts[-1].getpnt().getnum()+1]))
    
    verts.append(obj.Vert(37, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(146, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(126, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(69, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(106, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(21, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(93, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(152, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(132, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(92, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(112, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(91, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(38, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(151, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(131, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(73, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(111, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(22, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done outer vertices")


    # film inlet region
    # lower zint
    verts.append(obj.Vert(190, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(189, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(188, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(187, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    verts.append(obj.Vert(230, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(229, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(228, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(227, pnts[verts[-1].getpnt().getnum()+1]))

    # film outlet region
    # lower zint
    verts.append(obj.Vert(182, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(179, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(178, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(177, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(174, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(173, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(172, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(171, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(170, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(169, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    verts.append(obj.Vert(222, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(219, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(218, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(217, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(214, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(213, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(212, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(211, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(210, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(209, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done inner vertices")



# geometry type 4
elif geomnum == 4:
    # film inlet region
    # lower zbound
    verts.append(obj.Vert(41, pnts[0]))
    verts.append(obj.Vert(130, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(108, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(129, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(177, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(107, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(42, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(136, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(113, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(135, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(183, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(112, pnts[verts[-1].getpnt().getnum()+1]))

    # film outlet region
    # lower zbound
    verts.append(obj.Vert(88, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(128, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(176, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(87, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(152, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(86, pnts[verts[-1].getpnt().getnum()+1]))
    
    verts.append(obj.Vert(37, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(127, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(175, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(69, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(151, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(21, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zbound
    verts.append(obj.Vert(93, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(134, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(182, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(92, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(158, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(91, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(38, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(133, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(181, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(73, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(157, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(22, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done outer vertices")


    # film inlet region
    # lower zint
    verts.append(obj.Vert(230, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(229, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(222, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(221, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(220, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(219, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    verts.append(obj.Vert(278, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(277, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(270, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(269, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(268, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(267, pnts[verts[-1].getpnt().getnum()+1]))

    # film outlet region
    # lower zint
    verts.append(obj.Vert(214, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(211, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(210, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(209, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(206, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(205, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(204, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(203, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(202, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(201, pnts[verts[-1].getpnt().getnum()+1]))

    # upper zint
    verts.append(obj.Vert(262, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(259, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(258, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(257, pnts[verts[-1].getpnt().getnum()+1]))

    verts.append(obj.Vert(254, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(253, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(252, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(251, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(250, pnts[verts[-1].getpnt().getnum()+1]))
    verts.append(obj.Vert(249, pnts[verts[-1].getpnt().getnum()+1]))
    print("\t- done inner vertices")



#################################################################### MESHING ####################################################################
print("\nMeshing...")
mshg = []        # meshing operations


# geometry type 1
if geomnum == 1:
    # x direction
    mshg.append(obj.Mesh(26, 74, hi_mesh))          # film
    mshg.append(obj.Mesh(74, 90, hd_mesh))          # distributor
    mshg.append(obj.Mesh(90, 42, hg_mesh))          # gas space
    print("\t- done x direction")

    # y direction
    mshg.append(obj.Mesh(22, 26, lt_mesh))          # total domain
    print("\t- done y direction")

    # z direction
    mshg.append(obj.Mesh(41, 112, ws1_mesh))        # side section 1 (at lower zbound)
    mshg.append(obj.Mesh(112, 136, wc_mesh))        # central section
    mshg.append(obj.Mesh(136, 42, ws2_mesh))        # side section 2 (at upper zbound)
    print("\t- done z direction")


# geometry type 2
elif geomnum == 2:
    # x direction
    mshg.append(obj.Mesh(91, 112, hi_mesh))         # film
    mshg.append(obj.Mesh(112, 92, hd_mesh))         # distributor
    mshg.append(obj.Mesh(92, 93, hg_mesh))          # gas space
    print("\t- done x direction")
    
    # y direction
    mshg.append(obj.Mesh(92, 74, lag_mesh))         # additional gas space
    mshg.append(obj.Mesh(22, 91, lt_mesh))          # total domain
    print("\t- done y direction")

    # z direction
    mshg.append(obj.Mesh(41, 142, ws1_mesh))        # side section 1 (at lower zbound)
    mshg.append(obj.Mesh(142, 172, wc_mesh))        # central section
    mshg.append(obj.Mesh(172, 42, ws2_mesh))        # side section 2 (at upper zbound)
    print("\t- done z direction")
    

# geometry type 3
elif geomnum == 3:
    # x direction
    mshg.append(obj.Mesh(87, 127, hi_mesh))         # film
    mshg.append(obj.Mesh(127, 147, hd_mesh))        # distributor
    mshg.append(obj.Mesh(147, 88, hg_mesh))         # gas space
    mshg.append(obj.Mesh(107, 87, heo_mesh))        # edge of outlet
    mshg.append(obj.Mesh(86, 107, hro_mesh))        # recessed outlet
    print("\t- done x direction")
    
    # y direction
    mshg.append(obj.Mesh(87, 70, lt_mesh))          # total domain
    mshg.append(obj.Mesh(69, 87, lro_mesh))         # recessed outlet
    print("\t- done y direction")

    # z direction
    mshg.append(obj.Mesh(41, 190, ws1_mesh))        # side section 1 (at lower zbound)
    mshg.append(obj.Mesh(190, 230, wc_mesh))        # central section
    mshg.append(obj.Mesh(230, 42, ws2_mesh))        # side section 2 (at upper zbound)
    print("\t- done z direction")


# geometry type 4
elif geomnum == 4:
    # x direction
    mshg.append(obj.Mesh(87, 176, hi_mesh))         # film
    mshg.append(obj.Mesh(176, 128, hd_mesh))        # distributor
    mshg.append(obj.Mesh(128, 88, hg_mesh))         # gas space
    mshg.append(obj.Mesh(152, 87, heo_mesh))        # edge of outlet
    mshg.append(obj.Mesh(86, 152, hro_mesh))        # recessed outlet
    print("\t- done x direction")
    
    # y direction
    mshg.append(obj.Mesh(129, 130, lag_mesh))       # additional gas space
    mshg.append(obj.Mesh(87, 107, lt_mesh))         # total domain
    mshg.append(obj.Mesh(69, 87, lro_mesh))         # recessed outlet
    print("\t- done y direction")

    # z direction
    mshg.append(obj.Mesh(41, 230, ws1_mesh))        # side section 1 (at lower zbound)
    mshg.append(obj.Mesh(230, 278, wc_mesh))        # central section
    mshg.append(obj.Mesh(278, 42, ws2_mesh))        # side section 2 (at upper zbound)
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