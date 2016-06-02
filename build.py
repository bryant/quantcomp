from pylatex import (Document, Package, Section, Command, NoEscape, Enumerate,
                     Subsection)
from argparse import ArgumentParser
import os
import re

def make_doc(preamble="preamble.tex"):
    doc = Document(fontenc=None)
    if preamble is not None:
        doc.preamble.append(NoEscape(open(preamble).read()))
    doc.append(Command("ignorespaces"))
    return doc

def read_one(texfile):
    raw = open(texfile).read()
    return NoEscape(raw.replace("\n\n", ""))

def build_one(texfile, preamble="preamble.tex"):
    doc = make_doc(preamble)
    doc.append(read_one(texfile))
    return doc

class ProblemList(Enumerate):
    def set_counter(self, num):
        self.append(Command("setcounter", "enumi", extra_arguments=num))
        return self
    @property
    def latex_name(self):
        return "enumerate"

def build_chap(subdir, preamble="preamble.tex"):
    exos = ProblemList()
    probs = ProblemList()

    files = sorted(os.listdir(subdir))
    for subfile in files:
        path = os.path.join(subdir, subfile)

        if subfile.startswith("p"):
            pnum = int(re.match(r"p(\d+)\.tex", subfile).group(1))
            probs.set_counter(pnum - 1).add_item(read_one(path))
        elif re.match(r"^\d+\.tex", subfile):
            pnum = int(re.match(r"(\d+)\.tex", subfile).group(1))
            exos.set_counter(pnum - 1).add_item(read_one(path))

    return exos, probs

def build_all(subdirs, preamble="preamble.tex"):
    doc = d = make_doc(preamble)
    for subdir in subdirs:
        chap = re.search(r"\d+", subdir).group(0)
        with d.create(Section(chap, numbering=False)):
            exos, probs = build_chap(chap, preamble)
            d.append(Subsection("Exercises", numbering=False, data=exos))
            if len(probs) > 0:
                d.append(Subsection("Problems", numbering=False, data=probs))
    return doc

args = ArgumentParser()
args.add_argument("texfile_or_chapdir", nargs="+",
                   help="Either a path to a solution TeX file or a subdirectory\
                         containing the all solutions of a chapter.")
args.add_argument("-c", dest="compiler", default="xelatex",
                  help="TeX compiler (default: xelatex)")
args.add_argument("-q", dest="quiet", default=False, action="store_true",
                  help="Suppress TeX compiler output (default: False)")
args.add_argument("-a", dest="all", default=False, action="store_true",
                  help="Build an entire chapter.")

if __name__ == "__main__":
    opts = args.parse_args()
    if opts.all:
        build_all(opts.texfile_or_chapdir).generate_pdf(compiler=opts.compiler,
                                                        silent=opts.quiet)
    else:
        build_one(opts.texfile_or_chapdir[0]) \
                .generate_pdf(compiler=opts.compiler, silent=opts.quiet)
