"""Reproducible Blender physical pipe shots. Run Blender -b -P this_file -- ROOT."""
import bpy, math, os, sys, random
from mathutils import Vector
ROOT = os.path.abspath(sys.argv[sys.argv.index('--') + 1]) if '--' in sys.argv else os.getcwd()
OUT = os.path.join(ROOT, 'cinematic-production', 'frames', 'pipe-v2')
os.makedirs(OUT, exist_ok=True)
random.seed(25)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES'
scene.cycles.samples=int(os.environ.get('CINEMATIC_SAMPLES','8'))
scene.cycles.use_denoising=True
scene.render.resolution_x=960; scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.fps=30;scene.world.color=(0.005,0.008,0.012)
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.5
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences
    for backend in ['OPTIX','CUDA','HIP','ONEAPI']:
        try:
            prefs.compute_device_type=backend;prefs.get_devices()
            devices=[d for d in prefs.devices if d.type!='CPU']
            if devices:
                for d in prefs.devices:d.use=d.type!='CPU'
                scene.cycles.device='GPU';print('RENDER_DEVICE',backend,[d.name for d in devices]);break
        except Exception:pass
except Exception:pass

def material(name, color, metal=0, rough=.3, transmission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Transmission Weight'].default_value=transmission;p.inputs['IOR'].default_value=1.333 if transmission else 1.45
    return m,p
copper,p=material('Brushed copper with fine moisture and machining marks',(.39,.13,.052),.92,.29)
n=copper.node_tree.nodes;l=copper.node_tree.links
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=58;tex.inputs['Detail'].default_value=4
bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.012;l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.20,.045,.016,1);ramp.color_ramp.elements[1].color=(.54,.25,.11,1);l.new(tex.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
water,wp=material('Clear water with small ripples',(.68,.82,.84),0,.09,.96)
n=water.node_tree.nodes;l=water.node_tree.links;noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9;noise.inputs['Detail'].default_value=3;bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.025;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],wp.inputs['Normal'])

def tube(name, centers, radius=.64, mat=copper, sides=72):
    verts=[];faces=[]
    for i,c in enumerate(centers):
        c=Vector(c);t=Vector(centers[min(i+1,len(centers)-1)])-Vector(centers[max(0,i-1)])
        t.normalize();a=t.cross(Vector((0,0,1))).normalized();b=t.cross(a).normalized()
        for j in range(sides):
            v=c+radius*(a*math.cos(j*math.tau/sides)+b*math.sin(j*math.tau/sides));verts.append(v)
    for i in range(len(centers)-1):
        for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.data.materials.append(mat)
    for poly in mesh.polygons:poly.use_smooth=True
    return obj
# Real-radius copper supply pipe and a perpendicular T branch, with an opening.
main=tube('Copper main supply',[(0,i*.25,0)for i in range(45)])
branch=tube('Copper branch of T junction',[(-3+i*.2,8,0)for i in range(41)])
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.65,depth=9,location=(0,8,0),rotation=(0,math.pi/2,0));cutter=bpy.context.object
mod=main.modifiers.new('Actual T opening','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
bpy.context.view_layer.objects.active=main
try:bpy.ops.object.modifier_apply(modifier=mod.name)
except Exception:pass
bpy.data.objects.remove(cutter,do_unlink=True)
bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.645,depth=16,location=(0,7,0),rotation=(math.pi/2,0,0));cutter=bpy.context.object
mod=branch.modifiers.new('Open connection to main','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
bpy.context.view_layer.objects.active=branch
try:bpy.ops.object.modifier_apply(modifier=mod.name)
except Exception:pass
bpy.data.objects.remove(cutter,do_unlink=True)
for y in [2.8,5.7,7.65,8.35]:
    tube('Copper coupling',[(0,y-.06,0),(0,y+.06,0)],.638)
for x in [.5,2.4,4.25]:tube('Branch coupling',[(x-.06,8,0),(x+.06,8,0)],.638)

def surface(name,x0,x1,y0,y1,z=-.38):
    nx=28;ny=140;vertices=[];faces=[]
    for j in range(ny+1):
        for i in range(nx+1):vertices.append((x0+(x1-x0)*i/nx,y0+(y1-y0)*j/ny,z))
    for j in range(ny):
        for i in range(nx):a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj);obj.data.materials.append(water)
    for p in mesh.polygons:p.use_smooth=True
    return obj,vertices
watermain,wm=surface('Shallow flowing water in main',-.49,.49,0,11)
waterbranch,wb=surface('Water through T branch',-3,5,7.5,8.5)
for i in range(70):
    y=random.uniform(.2,9);angle=random.uniform(0,math.tau);r=.622
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=random.uniform(.008,.025),location=(r*math.sin(angle),y,r*math.cos(angle)))
    bead=bpy.context.object;bead.name='Condensation';bead.data.materials.append(water);bead.scale=(1,.8,.7)
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,radius=.035,location=(0,.8,.49));drop=bpy.context.object;drop.data.materials.append(water);drop.name='First water droplet'
bpy.ops.mesh.primitive_torus_add(major_radius=.055,minor_radius=.006,location=(0,.8,-.365));ring=bpy.context.object;ring.data.materials.append(water);ring.name='Droplet impact ripple'

def light(name,loc,color,energy,size=.4,target=None):
    data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.color=color;data.shape='DISK';data.size=size;obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=loc
    if target:obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj
for y in [1,3,5,7,9]:light('Warm copper bounce',(0,y,.35),(1,.72,.46),5,.3,(0,y+.7,-.4))
for x in [1,3,4.8]:light('Natural light through faucet',(x,8,.35),(.84,.92,1),7,.3,(x-.6,8,-.35))
light('Faucet daylight',(5.1,8,0),(1,.92,.78),25,1,(3,8,0))
# The approved architectural image is an illuminated kitchen backplate at the
# outlet. The following finishing shot uses the same image and source crop.
bpy.ops.mesh.primitive_plane_add(size=3,location=(5.16,8,0),rotation=(0,-math.pi/2,0))
backplate=bpy.context.object;backplate.name='Kitchen through the faucet outlet'
backmat=bpy.data.materials.new('Approved kitchen macro backplate');backmat.use_nodes=True
nodes=backmat.node_tree.nodes;nodes.clear();links=backmat.node_tree.links
output=nodes.new('ShaderNodeOutputMaterial');emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=.65
image=nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(os.path.join(ROOT,'public','assets','hero-desktop.webp'))
uv=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(.36,.36,1);mapping.inputs['Location'].default_value=(.61,.40,0)
links.new(uv.outputs['UV'],mapping.inputs['Vector']);links.new(mapping.outputs['Vector'],image.inputs['Vector']);links.new(image.outputs['Color'],emission.inputs['Color']);links.new(emission.outputs['Emission'],output.inputs['Surface']);backplate.data.materials.append(backmat)
bpy.ops.object.camera_add();camera=bpy.context.object;scene.camera=camera;camera.data.lens=19;camera.data.clip_start=.01;camera.data.clip_end=50
data=bpy.data.lights.new('Camera reflection fill','POINT');data.energy=3;data.color=(1,.78,.57);data.shadow_soft_size=.08;fill=bpy.data.objects.new('Camera reflection fill',data);scene.collection.objects.link(fill)
def ease(t):return t*t*(3-2*t)
def frame(f):
    t=f/30
    if t<.5:pos=(.10,.10,-.08);target=(0,1,-.3)
    elif t<1.5:
        u=(t-.5);pos=(.08,.1+6.1*u*u,-.10);target=(0,min(8.3,pos[1]+1.6),-.12)
    elif t<2.3:
        u=ease((t-1.5)/.8);pos=(1.35*u,6.2+1.8*min(1,u*1.35),-.10);target=(1.1+2.1*u,8,-.08)
    else:
        u=ease(min(1,(t-2.3)/.7));pos=(1.35+3.3*u,8,-.10);target=(6,8,0)
    camera.location=pos;camera.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();fill.location=Vector(pos)+Vector((0,0,.20))
    drop.hide_render=t>=.48;drop.location.z=.49-.86*min(1,(t/.46)**2);drop.scale=(.8,.8,1.3 if t<.38 else .7)
    ring.hide_render=t<.44 or t>.85;ring.scale=(max(.01,(t-.44)*5),)*2+(1,)
    for obj,verts in [(watermain,wm),(waterbranch,wb)]:
        for v,orig in zip(obj.data.vertices,verts):
            x,y,z=orig;v.co.z=z+.008*math.sin(y*13-t*18)+.006*math.sin(x*16+y*8-t*11)
        obj.data.update()
    scene.frame_set(f+1);scene.render.filepath=os.path.join(OUT,f'{f:04d}.png')
    bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'cinematic-production','inside-the-flow.blend'))
frames=[0,13,32,48,65,80,89] if os.environ.get('CINEMATIC_PREVIEW')=='1' else range(90)
for f in frames:
    if not os.path.exists(os.path.join(OUT,f'{f:04d}.png')):frame(f)
print('PIPE_RENDER_COMPLETE',OUT)
