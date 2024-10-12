# this file contains all function definitions used in ICEM mesh creation scripts
# it is required to run any ICEM mesh creation script


############################################################### DO NOT EDIT BELOW ###############################################################
# dependencies
import numpy as np                          # numerical python
import rpl_gen_obj as obj                   # import class source file
import re                                   # regular expressions
import os                                   # operating system operations
from colorama import Fore, Style, init      # console output formatting (validated to run on a windows system)


# numerical precision (specify in obj!)
geomprec = obj.geomprec         	# numerical precision of point locations
meshprec = obj.meshprec             # numerical precision for mesh calculations


################################################################# PROGRAM START #################################################################
# initialize console formatting
init(autoreset=True)


# check for valid project name
def checkname(dir, projname):
    allowedchars = r'^[a-zA-Z0-9_+\-]+$'            # only letters, numbers and '_', '+', '-' are allowed
    validname = False

    if re.match(allowedchars, projname):
        projdir = os.path.join(dir, projname)       # project directory

        # directory already exists
        if os.path.exists(projdir):
            while True:
                # prompt to continue with existing folder
                q_folder = input(f"{Fore.RED}\nA folder with the specified project name '{projname}' already exists.{Style.RESET_ALL} Existing files in this folder with the project name will be overwritten.\nUse this folder anyway? (y/n)\n>>> ").lower()                
                
                # override existing files
                if q_folder == "y":
                    validname = True
                    break               
                # do not override
                elif q_folder == "n":
                    break
                else:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.\n")
        
        # directory does not exist
        else:
            validname = True

    # project name does not meet requirements
    else:
        print(f"{Fore.RED}Invalid project name.{Style.RESET_ALL} Only letters, numbers and '_', '+', '-' are allowed.\n")

    return validname


# checks config file if the geomtype matches the current selection
def checkconf(conffile, geomtype):
    typematch = False
    with open(conffile, 'r') as file:
        # reset pointer to first line
        file.seek(0)
        
        # check if file contains "geomtype" specification
        for line in file:
            line = line.strip()
            if line == geomtype:
                typematch = True
                break
    file.close()
    return typematch


# use specific config file
def useconf(dir, chosenfile, geomtype, typematch):
    # use file if geometry types match
    if typematch:
        print(f"{Fore.GREEN}\nReading from file ~\{os.path.relpath(chosenfile, dir)}{Style.RESET_ALL}")
        choosefile = True 
    
    # if types do nt match, user can choose it anyway
    else:
        while True:
            print(f"{Fore.RED}\nFile ~\{os.path.relpath(chosenfile, dir)} was not created for geometry type '{geomtype}'.{Style.RESET_ALL}")
            print("Using this file for reference might require additional user inputs.")
            q_use = input("Use file anyway? (y/n)\n>>> ").lower()

            if q_use == "y":
                choosefile = True
                print(f"{Fore.GREEN}\nReading from file ~\{os.path.relpath(chosenfile, dir)}{Style.RESET_ALL}")
                break
            elif q_use == "n":
                choosefile = False
                break
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.")
    return choosefile


# gets config file from directory and subdirectories, matching geomtype
def getconf(dir, geomtype):         
    while True:
        # input config file name
        confinput = input("\nEnter filename of .conf file to be read:\n>>> ")
        
        # define name and filename
        if confinput.endswith(".conf"):
            confname = confinput.replace(".conf","")
            conffile = confinput
        else:
            confname = confinput
            conffile = confinput + ".conf"

        # generate filelist matching specified conffile
        filelist = []
        # search dir and subdirectories for conffile
        for foldername, subfolders, filenames in os.walk(dir):
            for name in filenames:
                # check for conffile
                if conffile in name:
                    filepath = os.path.join(foldername, name)
                    relpath = os.path.relpath(filepath, dir)
                    filelist.append(relpath)
        length = len(filelist)
        
        # prompt user to choose file in case of multiple options
        if length > 1:
            typematch = False
            
            while True:
                # print filelist
                print(f"\nFound {length} config files matching the name '{confname}':")
                for i in range(length):
                    print(f"\t{i + 1}: ~\{filelist[i]}")

                # input config file to be read
                q_input = input("Enter number of file to be read or 'q' to enter a different filename:\n>>> ")
                try:
                    index = int(q_input) - 1
                    if 0 <= index < length:
                        chosenfile = os.path.join(dir, filelist[index])
                        typematch = checkconf(chosenfile, geomtype)
                        
                        if useconf(dir, chosenfile, geomtype, typematch):
                            typematch = True
                            break
                    else:
                        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number between 1 and {length}.\n")
                except ValueError:
                    # quit = enter new conf filename
                    if q_input.lower() == "q":
                        print()
                        break
                    else:
                        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number between 1 and {length}.\n")
            if typematch:
                break
        
        # single file found
        elif length == 1:
            chosenfile = os.path.join(dir, filelist[0])
            typematch = checkconf(chosenfile, geomtype)
            
            if useconf(dir, chosenfile, geomtype, typematch):
                break
        
        # no matching files found
        else:
            print(f"{Fore.RED}No matching files found.{Style.RESET_ALL}\n")
    return chosenfile


################################################################ PARAMETER INPUT ################################################################
# get specific object from list
def getobj(name, objs):
    for obj in objs:
        if obj.getname() == name:
            return obj
        

# get geometry info from config file
def getconfgeom(conffile, geom):
    with open(conffile, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith(geom):
                confgeoms = line.split()[1:]
                break
    file.close()
    return confgeoms


# assign config geometry to geometry
def assignconfgeom(geoms, confgeoms):
    for geom in geoms:
        geommatch = False               # matching geometry found in config file
        name = geom.getname()           # name of geometry
        
        # look for match in config file
        for confgeom in confgeoms:
            if confgeom.startswith(name):
                geommatch = True
                
                if "=" in confgeom:
                    geom.setval(float(confgeom.split("=")[-1]))
                else:
                    print(f"{Fore.RED}\nNo reference for '{name}' found.{Style.RESET_ALL} Specify size manually.")
                    setgeomval(geom)
                break

        if not geommatch:
            print(f"{Fore.RED}\nNo reference for '{name}' found.{Style.RESET_ALL} Specify size manually.")
            setgeomval(geom)


# set value of specified geometry
def setgeomval(geom):
    print()
    # if no value has been assigned to geometry
    if geom.getval() == 0.0:
        while True:
            val_inp = input(f"Enter {geom.getdescr()} ({geom.getname()}):\n>>> ")                 
            try:
                # accounting for numbers
                if "number" in geom.getdescr():
                    val = abs(int(val_inp))
                # conversion from [mm] to [m]
                else:
                    val = abs(float(val_inp)/1000.0)
                geom.setval(val)
                break
            except ValueError:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
    
    # value has been previously defined
    else:
        while True:
            # accounting for numbers
            if "number" in geom.getdescr():
                val_inp = input(f"Enter {geom.getdescr()} ({geom.getname()}):\n>>> ({geom.getval()}) ")   
            else:
                val_inp = input(f"Enter {geom.getdescr()} ({geom.getname()}):\n>>> ({round(geom.getval()*1000.0, geomprec)}) ")           
            
            try:
                # accounting for numbers
                if "number" in geom.getdescr():
                    val = abs(int(val_inp))        
                # conversion from [mm] to [m]
                else:
                    val = abs(float(val_inp)/1000.0)
                geom.setval(val)
                break
            except ValueError:
                # no change in value if value is already the desired one
                if val_inp == "":
                    break
                else:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")


# check geom for nonzero values
def checkgeom(geoms):
    nonzero = True
    for geom in geoms:
        if geom.getval == 0.0:
            nonzero = False
            break

    if not nonzero:
        print(f"{Fore.RED}\nGeometry with value 0.0 found.{Style.RESET_ALL}")
    return nonzero


# check for valid xgeom parameters
def checkxgeom(xgeom):
    valid = False

    # get values for calculation           
    ht = getobj(obj.ht_geomname, xgeom).getval()        # total domain size  
    hi = getobj(obj.hi_geomname, xgeom).getval()        # size of film inlet  
    hd = getobj(obj.hd_geomname, xgeom).getval()        # size of distributor
    
    # sum of inlet and distributor sizes must be smaller than total size 
    if (hi + hd) < ht:
        valid = True
    else:
        print(f"\n{Fore.RED}Invalid choice of values for x geometry parameters.{Style.RESET_ALL}")
    return valid


# set values for xgeom
def setxgeom(xgeom):
    while True:
        for geom in xgeom:
            setgeomval(geom)

        # check for valid parameters
        if checkxgeom(xgeom):
            break


# check for valid ygeom parameters with horizontal structures
def checkygeom_hstruct(ygeom):
    valid = False
    
    # get values for calculation
    lt = getobj(obj.lt_geomname, ygeom).getval()        # total domain size
    ls = getobj(obj.ls_geomname, ygeom).getval()        # structures
    lgr = getobj(obj.lgr_geomname, ygeom).getval()      # grooves
    li = getobj(obj.li_geomname, ygeom).getval()        # inlet section
    lo = getobj(obj.lo_geomname, ygeom).getval()        # outlet section

    # minimum possible values for domain length with structures
    if (li + ls + 2*lgr + lo) <= lt:
        valid = True
    else:
        print(f"\n{Fore.RED}Invalid choice of values for y geometry parameters.{Style.RESET_ALL}")
    return valid


# set values for ygeom with horizontal structures
def setygeom_hstruc(ygeom):
    while True:
        # set total size (L) or number of structures (n_s)
        while True:
            q_quant = input("\nSpecify the total domain length (L) [mm] or the total number of structures (N)? (l/n)\nThe other value will be computed.\n>>> ").lower()

            # set total domain size
            if q_quant == "l":
                setgeomval(getobj(obj.lt_geomname, ygeom))      # total domain size
                break

            # set number of structures
            elif q_quant == "n":
                setgeomval(getobj(obj.ns_geomname, ygeom))      # number of structures
                break
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'l' or 'n'.")

        # set values for all other geometry parts
        for geom in ygeom:
            if not geom.getname() == obj.lt_geomname and not geom.getname() == obj.ns_geomname:
                setgeomval(geom)

        # get values for calculation
        lt = getobj(obj.lt_geomname, ygeom).getval()        # total domain size
        ls = getobj(obj.ls_geomname, ygeom).getval()        # structures
        lgr = getobj(obj.lgr_geomname, ygeom).getval()      # grooves
        li = getobj(obj.li_geomname, ygeom).getval()        # inlet section
        lo = getobj(obj.lo_geomname, ygeom).getval()        # outlet section
        ns = getobj(obj.ns_geomname, ygeom).getval()        # number of structures

        if q_quant == "n":
            break
        else:
            # check for valid parameters
            if checkygeom_hstruct(ygeom):
                break

    # calculate number of structures
    if q_quant == "l":
        ns = int(round(np.floor(round((lt-li-lo-lgr)/(ls+lgr), geomprec))))
        
        # set number of structures
        getobj(obj.ns_geomname, ygeom).setval(ns)
        ns_geom = getobj(obj.ns_geomname, ygeom)            # temp object
        print(f"{Style.BRIGHT}\nSetting {ns_geom.getdescr()}: {ns_geom.getname()} = {ns_geom.getval()}{Style.RESET_ALL}")
        
        # calculating extra length to reach desired total domain length
        if (li + ns*(ls + lgr) + lgr + lo) < lt:
            ext = round(lt - (li + ns*(ls + lgr) + lgr + lo), geomprec)     # set remainder of total length minus sum of length computed from inlet
            lo = round(lo + ext, geomprec)                                  # adjust length of smooth outlet region
            
            # adjust value of smooth outlet region
            getobj(obj.lo_geomname, ygeom).setval(lo)
            lo_geom = getobj(obj.lo_geomname, ygeom)        # temp object
            print(f"{Style.BRIGHT}\nAdjusting {lo_geom.getdescr()}: {lo_geom.getname()} = {round(lo_geom.getval()*1000.0, geomprec)}{Style.RESET_ALL}")

    # calculate total domain length
    else:
        lt = round(li + ns*(ls + lgr) + lgr + lo, geomprec)
        
        # set total length of domain
        getobj(obj.lt_geomname, ygeom).setval(lt)
        lt_geom = getobj(obj.lt_geomname, ygeom)            # temp object
        print(f"{Style.BRIGHT}\nSetting {lt_geom.getdescr()}: {lt_geom.getname()} = {round(lt_geom.getval()*1000.0, geomprec)}{Style.RESET_ALL}")
        
        # extend/reduce smooth part at the end of domain to reach a certain y-length
        while True:
            q_addl = input("\nDo you want to add/remove domain length at the film outlet (l_o)? (y/n)\n>>> ").lower()
            if q_addl == "y":
                while True:
                    while True:
                        # get additional domain length
                        ext_inp = input("\nEnter additional domain size in y-direction (ext) [mm].\nThis value can be negative but its absolute value must be smaller than the length of the unstructured wall at the outlet.\n>>> ")
                        try:
                            ext = float(ext_inp)/1000.0     # conversion from [mm] to [m]
                            break
                        except ValueError:
                            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
                    if ext <= -lo:
                        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
                    else:
                        break
                
                # adjust lengths
                getobj(obj.lt_geomname, ygeom).setval(lt + ext)         # adjust total length of domain
                lt_geom = getobj(obj.lt_geomname, ygeom)                # temp object
                print(f"{Style.BRIGHT}\nSetting {lt_geom.getdescr()}: {lt_geom.getname()} = {round(lt_geom.getval()*1000.0, geomprec)}{Style.RESET_ALL}")
                
                getobj(obj.lo_geomname, ygeom).setval(lo + ext)         # adjust length of smooth outlet region
                lo_geom = getobj(obj.lo_geomname, ygeom)                # temp object
                print(f"{Style.BRIGHT}\nSetting {lo_geom.getdescr()}: {lo_geom.getname()} = {round(lo_geom.getval()*1000.0, geomprec)}{Style.RESET_ALL}")

                break
            elif q_addl == "n":
                break
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter 'y' or 'n'.")


# set values for ygeom with smooth filmwall
def setygeom_smooth(ygeom):
    for geom in ygeom:
        setgeomval(geom)


# check for valid zgeom parameters
def checkzgeom(zgeom):
    valid = False
    
    # get values for calculation    
    wt = getobj(obj.wt_geomname, zgeom).getval()        # total domain size
    wc = getobj(obj.wc_geomname, zgeom).getval()        # central section

    if wc < wt:
        valid = True
    else:
        print(f"\n{Fore.RED}Invalid choice of values for z geometry parameters.{Style.RESET_ALL}")
    return valid


# set values for zgeom
def setzgeom(zgeom):
    while True:
        setgeomval(getobj(obj.wt_geomname, zgeom))      # total domain size
        setgeomval(getobj(obj.wc_geomname, zgeom))      # central section

        # get values for calculation    
        wt = getobj(obj.wt_geomname, zgeom).getval()    # total domain size
        wc = getobj(obj.wc_geomname, zgeom).getval()    # central section

        # check for valid parameters
        if checkzgeom(zgeom):
            break

    # set side sections
    val = round((wt - wc)/2.0, geomprec)            # side sections
    getobj(obj.ws_geomname, zgeom).setval(val)

        
################################################################ MESHING RULES ##################################################################
# calculate uniform node distribution
def uniform(sect, h):
    # create meshing array
    mesh = [None]*7
    mesh[0] = "uniform"                             # rule
    mesh[1] = int(np.ceil(sect.getsize()/h)) + 1    # n
    mesh[2] = 0.0                                   # h1rel
    mesh[3] = 0.0                                   # h2rel
    mesh[4] = 2                                     # r1
    mesh[5] = 2                                     # r2
    mesh[6] = h                                     # lmax (absolute)

    sect.setmesh(mesh)


# calculate sum of relative cell sizes, geometric distribution
def geomsum(hrel, nodes, rate):
    # sum over all n-1 cells
    sum = hrel * (1 - rate**(nodes - 1)) / (1 - rate)
    return round(sum, meshprec)

# calculate growth rate, geometric distribution
def geomrate(hrel_min, hrel_max, nodes):
    # growth rate to fit hrel_min to hrel_max to nodes-1 cells
    rate = (hrel_max/hrel_min)**(1/(nodes-2))
    return round(rate, meshprec)

# calculate geometric node distribution
def geomcalc(length, hmin, hmax):
    hrel_min = hmin/length                      # relative minimum cell size (fixed)
    hrel_max = hmax/length                      # relative maximum cell size (max. allowed)
    nodes = int(np.ceil(1.0/hrel_min) + 1)      # starting number of nodes, corresponding to uniform distribution with max. h1rel
    rate = geomrate(hrel_min, hrel_max, nodes)  # starting growth rate
    htot = geomsum(hrel_min, nodes, rate)       # total relative length of all cells combined
    
    # calculate maximum possible number of nodes for which hrel_max can be retained (fewer nodes lead to higher values of hrel_max)
    while htot > 1:
        nodes -= 1
        rate = geomrate(hrel_min, hrel_max, nodes)
        htot = geomsum(hrel_min, nodes, rate)
    nodes += 1
    
    # adapt growth rate to maximum possible number of nodes
    rate = geomrate(hrel_min, hrel_max, nodes)
    htot = geomsum(hrel_min, nodes, rate)
    while htot > 1:
        rate -= 10**(-meshprec)
        htot = geomsum(hrel_min, nodes, rate)
    rate = round(rate, meshprec)

    return rate, nodes

# calculate geo1 node distribution
def geo1(sect, hmin, hmax):
    size = sect.getsize()
    
    # perform geo1 calculation
    if hmin + hmax <= size:
        # geo calculation
        rate, nodes = geomcalc(size, hmin, hmax)

        # create meshing array
        mesh = [None]*7
        mesh[0] = "geo1"        # rule
        mesh[1] = nodes         # n
        mesh[2] = hmin/size     # h1rel
        mesh[3] = hmax/size     # h2rel
        mesh[4] = rate          # r1
        mesh[5] = 1.0           # r2
        mesh[6] = hmax          # lmax (absolute)

        sect.setmesh(mesh)
    
    # for unsuitable values, use uniform distribution
    else:
        uniform(sect, hmin)

# calculate geo2 node distribution
def geo2(sect, hmin, hmax):
    size = sect.getsize()
    
    # perform geo2 calculation
    if hmin + hmax <= size:
        # geo calculation
        rate, nodes = geomcalc(size, hmin, hmax)

        # create meshing array
        mesh = [None]*7
        mesh[0] = "geo2"        # rule
        mesh[1] = nodes         # n
        mesh[2] = hmax/size     # h1rel
        mesh[3] = hmin/size     # h2rel
        mesh[4] = 1.0           # r1
        mesh[5] = rate          # r2
        mesh[6] = hmax          # lmax (absolute)

        sect.setmesh(mesh)

    # for unsuitable values, use uniform distribution
    else:
        uniform(sect, hmin)


############################################################## MESHING FUNCTIONS ################################################################
# message to be displayed when custom meshing is selected
def custommeshing_info(): 
    print(f"{Style.BRIGHT}\n\nCustom meshing:{Style.RESET_ALL}")
    print("    - In every coordinate direction, the domain is split into sections for meshing through blocking.")
    print("    - Meshing parameters are set once for every section and apply to all related edges of that section.")
    print("    - See documentation for more information.")
    print("\nAvailable meshing rules:")
    print("    - uniform:     'uni'   uniform cell size along edge")
    print("    - geometric1:  'geo1'  increasing cell size in line with positive coordinate direction (normal vector)")
    print("    - geometric2:  'geo2'  decreasing cell size in line with positive coordinate direction (normal vector)")
    print("Always check your mesh after creation in ICEM!")
    input("\nPress any key to continue...")


# distribution rule in custom meshing
def custommeshing_distr(sect):
    print()
    
    # no mesh has been assigned to section
    if sect.getmesh()[0] is None:
        while True:
            # meshing rule to be used
            q_distr = input(f"Enter node distribution for section '{sect.getname()}':\n    - geo1\n    - geo2\n    - uni\n>>> ").lower()

            if q_distr == "geo1" or q_distr == "geo2" or q_distr == "uni":
                break
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter one of the provided options.")
    
    # mesh has been previously defined
    else:
        while True:
            prevdistr = sect.getmesh()[0].replace("form", "")
            
            # meshing rule to be used
            q_distr = input(f"Enter node distribution for section '{sect.getname()}':\n    - geo1\n    - geo2\n    - uni\n>>> ({prevdistr}) ").lower()

            # new distribution
            if q_distr == "geo1" or q_distr == "geo2" or q_distr == "uni":
                break
            # retain distribution
            elif q_distr == "":
                q_distr = prevdistr
                break
            else:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter one of the provided options.")
    return q_distr


# uniform custom meshing
def custommeshing_uni(sect, distr):
    length = sect.getsize()     # edge length in m
    
    # mesh has been previously defined with uniform distribution
    try:
        if sect.mesh[0].replace("form", "") == distr:
            while True:
                while True:
                    # previous value for maximum uniform cell size
                    prevh = sect.getmesh()[6]
                    
                    # query for maximum cell size
                    q_h = input(f"Enter maximum cell size in [mm] for uniform distribution.\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ({round(prevh*1000.0, meshprec)}) ")
                    try:
                        # conversion from [mm] to [m]
                        h = round(float(q_h)/1000.0, meshprec)
                        break
                    except ValueError:
                        # assing previous value of h
                        if q_h == "":
                            h = prevh
                            break
                        else:
                            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.") 
                if length < h:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
                else:
                    break
            
        # different distribution has been previously assigned to section
        else:
            while True:
                while True:
                    # maximum cell size
                    q_h = input(f"Enter maximum cell size in [mm] for uniform distribution.\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ")
                    try:
                        h = round(float(q_h)/1000.0, meshprec)
                        break
                    except ValueError:
                        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
                
                if length < h:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
                else:
                    break
    
    # no mesh has been previously assigned to section
    except AttributeError:
        while True:
            while True:
                # maximum cell size
                q_h = input(f"Enter maximum cell size in [mm] for uniform distribution.\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ")
                try:
                    h = round(float(q_h)/1000.0, meshprec)
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
            
            if length < h:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
            else:
                break

    # uniform meshing
    uniform(sect, h)


# geometric1/2 custom meshing
def custommeshing_geo(sect, distr):
    length = sect.getsize()     # edge length in m
    
    # mesh has been previously defined with geometric distribution
    try:
        if sect.getmesh()[0] == distr:
            while True:
                while True:
                    # previous value for minimum cell size
                    prevhmin = min(sect.getmesh()[2], sect.getmesh()[3])*length
                    
                    # minimum cell size
                    q_hmin = input(f"Enter minimum cell size in [mm].\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ({round(prevhmin*1000.0, meshprec)}) ")
                    try:
                        hmin = round(float(q_hmin)/1000.0, meshprec)
                        break
                    except ValueError:
                        # assing previous value of hmin
                        if q_hmin == "":
                            hmin = prevhmin
                            break
                        else:
                            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
                
                while True:
                    # previous value for maximum cell size
                    prevhmax = sect.getmesh()[6]
                    
                    # maximum cell size
                    q_hmax = input(f"Enter maximum cell size in [mm].\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ({round(prevhmax*1000.0, meshprec)}) ")
                    try:
                        hmax = round(float(q_hmax)/1000.0, meshprec)
                        break
                    except ValueError:
                        # assing previous value of hmax
                        if q_hmax == "":
                            hmax = prevhmax
                            break
                        else:
                            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")

                if hmin >= hmax or length < hmin or length < hmax:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
                else:
                    break
    
        # different distribution has been previously assigned to section
        else:
            while True:
                while True:
                    # minimum cell size
                    q_hmin = input(f"Enter minimum cell size in [mm].\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ")
                    try:
                        hmin = round(float(q_hmin)/1000.0, meshprec)
                        break
                    except ValueError:
                        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
                
                while True:
                    # maximum cell size
                    q_hmax = input(f"Enter maximum cell size in [mm].\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ")
                    try:
                        hmax = round(float(q_hmax)/1000.0, meshprec)
                        break
                    except ValueError:
                        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")

                if hmin >= hmax or length < hmin or length < hmax:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
                else:
                    break
    
    # no mesh has been previously assigned to section
    except AttributeError:
        while True:
            while True:
                # minimum cell size
                q_hmin = input(f"Enter minimum cell size in [mm].\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ")
                try:
                    hmin = round(float(q_hmin)/1000.0, meshprec)
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
            
            while True:
                # maximum cell size
                q_hmax = input(f"Enter maximum cell size in [mm].\nMust be smaller than the respective edge length {round(length*1000.0, geomprec)} mm\n>>> ")
                try:
                    hmax = round(float(q_hmax)/1000.0, meshprec)
                    break
                except ValueError:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")

            if hmin >= hmax or length < hmin or length < hmax:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
            else:
                break

    # geometric meshing
    if distr == "geo1":
        geo1(sect, hmin, hmax)
    else:
        geo2(sect, hmin, hmax)


# custom meshing
def custommeshing(sect):
    # mesh distribution rule
    distr = custommeshing_distr(sect)

    # uniform meshing
    if distr == "uni":
        custommeshing_uni(sect, distr)

    # geo1 meshing
    elif distr == "geo1":
        custommeshing_geo(sect, distr)

    # geo2 meshing
    elif distr == "geo2":
        custommeshing_geo(sect, distr)

    print(sect.meshinfo().lstrip("\t").replace("- ", ""))


# get refinement factor for meshing with config file
def confmeshing_factor():
    print()
    print()

    while True:
        while True:
            inp_factor = input("Specify factor for mesh refinement/coarsening.\nIt will be applied to all specified absolute cell sizes, respective growth factors and node counts will be calculated.\nThe default is '1.0'. Larger values will coarsen the mesh, smaller values refine it. Values can be given in decimal or fraction representation.\n>>> (1.0) ")
            try:
                factor = float(eval(inp_factor))
                break
            except ValueError:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
            except NameError:
                print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
            except SyntaxError:
                if inp_factor == "":
                    factor = 1.0
                    break
                else:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Please enter a valid number.")
        if factor <= 0.0:
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL} Refinement factor must be larger than zero.")
        else:
            break
    return factor


# reference meshing function
def confmeshing_fnc(sect, factor, mesh):
    # uniform distribution
    if mesh[0] == "uniform":
        h = round(factor*float(mesh[6]), meshprec)
        uniform(sect, h)
    
    # geo1 distribution
    elif mesh[0] == "geo1":
        hmin = round(factor*float(mesh[2])*sect.getsize(), meshprec)
        hmax = round(factor*float(mesh[3])*sect.getsize(), meshprec)
        geo1(sect, hmin, hmax)

    # geo2 distribution
    elif mesh[0] == "geo2":
        hmin = round(factor*float(mesh[3])*sect.getsize(), meshprec)
        hmax = round(factor*float(mesh[2])*sect.getsize(), meshprec)
        geo2(sect, hmin, hmax)

    # custom meshing
    else:
        print(f"{Fore.RED}Meshing with reference for section '{sect.getname()}' failed.{Style.RESET_ALL} Custom meshing:")
        custommeshing(sect)


# meshing with reference config file
def confmeshing(conffile, sects, factor):
    with open(conffile, 'r') as file:        
        for sect in sects:
            sectmatch = False               # matching section found in config file        
            name = sect.getname()
            
            # reset pointer to first line
            file.seek(0)

            for line in file:
                line = line.strip()
                if line.startswith(name):
                    sectmatch = True
                    mesh = line.split()[1:]
                    break
            # custom meshing
            if not sectmatch:
                print(f"{Fore.RED}\nNo reference mesh for section '{name}' found.{Style.RESET_ALL} Custom meshing:")
                custommeshing(sect)
            # reference meshing   
            else:
                confmeshing_fnc(sect, factor, mesh)
    file.close()


################################################################# WRITE TO FILE #################################################################
# add list entries at start of .rpl file
def rpl_start(list):
    #list.append("ic_set_global geo_cad 0 toptol_userset\n")
    list.append("ic_set_global geo_cad 0.0 toler\n")
    list.append("ic_undo_group_begin\n")
    list.append("ic_geo_new_family GEOM\n")
    list.append("ic_boco_set_part_color GEOM\n")
    list.append("ic_empty_tetin\n")
    list.append("\n")
    return list


# add class object entries to .rpl file
def rpl_obj(list, geoms):
    for geom in geoms:
        list = geom.print(list)

    if isinstance(geoms[0], obj.Part) or isinstance(geoms[0], obj.Body):
        list.append("ic_delete_empty_parts\n")
    
    list.append("\n")
    return list


# add list entries for 2D blocking initialization to .rpl file
def rpl_2Dblocking(list, body):
    list.append("ic_hex_unload_blocking\n")
    list.append("ic_hex_initialize_mesh 2d new_numbering new_blocking " + body.getname() + "\n")
    list.append("ic_hex_unblank_blocks\n")
    list.append("ic_hex_multi_grid_level 0\n")
    list.append("ic_hex_projection_limit 0\n")
    list.append("ic_hex_default_bunching_law default 2.0\n")
    list.append("ic_hex_floating_grid off\n")
    list.append("ic_hex_transfinite_degree 1\n")
    list.append("ic_hex_unstruct_face_type one_tri\n")
    list.append("ic_hex_set_unstruct_face_method uniform_quad\n")
    list.append("ic_hex_set_n_tetra_smoothing_steps 20\n")
    list.append("ic_hex_error_messages off_minor\n")
    list.append("ic_hex_set_piercing 0\n")
    list.append("\n")
    return list


# add list entries for 3D blocking initialization to .rpl file
def rpl_3Dblocking(list, body):
    list.append("ic_hex_unload_blocking\n")
    list.append("ic_hex_initialize_blocking {} " + body.getname() + " 0 101\n")
    list.append("ic_hex_unblank_blocks\n")
    list.append("ic_hex_multi_grid_level 0\n")
    list.append("ic_hex_projection_limit 0\n")
    list.append("ic_hex_default_bunching_law default 2.0\n")
    list.append("ic_hex_floating_grid off\n")
    list.append("ic_hex_transfinite_degree 1\n")
    list.append("ic_hex_unstruct_face_type one_tri\n")
    list.append("ic_hex_set_unstruct_face_method uniform_quad\n")
    list.append("ic_hex_set_n_tetra_smoothing_steps 20\n")
    list.append("ic_hex_error_messages off_minor\n")
    list.append("ic_hex_set_piercing 0\n")
    list.append("\n")
    return list


# add list entries at end of file to .rpl file
def rpl_end(list):
    list.append("ic_undo_group_end\n")
    return list


# add list entries at start of .conf file
def conf_start(list, projname):
    list.append(f"Configuration file for {projname}\n")
    list.append("\n")
    return list


# add list entries for 2D geometry to .conf file
def conf_geom2D(list, xgeom, ygeom):
    list.append("Summary of geometric parameters:\n")
    list.append("x-dimension:\n")
    for geom in xgeom:
        list.append(geom.print())
    
    list.append("y-dimension:\n")
    for geom in ygeom:
        list.append(geom.print())

    list.append("\n")
    return list


# add list entries for 3D geometry to .conf file
def conf_geom3D(list, xgeom, ygeom, zgeom):
    list.append("Summary of geometric parameters:\n")
    list.append("x-dimension:\n")
    for geom in xgeom:
        list.append(geom.print())
    
    list.append("y-dimension:\n")
    for geom in ygeom:
        list.append(geom.print())
    
    list.append("z-dimension:\n")
    for geom in zgeom:
        list.append(geom.print())

    list.append("\n")
    return list


# add list entries for 2D meshing to .conf file
def conf_mesh2D(list, xsects, ysects):
    list.append("Summary of meshing parameters:\n")
    list.append("x-dimension:\n")
    for sect in xsects:
        list.append(sect.print())
    
    list.append("y-dimension:\n")
    for sect in ysects:
        list.append(sect.print())

    list.append("\n")
    list.append("\n")
    return list


# add list entries for 3D meshing to .conf file
def conf_mesh3D(list, xsects, ysects, zsects):
    list.append("Summary of meshing parameters:\n")
    list.append("x-dimension:\n")
    for sect in xsects:
        list.append(sect.print())
    
    list.append("y-dimension:\n")
    for sect in ysects:
        list.append(sect.print())
    
    list.append("z-dimension:\n")
    for sect in zsects:
        list.append(sect.print())

    list.append("\n")
    list.append("\n")
    return list


# add geometry type specification to .conf file
def conf_type(list, type):
    list.append("######################################################################################################################################################################\n")
    list.append("\n")
    list.append("\n")
    list.append(f"{type}\n")
    list.append("\n")
    return list


# add geometry data to .conf file
def conf_geomdata(list, type, geoms):
    line = type.strip() + " "
    for geom in geoms:
        line += geom.export()
    line += "\n"
    list.append(line)
    list.append("\n")
    return list


# add mesh data to .conf file
def conf_meshdata(list, sects):
    for sect in sects:
        list.append(sect.export())
    list.append("\n")
    return list