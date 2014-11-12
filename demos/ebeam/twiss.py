import sys
from ocelot.gui.accelerator import plot_lattice
from ocelot.cpbd.elements import Element, Quadrupole, RBend, Drift, Undulator, MagneticLattice, Hcor, Vcor
from ocelot.cpbd.beam import Beam, ParticleArray
from ocelot.cpbd.optics import *
from pylab import *

def rematch(beta_mean, l_fodo, qdh, lat, extra_fodo, beam, qf, qd):
    
    '''
    requires l_fodo to be defined in the lattice
    '''
    
    k, betaMin, betaMax, __ = fodo_parameters(betaXmean=beta_mean, L=l_fodo, verbose = True)
    
    k1 = k[0] / qdh.l
    
    tw0 = Twiss(beam)
    
    print 'before rematching k=%f %f   beta=%f %f alpha=%f %f' % (qf.k1, qd.k1, tw0.beta_x, tw0.beta_y, tw0.alpha_x, tw0.alpha_y)

        
    extra = MagneticLattice(extra_fodo, energy=lat.energy)
    tws=twiss(extra, tw0)
    tw2 = tws[-1]
    
    tw2m = Twiss(tw2)
    tw2m.beta_x = betaMin[0]
    tw2m.beta_y = betaMax[0]
    tw2m.alpha_x = 0.0
    tw2m.alpha_y = 0.0
    tw2m.gamma_x = (1 + tw2m.alpha_x * tw2m.alpha_x) / tw2m.beta_x
    tw2m.gamma_y = (1 + tw2m.alpha_y * tw2m.alpha_y) / tw2m.beta_y

    
    #k1 += 0.5
    
    qf.k1 = k1
    qd.k1 = -k1
    qdh.k1 = -k1
    
    lat.update_transfer_maps()
    extra.update_transfer_maps()
    
    m1 = lattice_transfer_map( extra )
    m1.R = np.linalg.inv(m1.R)
    
    tw0m = m1.map_x_twiss(tw2m)
    print 'after rematching k=%f %f   beta=%f %f alpha=%f %f' % (qf.k1, qd.k1, tw0m.beta_x, tw0m.beta_y, tw0m.alpha_x, tw0m.alpha_y)

    beam.beta_x, beam.alpha_x = tw0m.beta_x, tw0m.alpha_x
    beam.beta_y, beam.alpha_y = tw0m.beta_y, tw0m.alpha_y


from sase3 import *

#lat = MagneticLattice(sase3_segment(n=7), energy=17.5)
lat = MagneticLattice(sase3_ss, energy=17.5)

rematch(29.0, l_fodo, qdh, lat, extra_fodo, beam, qf, qd) # jeez...

tw0 = Twiss(beam)
print tw0
tws=twiss(lat, tw0, nPoints = 1000)


f=plt.figure()
ax = f.add_subplot(211)
ax.set_xlim(0, lat.totalLen)

f.canvas.set_window_title('Betas [m]') 
p1, = plt.plot(map(lambda p: p.s, tws), map(lambda p: p.beta_x, tws), lw=2.0)
p2, = plt.plot(map(lambda p: p.s, tws), map(lambda p: p.beta_y, tws), lw=2.0)
plt.grid(True)
plt.legend([p1,p2], [r'$\beta_x$',r'$\beta_y$', r'$D_x$'])

ax2 = f.add_subplot(212)
plot_lattice(lat, ax2, alpha=0.5)

# add beam size (arbitrary scale)

s = np.array(map(lambda p: p.s, tws))

scale = 5000

sig_x = scale * np.array(map(lambda p: np.sqrt(p.beta_x*beam.emit_x), tws)) # 0.03 is for plotting same scale
sig_y = scale * np.array(map(lambda p: np.sqrt(p.beta_y*beam.emit_y), tws))

x = scale * np.array(map(lambda p: p.x, tws))
y = scale * np.array(map(lambda p: p.y, tws))


plt.plot(s, x + sig_x, color='#0000AA', lw=2.0)
plt.plot(s, x-sig_x, color='#0000AA', lw=2.0)

plt.plot(s, sig_y, color='#00AA00', lw=2.0)
plt.plot(s, -sig_y, color='#00AA00', lw=2.0)

#f=plt.figure()
plt.plot(s, x, 'r--', lw=2.0)
#plt.plot(s, y, 'r--', lw=2.0)

plt.show()

