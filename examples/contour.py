"""A simple example of how to use PyAsy."""

import math
import numpy
import pyasy.plot

plot = pyasy.plot.Plot()

x = numpy.linspace(-math.pi, math.pi, 201)
y = numpy.linspace(-math.pi, math.pi, 201)
z = numpy.zeros((x.size,y.size))
for i in xrange(x.size):
    for j in xrange(y.size):
        z[i,j] = numpy.sin(1.0/(1.0 + math.sqrt(x[i]**2 + y[j]**2)))

plot.colour_contour(x, y, z)
plot.axis(xlabel='$x$', ylabel='$y$')
plot.shipout('contour')
