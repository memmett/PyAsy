"""PyAsy base object (helper functions)."""

import textwrap

import numpy as np

import asymptote


######################################################################

class Base(object):
    """PyAsy base object."""

    def __init__(self,
                 xlims=None, ylims=None,
                 smooth=None,
                 size=(4,4,False),
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
        self.ylims = ylims
        self.size = size
        self.picture = 0
        self.plots = []
        self.palette = False
        self.export_tex = False
        self.smooth = smooth


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

        # XXX: see http://www.scipy.org/Cookbook/SignalSmooth for more smoothing options...

        if self.smooth:                 # moving average
            w = np.ones(self.smooth)
            y = np.convolve(w/w.sum(), y, mode='same')

        self.asy.slurp2(x, y)

        self.x = x
        self.y = y
        self._bounds(x, y)


    def _slurp3(self, x, y, z, **kwargs):

        self.asy.slurp3(x, y, z)

    def _bounds(self, x, y):
        if 'bounds' in self.plots[-1]:
            d = self.plots[-1]['bounds']
            x_min = d['min'][0]
            x_max = d['max'][0]
            y_min = d['min'][1]
            y_max = d['max'][1]
            self.plots[-1]['bounds'] = {'min': (min(x_min, min(x)), min(y_min, min(y))),
                                        'max': (max(x_max, max(x)), max(y_max, max(y)))}
        else:
            self.plots[-1]['bounds'] = {'min': (min(x), min(y)),
                                        'max': (max(x), max(y))}


    def _dict_to_arguments(self, d):
        return '(' + ','.join(['%s=%s' % (str(k), str(d[k])) for k in d]) + ')'


    ##################################################################

    def _axis(self,
              title='',
              xlabel='$x$', ylabel='',
              xticks=('LeftTicks', {}),
              yticks=('RightTicks', {}),
              picture=None,
              **kwargs):

        asy   = self.asy
        xlims = self.xlims
        ylims = self.ylims

        if picture is None:
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

        # title

        asy.send('''xaxis(%(pic)s,
                          Label("%(title)s", MidPoint, N),
                          YEquals(y2),
                          x1, x2, above=true
                          )'''
                 % { 'pic': picture, 'title': title } )


        # x ticks and axis
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

        # y ticks and axis
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

        self._bounds(xlims, ylims)


    ##################################################################

    def axis(self, title='',
             xlabel='$x$', ylabel='',
             ylims=None,                # XXX: move elsewhere?
             xticks=('LeftTicks', {}),
             yticks=('RightTicks', {}),
             picture=None,
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

        if picture is None:
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

    def caption(self, caption='', label='',
                includegraphics_options='', **kwargs):
        """Set caption used for LaTeX export (see *shipout*
           method)."""

        self.caption = caption
        self.label = label
        self.includegraphics_options = includegraphics_options

        self.export_tex = True


    ##################################################################

    def shipout(self, basename='plot', format='pdf'):
        """Shipout the current plot(s).

           The current plot(s) is rendered and output to the file
           *basename.format* (eg, ``plot.pdf``).

           If a caption was set, the LaTeX commands for including and
           annotating the plot (in a LaTeX *figure* environment) are
           output to *basename*.tex (eg, ``plot.tex``).

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
