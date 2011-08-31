"""A simple example of how to use PyAsy."""

import numpy
import pyasy.plot

p = pyasy.plot.Plot()

x = numpy.linspace(-10.0, 20.0, 101)
y = x**2

p.line(x, y, marker='marker(unitcircle,red,Fill)', legend='data')
p.axis(xlabel='$x$', ylabel='$y$')
p.legend((-5,350), length="0.5inch")
p.shipout('data')
