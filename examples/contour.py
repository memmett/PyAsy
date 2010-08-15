"""A simple example of how to create coloured contour plots in PyAsy."""

import math
import numpy
import pyasy.plot

p = pyasy.plot.Plot(size=(4,4,True))

x = numpy.linspace(-math.pi, math.pi, 201)
y = numpy.linspace(-math.pi, math.pi, 201)
z = numpy.zeros((x.size,y.size))
for i in xrange(x.size):
    for j in xrange(y.size):
        z[i,j] = numpy.sin(1.0/(1.0 + x[i]**2 + y[j]**2))

p.density(x, y, z,
          bar={'label': '$z$',
               'initial': (4.0, -math.pi),
               'final': (4.25, math.pi)})
p.axis(xlabel='$x$', ylabel='$y$')
p.shipout('contour')
