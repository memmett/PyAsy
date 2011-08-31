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
                 markers=False,
                 **kwargs):

        # init asy
        asy = asymptote.Asymptote(**kwargs)
        asy.send('import graph')
        asy.send('import contour')
        asy.send('import palette')

        # init pens
        if defaultpen is not None:
            if isinstance(defaultpen, str):
                defaultpen = [defaultpen]

            asy.send('defaultpen(%s)' % '+'.join(defaultpen))
            self.defaultpen = '+'.join(defaultpen)
        else:
            asy.send('defaultpen(fontsize(10pt))')
            self.defaultpen = 'fontsize(10pt)'


        if plotpen is not None:
            if isinstance(plotpen, str):
                plotpen = [plotpen]

            asy.send('pen plotpen = %s' % '+'.join(plotpen))
        else:
            asy.send('pen plotpen = %s' % self.defaultpen)

        # init markers
        if markers:
            import markers
            asy.send(markers.markers)

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
                #pen = ['plotpen'] + pen.split('+')
                pen = pen.split('+')
            # elif isinstance(pen, list):
            #     pen.append('plotpen')
        # else:
        #     pen = ['plotpen']
        else:
            pen = ['defaultpen']

        return '+'.join(pen)


    def _picture(self, **kwargs):

        if self.picture == 0:
            self.new_plot(self.size)

        return 'p%d' % (self.picture)


    def _filter_and_slurp2(self, x, y, **kwargs):

        x = 1.0*np.array(x)
        y = 1.0*np.array(y)

        if len(y) > len(x):
           y = y[:len(x)]

        if self.xlims is not None:
            i = x > self.xlims[0]
            x = x[i]
            y = y[i]

            i = x < self.xlims[1]
            x = x[i]
            y = y[i]

        # XXX: document this somewhere
        # XXX: see http://www.scipy.org/Cookbook/SignalSmooth for more smoothing options...

        if self.smooth:                 # moving average
            w = np.ones(self.smooth)
            y = np.convolve(w/w.sum(), y, mode='same')

        self.asy.slurp2(x, y)

        self.x = x
        self.y = y
        self._bounds(x, y)


    def _slurp3(self, x, y, z, **kwargs):

        x = 1.0*np.array(x)
        y = 1.0*np.array(y)
        z = 1.0*np.array(z)

        self.asy.slurp3(x, y, z)


    def _bounds(self, x, y):

        x = 1.0*np.array(x)
        y = 1.0*np.array(y)

        if 'bounds' in self.plots[-1]:
            d = self.plots[-1]['bounds']
            x_min = d['min'][0]
            x_max = d['max'][0]
            y_min = d['min'][1]
            y_max = d['max'][1]
            self.plots[-1]['bounds'] = {'min': (min(x_min, x.min()), min(y_min, y.min())),
                                        'max': (max(x_max, x.max()), max(y_max, y.max()))}
        else:
            self.plots[-1]['bounds'] = {'min': (x.min(), y.min()),
                                        'max': (x.max(), y.max())}

    def _dict_to_arguments(self, d):
        return '(' + ','.join(['%s=%s' % (str(k), str(d[k])) for k in d]) + ')'
