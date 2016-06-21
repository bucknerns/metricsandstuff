import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# Establish a consistent base directory relative to the setup.py file
os.chdir(os.path.abspath(os.path.dirname(__file__)))


# tox integration
class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

setup(
    name='myapp',
    version='0.0.1',
    description='Metrics api',
    long_description='{0}'.format(open('README.rst').read()),
    author='Nathan Buckner',
    install_requires=[
        "falcon", "redis", "pytz", "python-dateutil", "requests"],
    packages=find_packages(exclude=('doc')),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    tests_require=['tox'],
    cmdclass={'test': Tox})
