"""
Examples:
    odx(25)         => 25 -> 031 / 25 / 0x19
    odx(0124)       => 0124 -> 0124 / 84 / 0x54
    odx(0x1f1f)     => 0x1f1f -> 017437 / 7967 / 0x1f1f
    odx(2ab)        => ValueError
    odx(0987)       => ValueError
    odx(0x5234g7)   => ValueError
"""
from bscr import odx
import pexpect
import pytest


# -----------------------------------------------------------------------------
def test_decimal_good():
    """
    Verify output of odx with good decimal input
    """
    exp = "25 -> 031 / 25 / 0x19"
    assert exp == odx.odx('25')


# -----------------------------------------------------------------------------
def test_decimal_bad():
    """
    Verify output of odx with bad decimal input
    """
    exp = "invalid literal for int() with base 10"
    with pytest.raises(ValueError) as err:
        odx.odx("2ab")
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_octal_good():
    """
    Verify output of odx with good octal input
    """
    exp = "0124 -> 0124 / 84 / 0x54"
    assert exp == odx.odx('0124')


# -----------------------------------------------------------------------------
def test_octal_bad():
    """
    Verify output of odx with bad octal input
    """
    exp = "invalid literal for int() with base 8"
    with pytest.raises(ValueError) as err:
        odx.odx("0987")
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_hex_good():
    """
    Verify output of odx with good hex input
    """
    exp = "0x1f1f -> 017437 / 7967 / 0x1f1f"
    assert exp == odx.odx("0x1f1f")


# -----------------------------------------------------------------------------
def test_hex_bad():
    """
    Verify output of odx with bad hex input
    """
    exp = "invalid literal for int() with base 16"
    with pytest.raises(ValueError) as err:
        odx.odx("0x5234g7")
    assert exp in str(err)


# -----------------------------------------------------------------------------
def test_odx_help():
    """
    Verify that 'odx --help' does the right thing
    """
    txt = ["Usage: odx {0<octal-value>|<decimal-value>|0x<hex-value>} ...",
           "",
           "    report each argument in octal, decimal, and hex format",
           "",
           "Options:",
           "  -h, --help   show this help message and exit",
           "  -d, --debug  run under debugger",
           ]
    exp = "\r\n".join(txt) + "\r\n"
    actual = pexpect.run("odx --help")
    assert exp == actual
