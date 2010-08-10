"""PyAsy Animation object."""

import textwrap

import base

######################################################################

class Animation(base.Base):
    """PyAsy Asymptote wrapper for creating PDF animations.

       To create a stand-alone PDF animation (ie, a PDF document that
       only contains the animation and controls), set the *render*
       flag to True when shipping out the animation.  To create a
       multipage PDF animation (so that you can include the animation
       in, eg, LaTeX presentations), leave the *render* flag set to
       False when shipping out the animation.

       To include a multipage animation in a LaTeX document, you must
       include the *animate* package in the preamble:

         \usepackage{animate}

       and use the *animategraphics* macro in the body:

         \animategraphics[controls]{12}{filename}{}{}.


       **Basic usage**

       >>> import pyasy.animation
       >>> a = pyasy.animation.Animation(size=(4, 1.2, False))

       XXX

       """

    def __init__(self, **kwargs):

        base.Base.__init__(self, **kwargs)

        self.asy.send('import animate')
        self.asy.send('settings.tex="pdflatex"')
        #self.asy.send('settings.keep=true')


    ##################################################################

    def animate(self, x, t, y, pen=None,
                xlabel='$x$', ylabel='',
                xticks=('LeftTicks', {}),
                yticks=('RightTicks', {}),
                xlims=None,
                ylims=None,
                tlabel=None,
                **kwargs):
        """Create an animation of *y* vs *x* for the various values of
           time in *t*.

           The x, t, and y ndarrays are indexed as: ``x[i]``,
           ``t[n]``, and ``y[n,i]`` respectively.

           **Arguments**

           * *xlabel*:
           * *ylabel*:
           * *xticks*:
           * *yticks*:
           * *xlims*:
           * *ylims*:

        """

        asy = self.asy
        pen = self._pen(pen, **kwargs)

        # size
        w, h, k = self.size
        k = str(k).lower()
        w = str(w) + '*inch'
        h = str(h) + '*inch'
        size = '%s, %s, %s ' % (w, h, k)

        # limits
        if xlims is None:
            xlims = [x.min(), x.max()]

        if ylims is None:
            ylims = [y.min(), y.max()]

        asy.send('real x1 = %lf' % xlims[0])
        asy.send('real x2 = %lf' % xlims[1])

        asy.send('real y1 = %lf' % ylims[0])
        asy.send('real y2 = %lf' % ylims[1])


        # x ticks
        o = xticks[1]
        ticks = xticks[0] + '(' + ','.join(['%s=%s' % (str(k), str(o[k])) for k in o]) + ')'

        xaxis = '''xaxis(p,
                         Label("%(xlabel)s", MidPoint, S),
                         YEquals(y1),
                         x1, x2,
                         %(ticks)s,
                         above=true
                         )''' % { 'xlabel': xlabel,
                                  'ticks': ticks }

        # y ticks
        o = yticks[1]
        ticks = yticks[0] + '(' + ','.join(['%s=%s' % (str(k), str(o[k])) for k in o]) + ')'

        yaxis = '''yaxis(p,
                         "%(ylabel)s",
                         LeftRight,
                         y1, y2,
                         %(ticks)s,
                         above=true
                         )''' % { 'ylabel': ylabel,
                                   'ticks': ticks }

        # time label
        if tlabel is None:
            tlabel = ''
        else:
            tlabel = 'label(p, %(format)s, (%(x)s, %(y)s), %(direction)s);' % tlabel


        # animate!
        self._slurp3(x, t, y)
        self.asy.send('''animation a;
          ZZ = transpose(ZZ);

          for (int i=0; i<Y.length; ++i) {
            picture p;
            real t = Y[i];
            size(p, %(size)s);
            draw(p, graph(X, ZZ[i][:]), %(pen)s);
            %(xaxis)s;
            %(yaxis)s;
            %(tlabel)s
            a.add(p);
          }

        ''' % {'size': size, 'pen': pen,
               'xaxis': xaxis, 'yaxis': yaxis, 'tlabel': tlabel })


    ##################################################################

    def shipout(self, basename='animation', render=False):
        """Shipout the current animation."""

        asy = self.asy

        if render:
            ship = '''
              label(a.pdf("controls", multipage=false));
              shipout("%(basename)s", "pdf")'''
        else:
            ship = '''
              a.global=true;
              a.export("%(basename)s", NoBox, multipage=true)'''

        asy.send(ship % {'basename': basename})
        asy.close()
