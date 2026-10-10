"""Single-world copper-to-faucet-to-kitchen shot, offline Cycles rendering.
Blender -b -t 8 -P render_entrance.py -- PROJECT_ROOT
ENTRANCE_PREVIEW=1 renders review frames; ENTRANCE_SIZE selects desktop/mobile.
"""
import bpy, math, os, sys, random
from mathutils import Vector
ROOT=os.path.abspath(sys.argv[sys.argv.index('--')+1]);random.seed(25)
SIZE=os.environ.get('ENTRANCE_SIZE','desktop');PREVIEW=os.environ.get('ENTRANCE_PREVIEW')=='1'
OUT=os.path.join(ROOT,'cinematic-production','frames','entrance-v4',('preview-' if PREVIEW else '')+SIZE);os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=8 if PREVIEW else 24;scene.cycles.use_denoising=True
scene.render.resolution_x=(640 if PREVIEW else 960) if SIZE=='desktop' else (360 if PREVIEW else 540)
scene.render.resolution_y=(360 if PREVIEW else 540) if SIZE=='desktop' else (510 if PREVIEW else 765)
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.fps=30
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.27,.34,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.18
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0
scene.cycles.max_bounces=6;scene.cycles.transmission_bounces=5;scene.cycles.transparent_max_bounces=5

def mat(name,color,metal=0,rough=.35,trans=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Transmission Weight'].default_value=trans;p.inputs['IOR'].default_value=1.333 if trans else 1.5;return m
def texture(m,scale,colors,strength=.08,distance=.02):
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3;r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*colors[0],1);r.color_ramp.elements[1].color=(*colors[1],1);l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=distance;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
copper=mat('Copper / machining and oxidation',(.46,.16,.06),.94,.27);texture(copper,85,[(.19,.05,.02),(.54,.23,.085)],.2,.006)
chrome=mat('Brushed stainless faucet',(.66,.71,.74),1,.15);texture(chrome,220,[(.55,.59,.62),(.72,.76,.79)],.04,.0005)
water=mat('Clear water / IOR 1.333',(.94,.98,1),0,.04,1)
navy=mat('Painted navy joinery',(.017,.033,.055),0,.32);texture(navy,120,[(.014,.027,.046),(.021,.04,.062)],.08,.005)
wall=mat('Warm plaster',(.73,.71,.66),0,.75);texture(wall,45,[(.68,.66,.61),(.78,.76,.7)],.1,.012)
stone=mat('Honed limestone',(.67,.64,.56),0,.31);texture(stone,4,[(.5,.48,.43),(.79,.76,.68)],.08,.012)
oak=mat('Natural oak',(.29,.15,.075),0,.42);texture(oak,8,[(.18,.09,.038),(.48,.28,.13)],.15,.008)
brass=mat('Satin brass hardware',(.56,.35,.12),.9,.26);ceramic=mat('Ivory ceramic',(.87,.85,.77),0,.23);black=mat('Black glass',(.006,.008,.011),.3,.16);leaf=mat('Olive leaves',(.055,.12,.032),0,.55)

def box(name,loc,scale,material,bevel=.06):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:mod=o.modifiers.new('Soft manufactured edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def cylinder(name,loc,radius,depth,material,vertices=40):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 mod=o.modifiers.new('Machined edge','BEVEL');mod.width=.035;mod.segments=2;return o
def tube(name,points,radius,material,sides=48):
 verts=[];faces=[];previous=None
 for i,pt in enumerate(points):
  c=Vector(pt);t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)]);t.normalize();axis=Vector((0,1,0)) if abs(t.y)<.95 else Vector((1,0,0));a=t.cross(axis).normalized();b=t.cross(a).normalized()
  if previous is not None and a.dot(previous)<0:a=-a;b=-b
  previous=a
  for j in range(sides):verts.append(c+radius*(math.cos(j*math.tau/sides)*a+math.sin(j*math.tau/sides)*b))
 for i in range(len(points)-1):
  for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);scene.collection.objects.link(o);o.data.materials.append(material)
 for p in mesh.polygons:p.use_smooth=True
 return o
def sphere(name,loc,r,material,scale=(1,1,1)):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=r,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o
def light(name,loc,energy,color,size,target):
 d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();return o

# Architectural scene at centimetre-like scale. The faucet and the internal journey share the same world.
box('Plaster back wall',(0,10,20),(90,1,40),wall);box('Right plaster wall',(42,-8,20),(1,38,40),wall)
box('Oak floor',(0,-5,-.3),(90,55,.6),oak)
for x in range(-38,40,4):box('Floorboard joint',(x,-8,.015),(.016,45,.012),black,0)
for x in [-30,-20,-10,0,10,20,30]:
 box('Base cabinet',(x,4,4.5),(9.8,10,9),navy);box('Recessed door',(x,-1.08,4.6),(9.1,.25,8.2),navy,.08)
 box('Door upper rail',(x,-1.3,8.35),(9,.14,.65),navy);box('Door lower rail',(x,-1.3,.85),(9,.14,.65),navy)
 for side in [-1,1]:box('Door stile',(x+side*4.1,-1.3,4.6),(.7,.14,7.7),navy)
 box('Cabinet brass pull',(x,-1.62,7.25),(2.6,.16,.16),brass,.06)
# Counter cutout assembled as continuous stone around a recessed stainless sink.
box('Counter left',(-14,3.5,9.8),(43,12,.55),stone);box('Counter right',(30,3.5,9.8),(13,12,.55),stone)
box('Counter behind sink',(15,7.4,9.8),(17,4.2,.55),stone);box('Counter front sink lip',(15,-1.2,9.8),(17,2.5,.55),stone)
box('Sink bowl bottom',(15,2,7.7),(14,6.2,.3),chrome,.3)
box('Sink bowl back',(15,5,8.8),(14,.25,2.4),chrome,.12);box('Sink bowl front',(15,-.8,8.8),(14,.25,2.4),chrome,.12)
for x in [8.1,21.9]:box('Sink bowl side',(x,2,8.8),(.25,6,2.4),chrome,.12)
for x in [7.8,22.65]:box('Sink flange',(x,2.25,10.1),(1.5,6.3,.16),chrome,.06)
cylinder('Drain strainer',(15,2,7.88),.65,.06,chrome)
for i in range(8):box('Drain slot',(15+.42*math.cos(i*math.tau/8),2+.42*math.sin(i*math.tau/8),7.92),(.06,.12,.012),black,.008)
box('Limestone backsplash',(0,9.35,13),(75,.4,5.8),stone)
for z in [11,13,15]:box('Tile grout horizontal',(0,9.09,z),(76,.025,.025),wall,0)
for x in range(-35,39,6):box('Tile grout vertical',(x,9.09,13),(.025,.025,6),wall,0)
for x in [-28,-15,0]:
 box('Upper cabinet',(x,7.1,25.6),(12.5,5.6,12),wall,.08);box('Upper door',(x,4.2,25.6),(12.1,.25,11.6),wall,.05);box('Upper handle',(x+4.8,3.9,23.3),(.12,.16,2),brass)
box('Floating oak shelf',(24,6.7,23),(20,5.8,.5),oak)
box('Range cooktop',(-22,3.4,10.14),(12,8,.22),black)
for x in [-25,-19]:
 for y in [1,5]:cylinder('Cooktop ring',(x,y,10.28),1.1,.12,chrome);cylinder('Burner cap',(x,y,10.36),.72,.12,black)
box('Built in oven',(-20,-1.36,4.8),(9,.2,5.2),black,.15);box('Oven handle',(-20,-1.65,6.8),(7,.3,.3),chrome,.08)
box('Oak chopping board',(28,3.6,10.25),(5,6,.25),oak,.2)
cylinder('Ceramic utensil pot',(31,7,11.5),.8,2.8,ceramic)
for i in range(4):tube('Wooden utensil',[(30.6+i*.27,7,11.5),(30.4+i*.28,7,14.5)],.1,oak,12)
cylinder('Stoneware vase',(27,6.7,25),1.1,3.2,ceramic)
for i in range(5):
 a=i*math.tau/5;end=(27+1.9*math.cos(a),6.7+1.2*math.sin(a),30+i*.35);tube('Olive stem',[(27,6.7,26),end],.035,oak,10)
 for j in range(3):sphere('Leaf',(end[0]-.3*j,end[1]+.2*j,end[2]-.55*j),.42,leaf,(1,.27,.5))
for x in [18,21]:cylinder('Shelf cup',(x,6.5,24),.7,1.6,ceramic)
for i in range(4):cylinder('Stacked plate',(-5,6,10.2+i*.13),1.1,.12,ceramic)
box('Window reveal',(-40,-3,22),(1,17,19),wall)
box('Bright window glass',(-40.3,-3,22),(.1,15.5,17.5),ceramic)
for y in [-10,-3,4]:box('Window upright',(-39.5,y,22),(.6,.35,19),wall)
box('Window transom',(-39.5,-3,22),(.6,17,.35),wall)
light('Large soft window',(-34,-8,25),34000,(1,.89,.72),15,(8,3,10));light('Kitchen reflected daylight',(20,-18,29),14000,(.8,.9,1),17,(15,3,10));light('Under cabinet warmth',(-13,4,18.9),900,(1,.79,.52),14,(-13,6,10))
d=bpy.data.lights.new('Late afternoon sun','SUN');d.energy=1.3;d.angle=.08;d.color=(1,.87,.68);sun=bpy.data.objects.new('Late afternoon sun',d);scene.collection.objects.link(sun);sun.rotation_euler=(.55,-.5,-.6)

# True hollow copper main, elbow into riser, then the real stainless gooseneck.
main=tube('Copper main supply',[(-4,6,-10),(22,6,-10)],.36,copper)
branch=tube('Vertical copper riser',[(15,6,-10),(15,6,9.9)],.36,copper)
for o,loc,rotation,depth in [(main,(15,6,-9.5),(0,0,0),42),(branch,(15,6,-10),(0,math.pi/2,0),32)]:
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.365,depth=depth,location=loc,rotation=rotation);cut=bpy.context.object;mod=o.modifiers.new('Open T junction','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=o
 try:bpy.ops.object.modifier_apply(modifier=mod.name)
 except Exception:pass
 bpy.data.objects.remove(cut,do_unlink=True)
faucet_points=[(15,6,9.9),(15,6,14.6)]+[(15,3.5+2.5*math.cos(a),14.6+2.5*math.sin(a))for a in [i*math.pi/48 for i in range(49)]]+[(15,1,13.6)]
tube('Hollow gooseneck faucet',faucet_points,.39,chrome,64)
cylinder('Faucet escutcheon',(15,6,10.15),.72,.2,chrome);cylinder('Faucet valve body',(15,6,10.9),.53,1.35,chrome)
for name in ['Faucet escutcheon','Faucet valve body','Counter behind sink']:
 o=bpy.data.objects[name];bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.395,depth=3,location=(15,6,10.9));cut=bpy.context.object;mod=o.modifiers.new('Internal water bore','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=o
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
o=bpy.data.objects['Oak floor'];bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.395,depth=2,location=(15,6,0));cut=bpy.context.object;mod=o.modifiers.new('Supply penetration','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
box('Single lever',(15.9,6,11.8),(2,.22,.22),chrome,.08)
for z in [13.45,13.55]:tube('Outlet aerator rim',[(15,1,z),(15,1,z+.1)],.41,chrome,64)
# Thin water skin follows the internal riser; refractive ripples remain subtle.
film=tube('Riser water film',[(15,6,-9.3),(15,6,14.6)],.355,water,40);film.hide_render=True
stream=tube('Clear faucet stream',[(15+.02*math.sin(i*.7),1+.018*math.cos(i*.4),13.58-i*.16)for i in range(36)],.22,water,32)
import bmesh
bm=bmesh.new();bm.from_mesh(stream.data);bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(stream.data);bm.free()
for i in range(42):
 x=random.uniform(-.5,13);a=random.uniform(0,math.tau);sphere('Condensation bead',(x,6+.345*math.sin(a),-10+.345*math.cos(a)),random.uniform(.008,.018),water)
drop=sphere('Opening droplet',(1,6,-9.72),.045,water,(.8,.8,1.2))
bpy.ops.mesh.primitive_torus_add(major_radius=.05,minor_radius=.005,location=(1,6,-10.31));ripple=bpy.context.object;ripple.data.materials.append(water)
# Shallow flowing surface at the bottom of the horizontal supply.
verts=[];faces=[]
for i in range(161):
 for j in range(9):verts.append((-3+i*.155,5.78+j*.055,-10.29))
for i in range(160):
 for j in range(8):a=i*9+j;faces.append((a,a+1,a+10,a+9))
mesh=bpy.data.meshes.new('Shallow water');mesh.from_pydata(verts,[],faces);mesh.update();flow=bpy.data.objects.new('Flowing water',mesh);scene.collection.objects.link(flow);flow.data.materials.append(water)
for p in mesh.polygons:p.use_smooth=True
for x in [1,5,9,13]:light('Copper bounce',(x,6,-9.78),2.5,(1,.68,.39),.2,(x+.5,6,-10.25))
for z in [-6,-1,4,9,14]:light('Riser reflected daylight',(15,6,z),2,(.86,.93,1),.17,(15,6,z+1))
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.lens=22;camera.data.clip_start=.002;camera.data.clip_end=300
camera.data.dof.use_dof=False
d=bpy.data.lights.new('Camera subtle fill','POINT');d.energy=.9;d.color=(1,.8,.6);d.shadow_soft_size=.08;fill=bpy.data.objects.new('Camera subtle fill',d);scene.collection.objects.link(fill)
def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def mix(a,b,u):return Vector(a).lerp(Vector(b),u)
def path_frame(f):
 t=f/30
 if t<.5:pos=Vector((0,6,-10));target=Vector((1,6,-10.25))
 elif t<1.5:
  u=(t-.5);pos=Vector((13*u*u,6,-10));target=pos+Vector((1,0,.03))
 elif t<1.62:
  pos=Vector((13+1.8*ease((t-1.5)/.12),6,-10));target=pos+Vector((1,0,0))
 elif t<1.8:
  a=ease((t-1.62)/.18)*math.pi/2;pos=Vector((14.8+.2*math.sin(a),6,-9.8-.2*math.cos(a)));target=pos+Vector((math.cos(a),0,math.sin(a)))
 elif t<2.3:
  u=ease((t-1.8)/.5);pos=Vector((15,6,-9.8+24.4*u));target=pos+Vector((0,0,1))
 elif t<2.94:
  a=ease((t-2.3)/.64)*math.pi;pos=Vector((15,3.5+2.5*math.cos(a),14.6+2.5*math.sin(a)));target=pos+Vector((0,-math.sin(a),math.cos(a)))
 elif t<3.1:
  u=ease((t-2.94)/.16);pos=Vector((15,1,14.6-2.4*u));target=pos+Vector((0,0,-1))
 else:
  u=ease((t-3.1)/.7);end=(30,-48,25) if SIZE=='desktop' else (24,-42,26);look=(2,4,12) if SIZE=='desktop' else (13,6,13)
  pos=mix((15,1,12.2),end,u);target=mix((15,1,9.5),look,u)
 camera.location=pos;camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();camera.data.lens=22+10*ease((t-3.1)/.7)
 fill.location=pos+Vector((0,0,.08));fill.hide_render=t>3.1;stream.hide_render=t<3.1
 drop.hide_render=t>.49;drop.location.z=-9.72-.58*min(1,(t/.47)**2);ripple.hide_render=t<.45 or t>.82;ripple.scale=(max(.01,(t-.45)*6),max(.01,(t-.45)*6),1)
 for v,orig in zip(flow.data.vertices,verts):v.co.z=orig[2]+.006*math.sin(orig[0]*19-t*25)+.004*math.sin(orig[1]*22-t*14)
 flow.data.update()
 scene.view_settings.exposure=-1.5+1.5*ease((t-2.7)/.45)
 scene.cycles.samples=8 if PREVIEW else (12 if f<94 else (32 if f>=114 else 16))
 scene.frame_set(f+1);scene.render.filepath=os.path.join(OUT,f'{f if PREVIEW else f//2:04d}.png')
 return camera
frames=[92,100,134] if PREVIEW else range(0,115,2)
if not PREVIEW and SIZE=='mobile':frames=[114]+list(range(94,114,2))
for f in frames:
 path_frame(f)
 if not os.path.exists(scene.render.filepath) or (os.environ.get('ENTRANCE_RERENDER_EXIT')=='1' and f>=94) or (os.environ.get('ENTRANCE_RERENDER_RISER')=='1' and 46<=f<=70):bpy.ops.render.render(write_still=True)
if not PREVIEW:
 import shutil
 for f in range(58,70):shutil.copyfile(os.path.join(OUT,'0057.png'),os.path.join(OUT,f'{f:04d}.png'))
path_frame(134);bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'cinematic-production',f'entrance-{SIZE}.blend'))
print('ENTRANCE_COMPLETE',SIZE,OUT)
