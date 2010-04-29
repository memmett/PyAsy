"""PyAsy setup script."""

import glob
import os
import re

import setuptools

######################################################################
# version
execfile('version.py')                  # this sets 'version'


######################################################################
# save git version to 'pyasy/__git_version__.py'

try:
    git_head_file = os.path.join(os.path.dirname(__file__), '.git', 'HEAD')
    f = open(git_head_file)
    m = re.match(r'ref: (.+)', f.readline())
    ref = m.group(1)
    f.close()

    git_head_file = os.path.join(os.path.dirname(__file__), '.git', ref)
    f = open(git_head_file)
    git_version = f.readline().rstrip()
    f.close()

except:
    git_version = 'not_available'

git_version_file = os.path.join(os.path.dirname(__file__),
                                'pyasy','__git_version__.py')
f = open(git_version_file, 'w')
f.write("version = '%s'\n" % (git_version))
f.close()


######################################################################
# save version to 'pyasy/__version__.py'

version_file = os.path.join(os.path.dirname(__file__),
                            'pyasy','__version__.py')
f = open(version_file, 'w')
f.write("version = '%s'\n" % (version))
f.close()


######################################################################
# setup!

setuptools.setup(

    name = "PyAsy",
    version = version,
    packages = ['pyasy'],
    zip_safe = False,

#    test_suite = 'nose.collector',
#    install_requires = [ "numpy >= 1.0.3", "scipy >= 0.7.0" ], # , "sympy >= 0.6.0" ],

    package_data = {'': ['__version__.py', '__git_version__.py']},
    exclude_package_data = {'': ['.gitignore']},

    author = "Matthew Emmett",
    author_email = "matthew.emmett@ualberta.ca",
    description = "PyAsy is a Python wrapper of the Asymptote vector graphics language.",
    license = "BSD",
    keywords = "vector, graphics, asymptote",
    url = "http://github.com/memmett/PyAsy"

    )
