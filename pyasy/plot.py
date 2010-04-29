"""PyAsy Plot object."""

import asymptote

import os
import math
import struct

import h5py
import numpy as np

from textwrap import dedent


######################################################################

class Plot(object):
    """PyAsy Asymptote wrapper.

       **Basic usage**

       >>> import pyasy.plot
       >>> import numpy
       >>>
       >>> x = numpy.linspace(-10.0, 20.0, 101)
       >>> y = x**2
       >>>
       >>> plot = pyasy.plot.Plot(xlims=[0.0, 10.0], size=(2,3,False))
       >>> plot.line(x, y)
       >>> plot.axis(title='some plot', xlabel='$x$', ylabel='$y$')
       >>> plot.shipout('x_squared')

       **Sending Asymptote commands**

       You can send commands directly to the Asymptote engine by, eg::

       >>> plot.asy.send('real x = 1.0')

       **Arguments**

       * *xlims* - Sets the default xlimits ([xmin, xmax]).

       * *size* - Sets the default size of the plot.  This is a tuple
                  of the form (width, height, aspect).  The *width*
                  and *height* are in inches.  The *aspect* is boolean
                  and corresponds to Asymptotes' IgnoreAspect.

       * *defaultpen* - Sets the default pen.

       * *plotpen* - Sets the plot pen (used when drawing lines and
                     dots in the plots, but not for axis etc).

       Any other keyword arugments are passed on to the
       pyasy.asymptote.Asymptote constructor.

       **Methods**

       """

    def __init__(self,
                 xlims=None, size=(4,4,False),
                 defaultpen=None, plotpen=None,
                 **kwargs):

        # init asy
        asy = asymptote.Asymptote(**kwargs)
        asy.send('import graph')
        asy.send('defaultpen(fontsize(10pt))')

        # init pens
        if defaultpen is not None:
            if isinstance(defaultpen, str):
                defaultpen = [defaultpen]

            asy.send('defaultpen(%s)' % '+'.join(defaultpen))

        if plotpen is not None:
            if isinstance(plotpen, str):
                plotpen = [plotpen]

            asy.send('pen plotpen = %s' % '+'.join(plotpen))
        else:
            asy.send('pen plotpen = defaultpen')

        # init self
        self.asy = asy
        self.xlims = xlims
        self.size = size
        self.picture = 0
        self.plots = []
        self.export_tex = False
        self.count = 0


    ##################################################################

    def axis(self, title='',
             xlabel='$x$', ylabel='', ylims=None,
             nxtics=None, nytics=None, **kwargs):
        """Label the current plot and axis.

           **Arguments**

           XXX

           """

        asy   = self.asy
        xlims = self.xlims
        q     = self.q

        picture = 'p%d' % (self.picture)

        if xlims is None:
            x = self.x
            xlims = [x[0], x[-1]]

        asy.send('real x1 = %lf' % xlims[0])
        asy.send('real x2 = %lf' % xlims[1])

        if ylims is None:
            ylims = [q.min(), q.max()]

        asy.send('real y1 = %lf' % ylims[0])
        asy.send('real y2 = %lf' % ylims[1])

        asy.send('''xaxis(%(pic)s,
                          Label("%(title)s", MidPoint, N),
                          YEquals(y2),
                          x1, x2
                          )'''
                 % { 'pic': picture, 'title': title } )

        if nxtics is not None:
            asy.send('''xaxis(%(pic)s,
                              Label("%(xlabel)s", MidPoint, S),
                              YEquals(y1),
                              x1, x2,
                              LeftTicks(N=%(N)d, n=%(n)d)
                              )'''
                     % { 'pic': picture, 'xlabel': xlabel,
                         'N': nxtics[0], 'n': nxtics[1] } )
        else:
            asy.send('''xaxis(%(pic)s,
                              Label("%(xlabel)s", MidPoint, S),
                              YEquals(y1),
                              x1, x2,
                              LeftTicks
                              )'''
                     % { 'pic': picture, 'xlabel': xlabel } )

        if nytics is not None:
            asy.send('''yaxis(%(pic)s,
                              "%(ylabel)s",
                              LeftRight,
                              y1, y2,
                              RightTicks(N=%(N)d, n=%(n)d)
                              )'''
                     % { 'pic': picture, 'ylabel': ylabel,
                         'N': nytics[0], 'n': nytics[1] } )
        else:
            asy.send('''yaxis(%(pic)s,
                              "%(ylabel)s",
                              LeftRight,
                              y1, y2,
                              RightTicks
                              )'''
                     % { 'pic': picture, 'ylabel': ylabel } )


    ##################################################################

    def scatter(self, x, y, pen=None, **kwargs):
        """Scatter plot of *y* vs *x* (1d arrays)."""

        asy = self.asy

        if self.picture == 0:
            self.new_plot(self.size)

        picture = 'p%d' % (self.picture)

        # slurp data into asy
        self.asy.slurp(self._write(x, y))

        # draw the graph
        if pen is not None:
            if isinstance(pen, str):
                pen = ['plotpen', pen]
            else:
                pen.append('plotpen')
        else:
            pen = ['plotpen']

        asy.send('''for (int i=0; i<xq[0][:].length; ++i)
                      { dot(%s, (xq[0][i], xq[1][i]), %s); }'''
                 % (picture, '+'.join(pen)))

        self.x = x
        self.q = y


    ##################################################################

    def line(self, x, y, pen=None, **kwargs):
        """Line plot of *y* vs *x* (1d arrays)."""

        asy = self.asy

        if self.picture == 0:
            self.new_plot(self.size)

        picture = 'p%d' % (self.picture)

        # slurp data into asy
        self.asy.slurp(self._write(x, y))

        # draw the graph
        if pen is not None:
            if isinstance(pen, str):
                pen = ['plotpen', pen]
            else:
                pen.append('plotpen')
        else:
            pen = ['plotpen']

        asy.send('draw(%s, graph(xq[0][:], xq[1][:]), %s)' % (picture, '+'.join(pen)))

        self.x = x
        self.q = y


    ##################################################################

    def horizontal_line(self, y=0.0, pen='plotpen+dotted', **kwargs):
        """Draw a horizontal line at *y* on the graph."""

        picture = 'p%d' % (self.picture)

        self.asy.send('real x1 = %lf' % self.xlims[0])
        self.asy.send('real x2 = %lf' % self.xlims[1])
        self.asy.send('xaxis(%s, YEquals(%lf, false), x1, x2, %s)'
                      % (picture, y, pen))


    ##################################################################

    def caption(self, caption='', label='',
                includegraphics_options=''):
        """Set caption used for TeX export."""

        self.caption = caption
        self.label = label
        self.includegraphics_options = includegraphics_options

        self.export_tex = True


    ##################################################################

    def new_plot(self, size=(6,2,False), shift=(0,0)):
        """Create a new subplot."""
        self.plots.append({'size': size, 'shift': shift})
        self.picture = self.picture + 1
        self.asy.send('picture p%d' % (self.picture))


    ##################################################################

    def shipout(self, basename='plot', format='pdf'):
        """Shipout the current plot(s).

           The current plot(s) is rendered and output to the file
           *basename*.*format* (eg, 'plot.pdf').

           If a caption was set, the LaTeX commands for including and
           annotating the plot are output to *basename*.tex.

           """

        for i, p in enumerate(self.plots):
            picture = 'p%d' % (i+1)
            shift = '(%lf*inch,%lf*inch)' % p['shift']

            if p['size'][2]:
                size = '%lf*inch,%lf*inch,true' % (p['size'][0], p['size'][1])
            else:
                size = '%lf*inch,%lf*inch,false' % (p['size'][0], p['size'][1])

            self.asy.send('add(shift(%s)*%s.fit(%s))'
                          % (shift, picture, size))

        self.asy.send('shipout("%s", "%s")' % (basename, format))
        self.asy.close()

        if self.export_tex:

            caption = self.caption
            label   = self.label
            options = self.includegraphics_options

            f = open('%s.tex' % (basename), 'w')
            f.write(dedent(
                '''\
                \\begin{figure}
                  \\centering
                  \\includegraphics[%(options)s]{plots/%(basename)s}
                  \\caption{%(caption)s}
                  \\label{%(label)s}
                \\end{figure}
                ''' % { 'basename': basename,
                        'options': options,
                        'caption': caption,
                        'label': label
                        }  ))
            f.close()

            self.export_tex = False


    ##################################################################

    def _write(self, x, q, **kwargs):

        count = self.count

        slurp = '.tmp%d.dat' % (count)

        f = open(slurp, 'wb')
        f.write(struct.pack("i", x.size))
        x.tofile(f)
        q.tofile(f)
        f.close()

        self.count = count + 1

        return slurp
