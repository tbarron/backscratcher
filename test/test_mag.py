from bscr import mag
import docopt
import pytest


# -----------------------------------------------------------------------------
def test_mag_docopt(fx_usage):
    """
    Check that mag.__doc__ contains what docopt requires
    """
    pytest.debug_func()
    for strval in fx_usage:
        assert any([strval in line for line in mag.__doc__.split("\n")])


# -----------------------------------------------------------------------------
def test_bit(fx_mchk):
    """
    Test 'mag' for bits (1000^0)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "999", "999.00 b"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_bbit(fx_mchk):
    """
    Test 'mag' for bits (1024^0)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "999", "999.00 b"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_kilo(fx_mchk):
    """
    Test 'mag' for bits (1000^0)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "98765", "98.77 Kb"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -------------------------------------------------------------------------
def test_bkilo(fx_mchk):
    """
    Test 'mag' for kibibits (1024^1)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "98765", "96.45 Kib"
    fx_mchk.result = mag.main(["-b", fx_mchk.inp], True)


# -------------------------------------------------------------------------
def test_mega(fx_mchk):
    """
    Test 'mag' for megabits (1000^2)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "98765432", "98.77 Mb"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -------------------------------------------------------------------------
def test_bmega(fx_mchk):
    """
    Test 'mag' for mebibits (1024^2)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "98765432", "94.19 Mib"
    fx_mchk.result = mag.main(["-b", fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_giga(fx_mchk):
    """
    Test 'mag' for megabits (1000^3)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "12398765432", "12.40 Gb"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_bgiga(fx_mchk):
    """
    Test 'mag' for gibibits (1024^3)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "12398765432", "11.55 Gib"
    fx_mchk.result = mag.main(["-b", fx_mchk.inp], True)


# -------------------------------------------------------------------------
def test_tera(fx_mchk):
    """
    Test 'mag' for terabits (1000^4)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "12390008765432", "12.39 Tb"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_btera(fx_mchk):
    """
    Test 'mag' for tibibits (1024^4)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "12390008765432", "11.27 Tib"
    fx_mchk.result = mag.main(["-b", fx_mchk.inp], True)


# -------------------------------------------------------------------------
def test_peta(fx_mchk):
    """
    Test 'mag' for terabits (1000^5)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "17239090087685432", "17.24 Pb"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_bpeta(fx_mchk):
    """
    Test 'mag' for tibibits (1024^5)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "71233986700065432", "63.27 Pib"
    fx_mchk.result = mag.main(["-b", fx_mchk.inp], True)


# -------------------------------------------------------------------------
def test_exa(fx_mchk):
    """
    Test 'mag' for terabits (1000^6)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "41873239090087685432", "41.87 Eb"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_bexa(fx_mchk):
    """
    Test 'mag' for tibibits (1024^6)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "87271233986700065432", "75.70 Eib"
    fx_mchk.result = mag.main(["-b", fx_mchk.inp], True)


# -------------------------------------------------------------------------
def test_zetta(fx_mchk):
    """
    Test 'mag' for terabits (1000^7)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "43541873239090087685432", "43.54 Zb"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_bzetta(fx_mchk):
    """
    Test 'mag' for tibibits (1024^7)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "23487271233986700065432", "19.89 Zib"
    fx_mchk.result = mag.main(["-b", fx_mchk.inp], True)


# -------------------------------------------------------------------------
def test_yotta(fx_mchk):
    """
    Test 'mag' for terabits (1000^8)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "75843541873239090087685432", "75.84 Yb"
    fx_mchk.result = mag.main([fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_byotta(fx_mchk):
    """
    Test 'mag' for tibibits (1024^8)
    """
    pytest.debug_func()
    fx_mchk.inp, fx_mchk.exp = "39423487271233986700065432", "32.61 Yib"
    fx_mchk.result = mag.main(["-b", fx_mchk.inp], True)


# -----------------------------------------------------------------------------
def test_usage(fx_usage):
    """
    'mag' with no args should get the usage message
    """
    pytest.debug_func()
    with pytest.raises(docopt.DocoptExit) as err:
        a = mag.main([])                              # noqa: ignore=F841
    assert "\n".join(fx_usage) == str(err.value)


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_mchk():
    """
    Check the result of mag tests
    """
    fx_mchk.inp = fx_mchk.exp = fx_mchk.result = None
    yield fx_mchk
    assert fx_mchk.exp in fx_mchk.result
    expstr = "{} = {}".format(fx_mchk.inp, fx_mchk.exp)
    assert expstr in fx_mchk.result


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_usage():
    """
    Set up expected help/usage data for tests
    """
    rval = ["Usage:",
            "    mag [-d] [-b] NUMBER",
            ]
    return rval
