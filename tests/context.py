import os
import sys
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__),
                                '../lolat')))
# Yes flake8 warns about this import lolat stuff in the tests
# but it's already cost too much time just trying to get it to work :-(
# noqa
import lolat
