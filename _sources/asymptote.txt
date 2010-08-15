Interacting with Asymptote directly
===================================

PyAsy communicates with Asymptote through the
:class:`pyasy.asymptote.Asymptote` class.  Each of the PyAsy plotting
classes create an instance of this object called ``asy`` when created.
For more complicated plots you might need to send commands directly to
the Asymptote engine by using the ``send`` method.  Alternatively, you
can instantiate an ``Asymptote`` object directly and roll your own
plots.

For example, to tweak a PyAsy plot::

>>> p = pyasy.plot.Plot()
>>> p.plot(x, y)
>>> p.asy.send('label("maximum", (2.0, 4.0), N)')

Alternatively, to roll your own::

>>> asy = pyasy.asymptote.Asymptote()
>>> asy.slurp2(x, y)
>>> asy.send('''draw(graph(X,Y))''')
>>> asy.send('label("maximum", (2.0, 4.0), N)')

Data is sent to the Asymptote engine through the ``slurp2(x, y)`` and
``slurp3(x, y, z)`` methods of the ``Asymptote`` object.  These
methods store the ``x``, ``y``, and ``z`` Python arrays in the ``X``,
``Y``, and ``Z`` Asymptote arrays, respectively.  For the slurp2
method, the arrays are indexed as ``X[i]`` and ``Y[i]``.  For the
slurp3 method, the arrays are indexed as ``X[i]``, ``Y[j]``, and
``Z[i*Y.length+j]``.  Finally, for the slurp3 method, a
two-dimensional Asymptote array ``ZZ`` is created for convenience and
is indexed as ``ZZ[i][j]``.
