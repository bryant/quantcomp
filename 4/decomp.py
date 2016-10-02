from sympy import Number, sqrt, I
from numpy import eye as identity, mat, vectorize

def _mb_int(n):
    from sympy.core.numbers import ImaginaryUnit
    try:
        return Number(n)
    except TypeError:
        return n
mb_int = vectorize(_mb_int)
asint = vectorize(lambda n: Number(n))
simp = vectorize(lambda x: x.simplify())
conj = vectorize(lambda n: n.conjugate())

def decomp_one(xs, col, row0, row1):
    """
    Perform one round of decomposition on (row0, col) and (row1, col) of xs.
    """
    j, k, m, n = (row0, col), (row0, row1), (row1, col), (row1, row1)
    a, b = xs[j], xs[m]
    denom = sqrt(a*a.conjugate() + b*b.conjugate())
    rv = asint(mat(identity(len(xs), dtype=int)))
    rv[j] = (a.conjugate() / denom).simplify()
    rv[k] = (b.conjugate() / denom).simplify()
    rv[m] = (b / denom).simplify()
    rv[n] = -(a / denom).simplify()
    return rv

def decomp_final(xs):
    """
    `xs` is assumed to be the identity up till its bottom-right-most 2x2.
    """
    e, f, g, h = xs[-2, -2], xs[-2, -1], xs[-1, -2], xs[-1, -1]
    rv = asint(mat(identity(len(xs), dtype=int)))
    rv[-2, -2] = xs[-2, -2].conjugate()
    rv[-2, -1] = xs[-1, -2].conjugate()
    rv[-1, -2] = xs[-2, -1].conjugate()
    rv[-1, -1] = xs[-1, -1].conjugate()
    return rv

def print_mat(xs):
    from sympy.printing import latex
    rv = "\\begin{pmatrix} "
    for row in xrange(0, len(xs)):
        s = latex(xs[row, 0])
        for col in xrange(1, len(xs)):
            s += " & " + latex(xs[row, col])
        rv += s + " \\\\ "
    return rv[:-3] + " \\end{pmatrix}"

def decomp(xs):
    order = [((col, col), (row, col)) for col in range(0, len(xs) - 2)
                                      for row in range(col + 1, len(xs))]
    rv = []
    for col in xrange(0, len(xs) - 2):
        for row in xrange(col + 1, len(xs)):
            p = decomp_one(xs, col, col, row)
            rv.insert(0, p)
            xs = simp(p * xs)
    rv.insert(0, decomp_final(xs))
    return rv

if __name__ == "__main__":
    # exercise 4.37
    q = mb_int(mat([[1]*4, [1, I, -1, -I], [1, -1, 1, -1], [1, -I, -1, I]])) / 2
    xs = decomp(q)
    inv = map(lambda x: conj(x.T), xs[::-1])
    print " \\\\\n".join(map(print_mat, inv))
    print simp(reduce(lambda x, y: simp(x * y), inv)) == q
