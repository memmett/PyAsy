"""PyAsy Asymptote class."""

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
                  they are sent to the Asymptote engine (useful for
                  debugging).

       """

    asy_slurp = """real[][] slurp(string filename) {
                     file dat = binput(filename);

                     int N = dat;

                     real[][] xq = new real[N][N];
                     xq[0][:] = dimension(dat, N);
                     xq[1][:] = dimension(dat, N);

                     close(dat);

                     return xq;
                   }"""


    def __init__(self, echo=False, **kwargs):
        self.echo = echo
        self.open()
        self.send(self.asy_slurp)


    def send(self, cmd):
        """Send a command to the Asymptote engine."""
        if self.echo:
            print cmd

        self.session.stdin.write(cmd+';\n')
        self.session.stdin.flush()


    def slurp(self, slurp):
        """Instruct Asymptote to read the data stored in the
           (temporary) file *slurp*.

           The slurpped data is stored, in Asymptote, in the 2d ``xq``
           array.

           """

        self.send('real[][] xq')
        self.send('xq = slurp("%s")' % (slurp))


    def open(self):
        self.session = subprocess.Popen(['asy'],stdin=subprocess.PIPE)


    def close(self):
        self.session.stdin.close();
        self.session.wait()
