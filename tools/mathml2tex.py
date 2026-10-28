"""Convert MathML (as used in OpenStax CNXML) to LaTeX for MathJax or KaTeX."""

M = "{http://www.w3.org/1998/Math/MathML}"

GREEK = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta", "ε": r"\varepsilon",
    "ϵ": r"\epsilon", "ζ": r"\zeta", "η": r"\eta", "θ": r"\theta", "ι": r"\iota",
    "κ": r"\kappa", "λ": r"\lambda", "μ": r"\mu", "ν": r"\nu", "ξ": r"\xi", "π": r"\pi",
    "ρ": r"\rho", "σ": r"\sigma", "τ": r"\tau", "υ": r"\upsilon", "φ": r"\phi",
    "ϕ": r"\phi", "χ": r"\chi", "ψ": r"\psi", "ω": r"\omega", "Γ": r"\Gamma",
    "Δ": r"\Delta", "Θ": r"\Theta", "Λ": r"\Lambda", "Π": r"\Pi", "Σ": r"\Sigma",
    "Φ": r"\Phi", "Ψ": r"\Psi", "Ω": r"\Omega", "∞": r"\infty", "°": r"^{\circ}",
}

OPS = {
    "−": "-", "–": "-", "—": "-", "×": r"\times", "·": r"\cdot", "⋅": r"\cdot",
    "∑": r"\sum", "∫": r"\int", "≈": r"\approx", "≤": r"\le", "≥": r"\ge",
    "≠": r"\ne", "→": r"\to", "±": r"\pm", "∓": r"\mp", "{": r"\{", "}": r"\}",
    "%": r"\%", "∝": r"\propto", "′": "'", "″": "''", "∂": r"\partial",
    "⇒": r"\Rightarrow", "≡": r"\equiv", "∼": r"\sim", "~": r"\sim", "÷": r"\div",
    "∘": r"\circ", "⊥": r"\perp", "∥": r"\parallel", "…": r"\ldots", "⋯": r"\cdots",
    "⁄": "/", "⁡": "", "⁢": "", "⁣": "", " ": " ",
}

FUNCS = {"sin", "cos", "tan", "sec", "csc", "cot", "log", "ln", "exp", "lim", "max", "min"}


def _esc_text(s):
    out = []
    for ch in s:
        if ch in "\\":
            out.append(r"\backslash ")
        elif ch in "%&#_$":
            out.append("\\" + ch)
        elif ch == "{":
            out.append(r"\{")
        elif ch == "}":
            out.append(r"\}")
        elif ch in "−–":
            out.append("-")
        elif ch == " ":
            out.append(" ")
        else:
            out.append(ch)
    return "".join(out)


def _sym(s):
    """Map a run of characters to math mode symbols."""
    out = []
    for ch in s:
        if ch in GREEK:
            out.append(GREEK[ch] + " ")
        elif ch in OPS:
            out.append(OPS[ch] + (" " if OPS[ch].startswith("\\") else ""))
        else:
            out.append(ch)
    return "".join(out)


def _tag(el):
    return el.tag.replace(M, "") if isinstance(el.tag, str) else ""


def _kids(el):
    return [c for c in el if isinstance(c.tag, str)]


def _text(el):
    return "".join(el.itertext())


def _grp(s):
    s = s.strip()
    return "{" + s + "}"


def conv(el):
    t = _tag(el)
    k = _kids(el)
    if t in ("math", "mrow", "semantics", "mpadded", "menclose", "mstyle", "merror"):
        if t == "semantics":
            k = k[:1]
        inner = _row(k)
        if t == "mstyle":
            mv = el.get("mathvariant")
            if mv == "bold":
                return r"\mathbf{" + inner + "}"
        return inner
    if t == "mi":
        s = _text(el).strip()
        if not s:
            return ""
        if s in FUNCS:
            return "\\" + s + " "
        if len(s) == 1 and s not in GREEK:
            if el.get("mathvariant") == "bold":
                return r"\mathbf{" + s + "}"
            if el.get("mathvariant") == "normal":
                return r"\mathrm{" + s + "}"
            return s
        if all(c in GREEK for c in s):
            return _sym(s)
        return r"\mathrm{" + _esc_text(s) + "}"
    if t == "mn":
        s = _text(el).replace(" ", " ").strip()
        s2 = s.replace("−", "-").replace("–", "-")
        if all(c in "0123456789.,- " for c in s2):
            return s2.replace(" ", r"\,")
        # numbers glued to units, e.g. "40.0 s" or "10.0 m/s."
        num = ""
        i = 0
        while i < len(s2) and s2[i] in "0123456789.,-":
            num += s2[i]
            i += 1
        rest = s2[i:]
        return num + (r"\text{" + _esc_text(rest) + "}" if rest else "")
    if t == "mo":
        s = _text(el).strip()
        if s in ("(", ")", "[", "]", "|", "=", "+", ",", ".", ":", ";", "!", "?", "<", ">", "/"):
            return {"<": r"\lt ", ">": r"\gt "}.get(s, s)
        if s in FUNCS:
            return "\\" + s + " "
        return _sym(s)
    if t == "mtext":
        s = _text(el)
        if not s.strip():
            return r"\ " if s else ""
        stripped = s.strip()
        if all(c in GREEK for c in stripped):
            return _sym(stripped)
        if stripped in FUNCS:
            return "\\" + stripped + " "
        if stripped in OPS or stripped in ("–", "−"):
            return _sym(stripped)
        return r"\text{" + _esc_text(s) + "}"
    if t == "mspace":
        w = el.get("width", "0.2em")
        try:
            val = float(w.replace("em", ""))
        except ValueError:
            val = 0.2
        return r"\quad " if val >= 0.8 else (r"\; " if val >= 0.4 else r"\, ")
    if t in ("msub", "msup") and len(k) >= 2:
        op = "_" if t == "msub" else "^"
        return _grp(conv(k[0])) + op + _grp(conv(k[1]))
    if t == "msubsup" and len(k) >= 3:
        return _grp(conv(k[0])) + "_" + _grp(conv(k[1])) + "^" + _grp(conv(k[2]))
    if t == "mfrac" and len(k) >= 2:
        if el.get("linethickness") in ("0", "0px", "0pt"):
            return r"\genfrac{}{}{0pt}{}" + _grp(conv(k[0])) + _grp(conv(k[1]))
        return r"\frac" + _grp(conv(k[0])) + _grp(conv(k[1]))
    if t == "msqrt":
        return r"\sqrt{" + _row(k) + "}"
    if t == "mroot" and len(k) >= 2:
        return r"\sqrt[" + conv(k[1]) + "]{" + conv(k[0]) + "}"
    if t == "mover" and len(k) >= 2:
        base = conv(k[0])
        over = _text(k[1]).strip()
        if over in ("→", "⇀", "⃗"):
            return r"\vec{" + base + "}"
        if over in ("^", "ˆ", "̂"):
            return r"\hat{" + base + "}"
        if over in ("–", "¯", "‾", "_", "-", "−", "―", "̅"):
            return r"\bar{" + base + "}"
        if over in (".", "˙", "·"):
            return r"\dot{" + base + "}"
        if over in ("¨", ".."):
            return r"\ddot{" + base + "}"
        if over in ("~", "˜"):
            return r"\tilde{" + base + "}"
        return r"\overset{" + conv(k[1]) + "}{" + base + "}"
    if t == "munder" and len(k) >= 2:
        base = conv(k[0])
        if _text(k[0]).strip() in ("∑", "∫", "lim", "∏"):
            return base + "_{" + conv(k[1]) + "}"
        return r"\underset{" + conv(k[1]) + "}{" + base + "}"
    if t == "munderover" and len(k) >= 3:
        return _grp(conv(k[0])) + "_" + _grp(conv(k[1])) + "^" + _grp(conv(k[2]))
    if t == "mfenced":
        o = el.get("open", "(")
        c = el.get("close", ")")
        sep = el.get("separators", ",")
        parts = [conv(x) for x in k]
        o = {"{": r"\{", "": "."}.get(o, o)
        c = {"}": r"\}", "": "."}.get(c, c)
        return r"\left" + o + " " + (sep[:1] if sep else "").join(parts) + r" \right" + c
    if t == "mtable":
        rows = []
        for tr in k:
            cells = [conv(td) for td in _kids(tr)]
            rows.append(" & ".join(cells))
        ncol = max((len(_kids(tr)) for tr in k), default=1)
        return r"\begin{array}{" + "l" * max(ncol, 1) + "}" + r" \\ ".join(rows) + r"\end{array}"
    if t in ("mtr", "mtd", "mlabeledtr"):
        return _row(k)
    if t == "mphantom":
        return r"\phantom{" + _row(k) + "}"
    if t in ("annotation", "annotation-xml", "maligngroup", "malignmark", "none", "mprescripts"):
        return ""
    return _row(k)


def _row(kids):
    # brace + table pattern -> cases
    if len(kids) == 2 and _tag(kids[0]) == "mo" and _text(kids[0]).strip() == "{":
        tables = [x for x in kids[1].iter() if _tag(x) == "mtable"]
        if tables:
            rows = [" & ".join(conv(td) for td in _kids(tr)) for tr in _kids(tables[0])]
            return r"\begin{cases}" + r" \\ ".join(rows) + r"\end{cases}"
    parts = [conv(x) for x in kids]
    out = ""
    for p in parts:
        # keep commands like \Delta from gluing onto the next letter
        if out and out[-1].isalpha() and p[:1].isalpha():
            m = out.rstrip()
            j = len(m) - 1
            while j >= 0 and m[j].isalpha():
                j -= 1
            if j >= 0 and m[j] == "\\":
                out += " "
        out += p
    return out


def to_tex(math_el):
    s = conv(math_el)
    s = " ".join(s.split())
    return s
