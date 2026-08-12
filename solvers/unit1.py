"""
Unit 1 Solvers (Basic & Readable Python Code):
  1. Gaussian Elimination (REF + Back-Substitution)
  2. Gauss-Jordan Elimination (RREF)
  3. Vector Operations (Dot product, Cross product, Magnitudes, Angle)
  4. Vector Spaces (Linear Independence, Basis, Rank)

Designed for easy explanation during code presentation to a teacher.
Uses simple 'for' loops, explicit variable names, and clear comments.
"""

from fractions import Fraction
import math


# ==============================================================================
#  HELPER FUNCTIONS (Basic Math & LaTeX Formatting)
# ==============================================================================

def frac(x):
    """
    Convert a number or string to an exact Fraction object.
    Prevents floating-point precision errors (e.g. 0.3333... vs 1/3).
    """
    if isinstance(x, Fraction):
        return x
    try:
        if isinstance(x, float):
            # Limit denominator for clean fractions from float inputs
            return Fraction(x).limit_denominator(100000)
        return Fraction(str(x))
    except Exception:
        return Fraction(0)


def frac_to_latex(val):
    """
    Convert a Fraction or number into clean LaTeX math code.
    Example: Fraction(3, 4) -> '\dfrac{3}{4}'
             Fraction(-1, 2) -> '-\dfrac{1}{2}'
             Fraction(5, 1) -> '5'
    """
    if isinstance(val, Fraction):
        # If denominator is 1, return simple integer string
        if val.denominator == 1:
            return str(val.numerator)
        
        # Format fraction numerator and denominator
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
    """
    Convert a 2D matrix (list of lists) to a LaTeX pmatrix string.
    """
    row_strings = []
    for row in mat:
        # Join elements in each row with ' & '
        formatted_row = []
        for val in row:
            formatted_row.append(frac_to_latex(val))
        row_strings.append(" & ".join(formatted_row))
    
    # Join rows with double backslash (LaTeX line break)
    body = " \\\\\n".join(row_strings)
    return f"\\begin{{{env}}}{body}\\end{{{env}}}"


def augm_to_latex(mat, n_var):
    """
    Convert an augmented matrix [A | b] to LaTeX array with vertical line separator.
    """
    row_strings = []
    for row in mat:
        # Separate coefficients (left) and constants (right)
        left_parts = []
        for v in row[:n_var]:
            left_parts.append(frac_to_latex(v))
        left_str = " & ".join(left_parts)

        right_parts = []
        for v in row[n_var:]:
            right_parts.append(frac_to_latex(v))
        right_str = " & ".join(right_parts)

        row_strings.append(f"{left_str} & {right_str}")

    n_aug = len(mat[0]) - n_var
    col_spec = "r" * n_var + "|" + "r" * n_aug
    body = " \\\\\n".join(row_strings)
    return f"\\left[\\begin{{array}}{{{col_spec}}}{body}\\end{{array}}\\right]"


def col_vec_latex(vec):
    """
    Convert a 1D vector (list) into a LaTeX column vector string.
    """
    formatted_elements = []
    for val in vec:
        formatted_elements.append(frac_to_latex(val))
    body = " \\\\ ".join(formatted_elements)
    return f"\\begin{{pmatrix}}{body}\\end{{pmatrix}}"


def parse_augmented(data_matrix, max_rows=5, max_n_var=5):
    """
    Validate the input matrix and convert every entry into an exact Fraction.
    """
    if not data_matrix:
        raise ValueError("Matrix cannot be empty.")

    num_rows = len(data_matrix)
    num_cols = len(data_matrix[0])

    if num_rows > max_rows:
        raise ValueError(f"Maximum {max_rows} equations supported. Got {num_rows}.")

    n_var = num_cols - 1
    if n_var < 1:
        raise ValueError("Augmented matrix needs at least 2 columns (1 variable + constants).")
    if n_var > max_n_var:
        raise ValueError(f"Maximum {max_n_var} variables supported. Got {n_var}.")

    for i in range(num_rows):
        if len(data_matrix[i]) != num_cols:
            raise ValueError(f"Row {i+1} has {len(data_matrix[i])} entries; expected {num_cols}.")

    # Convert all numbers to Fraction objects
    converted_matrix = []
    for r in range(num_rows):
        new_row = []
        for c in range(num_cols):
            new_row.append(frac(data_matrix[r][c]))
        converted_matrix.append(new_row)

    return converted_matrix


def find_pivots(mat, n_var):
    """
    Find pivot positions (row_index, col_index) in a matrix.
    A pivot is the first non-zero element in a row.
    """
    pivots = []
    used_rows = set()

    for col in range(n_var):
        for row in range(len(mat)):
            if row not in used_rows and mat[row][col] != 0:
                # Check if all entries before this column in this row are 0
                is_leading = True
                for prev_col in range(col):
                    if mat[row][prev_col] != 0:
                        is_leading = False
                        break
                
                if is_leading:
                    pivots.append((row, col))
                    used_rows.add(row)
                    break

    return pivots


# ==============================================================================
#  MODULE 1A — GAUSSIAN ELIMINATION
# ==============================================================================

def solve_gaussian(data):
    """
    Solves a linear system using Gaussian Elimination:
    Step 1: Forward elimination to Row Echelon Form (REF).
    Step 2: Back-substitution to find unknown variables.
    """
    mat_data = data.get('matrix', [])
    A = parse_augmented(mat_data)
    rows = len(A)
    cols = len(A[0])
    n_var = cols - 1

    steps = []
    step_num = 1

    # Add initial matrix step
    steps.append({
        "title": "Initial Augmented Matrix $[A\\mid\\mathbf{b}]$",
        "description": (
            f"We have **{rows}** equation(s) and **{n_var}** variable(s). "
            "Form the augmented matrix by placing constants in the rightmost column:"
        ),
        "matrix_latex": augm_to_latex(A, n_var),
        "type": "initial"
    })

    pivot_row = 0

    # --------------------------------------------------------------------------
    # Step 1: Forward Elimination to reach Row Echelon Form (REF)
    # --------------------------------------------------------------------------
    for col in range(n_var):
        if pivot_row >= rows:
            break

        # Search for a row with a non-zero pivot in this column
        found_pivot_row = -1
        for r in range(pivot_row, rows):
            if A[r][col] != 0:
                found_pivot_row = r
                break

        # If no pivot found in this column, it corresponds to a free variable
        if found_pivot_row == -1:
            steps.append({
                "title": f"Step {step_num}: Column {col+1} (Free Variable)",
                "description": (
                    f"All entries in column {col+1} below row {pivot_row+1} are zero. "
                    f"Variable $x_{{{col+1}}}$ will be a **free variable**."
                ),
                "type": "info"
            })
            step_num += 1
            continue

        # Interchange current row with found pivot row if necessary
        if found_pivot_row != pivot_row:
            A[pivot_row], A[found_pivot_row] = A[found_pivot_row], A[pivot_row]
            steps.append({
                "title": f"Step {step_num}: Row Interchange",
                "description": f"Swap row {pivot_row+1} and row {found_pivot_row+1} to get a non-zero pivot:",
                "operation_latex": f"R_{{{pivot_row+1}}} \\longleftrightarrow R_{{{found_pivot_row+1}}}",
                "matrix_latex": augm_to_latex(A, n_var),
                "type": "swap"
            })
            step_num += 1

        pivot_val = A[pivot_row][col]

        # Eliminate entries below the pivot
        for r in range(pivot_row + 1, rows):
            if A[r][col] == 0:
                continue

            # Calculate multiplier: m = row_entry / pivot_entry
            multiplier = A[r][col] / pivot_val
            m_latex = frac_to_latex(multiplier)

            # Row operation: Row_r = Row_r - multiplier * Row_pivot
            for j in range(cols):
                A[r][j] = A[r][j] - (multiplier * A[pivot_row][j])

            # Build LaTeX formula description for row operation
            if multiplier == 1:
                op_str = f"R_{{{r+1}}} \\leftarrow R_{{{r+1}}} - R_{{{pivot_row+1}}}"
            elif multiplier == -1:
                op_str = f"R_{{{r+1}}} \\leftarrow R_{{{r+1}}} + R_{{{pivot_row+1}}}"
            elif multiplier > 0:
                op_str = f"R_{{{r+1}}} \\leftarrow R_{{{r+1}}} - {m_latex}\\,R_{{{pivot_row+1}}}"
            else:
                op_str = f"R_{{{r+1}}} \\leftarrow R_{{{r+1}}} + {frac_to_latex(-multiplier)}\\,R_{{{pivot_row+1}}}"

            steps.append({
                "title": f"Step {step_num}: Eliminate Entry at Row {r+1}, Column {col+1}",
                "description": f"Zero out row {r+1}, column {col+1} using multiplier $m = {m_latex}$:",
                "operation_latex": op_str,
                "matrix_latex": augm_to_latex(A, n_var),
                "type": "eliminate"
            })
            step_num += 1

        pivot_row += 1

    # REF Milestone
    steps.append({
        "title": "✓ Row Echelon Form (REF) Reached",
        "description": "The matrix is now in Row Echelon Form (all entries below pivots are zero):",
        "matrix_latex": augm_to_latex(A, n_var),
        "type": "milestone",
        "highlight": True
    })

    # Check for inconsistency (0 = non-zero constant)
    for r in range(rows):
        all_zeros = True
        for c in range(n_var):
            if A[r][c] != 0:
                all_zeros = False
                break
        
        if all_zeros and A[r][n_var] != 0:
            steps.append({
                "title": "✗ System is Inconsistent (No Solution)",
                "description": f"Row {r+1} yields $0 = {frac_to_latex(A[r][n_var])}$, which is impossible.",
                "type": "error",
                "highlight": True
            })
            return steps

    # Identify pivot columns and free variables
    pivots = find_pivots(A, n_var)
    pivot_cols = set()
    for p_row, p_col in pivots:
        pivot_cols.add(p_col)

    free_cols = []
    for c in range(n_var):
        if c not in pivot_cols:
            free_cols.append(c)

    if len(free_cols) > 0:
        free_var_names = []
        for c in free_cols:
            free_var_names.append(f"$x_{{{c+1}}}$")
        steps.append({
            "title": "Free Variables Present",
            "description": f"Variables {', '.join(free_var_names)} are free. The system has **infinitely many solutions**.",
            "type": "info",
            "highlight": True
        })

    # --------------------------------------------------------------------------
    # Step 2: Back-Substitution
    # --------------------------------------------------------------------------
    steps.append({
        "title": "Back-Substitution Phase",
        "description": "Working from bottom to top, solve for each pivot variable:",
        "type": "header"
    })

    x_values = {}

    for idx in range(len(pivots) - 1, -1, -1):
        r, pc = pivots[idx]

        # Build row equation string
        terms = []
        for c in range(n_var):
            coeff = A[r][c]
            if coeff == 0:
                continue
            c_str = frac_to_latex(coeff)
            if coeff == 1:
                terms.append(f"x_{{{c+1}}}")
            elif coeff == -1:
                terms.append(f"-x_{{{c+1}}}")
            else:
                terms.append(f"{c_str}\\,x_{{{c+1}}}")
        
        eq_lhs = " + ".join(terms).replace("+ -", "- ")
        eq_rhs = frac_to_latex(A[r][n_var])

        if len(free_cols) == 0:
            # Unique solution case
            rhs_num = A[r][n_var]
            for c in range(pc + 1, n_var):
                if A[r][c] != 0 and c in x_values:
                    rhs_num = rhs_num - (A[r][c] * x_values[c])
            
            x_values[pc] = rhs_num / A[r][pc]
            res_latex = frac_to_latex(x_values[pc])
            op_latex = f"x_{{{pc+1}}} = \\dfrac{{{frac_to_latex(rhs_num)}}}{{{frac_to_latex(A[r][pc])}}} = {res_latex}"
        else:
            # Parametric solution case
            op_latex = f"x_{{{pc+1}}} = \\frac{{1}}{{{frac_to_latex(A[r][pc])}}}\\left({eq_rhs} ... \\right)"

        steps.append({
            "title": f"Solve for $x_{{{pc+1}}}$",
            "description": f"From row {r+1}: ${eq_lhs} = {eq_rhs}$",
            "operation_latex": op_latex,
            "type": "back_sub"
        })

    # Final result summary
    if len(free_cols) == 0 and len(x_values) > 0:
        sol_parts = []
        for c in range(n_var):
            val = x_values.get(c, frac(0))
            sol_parts.append(f"x_{{{c+1}}} = {frac_to_latex(val)}")
        sol_str = ", \\quad ".join(sol_parts)
        
        steps.append({
            "title": "✓ Final Unique Solution",
            "description": "The exact solution values for all variables:",
            "result_latex": f"\\boxed{{{sol_str}}}",
            "type": "solution",
            "highlight": True
        })
    elif len(free_cols) > 0:
        steps.append({
            "title": "General Parametric Solution",
            "description": "Express pivot variables in terms of free parameter(s).",
            "type": "solution",
            "highlight": True
        })

    return steps


# ==============================================================================
#  MODULE 1B — GAUSS-JORDAN ELIMINATION
# ==============================================================================

def solve_gauss_jordan(data):
    """
    Solves a linear system using Gauss-Jordan Elimination to reach
    Reduced Row Echelon Form (RREF).
    """
    mat_data = data.get('matrix', [])
    A = parse_augmented(mat_data)
    rows = len(A)
    cols = len(A[0])
    n_var = cols - 1

    steps = []
    step_num = 1

    steps.append({
        "title": "Initial Augmented Matrix $[A\\mid\\mathbf{b}]$",
        "description": "Transform matrix directly into Reduced Row Echelon Form (RREF):",
        "matrix_latex": augm_to_latex(A, n_var),
        "type": "initial"
    })

    pivot_row = 0

    for col in range(n_var):
        if pivot_row >= rows:
            break

        # Find pivot row
        found_pivot_row = -1
        for r in range(pivot_row, rows):
            if A[r][col] != 0:
                found_pivot_row = r
                break

        if found_pivot_row == -1:
            continue

        # Swap rows if necessary
        if found_pivot_row != pivot_row:
            A[pivot_row], A[found_pivot_row] = A[found_pivot_row], A[pivot_row]
            steps.append({
                "title": f"Step {step_num}: Row Interchange",
                "description": f"Swap row {pivot_row+1} and row {found_pivot_row+1}:",
                "operation_latex": f"R_{{{pivot_row+1}}} \\longleftrightarrow R_{{{found_pivot_row+1}}}",
                "matrix_latex": augm_to_latex(A, n_var),
                "type": "swap"
            })
            step_num += 1

        # Scale pivot row so leading entry becomes 1
        pivot_val = A[pivot_row][col]
        if pivot_val != 1:
            pv_latex = frac_to_latex(pivot_val)
            for j in range(cols):
                A[pivot_row][j] = A[pivot_row][j] / pivot_val
            
            steps.append({
                "title": f"Step {step_num}: Scale Row {pivot_row+1} to Make Pivot = 1",
                "description": f"Divide row {pivot_row+1} by {pv_latex}:",
                "operation_latex": f"R_{{{pivot_row+1}}} \\leftarrow \\dfrac{{1}}{{{pv_latex}}}\\,R_{{{pivot_row+1}}}",
                "matrix_latex": augm_to_latex(A, n_var),
                "type": "scale"
            })
            step_num += 1

        # Eliminate all other entries in this column (both above and below)
        for r in range(rows):
            if r == pivot_row or A[r][col] == 0:
                continue

            multiplier = A[r][col]
            m_latex = frac_to_latex(multiplier)

            for j in range(cols):
                A[r][j] = A[r][j] - (multiplier * A[pivot_row][j])

            direction = "above" if r < pivot_row else "below"
            if multiplier == 1:
                op_str = f"R_{{{r+1}}} \\leftarrow R_{{{r+1}}} - R_{{{pivot_row+1}}}"
            elif multiplier == -1:
                op_str = f"R_{{{r+1}}} \\leftarrow R_{{{r+1}}} + R_{{{pivot_row+1}}}"
            elif multiplier > 0:
                op_str = f"R_{{{r+1}}} \\leftarrow R_{{{r+1}}} - {m_latex}\\,R_{{{pivot_row+1}}}"
            else:
                op_str = f"R_{{{r+1}}} \\leftarrow R_{{{r+1}}} + {frac_to_latex(-multiplier)}\\,R_{{{pivot_row+1}}}"

            steps.append({
                "title": f"Step {step_num}: Eliminate Entry {direction} Pivot",
                "description": f"Zero out row {r+1}, column {col+1}:",
                "operation_latex": op_str,
                "matrix_latex": augm_to_latex(A, n_var),
                "type": "eliminate"
            })
            step_num += 1

        pivot_row += 1

    # RREF achieved
    steps.append({
        "title": "✓ Reduced Row Echelon Form (RREF) Reached",
        "description": "Every pivot is 1 and is the only non-zero entry in its column:",
        "matrix_latex": augm_to_latex(A, n_var),
        "type": "milestone",
        "highlight": True
    })

    # Inconsistency check
    for r in range(rows):
        all_zeros = True
        for c in range(n_var):
            if A[r][c] != 0:
                all_zeros = False
                break
        if all_zeros and A[r][n_var] != 0:
            steps.append({
                "title": "✗ System is Inconsistent",
                "description": f"Row {r+1} gives $0 = {frac_to_latex(A[r][n_var])}$. No solution exists.",
                "type": "error",
                "highlight": True
            })
            return steps

    # Read solution directly from RREF
    pivots = find_pivots(A, n_var)
    pivot_cols = set()
    for pr, pc in pivots:
        pivot_cols.add(pc)

    free_cols = []
    for c in range(n_var):
        if c not in pivot_cols:
            free_cols.append(c)

    if len(free_cols) == 0:
        sol_parts = []
        for r, c in pivots:
            sol_parts.append(f"x_{{{c+1}}} = {frac_to_latex(A[r][n_var])}")
        sol_str = ", \\quad ".join(sol_parts)

        steps.append({
            "title": "Direct RREF Solution Reading",
            "description": "Values are read directly from the rightmost column:",
            "result_latex": f"\\boxed{{{sol_str}}}",
            "type": "solution",
            "highlight": True
        })
    else:
        steps.append({
            "title": "General Parametric Solution",
            "description": "Express pivot variables in terms of free variables.",
            "type": "solution",
            "highlight": True
        })

    return steps


# ==============================================================================
#  MODULE 1C — VECTOR OPERATIONS
# ==============================================================================

def solve_vectors(data):
    """
    Computes dot product, 3D cross product, vector magnitudes, and angle theta.
    """
    u_raw = data.get('u', [])
    v_raw = data.get('v', [])

    if not u_raw or not v_raw:
        raise ValueError("Both vectors u and v must be provided.")
    if len(u_raw) != len(v_raw):
        raise ValueError("Vectors u and v must have equal dimensions.")
    
    dim = len(u_raw)
    if dim < 2 or dim > 6:
        raise ValueError("Vector dimension must be between 2 and 6.")

    u = []
    for val in u_raw:
        u.append(frac(val))

    v = []
    for val in v_raw:
        v.append(frac(val))

    steps = []

    # Display inputs
    steps.append({
        "title": f"Given Vectors in $\\mathbb{{R}}^{{{dim}}}$",
        "description": "Input vectors $\\mathbf{u}$ and $\\mathbf{v}$:",
        "result_latex": f"\\mathbf{{u}} = {col_vec_latex(u)}, \\qquad \\mathbf{{v}} = {col_vec_latex(v)}",
        "type": "initial"
    })

    # 1. Dot Product
    steps.append({
        "title": "Dot Product $\\mathbf{u} \\cdot \\mathbf{v}$",
        "description": "Multiply corresponding components and sum the products:",
        "type": "header"
    })

    term_strings = []
    product_strings = []
    dot_sum = frac(0)

    for i in range(dim):
        prod = u[i] * v[i]
        dot_sum = dot_sum + prod
        term_strings.append(f"({frac_to_latex(u[i])})({frac_to_latex(v[i])})")
        product_strings.append(frac_to_latex(prod))

    steps.append({
        "title": "Component-wise Multiplication",
        "description": "Sum of component products:",
        "operation_latex": (
            f"\\mathbf{{u}} \\cdot \\mathbf{{v}} = "
            f"{' + '.join(term_strings)} = {' + '.join(product_strings)} = {frac_to_latex(dot_sum)}"
        ),
        "type": "eliminate"
    })

    steps.append({
        "title": "Dot Product Result",
        "description": "",
        "result_latex": f"\\boxed{{\\mathbf{{u}} \\cdot \\mathbf{{v}} = {frac_to_latex(dot_sum)}}}",
        "type": "solution"
    })

    # 2. Cross Product (3D only)
    if dim == 3:
        u1, u2, u3 = u[0], u[1], u[2]
        v1, v2, v3 = v[0], v[1], v[2]

        c1 = (u2 * v3) - (u3 * v2)
        c2 = (u3 * v1) - (u1 * v3)
        c3 = (u1 * v2) - (u2 * v1)
        cross_vector = [c1, c2, c3]

        steps.append({
            "title": "Cross Product $\\mathbf{u} \\times \\mathbf{v}$ (3D)",
            "description": "Form 3×3 determinant expansion along standard unit vectors:",
            "operation_latex": (
                "\\mathbf{u} \\times \\mathbf{v} = \\begin{vmatrix}"
                "\\hat{\\imath} & \\hat{\\jmath} & \\hat{k} \\\\ "
                f"{frac_to_latex(u1)} & {frac_to_latex(u2)} & {frac_to_latex(u3)} \\\\ "
                f"{frac_to_latex(v1)} & {frac_to_latex(v2)} & {frac_to_latex(v3)}"
                "\\end{vmatrix}"
            ),
            "type": "header"
        })

        steps.append({
            "title": "Component Calculation",
            "description": "Compute each component using 2×2 sub-determinants:",
            "operation_latex": (
                "\\begin{aligned}"
                f"\\hat{{\\imath}} &: ({frac_to_latex(u2)})({frac_to_latex(v3)}) - ({frac_to_latex(u3)})({frac_to_latex(v2)}) = {frac_to_latex(c1)} \\\\[6pt]"
                f"\\hat{{\\jmath}} &: -\\left[({frac_to_latex(u1)})({frac_to_latex(v3)}) - ({frac_to_latex(u3)})({frac_to_latex(v1)})\\right] = {frac_to_latex(c2)} \\\\[6pt]"
                f"\\hat{{k}} &: ({frac_to_latex(u1)})({frac_to_latex(v2)}) - ({frac_to_latex(u2)})({frac_to_latex(v1)}) = {frac_to_latex(c3)}"
                "\\end{aligned}"
            ),
            "type": "eliminate"
        })

        steps.append({
            "title": "Cross Product Result",
            "description": "",
            "result_latex": f"\\boxed{{\\mathbf{{u}} \\times \\mathbf{{v}} = {col_vec_latex(cross_vector)}}}",
            "type": "solution"
        })
    else:
        steps.append({
            "title": "Cross Product (Not Applicable)",
            "description": f"Cross product is defined only in 3D. Given vectors are {dim}D.",
            "type": "info"
        })

    # 3. Vector Magnitudes
    u_sq_sum = frac(0)
    for x in u:
        u_sq_sum = u_sq_sum + (x * x)
    
    v_sq_sum = frac(0)
    for x in v:
        v_sq_sum = v_sq_sum + (x * x)

    u_mag = math.sqrt(float(u_sq_sum))
    v_mag = math.sqrt(float(v_sq_sum))

    steps.append({
        "title": "Vector Magnitudes",
        "description": "Euclidean length $\|\\mathbf{w}\| = \\sqrt{\\sum w_i^2}$:",
        "operation_latex": (
            "\\begin{aligned}"
            f"\\|\\mathbf{{u}}\\| &= \\sqrt{{{frac_to_latex(u_sq_sum)}}} \\approx {u_mag:.4f} \\\\[6pt]"
            f"\\|\\mathbf{{v}}\\| &= \\sqrt{{{frac_to_latex(v_sq_sum)}}} \\approx {v_mag:.4f}"
            "\\end{aligned}"
        ),
        "type": "eliminate"
    })

    # 4. Angle Theta
    if u_mag > 1e-10 and v_mag > 1e-10:
        cos_theta = float(dot_sum) / (u_mag * v_mag)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        rad = math.acos(cos_theta)
        deg = math.degrees(rad)

        steps.append({
            "title": "Angle Between Vectors",
            "description": "Using $\\cos\\theta = \\dfrac{\\mathbf{u}\\cdot\\mathbf{v}}{\\|\\mathbf{u}\\|\\|\\mathbf{v}\\|}$:",
            "result_latex": f"\\boxed{{\\theta \\approx {rad:.4f}\\text{{ rad}} \\approx {deg:.2f}^\\circ}}",
            "type": "solution"
        })

    return steps


# ==============================================================================
#  MODULE 1D — VECTOR SPACES (BASIS & RANK)
# ==============================================================================

def solve_vector_space(data):
    """
    Analyzes linear independence, basis, and column rank of a set of vectors.
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

    # Display input vectors
    vec_latex_list = []
    for i in range(k):
        vec_latex_list.append(f"\\mathbf{{v}}_{{{i+1}}} = {col_vec_latex(vecs[i])}")

    steps.append({
        "title": f"Input Vectors ({k} vectors in $\\mathbb{{R}}^{{{dim}}}$)",
        "description": "Given vector set $S$:",
        "result_latex": ", \\qquad ".join(vec_latex_list),
        "type": "initial"
    })

    # Build matrix A with vectors as columns
    A = []
    for r in range(dim):
        row = []
        for c in range(k):
            row.append(vecs[c][r])
        A.append(row)

    steps.append({
        "title": "Form Matrix $A$ (Vectors as Columns)",
        "description": "Place vectors as columns to analyze linear independence:",
        "matrix_latex": mat_to_latex(A),
        "type": "eliminate"
    })

    # Gaussian reduction to find pivots
    rows = dim
    cols = k
    pivot_count = 0

    pivot_rows = set()
    pivot_cols = []

    for c in range(cols):
        p_row = -1
        for r in range(rows):
            if r not in pivot_rows and A[r][c] != 0:
                p_row = r
                break
        
        if p_row != -1:
            pivot_count += 1
            pivot_rows.add(p_row)
            pivot_cols.append(c)

    rank = pivot_count
    is_linearly_independent = (rank == k)

    if is_linearly_independent:
        steps.append({
            "title": "✓ Linearly Independent",
            "description": f"All {k} column vectors contain pivots. The set is **linearly independent**.",
            "result_latex": f"\\text{{Rank}}(A) = {rank}",
            "type": "solution",
            "highlight": True
        })
    else:
        steps.append({
            "title": "⚠ Linearly Dependent",
            "description": f"Only {rank} out of {k} vectors have pivots. The set is **linearly dependent**.",
            "result_latex": f"\\text{{Rank}}(A) = {rank} < {k}",
            "type": "solution",
            "highlight": True
        })

    # Extract basis for Col(A)
    basis_vec_strings = []
    for col_idx in pivot_cols:
        basis_vec_strings.append(f"\\mathbf{{v}}_{{{col_idx+1}}} = {col_vec_latex(vecs[col_idx])}")

    steps.append({
        "title": "Basis for Column Space $\\text{Col}(A)$",
        "description": "The original vectors corresponding to pivot columns form a basis:",
        "result_latex": f"\\text{{Basis}} = \\left\\{{\\, {', '.join(basis_vec_strings)} \\,\\right\\}}",
        "type": "solution",
        "highlight": True
    })

    return steps
