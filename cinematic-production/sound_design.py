"""Original procedural water foley, modeled bubble resonance and copper echoes."""
import numpy as np, wave, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rate=48000;duration=4.5;n=int(rate*duration);t=np.arange(n)/rate;rng=np.random.default_rng(25)
def band_noise(low,high):
    white=rng.normal(size=n);spec=np.fft.rfft(white);freq=np.fft.rfftfreq(n,1/rate)
    weights=np.clip((freq-low)/max(low*.3,20),0,1)*np.clip((high-freq)/max(high*.3,20),0,1)
    output=np.fft.irfft(spec*weights,n);return output/(np.std(output)+1e-9)
left=np.zeros(n);right=np.zeros(n)
def add(sound,start,pan=.5):
    i=int(start*rate);size=min(len(sound),n-i)
    if size<0:return
    left[i:i+size]+=sound[:size]*np.sqrt(1-pan);right[i:i+size]+=sound[:size]*np.sqrt(pan)
# A single droplet impact at 0.44s, with rapidly decaying bubble modes.
u=np.arange(int(.2*rate))/rate
impact=.30*np.sin(2*np.pi*(1550-450*u)*u)*np.exp(-u*38)+.08*rng.normal(size=len(u))*np.exp(-u*100)
for delay,gain in [(0,1),(.022,.35),(.053,.16),(.091,.07)]:add(impact*gain,.44+delay,.45)
# Water turbulence opens up as the camera exits. No tonal music or electronic effects.
envelope=np.clip((t-.5)/.6,0,1)*np.clip((4.5-t)/.55,0,1)
water=band_noise(450,8500)*.037*envelope
left+=water;right+=np.roll(water,21)*.94
rumble=band_noise(35,180)*.025*np.clip((t-.65)/.7,0,1)*np.clip((3.45-t)/.7,0,1)
left+=rumble;right+=rumble
for start in sorted(rng.uniform(.57,4.1,330)):
    radius=rng.uniform(.0007,.0045);frequency=3.26/radius
    u=np.arange(int(.045*rate))/rate
    sound=.013*np.sin(2*np.pi*frequency*u)*np.exp(-u*rng.uniform(60,180))
    add(sound,float(start),float(rng.uniform(.15,.85)))
# Restrained metallic resonance at drop and at the physical junction.
for start,level in [(.44,.04),(1.62,.025),(2.24,.014)]:
    u=np.arange(int(.5*rate))/rate
    resonance=sum(level/(i+1)*np.sin(2*np.pi*f*u)*np.exp(-u*(10+i*7)) for i,f in enumerate([139,317,682,1207]))
    add(resonance,start,.52)
# Enclosed echo reduces naturally towards the faucet exit.
for channel in [left,right]:
    original=channel.copy()
    for delay,gain in [(int(.017*rate),.15),(int(.037*rate),.06)]:channel[delay:]+=original[:-delay]*gain*np.clip((3.1-t[delay:])/.8,0,1)
    channel*=np.minimum(1,t/.03)*np.minimum(1,(duration-t)/.35)
stereo=np.column_stack([left,right]);stereo*=.65/max(np.max(np.abs(stereo)),.65)
directory=os.path.join(ROOT,'public','assets','cinematic');os.makedirs(directory,exist_ok=True)
filename=os.path.join(directory,'plumbing-intro-audio.wav')
with wave.open(filename,'wb')as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(rate);f.writeframes((stereo*32767).astype('<i2').tobytes())
print('Original water foley:',filename,'duration',duration,'peak',float(np.max(np.abs(stereo))))
