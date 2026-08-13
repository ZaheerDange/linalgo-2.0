"""
Unit 2 Solvers (Basic & Readable Python Code):
  1. Determinant (Cofactor Expansion)
  2. Eigenvalues & Eigenvectors (via SymPy Characteristic Equation)
  3. Gram-Schmidt Orthogonalization & Normalization

Designed for easy explanation during code presentation to a teacher.
Uses basic 'for' loops, top-level helper functions, and clear step comments.
"""

from fractions import Fraction
import math

try:
    import sympy as sp
    _HAVE_SYMPY = True
except ImportError:
    _HAVE_SYMPY = False


# ==============================================================================
#  HELPER FUNCTIONS (Basic Math & LaTeX Formatting)
# ==============================================================================

def frac(x):
    """Convert number or string to an exact Fraction."""
    if isinstance(x, Fraction):
        return x
    try:
        if isinstance(x, float):
            return Fraction(x).limit_denominator(100000)
        return Fraction(str(x))
    except Exception:
        return Fraction(0)


def frac_to_latex(val):
    """Format Fraction or number into LaTeX string."""
    if isinstance(val, Fraction):
        if val.denominator == 1:
            return str(val.numerator)
        num = abs(val.numerator)
        den = val.denominator
        if val < 0:
            return f"-\\dfrac{{{num}}}{{{den}}}"
        else:
            return f"\\dfrac{{{num}}}{{{den}}}"
            
    if isinstance(val, float):
        if abs(val - round(val)) < 1e-9:
            return str(int(round(val)))
        return f"{val:.5g}"
        
    return str(val)


def mat_to_latex(mat, env='pmatrix'):
    """Convert a 2D matrix to LaTeX pmatrix/vmatrix."""
    row_strings = []
    for row in mat:
        formatted_row = []
        for val in row:
            formatted_row.append(frac_to_latex(val))
        row_strings.append(" & ".join(formatted_row))
    body = " \\\\\n".join(row_strings)
    return f"\\begin{{{env}}}{body}\\end{{{env}}}"


def col_vec_latex(vec):
    """Convert a 1D vector to LaTeX column vector."""
    formatted_elements = []
    for val in vec:
        formatted_elements.append(frac_to_latex(val))
    body = " \\\\ ".join(formatted_elements)
    return f"\\begin{{pmatrix}}{body}\\end{{pmatrix}}"


def parse_square(data_matrix, max_n=5):
    """Validate that the matrix is square and convert elements to Fractions."""
    if not data_matrix:
        raise ValueError("Matrix cannot be empty.")
    num_rows = len(data_matrix)
    if num_rows > max_n:
        raise ValueError(f"Maximum {max_n}×{max_n} matrix supported. Got {num_rows}×…")
    
    num_cols = len(data_matrix[0]) if num_rows > 0 else 0
    if num_rows != num_cols:
        raise ValueError(f"Matrix must be square. Got {num_rows}×{num_cols}.")

    for r in range(num_rows):
        if len(data_matrix[r]) != num_cols:
            raise ValueError(f"Row {r+1} has {len(data_matrix[r])} entries; expected {num_cols}.")

    converted_matrix = []
    for r in range(num_rows):
        new_row = []
        for c in range(num_cols):
            new_row.append(frac(data_matrix[r][c]))
        converted_matrix.append(new_row)

    return converted_matrix


# ==============================================================================
#  MODULE 2A — DETERMINANT VIA COFACTOR EXPANSION
# ==============================================================================

def get_minor_matrix(mat, delete_row, delete_col):
    """
    Returns the submatrix obtained by removing a specified row and column.
    """
    submatrix = []
    num_rows = len(mat)
    num_cols = len(mat[0])

    for r in range(num_rows):
        if r == delete_row:
            continue
        new_row = []
        for c in range(num_cols):
            if c == delete_col:
                continue
            new_row.append(mat[r][c])
        submatrix.append(new_row)

    return submatrix


def compute_det_recursive(mat):
    """
    Computes determinant recursively using basic loops.
    """
    n = len(mat)
    if n == 1:
        return mat[0][0]
    if n == 2:
        return (mat[0][0] * mat[1][1]) - (mat[0][1] * mat[1][0])

    det_sum = frac(0)
    for j in range(n):
        sign = frac((-1) ** j)
        minor = get_minor_matrix(mat, 0, j)
        term = mat[0][j] * sign * compute_det_recursive(minor)
        det_sum = det_sum + term

    return det_sum


def solve_determinant(data):
    """
    Calculates the determinant of a square matrix step-by-step
    using cofactor expansion along the first row.
    """
    mat_data = data.get('matrix', [])
    A = parse_square(mat_data, max_n=5)
    n = len(A)
    steps = []

    steps.append({
        "title": f"Input Matrix $A$ ({n}×{n})",
        "description": "Compute determinant $\\det(A)$ using cofactor expansion along Row 1:",
        "matrix_latex": mat_to_latex(A),
        "type": "initial"
    })

    # Case 1: 1x1 Matrix
    if n == 1:
        steps.append({
            "title": "1×1 Determinant",
            "description": "Determinant of a 1×1 matrix is its single value:",
            "result_latex": f"\\boxed{{\\det(A) = {frac_to_latex(A[0][0])}}}",
            "type": "solution",
            "highlight": True
        })
        return steps

    # Case 2: 2x2 Matrix
    if n == 2:
        a, b = A[0][0], A[0][1]
        c, d = A[1][0], A[1][1]
        det_val = (a * d) - (b * c)

        steps.append({
            "title": "2×2 Determinant Formula ($ad - bc$)",
            "description": "Multiply diagonals: $(\\text{main}) - (\\text{anti})$:",
            "operation_latex": (
                f"\\det(A) = ({frac_to_latex(a)})({frac_to_latex(d)}) - "
                f"({frac_to_latex(b)})({frac_to_latex(c)}) = {frac_to_latex(det_val)}"
            ),
            "type": "eliminate"
        })

        steps.append({
            "title": "Determinant Result",
            "description": "",
            "result_latex": f"\\boxed{{\\det(A) = {frac_to_latex(det_val)}}}",
            "type": "solution",
            "highlight": True
        })
        return steps

    # Case 3: n x n (n >= 3) Cofactor Expansion
    steps.append({
        "title": "Cofactor Expansion Formula along Row 1",
        "description": "Formula: $\\det(A) = \\sum_{j=1}^{n} (-1)^{1+j} a_{1j} M_{1j}$",
        "type": "header"
    })

    det_total = frac(0)
    term_strings = []

    for j in range(n):
        a1j = A[0][j]
        sign_val = frac((-1) ** j)
        sign_str = "+1" if sign_val == 1 else "-1"

        minor = get_minor_matrix(A, 0, j)
        minor_det = compute_det_recursive(minor)
        cofactor = sign_val * minor_det
        term_val = a1j * cofactor

        det_total = det_total + term_val

        if a1j == 0:
            steps.append({
                "title": f"Term $j={j+1}$: Entry $a_{{1,{j+1}}} = 0$",
                "description": "Entry is 0, so term contribution is 0.",
                "type": "info"
            })
            continue

        term_strings.append(f"({frac_to_latex(a1j)})({frac_to_latex(cofactor)})")

        steps.append({
            "title": f"Cofactor $C_{{1,{j+1}}}$ (Delete Row 1, Column {j+1})",
            "description": f"Submatrix minor $M_{{1,{j+1}}}$:",
            "matrix_latex": mat_to_latex(minor, env='vmatrix'),
            "operation_latex": (
                "\\begin{aligned}"
                f"\\det(M_{{1,{j+1}}}) &= {frac_to_latex(minor_det)} \\\\[6pt]"
                f"C_{{1,{j+1}}} &= ({sign_str}) \\times {frac_to_latex(minor_det)} = {frac_to_latex(cofactor)} \\\\[6pt]"
                f"a_{{1,{j+1}}} \\cdot C_{{1,{j+1}}} &= {frac_to_latex(term_val)}"
                "\\end{aligned}"
            ),
            "type": "eliminate"
        })

    steps.append({
        "title": "Sum All Terms",
        "description": "Add all cofactor contributions:",
        "operation_latex": f"\\det(A) = {' + '.join(term_strings)} = {frac_to_latex(det_total)}",
        "type": "eliminate"
    })

    steps.append({
        "title": "Final Determinant Result",
        "description": "",
        "result_latex": f"\\boxed{{\\det(A) = {frac_to_latex(det_total)}}}",
        "type": "solution",
        "highlight": True
    })

    return steps


# ==============================================================================
#  MODULE 2B — EIGENVALUES & EIGENVECTORS
# ==============================================================================

def solve_eigenvalues(data):
    """
    Finds eigenvalues and eigenvectors of a matrix A by solving
    det(A - lambda * I) = 0.
    """
    if not _HAVE_SYMPY:
        raise ValueError("SymPy package is required for eigenvalue computation.")

    mat_data = data.get('matrix', [])
    if not mat_data:
        raise ValueError("Matrix cannot be empty.")

    n = len(mat_data)
    if n not in (2, 3):
        raise ValueError(f"Only 2×2 or 3×3 matrices supported. Got {n}×{n}.")

    steps = []

    # Display initial matrix
    A_fr = []
    for r in range(n):
        new_row = []
        for c in range(n):
            new_row.append(frac(mat_data[r][c]))
        A_fr.append(new_row)

    steps.append({
        "title": f"Input Matrix $A$ ({n}×{n})",
        "description": "Find eigenvalues $\\lambda$ and eigenvectors $\\mathbf{v}$:",
        "matrix_latex": mat_to_latex(A_fr),
        "type": "initial"
    })

    # Step 1: Form (A - lambda * I)
    lam = sp.Symbol('lambda')
    A_sp = sp.Matrix([[sp.Rational(str(mat_data[i][j])) for j in range(n)] for i in range(n)])
    I_sp = sp.eye(n)
    A_minus_lam = A_sp - (lam * I_sp)

    rows_latex = []
    for i in range(n):
        row_items = []
        for j in range(n):
            row_items.append(sp.latex(A_minus_lam[i, j]))
        rows_latex.append(" & ".join(row_items))

    aml_matrix_latex = f"\\begin{{pmatrix}}{' \\\\\n'.join(rows_latex)}\\end{{pmatrix}}"

    steps.append({
        "title": "Step 1: Form Matrix $(A - \\lambda I)$",
        "description": "Subtract $\\lambda$ along the main diagonal:",
        "operation_latex": f"A - \\lambda I = {aml_matrix_latex}",
        "type": "eliminate"
    })

    # Step 2: Characteristic Polynomial
    char_poly = A_sp.charpoly(lam)
    cp_expr = char_poly.as_expr()
    cp_latex = sp.latex(cp_expr)

    steps.append({
        "title": "Step 2: Characteristic Equation $\\det(A - \\lambda I) = 0$",
        "description": "Compute the characteristic polynomial:",
        "operation_latex": f"p(\\lambda) = {cp_latex} = 0",
        "type": "header"
    })

    # Step 3: Solve for eigenvalues
    eig_tuples = A_sp.eigenvects()

    ev_strings = []
    for idx, (ev_val, mult, vec_list) in enumerate(eig_tuples):
        ev_str = f"\\lambda_{{{idx+1}}} = {sp.latex(ev_val)}"
        if mult > 1:
            ev_str += f"\\text{{ (multiplicity {mult})}}"
        ev_strings.append(ev_str)

    steps.append({
        "title": "Step 3: Eigenvalues Found",
        "description": "Solving $p(\\lambda) = 0$ gives the eigenvalues:",
        "result_latex": f"\\boxed{{{', \\quad '.join(ev_strings)}}}",
        "type": "solution",
        "highlight": True
    })

    # Step 4: Eigenvectors for each eigenvalue
    for ev_val, mult, vec_list in eig_tuples:
        ev_latex = sp.latex(ev_val)

        # Form matrix (A - lambda * I) for this specific eigenvalue
        A_sub = A_sp - (ev_val * I_sp)
        
        # Build augmented matrix [A - lambda I | 0]
        aug_rows = []
        for i in range(n):
            r_str = " & ".join(sp.latex(sp.simplify(A_sub[i, j])) for j in range(n))
            aug_rows.append(f"{r_str} & 0")
        
        col_spec = "r" * n + "|r"
        aug_latex = f"\\left[\\begin{{array}}{{{col_spec}}}{' \\\\\n'.join(aug_rows)}\\end{{array}}\\right]"

        steps.append({
            "title": f"Eigenvectors for $\\lambda = {ev_latex}$",
            "description": f"Solve homogeneous system $(A - {ev_latex}I)\\mathbf{{v}} = \\mathbf{{0}}$:",
            "matrix_latex": aug_latex,
            "type": "header"
        })

        # Format eigenvectors
        vec_latex_parts = []
        for vec in vec_list:
            entries = " \\\\ ".join(sp.latex(sp.simplify(vec[i])) for i in range(n))
            vec_latex_parts.append(f"\\begin{{pmatrix}}{entries}\\end{{pmatrix}}")

        steps.append({
            "title": f"Eigenspace $E_{{{ev_latex}}}$",
            "description": f"Basis for eigenspace corresponding to $\\lambda = {ev_latex}$:",
            "result_latex": f"\\mathbf{{v}} \\in \\text{{span}}\\left\\{{\\, {', '.join(vec_latex_parts)} \\,\\right\\}}",
            "type": "solution",
            "highlight": True
        })

    return steps


# ==============================================================================
#  MODULE 2C — GRAM-SCHMIDT ORTHOGONALIZATION
# ==============================================================================

def dot_product(v1, v2):
    """Compute dot product of two vectors."""
    total = frac(0)
    for i in range(len(v1)):
        total = total + (v1[i] * v2[i])
    return total


def vector_norm_sq(v):
    """Compute squared magnitude of a vector."""
    return dot_product(v, v)


def scale_vector(c, v):
    """Multiply a vector by a scalar c."""
    res = []
    for val in v:
        res.append(c * val)
    return res


def subtract_vectors(v1, v2):
    """Subtract vector v2 from vector v1."""
    res = []
    for i in range(len(v1)):
        res.append(v1[i] - v2[i])
    return res


def solve_gram_schmidt(data):
    """
    Applies Gram-Schmidt process to convert vectors v_1..v_k into
    an orthogonal basis u_1..u_k and orthonormal basis e_1..e_k.
    """
    vecs_raw = data.get('vectors', [])
    if not vecs_raw:
        raise ValueError("At least one vector must be provided.")

    k = len(vecs_raw)
    dim = len(vecs_raw[0])

    vecs = []
    for v in vecs_raw:
        new_v = []
        for x in v:
            new_v.append(frac(x))
        vecs.append(new_v)

    steps = []

    # Input display
    input_str_list = []
    for i in range(k):
        input_str_list.append(f"\\mathbf{{v}}_{{{i+1}}} = {col_vec_latex(vecs[i])}")

    steps.append({
        "title": f"Input — {k} Vector(s) in $\\mathbb{{R}}^{{{dim}}}$",
        "description": "Initial linearly independent set:",
        "result_latex": ", \\qquad ".join(input_str_list),
        "type": "initial"
    })

    steps.append({
        "title": "Gram-Schmidt Formula",
        "description": "Construct orthogonal vectors $\\mathbf{u}_k$ by subtracting projections:",
        "operation_latex": (
            "\\mathbf{u}_1 = \\mathbf{v}_1 \\\\[6pt]"
            "\\mathbf{u}_k = \\mathbf{v}_k - \\sum_{j=1}^{k-1} "
            "\\dfrac{\\langle \\mathbf{v}_k, \\mathbf{u}_j \\rangle}{\\|\\mathbf{u}_j\\|^2} \\mathbf{u}_j"
        ),
        "type": "header"
    })

    u_vectors = []

    for ki in range(k):
        vk = vecs[ki]

        if ki == 0:
            # First vector u1 = v1
            u = list(vk)
            steps.append({
                "title": "$\\mathbf{u}_1 = \\mathbf{v}_1$",
                "description": "First vector is kept as is:",
                "result_latex": f"\\mathbf{{u}}_1 = {col_vec_latex(u)}",
                "type": "eliminate"
            })
        else:
            # Subsequent vectors: u_k = v_k - sum(proj)
            u = list(vk)
            for j in range(ki):
                uj = u_vectors[j]
                ip = dot_product(vk, uj)
                nsq = vector_norm_sq(uj)

                if nsq == 0:
                    continue

                coeff = ip / nsq
                proj = scale_vector(coeff, uj)

                steps.append({
                    "title": f"Subtract Projection of $\\mathbf{{v}}_{{{ki+1}}}$ onto $\\mathbf{{u}}_{{{j+1}}}$",
                    "description": f"Inner product = ${frac_to_latex(ip)}$, Norm squared = ${frac_to_latex(nsq)}$:",
                    "operation_latex": (
                        f"\\text{{proj}} = \\dfrac{{{frac_to_latex(ip)}}}{{{frac_to_latex(nsq)}}} "
                        f"{col_vec_latex(uj)} = {col_vec_latex(proj)}"
                    ),
                    "type": "eliminate"
                })

                u = subtract_vectors(u, proj)

            steps.append({
                "title": f"Result for Orthogonal Vector $\\mathbf{{u}}_{{{ki+1}}}$",
                "description": "After subtracting all projections:",
                "result_latex": f"\\mathbf{{u}}_{{{ki+1}}} = {col_vec_latex(u)}",
                "type": "eliminate"
            })

        u_vectors.append(u)

    # Orthogonal set summary
    orth_str_list = []
    for i in range(len(u_vectors)):
        orth_str_list.append(f"\\mathbf{{u}}_{{{i+1}}} = {col_vec_latex(u_vectors[i])}")

    steps.append({
        "title": "✓ Orthogonal Basis $\\{\\mathbf{u}_1, \\ldots, \\mathbf{u}_k\\}$",
        "description": "All vectors are pairwise orthogonal ($\langle \\mathbf{u}_i, \\mathbf{u}_j \\rangle = 0$):",
        "result_latex": ", \\qquad ".join(orth_str_list),
        "type": "milestone",
        "highlight": True
    })

    # Normalization step -> Orthonormal basis
    steps.append({
        "title": "Normalization Phase (Orthonormal Basis)",
        "description": "Divide each vector $\\mathbf{u}_k$ by its norm $\|\\mathbf{u}_k\| = \\sqrt{\\langle \\mathbf{u}_k, \\mathbf{u}_k \\rangle}$:",
        "type": "header"
    })

    onb_str_list = []
    for i in range(len(u_vectors)):
        u = u_vectors[i]
        nsq = vector_norm_sq(u)
        norm_val = math.sqrt(float(nsq))

        if norm_val > 1e-10:
            onb_str_list.append(
                f"\\mathbf{{e}}_{{{i+1}}} = \\dfrac{{1}}{{\\sqrt{{{frac_to_latex(nsq)}}}}} {col_vec_latex(u)}"
            )

    steps.append({
        "title": "✓ Orthonormal Basis $\\{\\mathbf{e}_1, \\ldots, \\mathbf{e}_k\\}$",
        "description": "Final normalized unit vector basis:",
        "result_latex": ", \\qquad ".join(onb_str_list),
        "type": "solution",
        "highlight": True
    })

    return steps
