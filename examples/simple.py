"""A simple example of how to use PyAsy."""

import numpy
import pyasy.plot

p = pyasy.plot.Plot()

x = numpy.linspace(-10.0, 20.0, 101)
y = x**2

p.line(x, y)
p.axis(xlabel='$x$', ylabel='$y$')
p.shipout('simple')
