#! /usr/bin/env python

import sys, os, subprocess

scripts_dir = os.path.dirname(__file__)
package_dir = os.path.join(scripts_dir, '..', 'calabar')
os.chdir(package_dir)

try:
    import nose
except ImportError:
    print 'nose is required to run the calabar test suite'
    sys.exit(1)

try:
    import calabar
except ImportError:
    print "Can't find calabar to test: %s" % sys.exc_info()[1]
    sys.exit(1)
else:
    print "Calabar %s test suite running (Python %s)..." % (
        calabar.__version__, sys.version.split()[0])

covered_modules = ['calabar']
coverage_opts = ['--with-coverage', '--cover-erase']
for m in covered_modules:
    coverage_opts.append('--cover-package %s' % m)

excluded_tests = []
exclusion_opts = []
for t in excluded_tests:
    exclusion_opts.append('--exclude %s' % t)

opts = ['-v', '--with-id', '--with-xunit']

nose_cmd = ['nosetests']

if '--coverage' in sys.argv:
    sys.argv.remove('--coverage')
else:
    coverage_opts = []

if '--failed' in sys.argv:
    sys.argv.remove('--failed')
    opts.insert(1, '--failed')

# If the user didn't specify any modules on the command line, run the default
# modules.
user_args = sys.argv[1:]
cmd = nose_cmd + opts + coverage_opts + user_args
if len([a for a in user_args if not a.startswith('-')]) == 0:
    cmd += exclusion_opts + ['calabar']

cmd_string = ' '.join(cmd)
print "Running: [%s]" % cmd_string
subprocess.call(cmd_string, shell=True)
