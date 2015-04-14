import pytest
import tempfile
import os
import shutil
import subprocess as sp

from copy import copy
from selenium import webdriver

from .. import run_command

@pytest.fixture(scope="module")
def tempdir(request):
    tempdir = tempfile.mkdtemp()
    origdir = os.getcwd()
    os.chdir(tempdir)

    def fin():
        os.chdir(origdir)
        shutil.rmtree(tempdir)
    request.addfinalizer(fin)

    return tempdir


@pytest.fixture(scope="module")
def ipythondir(request):
    ipythondir = tempfile.mkdtemp()

    # ensure IPython dir exists.
    sp.call(['ipython', 'profile', 'create', '--ipython-dir', ipythondir])

    def fin():
        shutil.rmtree(ipythondir)
    request.addfinalizer(fin)

    return ipythondir


@pytest.fixture(scope="module")
def nbserver(request, tempdir, ipythondir):
    run_command(
        "python -m nbgrader --install --activate "
        "--ipython-dir={} --nbextensions={}".format(
            ipythondir, os.path.join(ipythondir, "nbextensions")))

    # bug in IPython cannot use --profile-dir
    # that does not set it for everything.
    # still this does not allow to have things that work.
    env = copy(os.environ)
    env['IPYTHONDIR'] = ipythondir

    nbserver = sp.Popen([
        "ipython", "notebook",
        "--no-browser",
        "--port", "9000"], stdout=sp.PIPE, stderr=sp.STDOUT, env=env)

    def fin():
        nbserver.kill()
    request.addfinalizer(fin)

    return nbserver


@pytest.fixture
def browser(request, tempdir, nbserver):
    shutil.copy(os.path.join(os.path.dirname(__file__), "files", "blank.ipynb"), os.path.join(tempdir, "blank.ipynb"))
    browser = webdriver.PhantomJS()
    browser.get("http://localhost:9000/notebooks/blank.ipynb")

    def fin():
        browser.quit()
    request.addfinalizer(fin)

    return browser

