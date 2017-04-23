"""
Tests for nvtool
"""
import os
import re

import pexpect
import pytest

from bscr import nvtool
import tbx


# -----------------------------------------------------------------------------
def test_nv_decap_dir(capsys):
    """
    Test nvtool.nv_decap(**{'VAR': PATHISH})
    """
    pytest.debug_func()
    indata, exp = pathish("A, B, C, D"), pathish("B, C, D")
    nvtool.nv_decap(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert indata not in output
    assert exp in output


# -----------------------------------------------------------------------------
def test_nv_decap_pxr(capsys):
    """
    Test pexpect.run('nvtool decap PATHISH')
    """
    pytest.debug_func()
    indata, exp = pathish("A,B,C,D"), pathish("B,C,D")
    output = pexpect.run("nvtool decap {}".format(indata))
    assert indata not in output
    assert exp in output


# -----------------------------------------------------------------------------
def test_nv_decap_show_dir(capsys):
    """
    Test nvtool.nv_decap_show(**{'VAR': PATHISH})
    """
    pytest.debug_func()
    indata, exp = pathish('X:Y:Z:Z:Y'), showish(list("YZZY"), "\n   ")
    nvtool.nv_decap_show(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_decap_show_pxr(capsys):
    """
    Test pexpect.run('nvtool decap --show PATHISH')
    """
    pytest.debug_func()
    indata, exp = pathish("X, Y, Z, Z, Y"), showish(list("YZZY"), "\r\n   ")
    output = pexpect.run("nvtool decap --show X:Y:Z:Z:Y")
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_dedup_dir(capsys):
    """
    Test nvtool.nv_dedup(**{'VAR': PATHISH})
    """
    pytest.debug_func()
    indata, exp = pathish('X,Y,Z,Z,Y'), pathish('X,Y,Z')
    nvtool.nv_dedup(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_dedup_pxr(capsys):
    """
    Test pexpect.run('nvtool dedup PATHISH')
    """
    pytest.debug_func()
    indata, exp = pathish('X:Y:Z:Z:Y'), pathish('X:Y:Z')
    output = pexpect.run("nvtool dedup X:Y:Z:Z:Y")
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_dedup_show_dir(capsys):
    """
    Test nvtool.nv_dedup_show(**{'VAR': PATHISH})
    """
    pytest.debug_func()
    indata, exp = pathish('X:Y:Z:Z:Y'), showish(list("XYZ"), "\n   ")
    nvtool.nv_dedup_show(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_dedup_show_pxr(capsys):
    """
    Test pexpect.run('nvtool dedup --show PATHISH')
    """
    pytest.debug_func()
    indata, exp = pathish("X, Y, Z, Z, Y"), showish(list("XYZ"), "\r\n   ")
    output = pexpect.run("nvtool dedup --show {}".format(indata))
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_deped_dir(capsys):
    """
    Test nvtool.nv_deped(**{'VAR': PATHISH})
    """
    pytest.debug_func()
    indata, exp = pathish('X,Y,Z,Z,Y'), pathish(list('XYZZ'))
    nvtool.nv_deped(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert exp in output
    assert indata not in output

# -----------------------------------------------------------------------------
def test_nv_deped_pxr(capsys):
    """
    Test pexpect.run('nvtool deped PATHISH')
    """
    pytest.debug_func()
    indata, exp = pathish('X:Y:Z:Z:Y'), pathish(list("XYZZ"))
    output = pexpect.run("nvtool deped {}".format(indata))
    assert exp in output
    assert indata not in output

# -----------------------------------------------------------------------------
def test_nv_deped_show_dir(capsys):
    """
    Test nv_deped()
    """
    pytest.debug_func()
    indata, exp = pathish('X:Y:Z:Z:Y'), showish(list("XYZZ"), "\n   ")
    nvtool.nv_deped_show(**{'VAR': indata})
    output, _ = capsys.readouterr()
    assert exp in output
    assert indata not in output

# -----------------------------------------------------------------------------
def test_nv_deped_show_pxr(capsys):
    """
    Test nv_deped()
    """
    pytest.debug_func()
    indata, exp = pathish(list("XYZZY")), showish(list("XYZ"), "\r\n   ")
    output = pexpect.run("nvtool deped --show {}".format(indata))
    assert exp in output
    assert indata not in output


# -----------------------------------------------------------------------------
def test_nv_load_dir(tmpdir, capsys):
    """
    Test nvtool.nv_load(**{'FILE': filename})
    """
    indata = ['foo, $HOME, aardvark']
    exp = ':'.join(indata)
    loadable = tmpdir.join('loadable')
    loadable.write(showish(['foo, $HOME, aardvark'], '\n'))
    nvtool.nv_load(**{'FILE': loadable.strpath})
    output, _ = capsys.readouterr()
    assert exp in output


# -----------------------------------------------------------------------------
def test_nv_load_pxr(tmpdir, capsys):
    """
    Test pexpect.run('nvtool load FILE')
    """
    indata = ['foo, $HOME, aardvark']
    exp = ':'.join(indata)
    loadable = tmpdir.join('loadable')
    loadable.write(showish(['foo, $HOME, aardvark'], '\n'))
    output = pexpect.run("nvtool load {}".format(loadable.strpath))
    assert exp in output


# -----------------------------------------------------------------------------
def test_nv_show(capsys):
    """
    Test nv_show
    """
    nvtool_trial(nvtool.nv_show,
                 capsys,
                 ['PATH'],
                 ['\n   ' + _ for _ in os.getenv('PATH').split(':')])

# -----------------------------------------------------------------------------
def test_nv_remove_join(capsys):
    """
    Test nv_remove
    """
    pytest.debug_func()
    testin = 'beautiful:explicit:simple:complex:sparse'
    c_exp = 'beautiful:explicit:complex:sparse'
    s_exp = ['   \n' + _ for _ in c_exp.split(':')]
    nvtool_trial(nvtool.nv_remove, capsys, ['impl', testin], c_exp)

# -----------------------------------------------------------------------------
def test_nv_remove_show(capsys):
    """
    Test nv_remove
    """
    pytest.debug_func()
    testin = 'beautiful:explicit:simple:complex:sparse'
    c_exp = 'beautiful:explicit:complex:sparse'
    s_exp = ['   \n' + _ for _ in c_exp.split(':')]
    nvtool_trial(nvtool.nv_remove, capsys, ['-s', 'impl', testin], s_exp)

# -----------------------------------------------------------------------------
def test_nv_help(capsys):
    """
    Verify that util.dispatch warns that it's deprecated when nvtool runs
    """
    pytest.debug_func()
    cmdlist = "help decap dedup deped load remove show".split()
    result = pexpect.run("nvtool help")
    assert "nvtool examples:" in result
    for _ in cmdlist:
        assert _ in result

    for _ in cmdlist:
        result = pexpect.run("nvtool help {}".format(_))
        assert "Traceback" not in result
        assert _ in result


# -----------------------------------------------------------------------------
def showish(seq, sep):
    """
    """
    if isinstance(seq, str):
        rval = sep.join([_.strip() for _ in re.split("[,:]", seq)])
    elif isinstance(seq, list):
        rval = sep.join(seq)
    else:
        rval = None
    return rval
    
# -----------------------------------------------------------------------------
def pathish(seq):
    """
    Given a comma- or colon-separated list in string *seq*, compose and return
    a string containing a colon-separated list with whitespace squeezed out.

    Given a list in *seq*, compose and return a string containing a
    colon-separated list of the elements.
    """
    if isinstance(seq, str):
        rval = ":".join([_.strip() for _ in re.split("[,:]", seq)])
    elif isinstance(seq, list):
        rval = ":".join(seq)
    else:
        rval = None
    return rval

# -----------------------------------------------------------------------------
def nvtool_trial(function, capsys, testin, expected):
    """
    Run an nvtool function on an input and verify the result
    """
    pytest.fail('obs')
    function(testin)
    stdo, _ = capsys.readouterr()
    if isinstance(expected, str):
        assert expected in stdo
    elif isinstance(expected, list):
        for item in expected:
            assert item in expected
