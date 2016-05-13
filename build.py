from pylatex import Document, Package, Section, Command, NoEscape, Enumerate
from argparse import ArgumentParser
import os
import re

def make_doc(preamble="preamble.tex"):
    doc = Document(fontenc=None)
    if preamble is not None:
        doc.preamble.append(NoEscape(open(preamble).read()))
    doc.append(Command("ignorespaces"))
    return doc

def build_one(texfile, preamble="preamble.tex"):
    doc = make_doc(preamble)
    doc.append(NoEscape(open(texfile).read()))
    return doc

class ProblemList(Enumerate):
    def set_counter(self, num):
        self.append(Command("setcounter", "enumi", extra_arguments=num))
        return self
    @property
    def latex_name(self):
        return "enumerate"

def build_all(subdir, preamble="preamble.tex"):
    def is_numbered_tex_file(s):
        path = os.path.join(subdir, s)
        return re.match(r"\d+\.tex", s) and os.path.isfile(path)

    doc = d = make_doc(preamble)
    with d.create(Section("", numbering=True)):
        with d.create(ProblemList()) as probs:
            files = sorted(filter(is_numbered_tex_file, os.listdir(subdir)))
            for subfile in files:
                path = os.path.join(subdir, subfile)
                pnum = int(re.match(r"(\d+)\.tex", subfile).group(1)) - 1
                probs.set_counter(pnum).add_item(NoEscape(open(path).read()))
    return doc

args = ArgumentParser()
args.add_argument("texfile_or_chapdir",
                   help="Either a path to a solution TeX file or a subdirectory\
                         containing the all solutions of a chapter.")
args.add_argument("-a", dest="all", default=False, action="store_true",
                  help="Build an entire chapter.")

if __name__ == "__main__":
    opts = args.parse_args()
    if opts.all:
        build_all(opts.texfile_or_chapdir).generate_pdf()
    else:
        build_one(opts.texfile_or_chapdir).generate_pdf()
