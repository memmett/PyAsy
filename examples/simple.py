"""A simple example of how to use PyAsy."""

import numpy
import pyasy.plot

plot = pyasy.plot.Plot()

x = numpy.linspace(-10.0, 20.0, 101)
y = x**2

plot.line(x, y)
plot.axis(xlabel='$x$', ylabel='$y$')
plot.shipout('simple')
