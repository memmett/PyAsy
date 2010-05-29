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

    asy_slurp2 = """void slurp2(string filename) {
                      file dat = binput(filename);

                      int N = dat;

                      X = new real[N];
                      Y = new real[N];

                      X[:] = dimension(dat, N);
                      Y[:] = dimension(dat, N);

                      close(dat);
                    }"""

    asy_slurp3 = """void slurp3(string filename) {
                      file dat = binput(filename);

                      int N = dat;
                      int M = dat;

                      X = new real[N];
                      Y = new real[M];
                      Z = new real[N*M];
                      ZZ = new real[N][M];

                      X[:] = dimension(dat, N);
                      Y[:] = dimension(dat, M);
                      Z[:] = dimension(dat, N*M);

                      for (int i=0; i<X.length; ++i)
                        for (int j=0; j<Y.length; ++j)
                          ZZ[i][j] = Z[i*Y.length+j];

                      close(dat);
                    }"""


    def __init__(self, echo=False, **kwargs):
        self.echo = echo
        self.open()
        self.send('real[] X, Y, Z')
        self.send('real[][] ZZ')
        self.send(self.asy_slurp2)
        self.send(self.asy_slurp3)

        self.count = 0


    def send(self, cmd):
        """Send a command to the Asymptote engine.  A trailing
           semicolon is added automatically."""
        if self.echo:
            print cmd

        self.session.stdin.write(cmd+';\n')
        self.session.stdin.flush()


    def slurp2(self, x, y, **kwargs):
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

        self.send('slurp2("%s")' % (slurp))


    def slurp3(self, x, y, z, **kwargs):
        """Send the *x*, *y*, and *z* ndarrays to the Asymptote engine.

           The slurpped data is stored, in Asymptote, in the 2d ``xy``
           array and the 2d ``z`` array.

           """

        slurp = '.tmp%d.dat' % (self.count)

        f = open(slurp, 'wb')
        f.write(struct.pack("i", x.size))
        f.write(struct.pack("i", y.size))
        x.tofile(f)
        y.tofile(f)
        z.tofile(f)
        f.close()

        self.count = self.count + 1

        self.send('slurp3("%s")' % (slurp))


    def open(self):
        self.session = subprocess.Popen(['asy'],stdin=subprocess.PIPE)


    def close(self):
        self.session.stdin.close();
        self.session.wait()
