import cadquery as cq, math, sys
OUT=sys.argv[1] if len(sys.argv)>1 else "/home/claude/spk/v2/"
import os; os.makedirs(OUT,exist_ok=True)
K=14/162.0                       # taper per mm
def Ro(z): return 62-K*(z-6)     # outer radius of body
def Ri(z): return Ro(z)-3
def rev(pts): return cq.Workplane("XZ").polyline(pts).close().revolve(360,(0,0,0),(0,1,0))
def cyl(r,h,z=0): return cq.Workplane("XY").workplane(offset=z).circle(r).extrude(h)
def ring(ro,ri,h,z=0): return cyl(ro,h,z).cut(cyl(ri,h,z))
def rotz(s,a): return s.rotate((0,0,0),(0,0,1),a)
def polar(r,angs): return [(r*math.cos(math.radians(a)),r*math.sin(math.radians(a))) for a in angs]
def cutter(wp): return wp

HOLES=[(sx*24.5,sy*29) for sx in(-1,1) for sy in(-1,1)]   # Pi 4/5 pattern, board portrait, centred

# ---------- BASE: floating foot with LED groove ----------
base=cyl(54,6).cut(cyl(46,1.2))
base=base.cut(ring(54.1,52,5,0.5))                     # LED strip groove on rim
sl=[]
for i in range(24):
    a=i*15; x,y=polar(36,[a])[0]
    if min(math.hypot(x-hx,y-hy) for hx,hy in HOLES)<10: continue
    sl.append(rotz(cq.Workplane("XY").center(36,0).slot2D(10,3,0).extrude(6),a).val())
base=base.cut(cq.Workplane("XY").newObject([cq.Compound.makeCompound(sl)]))
base=base.union(ring(45.5,43,5,6))                     # centring ring
base=base.union(cq.Workplane("XY").workplane(offset=6).pushPoints(HOLES).circle(3).extrude(6))
base=base.cut(cq.Workplane("XY").workplane(offset=6).pushPoints(HOLES).circle(1.1).extrude(6))
base=base.cut(cq.Workplane("XY").workplane(offset=0).pushPoints(polar(49,[90,210,330])).circle(1.7).extrude(6))
base=base.cut(cq.Workplane("XY").workplane(offset=0).pushPoints(polar(49,[90,210,330])).circle(3.2).extrude(2))

# ---------- SHELL: tapered, fluted ----------
shell=rev([(46,6),(62,6),(Ro(168),168),(Ri(168),168),(Ri(155),155),(38.5,155),(38.5,149),(Ri(149),149),(Ri(11),11),(46,11)])
shell=shell.cut(cq.Workplane("XY").workplane(offset=6).pushPoints(polar(49,[90,210,330])).circle(1.3).extrude(5))
cs=[]
d=cq.Vector(-K,0,1).normalized()
for i in range(56):
    c=cq.Solid.makeCylinder(2.0,172,cq.Vector(Ro(3)+1.0,0,3),d).rotate(cq.Vector(0,0,0),cq.Vector(0,0,1),i*360/56)
    cs.append(c)
shell=shell.cut(cq.Workplane("XY").newObject([cq.Compound.makeCompound(cs)]))
shell=shell.cut(cq.Workplane("XY").box(62,16,20).edges("|Y").fillet(4).translate((0,62,22)))      # rear: Ethernet/USB
shell=shell.cut(cq.Workplane("XY").box(16,40,12).edges("|X").fillet(3).translate((62,-17,18)))   # side: USB-C/HDMI

# ---------- BAFFLE (3" driver) ----------
rb=Ri(160)-0.4
baffle=cyl(rb,5,155).cut(cyl(33,5,155))
baffle=baffle.cut(cq.Workplane("XY").workplane(offset=155).pushPoints(polar(38,[45,135,225,315])).circle(1.6).extrude(5))
baffle=baffle.cut(cq.Workplane("XY").workplane(offset=155).center(0,-41.5).circle(2.5).extrude(5))

# ---------- CAP: soft dome, graded grille, mics, mute ----------
ZT=192
cap=rev([(0,168),(Ro(168),168),(Ro(ZT),ZT),(0,ZT)])
cap=cap.faces(">Z").edges().fillet(12).faces("<Z").edges().chamfer(0.6)
cap=cap.faces("<Z").shell(-5)
cap=cap.union(ring(44.6,42.4,5,163))
N=95; c=3.0
pts=[(c*math.sqrt(i)*math.cos(i*2.39996),c*math.sqrt(i)*math.sin(i*2.39996)) for i in range(0,N)]
for lo,hi,r in [(0,9,1.5),(9,20,1.25),(20,29,1.0)]:
    g=[p for p in pts if lo<=math.hypot(*p)<hi]
    cap=cap.cut(cq.Workplane("XY").workplane(offset=ZT-6).pushPoints(g).circle(r).extrude(8))
cap=cap.cut(cq.Workplane("XY").workplane(offset=ZT-6).pushPoints(polar(31.5,[30,90,150,210,270,330])).circle(0.8).extrude(8))
cap=cap.cut(cq.Workplane("XY").newObject([cq.Solid.makeCylinder(3,30,cq.Vector(0,-30,178),cq.Vector(0,-1,0))]))

pi=cq.Workplane("XY").box(56,85,1.6).translate((0,0,12.8)).union(cq.Workplane("XY").box(16,18,14).translate((0,38,21))).union(cq.Workplane("XY").box(18,36,6).translate((26,-17,17)))
parts=dict(base=base,shell=shell,baffle=baffle,cap=cap,pi5_dummy=pi)
for n,p in parts.items():
    cq.exporters.export(p,OUT+n+".stl",tolerance=0.1,angularTolerance=0.2)
    v=p.val(); bb=v.BoundingBox(); print(n,v.isValid(),round(bb.xlen),round(bb.ylen),round(bb.zmin),round(bb.zmax),round(v.Volume()/1000,1))
