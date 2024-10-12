# this file contains all class definitions used in ICEM mesh creation scripts
# it is required to run any ICEM mesh creation script


# definition of global precision
# numerical precision of point locations, default = 6
geomprec = 6        
# numerical precision for mesh calculations, default = 6
meshprec = 6            # potentially higher runtime with higher values!   


# definition of global geometry names (retain default names recommended to ensure reference config file compatibility)
# x dimension
ht_geomname = "H"           # total domain size (default "H")
hi_geomname = "h_i"         # film inlet (default "h_i")
hd_geomname = "h_d"         # distributor (default "h_d")
dgr_geomname = "d_gr"       # grooves (default "d_gr")
heo_geomname = "h_eo"       # outlet type 2: edge region at recessed outlet (default "h_eo")
hro_geomname = "h_ro"       # outlet type 2: recessed outlet (default "h_ro")
# y dimension
lt_geomname = "L"           # total domain size (default "L")
lag_geomname = "l_ag"       # inlet type 2: additional gas space (default "l_ag")
ls_geomname = "l_s"         # structures (default "l_s")
lgr_geomname = "l_gr"       # grooves (default "l_gr")
li_geomname = "l_i"         # smooth wall at inlet (default "l_i")
lo_geomname = "l_o"         # smooth wall at outlet (default "l_o")
ns_geomname = "n_s"         # number of structures (default "n_s")
lro_geomname = "l_ro"       # outlet type 2: recessed outlet (default l_ro)
# z dimension
wt_geomname = "W"           # total domain size (default "W")
wc_geomname = "w_c"         # central section required for meshing (default "w_c")
ws_geomname = "w_s"         # side sections required for meshing (default "w_s")


# definition of global meshing section names (retain default names recommended to ensure reference config file compatibility)
# x dimension
hi_sectname = "h_i"         # film inlet (default "h_i")
hd_sectname = "h_d"         # distributor (default "h_d")
hg_sectname = "h_g"         # gas space (default "h_g")
dgr_sectname = "d_gr"       # grooves (default "d_gr")
heo_sectname = "h_eo"       # outlet type 2: edge region at recessed outlet (default "h_eo")
hro_sectname = "h_ro"       # outlet type 2: remaining outlet (default "h_ro")
# y dimension
lt_sectname = "l_t"         # total domain size (default "L")
lag_sectname = "l_ag"       # inlet type 2: additional gas space (default "l_ag")
ls_sectname = "l_s"         # structures (default "l_s")
lgr_sectname = "l_gr"       # grooves (default "l_gr")
li_sectname = "l_i"         # smooth wall at inlet (default "l_i")
lo_sectname = "l_o"         # smooth wall at outlet (default "l_o")
lro_sectname = "l_ro"       # outlet type 2: recessed outlet (default l_ro)
# z dimension
wc_sectname = "w_c"         # central section (default "w_c")
ws1_sectname = "w_s1"       # side section 1 (default "w_s1")
ws2_sectname = "w_s2"       # side section 2 (default "w_s2")


############################################################### DO NOT EDIT BELOW ###############################################################
# definition of global geometry descriptions
# x dimension
ht_geomdescr = "total domain size in x [mm]"                    # total domain size
hi_geomdescr = "size of film inlet [mm]"                        # film inlet
hd_geomdescr = "size of distributor [mm]"                       # distributor
dgr_geomdescr = "groove depth [mm]"                             # grooves
heo_geomdescr = "size of edge region at outlet [mm]"            # outlet type 2: edge region at recessed outlet
hro_geomdescr = "size of recessed outlet (x) [mm]"              # outlet type 2: recessed outlet
# y dimension
lt_geomdescr = "size of film wall [mm]"                         # film wall
lag_geomdescr = "size of additional gas space [mm]"             # inlet type 2: additional gas space
ls_geomdescr = "size of structures [mm]"                        # structures
lgr_geomdescr = "size of grooves [mm]"                          # grooves
li_geomdescr = "size of unstructured wall at inlet [mm]"        # smooth wall at inlet
lo_geomdescr = "size of unstructured wall at outlet [mm]"       # smooth wall at outlet
ns_geomdescr = "number of structures"                           # number of structures
lro_geomdescr = "size of recessed outlet (y) [mm]"              # outlet type 2: recessed outlet
# z dimension
wt_geomdescr = "total domain size in z [mm]"                    # total domain size
wc_geomdescr = "size of central section [mm]"                   # central section required for meshing
ws_geomdescr = "size of side sections [mm]"                     # side sections required for meshing


############################################################### GEOMETRY OBJECTS ################################################################
# geometry class definition
class Geometry:
    # geometry constructor
    def __init__(self, name, descr):
        self.name = name                # name of geometry
        self.descr = descr              # description of geometry
        self.val = 0.0                  # value of geometry in [m]

    # geometry destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):                  # name of geometry
        return self.name
    def getdescr(self):                 # description of geometry
        return self.descr
    def getval(self):                   # value of geometry in [m]
        return self.val
    
    #setter functions
    def setval(self, val):                # value of geometry in [m]
        # accounting for numbers
        if "number" in self.descr:
            self.val = int(val)
        else:
            self.val = val
    
    # creates line with geometry info
    def geominfo(self):
        # accounting for numbers
        if "number" in self.descr:
            line = f"\t- {self.descr}: {self.name} = {self.val}"
        # conversion from [m] to [mm]
        else:
            line = f"\t- {self.descr}: {self.name} = {round(self.val*1000.0, geomprec)}"
        return line
    
    # print function for .conf - readable by user
    def print(self):
        line = self.geominfo() + "\n"
        return line
    
    # print function for .conf - readable by script
    def export(self):            
        line = f" {self.name}={self.val}"
        return line
    
    # print geometry info to console 
    def printinfo(self):
        print(self.geominfo())


# point class definition
class Point:
    count = 0
    
    # point constructor
    def __init__(self, x, y, z):
        # set coordinates 
        self.x = round(x, geomprec)     # x coordinate of point
        self.y = round(y, geomprec)     # y coordinate of point
        self.z = round(z, geomprec)     # z coordinate of point
        
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
    def getx(self):                     # x coordinate of point
        return self.x
    def gety(self):                     # y coordinate of point
        return self.y
    def getz(self):                     # z coordinate of point
        return self.z
    def getname(self):                  # name of point
        return self.name
    def getnum(self):                   # number of point
        return self.num
    
    # print function for .rpl
    def print(self, list):
        line = "ic_point {} GEOM " + f"{self.name} {self.x},{self.y},{self.z}\n"    
        list.append(line)
        return list


# curve class definition
class Curve:
    count = 0

    # curve constructor
    def __init__(self, pnt1, pnt2):
        # set point association
        self.pnt1 = pnt1                # first point
        self.pnt2 = pnt2                # second point
        
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
    def getpnt1(self):                  # first point                     
        return self.pnt1
    def getpnt2(self):                  # second point
        return self.pnt2
    def getname(self):                  # name of curve
        return self.name
    def getnum(self):                   # number of curve
        return self.num
    
    # print function for .rpl
    def print(self, list):
        line1 = f"ic_delete_geometry curve names {self.name} 0\n"
        line2 = f"ic_curve point GEOM {self.name} " + "{" + f"{self.pnt1.getname()} {self.pnt2.getname()}" + "}\n"
        list.append(line1)
        list.append(line2)
        return list


# surface class definition
class Surface:
    count = 0

    # surface constructor
    def __init__(self, curves):
        self.curves = curves            # list of curves
        
        # set surface name and number. expecting maximum of 9999 surfaces. 
        if Surface.count >= 0 and Surface.count <= 9:
            self.name = "srf.000" + str(Surface.count)
        elif Surface.count >= 10 and Surface.count <= 99:
            self.name = "srf.00" + str(Surface.count)
        elif Surface.count >= 100 and Surface.count <= 999:
            self.name = "srf.0" + str(Surface.count)
        else:
            self.name = "srf." + str(Surface.count)
        self.num = Surface.count
        
        # increase surface count everytime a surface gets created
        Surface.count += 1

    # surface destructor
    def __del__(self):
        pass

    # getter functions
    def getcrvs(self):                  # list of curves
        return self.curves
    def getname(self):                  # name of surface
        return self.name
    def getnum(self):                   # number of surface
        return self.num
    
    # print function for .rpl
    def print(self, list):
        # list of curves in one string
        if len(self.curves) > 1:
            crvlist = "{"
            for crv in self.curves[:-1]:
                crvlist += crv.getname() + " "
            crvlist += self.curves[-1].getname() + "}"
        else:
            crvlist = "{" + self.curves[0].getname() + "}"
        line = f"ic_surface 2-4crvs GEOM {self.name} " + "{0.0 " + crvlist + "}\n"
        list.append(line)
        return list


# body part class definition
class Body:
    # body constructor
    def __init__(self, name, x, y, z):
        self.name = name                # name of part as set at the top of script
        self.x = x                      # x location of body point
        self.y = y                      # y location of body point
        self.z = z                      # z location of body point

    # body destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):                  # name of part
        return self.name
    def getx(self):                     # x location of body point
        return self.x
    def gety(self):                     # y location of body point
        return self.y
    def getz(self):                     # z location of body point
        return self.z
    
    # print function for .rpl
    def print(self, list): 
        line1 = f"ic_geo_new_family {self.name}\n"
        line2 = f"ic_boco_set_part_color {self.name}\n"
        line3 = "ic_geo_create_volume {" + f"{self.x} {self.y} {self.z}" + "} {} " + f"{self.name}\n"
        list.append(line1)
        list.append(line2)
        list.append(line3)
        return list


# boundary part class definition
class Part:
    # part constructor
    def __init__(self, name):
        self.name = name                # name of part
        self.geom = []                  # list of geometry associated with this part

    # part destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):                  # name of part
        return self.name
    def getgeom(self):                  # list of geometry associated with this part
        return self.geom
    
    # setter functions
    def setgeom(self, geom):            # list of geometry
        self.geom = geom
    def addgeom(self, obj):             # additional entry to list of geometry
        self.geom.append(obj)
    
    # print function for .rpl
    def print(self, list): 
        if len(self.geom) > 0:
            # parts can be either curves or surfaces
            if isinstance(self.geom[0], Curve):
                line = "ic_geo_set_part curve "
            elif isinstance(self.geom[0], Surface):
                line = "ic_geo_set_part surface "
        # empty part list
        else:
            return list
        
        # make list of geometry
        if len(self.geom) > 1:
            geomlist = "{"
            for prt in self.geom[:-1]:
                geomlist += prt.getname() + " "
            geomlist += self.geom[-1].getname() + "}"
        else:            
            geomlist = self.geom[0].getname()
        
        line += geomlist + f" {self.name} 0\n"
        list.append(line)
        return list


############################################################### BLOCKING OBJECTS ################################################################
# split block operation class definition
class Split:
    # split constructor
    def __init__(self, pnt, vert1, vert2, parts):
        # set point and vertice associations
        self.pnt = pnt	                # point closest to edge(vert1,vert2), at which edge will be cut
        self.vert1 = vert1              # first vertex of edge to be cut
        self.vert2 = vert2              # second vertex of edge to be cut
        self.parts = parts              # list of parts for split definition

    # split destructor
    def __del__(self):
        pass

    # getter functions
    def getpnt(self):	                # point closest to edge(vert1,vert2), at which edge will be cut
        return self.pnt
    def getvert1(self):                 # first vertex of edge to be cut
        return self.vert1
    def getvert2(self):                 # second vertex of edge to be cut
        return self.vert2
    
    # build partlist
    def partlist(self):
        list = ""
        for part in self.parts:
            list += " " + part.getname()
        return list.strip()
    
    # print function for .rpl
    def print(self, list): 
        partlist = self.partlist()
        line1 = "ic_hex_undo_major_start split_grid\n"
        line2 = f"ic_hex_split_grid {self.vert1} {self.vert2} {self.pnt.getname()} m GEOM {partlist} VORFN\n"
        line3 = "ic_hex_undo_major_end split_grid\n"
        list.append(line1)
        list.append(line2)
        list.append(line3)
        return list
    

# delete block operation class definition
class Delete:
    # delete constructor
    def __init__(self, blk):
        # set point and vertice associations
        self.blk = blk 	                # block to delete

    # split destructor
    def __del__(self):
        pass

    # getter functions
    def getblk(self): 	                # block to delete
        return self.blk
    
    # print function for .rpl
    def print(self, list): 
        line1 = "ic_hex_mark_blocks unmark\n"
        line2 = f"ic_hex_mark_blocks superblock {self.blk}\n"
        line3 = "ic_hex_change_element_id VORFN\n"
        list.append(line1)
        list.append(line2)
        list.append(line3)
        return list


# vertex association operation class definition (3D)
class Vert:
    # vertex constructor
    def __init__(self, num, pnt):
        self.num = num                  # number of vertex
        self.pnt = pnt                  # vertex associated point

    # vertex destructor
    def __del__(self):
        pass

    # getter functions
    def getnum(self):                  # number of vertex
        return self.num
    def getpnt(self):                  # vertex associated point
        return self.pnt
    
    # print function for .rpl
    def print(self, list): 
        line = f"ic_hex_move_node {self.num} {self.pnt.getname()}\n"
        list.append(line)
        return list


# edge association operation class definition (2D)
class Edge:
    # edge constructor
    def __init__(self, vert1, vert2, crv):
        self.vert1 = vert1              # first vertex of edge
        self.vert2 = vert2              # second vertex of edge
        self.crv = crv                  # edge associated curve

    # edge destructor
    def __del__(self):
        pass

    # getter functions
    def getvert1(self):                 # first vertex of edge
        return self.vert1
    def getvert2(self):                 # second vertex of edge
        return self.vert2
    def getcrv(self):                   # edge associated curve
        return self.crv
    
    # print function for .rpl
    def print(self, list): 
        line1 = "ic_hex_undo_major_start set_edge_projection\n"
        line2 = f"ic_hex_set_edge_projection {self.vert1} {self.vert2} 0 1 {self.crv.getname()}\n"
        line3 = "ic_hex_undo_major_end set_edge_projection\n"     
        list.append(line1)
        list.append(line2)
        list.append(line3)
        return list


################################################################ MESHING OBJECTS ################################################################
# section class definition
class Section:
    # section constructor
    def __init__(self, name, size):
        self.name = name                    # name of section
        self.size = round(size, geomprec)   # size of section in [m]
        self.mesh = [None]*7                # list of meshing parameters 
        # 0: rule       meshing rule
        # 1: n          number of nodes
        # 2: h1rel      relative size of first cell
        # 3: h2rel      relative size of last cell
        # 4: r1         growth rate at first cell
        # 5: r2         growth rate at last
        # 6: lmax       maximum absolute allowed cell size

    # section destructor
    def __del__(self):
        pass

    # getter functions
    def getname(self):                      # name of section
        return self.name
    def getsize(self):                      # size of section [m]
        return self.size
    def getmesh(self):                      # meshing list
        return self.mesh
    
    #setter functions
    def setmesh(self, mesh):                # meshing list
        self.mesh = mesh
        
    # creates line with mesh info
    def meshinfo(self):
        if self.mesh[0] == "uniform":
            size = round(self.size/(self.mesh[1] - 1)*1000.0, meshprec)
            line = f"\t- {self.name}: {self.mesh[1] - 1} cells, uniform distribution, cell size {size} <= {self.mesh[6]*1000.0} mm"
        elif self.mesh[0] == "geo1":
            minsize = round(self.mesh[2]*self.size*1000.0, meshprec)
            calcsize = round(minsize*self.mesh[4]**(self.mesh[1] - 2), meshprec)
            maxsize = round(self.mesh[3]*self.size*1000.0, meshprec)
            line = f"\t- {self.name}: {self.mesh[1] - 1} cells, geo1 distribution, min cell size {minsize} mm, max cell size {calcsize} <= {maxsize} mm, rate {self.mesh[4]}"
        elif self.mesh[0] == "geo2":
            minsize = round(self.mesh[3]*self.size*1000.0, meshprec)
            calcsize = round(minsize*self.mesh[5]**(self.mesh[1] - 2), meshprec)
            maxsize = round(self.mesh[2]*self.size*1000.0, meshprec)
            line = f"\t- {self.name}: {self.mesh[1] - 1} cells, geo2 distribution, min cell size {minsize} mm, max cell size {calcsize} <= {maxsize} mm, rate {self.mesh[5]}"
        else:
            line = f"\t- {self.name}: no distribution defined"
        return line
    
    # print function for .conf - readable by user
    def print(self):
        line = self.meshinfo() + "\n"
        return line
    
    # print function for .conf - readable by script
    def export(self):
        # if mesh has been defined
        if not self.mesh[0] is None:
            # build export line
            line = f"{self.name} {self.mesh[0]}"
            for i in range(1, 7):
                line += f" {round(self.mesh[i], meshprec)}"         # rounding to prevent unnecessarily high precision
            line += "\n"
        # if no mesh has been defined
        else:
            line = f"{self.name}: N/A\n"            
        return line
    
    # print mesh info to console
    def printinfo(self):
        print(self.meshinfo())


# mesh class definition
class Mesh():
    # mesh constructor
    def __init__(self, vert1, vert2, mesh):
        self.vert1 = vert1                  # first vertex of edge to be meshed
        self.vert2 = vert2                  # second vertex of edge to be meshed
        self.mesh = mesh                    # meshing array from section
        # 0: rule       meshing rule
        # 1: n          number of nodes
        # 2: h1rel      relative size of first cell
        # 3: h2rel      relative size of last cell
        # 4: r1         growth rate at first cell
        # 5: r2         growth rate at last
        # 6: lmax       maximum allowed cell size

    # mesh destructor
    def __del__(self):
        pass

    # getter functions
    def getvert1(self):
        return self.vert1
    def getvert2(self):
        return self.vert2
    def getmesh(self):
        return self.mesh
    
    # print function for .rpl
    def print(self, list):
        line = f"ic_hex_set_mesh {self.vert1} {self.vert2} n {self.mesh[1]} h1rel {self.mesh[2]} h2rel {self.mesh[3]} r1 {self.mesh[4]} r2 {self.mesh[5]} lmax {self.mesh[6]} {self.mesh[0]} copy_to_parallel unlocked\n"
        list.append(line)
        return list
    