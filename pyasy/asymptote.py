"""PyAsy Asymptote class."""

import struct
import subprocess

class Asymptote(object):
    """PyAsy Asymptote class (used to communicate with an Asymptote
       subprocess).

       Usually this is class is instantiated by the PyAsy Plot class,
       but you may use it directly if required.

       You can send commands directly to the Asymptote engine by, eg::

       >>> plot.asy.send('real x = 1.0')

       **Arguments**

       * *echo* - If True, Asymptote commands are echoed to stdout as
         they are sent to the Asymptote engine (useful for debugging).
         (This can be enable later by setting the *echo* instance
         variable.)

       **Methods**

       """

    asy_slurp = """real[][] slurp(string filename) {
                     file dat = binput(filename);

                     int N = dat;

                     real[][] xy = new real[N][N];
                     xy[0][:] = dimension(dat, N);
                     xy[1][:] = dimension(dat, N);

                     close(dat);

                     return xy;
                   }"""


    def __init__(self, echo=False, **kwargs):
        self.echo = echo
        self.open()
        self.send(self.asy_slurp)

        self.count = 0


    def send(self, cmd):
        """Send a command to the Asymptote engine.  A trailing
           semicolon is added automatically."""
        if self.echo:
            print cmd

        self.session.stdin.write(cmd+';\n')
        self.session.stdin.flush()


    def slurp(self, x, y, **kwargs):
        """Send the *x* and *y* ndarrays to the Asymptote engine.

           The slurpped data is stored, in Asymptote, in the 2d ``xy``
           array.

           """

        slurp = '.tmp%d.dat' % (self.count)

        f = open(slurp, 'wb')
        f.write(struct.pack("i", x.size))
        x.tofile(f)
        y.tofile(f)
        f.close()

        self.count = self.count + 1

        self.send('real[][] xy')
        self.send('xy = slurp("%s")' % (slurp))


    def open(self):
        self.session = subprocess.Popen(['asy'],stdin=subprocess.PIPE)


    def close(self):
        self.session.stdin.close();
        self.session.wait()
