"""PyAsy Plot object."""

import textwrap

import asymptote


######################################################################

class Plot(object):
    """PyAsy Asymptote wrapper.

       **Basic usage**

       >>> import pyasy.plot
       >>> import numpy

       >>> x = numpy.linspace(-10.0, 20.0, 101)
       >>> y = x**2

       >>> plot = pyasy.plot.Plot(xlims=[0.0, 10.0], size=(2,3,False))
       >>> plot.line(x, y)
       >>> plot.axis(title='some plot', xlabel='$x$', ylabel='$y$')
       >>> plot.shipout('x_squared')

       You can use a different pen by, eg,

       >>> plot.line(x, y, 'red+dashed')

       or

       >>> plot.line(x, y, ['red', 'dashed'])

       or

       >>> plot.line(x, y, pen=['red', 'dashed'])

       **Sending Asymptote commands**

       You can send commands directly to the Asymptote engine by, eg::

       >>> plot.asy.send('real x = 1.0')

       **Debugging**

       To aid in debugging, you can echo all commands sent to the
       Asymptote engine by either::

       >>> plot = pyasy.plot.Plot(echo=True)

       or::

       >>> plot.asy.echo = True

       **Arguments**

       * *xlims* - Sets the default xlimits ([xmin, xmax]).

       * *size* - Sets the default size of the plot.  This is a tuple
         of the form ``(width, height, keep_aspect)``.  The *width*
         and *height* are in inches.  The boolean *keep_aspect*
         determines if the x and y aspects are to be kept equal
         (``True``) or not (``False``).

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
        asy.send('import contour')
        asy.send('import palette')
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


    ##################################################################

    def _pen(self, pen, **kwargs):

        if pen is not None:
            if isinstance(pen, str):
                pen = ['plotpen'] + pen.split('+')
            elif isinstance(pen, list):
                pen.append('plotpen')
        else:
            pen = ['plotpen']

        return '+'.join(pen)


    def _picture(self, **kwargs):

        if self.picture == 0:
            self.new_plot(self.size)

        return 'p%d' % (self.picture)


    def _filter_and_slurp2(self, x, y, **kwargs):

        if self.xlims is not None:
            i = x > self.xlims[0]
            x = x[i]
            y = y[i]

            i = x < self.xlims[1]
            x = x[i]
            y = y[i]


        self.asy.slurp2(x, y)


    def _filter_and_slurp3(self, x, y, z, **kwargs):

        # XXX: filter...

        self.asy.slurp3(x, y, z)


    ##################################################################

    def axis(self, title='',
             xlabel='$x$', ylabel='',
             ylims=None,                # XXX: move elsewhere?
             xticks=('LeftTicks', {}),
             yticks=('RightTicks', {}),
             **kwargs):
        """Label the current plot and axis.

           **Arguments**

           * *title* - plot title.

           * *xlabel* - x-axis label.

           * *ylabel* - y-axis label.

           * *xticks* - tuple (*type*, *options*) where *type* is the
              name of an Asymptote tick constructor (eg, 'LeftTicks'),
              and *options* is a dictionary of options (keys) and
              values that are passed to the tick constructor.

           * *yticks* - as above.

           """

        asy   = self.asy
        xlims = self.xlims
        y     = self.y

        picture = self._picture()

        if xlims is None:
            x = self.x
            xlims = [x[0], x[-1]]

        asy.send('real x1 = %lf' % xlims[0])
        asy.send('real x2 = %lf' % xlims[1])

        if ylims is None:
            ylims = [y.min(), y.max()]

        asy.send('real y1 = %lf' % ylims[0])
        asy.send('real y2 = %lf' % ylims[1])

        asy.send('''xaxis(%(pic)s,
                          Label("%(title)s", MidPoint, N),
                          YEquals(y2),
                          x1, x2, above=true
                          )'''
                 % { 'pic': picture, 'title': title } )


        # x ticks
        t = xticks[0]
        o = xticks[1]
        ticks = t + '(' + ','.join(['%s=%s' % (str(k), str(o[k])) for k in o]) + ')'

        print ticks

        asy.send('''xaxis(%(pic)s,
                          Label("%(xlabel)s", MidPoint, S),
                          YEquals(y1),
                          x1, x2,
                          %(ticks)s,
                          above=true
                          )'''
                 % { 'pic': picture,
                     'xlabel': xlabel,
                     'ticks': ticks })

        # y ticks
        t = yticks[0]
        o = yticks[1]
        ticks = t + '(' + ','.join(['%s=%s' % (str(k), str(o[k])) for k in o]) + ')'

        print ticks

        asy.send('''yaxis(%(pic)s,
                          "%(ylabel)s",
                          LeftRight,
                          y1, y2,
                          %(ticks)s,
                          above=true
                          )'''
                 % { 'pic': picture,
                     'ylabel': ylabel,
                     'ticks': ticks })



    ##################################################################

    def scatter(self, x, y, pen=None, **kwargs):
        """Scatter plot of *y* vs *x* (both of which should be 1d
           ndarrays)."""

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)

        self._filter_and_slurp2(x, y, **kwargs)

        self.asy.send('''for (int i=0; i<X.length; ++i)
                           { dot(%s, (X[i], Y[i]), %s); }'''
                      % (picture, pen))

        self.x = x
        self.y = y


    ##################################################################

    def line(self, x, y, pen=None, **kwargs):
        """Line plot of *y* vs *x* (both of which should be 1d
           ndarrays)."""

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)

        self._filter_and_slurp2(x, y)

        self.asy.send('draw(%s, graph(X, Y), %s)' % (picture, pen))

        self.x = x
        self.y = y


    ##################################################################

    def colour_contour(self, x, y, z, bar=False, pen=None, **kwargs):
        """Contour plot of *z* vs (*x*, *y*)."""

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)

        self._filter_and_slurp3(x, y, z)

        self.asy.send('pen[] pal = Rainbow(512)')
        self.asy.send('pair initial = (%lf, %lf)' % (x[0], y[0]))
        self.asy.send('pair final = (%lf, %lf)' % (x[-1], y[-1]))
        self.asy.send('''bounds range =
          image(%s, ZZ, initial, final, pal,
                antialias=true)''' % (picture))

        if bar:
            self.asy.send('initial = ' + str(bar['initial']))
            self.asy.send('final = ' + str(bar['final']))

            self.asy.send(
                'palette(%s, "%s", range, initial, final, pal, %s)'
                 % (picture, bar['label'], pen))

        self.x = x
        self.y = y


    ##################################################################

    def horizontal_line(self, y=0.0, pen='plotpen+dotted', **kwargs):
        """Draw a horizontal line at *y* on the graph."""

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)

        self.asy.send('real x1 = %lf' % self.xlims[0])
        self.asy.send('real x2 = %lf' % self.xlims[1])
        self.asy.send('xaxis(%s, YEquals(%lf, false), x1, x2, %s)'
                      % (picture, y, pen))


    ##################################################################

    def vertical_line(self, x=0.0, pen='plotpen+dotted', **kwargs):
        """Draw a vertical line at *x* on the graph."""

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)


        self.asy.send('yaxis(%s, XEquals(%lf, false), %s)'
                      % (picture, x, pen))


    ##################################################################

    def caption(self, caption='', label='',
                includegraphics_options='', **kwargs):
        """Set caption used for LaTeX export (see *shipout*
           method)."""

        self.caption = caption
        self.label = label
        self.includegraphics_options = includegraphics_options

        self.export_tex = True


    ##################################################################

    def new_plot(self, size=(4,4,False), shift=(0,0)):
        """Create a new subplot."""

        self.plots.append({'size': size, 'shift': shift})
        self.picture = self.picture + 1
        self.asy.send('picture p%d' % (self.picture))


    ##################################################################

    def shipout(self, basename='plot', format='pdf'):
        """Shipout the current plot(s).

           The current plot(s) is rendered and output to the file
           *basename.format* (eg, ``plot.pdf``).

           If a caption was set, the LaTeX commands for including and
           annotating the plot (in a LaTeX *figure* environment) are
           output to *basename*.tex (eg, ``plot.tex``).

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

            if options:
                f.write(textwrap.dedent(
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
            else:
                f.write(textwrap.dedent(
                    '''\
                    \\begin{figure}
                      \\centering
                      \\includegraphics{plots/%(basename)s}
                      \\caption{%(caption)s}
                      \\label{%(label)s}
                    \\end{figure}
                    ''' % { 'basename': basename,
                            'caption': caption,
                            'label': label
                            }  ))

            f.close()

            self.export_tex = False
