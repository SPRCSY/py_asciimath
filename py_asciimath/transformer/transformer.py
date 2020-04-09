from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
import re
from functools import wraps

# from future import standard_library
from lark import Transformer

from ..translation.latex import binary_functions as latex_bin
from ..translation.latex import left_parenthesis as latex_left
from ..translation.latex import right_parenthesis as latex_right
from ..translation.latex import smb as latex_smb
from ..translation.latex import unary_functions as latex_una
from ..translation.mathml import binary_functions as mathml_bin
from ..translation.mathml import left_parenthesis as mathml_left
from ..translation.mathml import right_parenthesis as mathml_right
from ..translation.mathml import colors
from ..translation.mathml import smb as mathml_smb
from ..translation.mathml import unary_functions as mathml_una
from ..utils.log import Log
from ..utils.utils import UtilsMat, concat

# standard_library.install_aliases()
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)


# TODO: MathematicaTransformer
""" class MathematicaTransformer(Transformer):
    def __init__(self):
        pass """


class ASCIIMathTransformer(Transformer):  # pragma: no cover
    def __init__(
        self, log=True, start_end_par_pattern="{}{}", visit_tokens=False
    ):
        Transformer.__init__(self, visit_tokens=visit_tokens)
        formatted_left_parenthesis = "|".join(
            ["\\(", "\\(:", "\\[", "\\{", "\\{:"]
        )
        formatted_right_parenthesis = "|".join(
            ["\\)", ":\\)", "\\]", "\\}", ":\\}"]
        )
        self.start_end_par_pattern = re.compile(
            start_end_par_pattern.format(
                formatted_left_parenthesis, formatted_right_parenthesis,
            )
        )
        self._logger_func = logging.info
        if not log:
            self._logger_func = lambda x: x
        self._logger = Log(logger_func=self._logger_func)

    def remove_parenthesis(self, s):
        return re.sub(self.start_end_par_pattern, r"\2", s)

    @classmethod
    def log(cls, f):
        @wraps(f)
        def decorator(*args, **kwargs):
            self = args[0]
            return self._logger.__call__(f)(*args, **kwargs)

        return decorator

    def exp(self, items):
        raise NotImplementedError

    def exp_interm(self, items):
        raise NotImplementedError

    def exp_frac(self, items):
        raise NotImplementedError

    def exp_under(self, items):
        raise NotImplementedError

    def exp_super(self, items):
        raise NotImplementedError

    def exp_under_super(self, items):
        raise NotImplementedError

    def exp_par(self, items):
        raise NotImplementedError

    def exp_unary(self, items):
        raise NotImplementedError

    def exp_binary(self, items):
        raise NotImplementedError

    def symbol(self, items):
        raise NotImplementedError

    def const(self, items):
        raise NotImplementedError

    def q_str(self, items):
        raise NotImplementedError


class LatexTransformer(ASCIIMathTransformer):  # pragma: no cover
    """Trasformer class, read `lark.Transformer`."""

    def __init__(self, log=True, visit_tokens=False):
        ASCIIMathTransformer.__init__(
            self,
            log,
            r"^(?:\\left(?:(?:\\)?({})))(.*?)(?:\\right(?:(?:\\)?({})))$",
            visit_tokens,
        )

    @ASCIIMathTransformer.log
    def remove_parenthesis(self, s):
        return ASCIIMathTransformer.remove_parenthesis(self, s)

    @ASCIIMathTransformer.log
    def exp(self, items):
        return " ".join(items)

    @ASCIIMathTransformer.log
    def exp_interm(self, items):
        return items[0]

    @ASCIIMathTransformer.log
    def exp_frac(self, items):
        items[0] = self.remove_parenthesis(items[0])
        items[1] = self.remove_parenthesis(items[1])
        return "\\frac{" + items[0] + "}{" + items[1] + "}"

    @ASCIIMathTransformer.log
    def exp_under(self, items):
        items[1] = self.remove_parenthesis(items[1])
        return items[0] + "_{" + items[1] + "}"

    @ASCIIMathTransformer.log
    def exp_super(self, items):
        items[1] = self.remove_parenthesis(items[1])
        return items[0] + "^{" + items[1] + "}"

    @ASCIIMathTransformer.log
    def exp_under_super(self, items):
        items[1] = self.remove_parenthesis(items[1])
        items[2] = self.remove_parenthesis(items[2])
        return items[0] + "_{" + items[1] + "}^{" + items[2] + "}"

    @ASCIIMathTransformer.log
    def exp_par(self, items):
        yeah_mat = False
        s = ", ".join(items[1:-1])
        if s.startswith("\\left"):
            yeah_mat, row_par = UtilsMat.check_mat(s)
            if yeah_mat:
                s = UtilsMat.get_latex_mat(s, row_par)
        lpar = latex_left[concat(items[0])]
        rpar = latex_right[concat(items[-1])]
        if lpar == "\\langle":
            left = "\\left" + lpar + " "
        elif lpar == "{:":
            left = "\\left."
        else:
            left = "\\left" + lpar
        if rpar == "\\rangle":
            right = " \\right" + rpar
        elif rpar == ":}":
            right = "\\right."
        else:
            right = "\\right" + rpar
        return (
            left
            + ("\\begin{matrix}" + s + "\\end{matrix}" if yeah_mat else s)
            + right
        )

    @ASCIIMathTransformer.log
    def exp_unary(self, items):
        unary = latex_una[concat(items[0])]
        items[1] = self.remove_parenthesis(items[1])
        if unary == "norm":
            return "\\left\\lVert " + items[1] + " \\right\\rVert"
        elif unary == "abs":
            return "\\left\\mid " + items[1] + " \\right\\mid"
        elif unary == "floor":
            return "\\left\\lfloor " + items[1] + " \\right\\rfloor"
        elif unary == "ceil":
            return "\\left\\lceil " + items[1] + " \\right\\rceil"
        else:
            return unary + "{" + items[1] + "}"

    @ASCIIMathTransformer.log
    def exp_binary(self, items):
        binary = latex_bin[concat(items[0])]
        items[1] = self.remove_parenthesis(items[1])
        items[2] = self.remove_parenthesis(items[2])
        if binary == "\\sqrt":
            return binary + "[" + items[1] + "]" + "{" + items[2] + "}"
        else:
            return binary + "{" + items[1] + "}" + "{" + items[2] + "}"

    @ASCIIMathTransformer.log
    def symbol(self, items):
        return latex_smb[concat(items[0])]

    @ASCIIMathTransformer.log
    def const(self, items):
        return items[0].value

    @ASCIIMathTransformer.log
    def q_str(self, items):
        return "\\text{" + items[0] + "}"


class MathMLTransformer(ASCIIMathTransformer):
    """Trasformer class, read `lark.Transformer`."""

    def __init__(self, log=True, visit_tokens=False):
        ASCIIMathTransformer.__init__(
            self,
            log,
            r"^(?:<mo>(?:({}))</mo>)(.*?)(?:<mo>(?:({}))</mo>)$",
            visit_tokens,
        )

    def encapsulate_mrow(self, s):
        return "<mrow>" + s + "</mrow>"

    @ASCIIMathTransformer.log
    def remove_parenthesis(self, s):
        return ASCIIMathTransformer.remove_parenthesis(self, s)

    @ASCIIMathTransformer.log
    def exp(self, items):
        return "".join(items)

    @ASCIIMathTransformer.log
    def exp_interm(self, items):
        return items[0]

    @ASCIIMathTransformer.log
    def exp_frac(self, items):
        items[0] = self.remove_parenthesis(items[0])
        items[1] = self.remove_parenthesis(items[1])
        return self.encapsulate_mrow(
            "<mfrac>"
            + self.encapsulate_mrow(items[0])
            + self.encapsulate_mrow(items[1])
            + "</mfrac>"
        )

    @ASCIIMathTransformer.log
    def exp_under(self, items):
        items[1] = self.remove_parenthesis(items[1])
        return self.encapsulate_mrow(
            "<munder>"
            + self.encapsulate_mrow(items[0])
            + self.encapsulate_mrow(items[1])
            + "</munder>"
        )

    @ASCIIMathTransformer.log
    def exp_super(self, items):
        items[1] = self.remove_parenthesis(items[1])
        return self.encapsulate_mrow(
            "<msup>"
            + self.encapsulate_mrow(items[0])
            + self.encapsulate_mrow(items[1])
            + "</msup>"
        )

    @ASCIIMathTransformer.log
    def exp_under_super(self, items):
        items[1] = self.remove_parenthesis(items[1])
        items[2] = self.remove_parenthesis(items[2])
        return self.encapsulate_mrow(
            "<msubsup>"
            + self.encapsulate_mrow(items[0])
            + self.encapsulate_mrow(items[1])
            + self.encapsulate_mrow(items[2])
            + "</msubsup>"
        )

    @ASCIIMathTransformer.log
    def exp_par(self, items):
        yeah_mat = False
        s = ", ".join(items[1:-1])
        if re.match(r"^<mo>(\[|\(|\{|\{:|\|:|\|\|:|<<|\(:|langle)</mo>", s):
            yeah_mat, row_par = UtilsMat.check_mat(s)
            if yeah_mat:
                s = (
                    "<mtable>"
                    + UtilsMat.get_mathml_mat(s, row_par)
                    + "</mtable>"
                )
        lpar = mathml_left[concat(items[0])]
        rpar = mathml_right[concat(items[-1])]
        return "<mo>" + lpar + "</mo>" + s + "<mo>" + rpar + "</mo>"

    @ASCIIMathTransformer.log
    def exp_unary(self, items):
        unary = mathml_una[concat(items[0])]
        items[1] = self.remove_parenthesis(items[1])
        return self.encapsulate_mrow(
            unary.format(self.encapsulate_mrow(items[1]))
        )

    @ASCIIMathTransformer.log
    def exp_binary(self, items):
        binary = mathml_bin[concat(items[0])]
        items[1] = self.remove_parenthesis(items[1])
        items[2] = self.remove_parenthesis(items[2])
        if concat(items[1]) in colors:
            s = binary.format(items[1], self.encapsulate_mrow(items[2]))
        elif items[0] != "root":
            s = binary.format(
                self.encapsulate_mrow(items[1]),
                self.encapsulate_mrow(items[2]),
            )
        else:
            s = binary.format(
                self.encapsulate_mrow(items[2]),
                self.encapsulate_mrow(items[1]),
            )
        return self.encapsulate_mrow(s)

    @ASCIIMathTransformer.log
    def symbol(self, items):
        if concat(items[0]) in colors:
            return mathml_smb[concat(items[0])]
        else:
            return "<mo>" + mathml_smb[concat(items[0])] + "</mo>"

    @ASCIIMathTransformer.log
    def const(self, items):
        if items[0].isnumeric():
            return "<mn>" + items[0].value + "</mn>"
        else:
            return "<mi>" + items[0].value + "</mi>"

    @ASCIIMathTransformer.log
    def q_str(self, items):
        return "<mtext>" + items[0] + "</mtext>"
