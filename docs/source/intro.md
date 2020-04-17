[![Build Status](https://travis-ci.com/belerico/py_asciimath.svg?branch=master)](https://travis-ci.com/belerico/py_asciimath) [![Coverage Status](https://coveralls.io/repos/github/belerico/py_asciimath/badge.svg?branch=master)](https://coveralls.io/github/belerico/py_asciimath?branch=master) [![PyPI](https://img.shields.io/pypi/v/py_asciimath?color=light%20green)](https://pypi.org/project/py-asciimath/0.2.2/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py_asciimath)](https://www.python.org/)

py_asciimath is a simple yet powerful Python module that:

* converts an ASCIIMath string to LaTeX or MathML
* converts a MathML string to LaTeX (the conversion is done thank to the [XSLT MathML Library](https://sourceforge.net/projects/xsltml/). Please report any unexpected behavior)
* exposes a single translation method `translate(exp, **kwargs)`, which semantic depends on the py_asciimath translator one wish to use. See the :py:mod:`py_asciimath.translator.translator` module or the :ref:`examples` for more info
* exposes a MathML parser. See :py:class:`py_asciimath.parser.parser.MathMLParser`