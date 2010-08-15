"""PyAsy Plot object."""

import textwrap

import base
import asymptote


######################################################################

class Plot(base.Base):
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

    ##################################################################

    def axis(self, title='',
             xlabel='$x$', ylabel='',
             ylims=None,                # XXX: move elsewhere?
             xticks=('LeftTicks', {}),
             yticks=('RightTicks', {}),
             **kwargs):
        """Label the current plot and axis.

           **Arguments**

           * *title*: Plot title.

           * *xlabel*: x-axis label.

           * *ylabel*: y-axis label.

           * *xticks*: Tuple ``(type, options)`` where *type* is the
             name of an Asymptote tick constructor (eg, 'LeftTicks'),
             and *options* is a dictionary of options (keys) and
             values that are passed to the tick constructor.  Please
             see the Asymptote_ documentation for more details.

           * *yticks*: As above.

           .. _`Asymptote`: http://asymptote.sf.net/

           """

        asy   = self.asy
        xlims = self.xlims
        y     = self.y

        picture = self._picture()

        if xlims is None:
            xlims = [self.plots[-1]['bounds']['min'][0],
                     self.plots[-1]['bounds']['max'][0]]

        if ylims is None:
            ylims = [self.plots[-1]['bounds']['min'][1],
                     self.plots[-1]['bounds']['max'][1]]

        asy.send('real x1 = %lf' % xlims[0])
        asy.send('real x2 = %lf' % xlims[1])

        asy.send('real y1 = %lf' % ylims[0])
        asy.send('real y2 = %lf' % ylims[1])

        asy.send('''xaxis(%(pic)s,
                          Label("%(title)s", MidPoint, N),
                          YEquals(y2),
                          x1, x2, above=true
                          )'''
                 % { 'pic': picture, 'title': title } )


        # x ticks
        ticks = xticks[0] + self._dict_to_arguments(xticks[1])

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
        ticks = yticks[0] + self._dict_to_arguments(yticks[1])

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

        # pallete
        if self.palette:
            asy.send(self.palette)
            self.palette = False

        self._bounds(xlims, ylims)


    ##################################################################

    def scatter(self, x, y, pen=None, **kwargs):
        """Scatter plot of *y* vs *x* (both of which should be 1d
           ndarrays).

           **Arguments**

           * *x*: Horizontal coordinates of data points.
           * *y*: Vertical coordindates of data points.
           * *pen*: Asymptote pen (array or '+' delimited string).
             Defaults to *plotpen*.

           """

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)

        self._filter_and_slurp2(x, y, **kwargs)

        self.asy.send('''for (int i=0; i<X.length; ++i)
                           { dot(%s, (X[i], Y[i]), %s); }'''
                      % (picture, pen))


    ##################################################################

    def line(self, x, y, pen=None, legend=None, **kwargs):
        """Line plot of *y* vs *x* (both of which should be 1d
           ndarrays).

           **Arguments**

           * *x*: Horizontal coordinates of data points.
           * *y*: Vertical coordinates of data points.
           * *pen*: Asymptote pen (array or '+' delimited string).
             Defaults to *plotpen*.
           * *legend*: Asymptote legend key
             (see :func:`pyasy.plot.Plot.legend`).

           """

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)

        self._filter_and_slurp2(x, y)

        if legend is not None:
            self.asy.send('draw(%s, graph(X, Y), %s, legend="%s")'
                          % (picture, pen, legend))
        else:
            self.asy.send('draw(%s, graph(X, Y), %s)'
                          % (picture, pen))

    ##################################################################

    def density(self, x, y, z, pen=None,
                palette='Rainbow(512)',
                brange='Full',
                bar=False,
                **kwargs):
        """Density (colour filled contour) plot of *z* vs (*x*, *y*).

           The x, y, and z ndarrays are indexed as: ``x[i]``,
           ``y[j]``, and ``z[i,j]`` respectively.

           **Arguments**

           * *x*: Horizontal coordinates of data values (indexed
             as ``x[i]``).
           * *y*: Vertical coordinates of data values (indexed
             as ``y[j]``).
           * *z*: Data values (indexed as ``z[i,j]``).
           * *palette*: `Asymptote palette`_.
           * *brange*: Range for data values (list or Asymptote
             string).
           * *bar*: Dictionary to control the display of the
             palette bar with entries:

             * *initial*: Tuple of coordinates for the bottom
               left corner of the bar.
             * *final*: Tuple of coordinates for the top
               right corner of the bar.
             * *label*: Label for the bar (eg, ``'$z$'``).

           .. _`Asymptote palette`: http://asymptote.sourceforge.net/doc/palette.html

        """

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)

        self._slurp3(x, y, z)

        if isinstance(brange, list):
            brange = 'Range(%lf, %lf)' % tuple(brange)

        self.asy.send('pen[] pal = %s' % palette)
        self.asy.send('pair initial = (%lf, %lf)' % (x[0], y[0]))
        self.asy.send('pair final = (%lf, %lf)' % (x[-1], y[-1]))
        self.asy.send('''bounds range =
          image(%s, ZZ, %s, initial, final, pal,
                antialias=true)''' % (picture, brange))

        if bar:
            self.palette = '''
              initial = %(initial)s;
              final = %(final)s;
              palette(%(picture)s, "%(label)s", range, initial, final, pal, %(pen)s)
              ''' % {'picture': picture,
                     'initial': str(bar['initial']),
                     'final':   str(bar['final']),
                     'label': bar['label'],
                     'pen': pen }

        self.x = x
        self.y = y
        self.z = z
        self.plots[-1]['bounds'] = {'min': (x.min(), y.min()),
                                    'max': (x.max(), y.max())}


    ##################################################################

    def horizontal_line(self, y=0.0, pen='plotpen+dotted', **kwargs):
        """Draw a horizontal line at *y* on the graph."""

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)

        self.asy.send('real x1 = %lf' % self.xlims[0])
        self.asy.send('real x2 = %lf' % self.xlims[1])
        self.asy.send('xaxis(%s, YEquals(%lf, false), x1, x2, %s, above=true)'
                      % (picture, y, pen))


    ##################################################################

    def vertical_line(self, x=0.0, pen='plotpen+dotted', **kwargs):
        """Draw a vertical line at *x* on the graph."""

        picture = self._picture(**kwargs)
        pen = self._pen(pen, **kwargs)


        self.asy.send('yaxis(%s, XEquals(%lf, false), %s, above=true)'
                      % (picture, x, pen))


    ##################################################################

    def caption(self, caption='', label='',
                includegraphics_options='', **kwargs):
        """Set caption used for LaTeX export (see the
           :func:`pyasy.plot.Plot.shipout` method).

           **Arguments**

           * *caption*: Figure caption (ie, LaTeX
             \\\\caption{*caption*}).
           * *label*: Figure label (ie, LaTeX
             \\\\label{*label*}).
           * *includegraphics_options*: Extra options for
             *includegraphics* (ie, \\\\includegraphics[*options*]{}).

           """

        self.caption = caption
        self.label = label
        self.includegraphics_options = includegraphics_options

        self.export_tex = True


    ##################################################################

    def legend(self, position=None, direction=None, **kwargs):
        """Draw a legend.

           **Arguments**

           * *position*: XXX
           * *direction*: XXX

           """

        picture = self._picture(**kwargs)

        if position is None:
            position = 'point(E)'

        if direction is None:
            direction = '10E'

        self.asy.send('''add(%(pic)s, legend(%(pic)s),
                         %(position)s, %(direction)s, UnFill)'''
                      % {'pic': picture,
                         'position': position,
                         'direction': direction })


    ##################################################################

    def new_plot(self, size=(4,4,False), shift=(0,0)):
        """Create a new subplot.

           **Arguments**

           * *size*: XXX
           * *shift*: XXX

           """

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
           output to *basename*.tex (eg, ``plot.tex``).  See
           :func:`pyasy.plot.Plot.caption`.

           """

        asy = self.asy

        for i, p in enumerate(self.plots):
            picture = 'p%d' % (i+1)
            frame = 'f%d' % (i+1)
            shift = '(%lf*inch,%lf*inch)' % p['shift']

            w, h, k = p['size']
            k = str(k).lower()
            w = str(w) + '*inch'
            h = str(h) + '*inch'

            bl = str(p['bounds']['min'])
            ur = str(p['bounds']['max'])
            dx = str(p['bounds']['max'][0] - p['bounds']['min'][0])
            dy = str(p['bounds']['max'][1] - p['bounds']['min'][1])

            # XXX: aspect!
            #asy.send('size(%s, %s, %s, %s, %s, %s)' % (picture, w, h, bl, ur, k))
            asy.send('size(%s, %s, %s, %s, %s)' % (picture, w, h, bl, ur))
            asy.send('frame %(frame)s = shift(%(x)s*%(w)s/%(dx)s, %(y)s*%(h)s/%(dy)s)*%(picture)s.fit()'
                     % {'frame': frame,
                        'picture': picture,
                        'x': str(-p['bounds']['min'][0]),
                        'y': str(-p['bounds']['min'][1]),
                        'w': w, 'h': h, 'dx': dx, 'dy': dy })


            self.asy.send('add(shift(%s)*%s)'
                          % (shift, frame))

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
