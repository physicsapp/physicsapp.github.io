"""Extract one chapter of OpenStax University Physics (CNXML source) into app JSON.

Usage: python3 -I extract.py <book_bundle_dir> <out_json> <first_module> <last_module> <chapter_number> <chapter_title> [--with-problems]

The JSON holds, per section: learning objectives, key concepts, boxed equations,
worked examples, and check your understanding items. Add --with-problems to also
keep end of chapter questions with the published answers (odd numbers). All math is LaTeX inside \\( \\) or \\[ \\].
"""
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathml2tex import to_tex  # noqa: E402

C = "{http://cnx.rice.edu/cnxml}"
M = "{http://www.w3.org/1998/Math/MathML}"
MD = "{http://cnx.rice.edu/mdml}"


def tag(el):
    return el.tag.replace(C, "").replace(M, "m:") if isinstance(el.tag, str) else ""


class Ctx:
    def __init__(self, root):
        self.ids = {}
        for el in root.iter():
            i = el.get("id")
            if i:
                self.ids[i] = el
        self.figs_used = []


def esc(s):
    return html.escape(s or "", quote=False)


def link_text(el, ctx):
    txt = "".join(el.itertext()).strip()
    if txt:
        return esc(txt)
    if el.get("document"):
        return "another section"
    tgt = ctx.ids.get(el.get("target-id", ""))
    if tgt is None:
        return "the text"
    t = tag(tgt)
    if t == "figure":
        return "the figure"
    if t == "example":
        ttl = tgt.find(f"{C}para/{C}title")
        return "the example" + (f" <i>{esc(ttl.text)}</i>" if ttl is not None and ttl.text else "")
    if t == "equation":
        return "the equation"
    if t == "table":
        return "the table"
    return "the text"


def inline(el, ctx, skip_title=True):
    """Render the mixed content of an element as HTML."""
    out = [esc(el.text)]
    for ch in el:
        t = tag(ch)
        if t == "title" and skip_title:
            pass
        elif t == "m:math":
            out.append(r"\(" + to_tex(ch) + r"\)")
        elif t == "emphasis":
            eff = ch.get("effect", "bold")
            h = {"italics": "i", "bold": "b", "underline": "u"}.get(eff, "b")
            out.append(f"<{h}>{inline(ch, ctx)}</{h}>")
        elif t in ("sup", "sub"):
            out.append(f"<{t}>{inline(ch, ctx)}</{t}>")
        elif t == "term":
            out.append(f"<b>{inline(ch, ctx)}</b>")
        elif t == "newline":
            out.append("<br>")
        elif t == "link":
            out.append(link_text(ch, ctx))
        elif t == "list":
            out.append(render_list(ch, ctx))
        elif t == "equation":
            out.append(render_equation(ch))
        elif t == "figure":
            out.append(render_figure(ch, ctx))
        elif t == "para":
            out.append("<p>" + inline(ch, ctx) + "</p>")
        elif t == "quote":
            out.append("“" + inline(ch, ctx) + "”")
        elif t == "footnote":
            pass
        elif t == "media":
            out.append(render_media(ch, ctx))
        else:
            out.append(inline(ch, ctx))
        out.append(esc(ch.tail))
    s = "".join(out)
    s = re.sub(r"\s+", " ", s).strip()
    # links rendered as "the figure" may open a sentence
    s = re.sub(r"(^|\. )the (figure|equation|example|table|text)",
               lambda m: m.group(1) + "The " + m.group(2), s)
    return s


def render_equation(el):
    m = el.find(f"{M}math")
    if m is None:
        return ""
    return r"<div class='eq'>\[" + to_tex(m) + r"\]</div>"


def render_list(el, ctx):
    ordered = el.get("list-type") == "enumerated"
    style = el.get("number-style", "")
    tg = "ol" if ordered else "ul"
    typ = " type='a'" if "alpha" in style else ""
    items = "".join("<li>" + inline(i, ctx) + "</li>" for i in el.findall(f"{C}item"))
    return f"<{tg}{typ}>{items}</{tg}>"


def credit_free(caption):
    return "credit" not in caption.lower()


def render_figure(el, ctx):
    img = el.find(f".//{C}image")
    media = el.find(f".//{C}media")
    cap_el = el.find(f"{C}caption")
    cap = inline(cap_el, ctx) if cap_el is not None else ""
    cap_plain = "".join(cap_el.itertext()) if cap_el is not None else ""
    if img is None or not credit_free(cap_plain):
        # third party photo: leave it out, its license differs from the book's
        return ""
    src = os.path.basename(img.get("src", ""))
    ctx.figs_used.append(src)
    alt = esc(media.get("alt", "")) if media is not None else ""
    return (f"<figure><img src='img/{src}' alt=\"{alt}\" loading='lazy'>"
            + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")


def render_media(el, ctx):
    """Bare images inside problems and solutions are OpenStax graphs (no credit line)."""
    img = el.find(f".//{C}image")
    if img is None:
        return ""
    src = os.path.basename(img.get("src", ""))
    ctx.figs_used.append(src)
    alt = esc(el.get("alt", ""))
    return f"<figure><img src='img/{src}' alt=\"{alt}\" loading='lazy'></figure>"


def block(el, ctx):
    t = tag(el)
    if t == "media":
        return render_media(el, ctx)
    if t == "para":
        return "<p>" + inline(el, ctx) + "</p>"
    if t == "equation":
        return render_equation(el)
    if t == "list":
        return render_list(el, ctx)
    if t == "figure":
        return render_figure(el, ctx)
    if t == "note":
        return "".join(block(c, ctx) for c in el)
    if t == "table":
        return ""
    return inline(el, ctx)


def parse_example(ex, ctx):
    """Split an example into Problem / Strategy / Solution / Significance parts."""
    parts = []
    title = ""
    cur = None
    for ch in ex:
        t = tag(ch)
        ttl = ch.find(f"{C}title") if t == "para" else None
        if t == "para" and ttl is not None:
            label = (ttl.text or "").strip()
            if not parts and not title:
                title = label
                cur = {"label": "Problem", "html": ""}
            else:
                cur = {"label": label, "html": ""}
            parts.append(cur)
            cur["html"] += "<p>" + inline(ch, ctx) + "</p>"
        else:
            if cur is None:
                cur = {"label": "Problem", "html": ""}
                parts.append(cur)
            cur["html"] += block(ch, ctx)
    for p in parts:
        p["html"] = p["html"].replace("<p></p>", "")
    return {"title": title, "parts": parts}


def parse_exercise(ex, ctx):
    prob = ex.find(f"{C}problem")
    sol = ex.find(f"{C}solution")
    q = "".join(block(c, ctx) for c in prob) if prob is not None else ""
    a = "".join(block(c, ctx) for c in sol) if sol is not None else None
    return {"q": q, "a": a}


def module_root(bundle, mid):
    path = os.path.join(bundle, "modules", mid, "index.cnxml")
    return ET.parse(path).getroot()


def extract_section(bundle, mid, num):
    root = module_root(bundle, mid)
    ctx = Ctx(root)
    title = root.find(f"{C}title").text.strip()
    md = root.find(f"{C}metadata")
    objectives = []
    abstract = md.find(f"{MD}abstract") if md is not None else None
    if abstract is not None:
        lst = abstract.find(f"{C}list")
        if lst is not None:
            objectives = [inline(i, ctx) for i in lst.findall(f"{C}item")]
    content = root.find(f"{C}content")

    callouts = []
    for note in content.iter(f"{C}note"):
        if "equation-callout" in (note.get("class") or ""):
            for m in note.iter(f"{M}math"):
                tex = to_tex(m).rstrip(" .,")
                callouts.append(tex)

    examples = []
    for ex in content.iter(f"{C}example"):
        examples.append(parse_example(ex, ctx))

    checks = []
    for note in content.iter(f"{C}note"):
        if "check-understanding" in (note.get("class") or ""):
            for ex in note.iter(f"{C}exercise"):
                checks.append(parse_exercise(ex, ctx))

    eoc = {}
    key_concepts = []
    key_equations = []
    for sec in content.findall(f"{C}section"):
        cls = sec.get("class") or ""
        if cls == "key-concepts":
            for lst in sec.iter(f"{C}list"):
                key_concepts += [inline(i, ctx) for i in lst.findall(f"{C}item")]
        elif cls == "key-equations":
            for row in sec.iter(f"{C}row"):
                ents = row.findall(f"{C}entry")
                if len(ents) == 2:
                    m = ents[1].find(f".//{M}math")
                    key_equations.append({
                        "name": "".join(ents[0].itertext()).strip(),
                        "tex": to_tex(m) if m is not None else inline(ents[1], ctx),
                    })
        elif cls.startswith("review-"):
            kind = cls.replace("review-", "")
            eoc.setdefault(kind, [])
            for ex in sec.iter(f"{C}exercise"):
                eoc[kind].append(parse_exercise(ex, ctx))

    return {
        "num": num, "module": mid, "title": title, "objectives": objectives,
        "callouts": callouts, "examples": examples, "checks": checks,
        "keyConcepts": key_concepts, "eoc": eoc, "_keyEquations": key_equations,
        "_figs": ctx.figs_used,
    }


def main():
    bundle, out, first, last, chnum, chtitle = sys.argv[1:7]
    a, b = int(first[1:]), int(last[1:])
    mids = [f"m{i}" for i in range(a, b + 1)]
    sections = [extract_section(bundle, mid, f"{chnum}.{n}") for n, mid in enumerate(mids, 1)]

    key_equations = []
    figs = []
    for s in sections:
        key_equations += s.pop("_keyEquations")
        figs += s.pop("_figs")

    # End of chapter numbering runs through the chapter in this order.
    order = ["conceptual-questions", "problems", "additional-problems", "challenge"]
    n = 1
    for kind in order:
        for s in sections:
            for item in s["eoc"].get(kind, []):
                item["n"] = n
                n += 1

    data = {
        "book": "University Physics Volume 1",
        "bookUrl": "https://openstax.org/details/books/university-physics-volume-1",
        "license": "CC BY-NC-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "chapter": {"num": int(chnum), "title": chtitle},
        "keyEquations": key_equations,
        "sections": sections,
        "figures": sorted(set(figs)),
    }
    if "--with-problems" not in sys.argv:
        # The app leaves out end of chapter problems; keep only figures still referenced.
        for sec in data["sections"]:
            sec.pop("eoc", None)
        used = set(re.findall(r"img/([\w.-]+\.jpg)", json.dumps(data)))
        data["figures"] = sorted(used)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("sections", len(sections), "key equations", len(key_equations),
          "eoc items", n - 1, "figures", len(set(figs)))


if __name__ == "__main__":
    main()
