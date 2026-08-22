"""
LinAlgo — Step-by-Step Linear Algebra Web Application

This file is the main Flask application controller.
It routes web browser requests to HTML templates and delegates
mathematical computations to the pure Python solver modules in `solvers/`.
"""

import traceback
from flask import Flask, render_template, request, jsonify, abort

# Import our 7 step-by-step linear algebra solvers
from solvers.unit1 import (
    solve_gaussian,       # Unit 1: Gaussian Elimination (REF + Back-Substitution)
    solve_gauss_jordan,   # Unit 1: Gauss-Jordan Elimination (RREF)
    solve_vectors,        # Unit 1: Dot/Cross Products, Magnitudes, Angle
    solve_vector_space    # Unit 1: Linear Independence, Basis, Dimension
)
from solvers.unit2 import (
    solve_determinant,    # Unit 2: Submatrix Minors & Cofactor Expansion
    solve_eigenvalues,    # Unit 2: Characteristic Equation & Eigenvectors
    solve_gram_schmidt    # Unit 2: Orthogonalization & Orthonormalization
)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'linalgo_caesar_super_secret_key_2026'
app.config['JSON_SORT_KEYS'] = False


# ==============================================================================
#  1. MODULE REGISTRY (Metadata for UI & Solver Routing)
# ==============================================================================

MODULES = {
    'gaussian': {
        'title': 'Gaussian Elimination',
        'subtitle': 'Row Echelon Form & Back-Substitution',
        'unit': 1,
        'icon': 'REF',
        'color': 'indigo',
        'input_type': 'augmented_matrix',
        'description': (
            'Convert an augmented matrix [A|b] to Row Echelon Form (REF) using '
            'elementary row operations (swap, scale, add), then apply back-substitution '
            'to extract the full solution.'
        ),
        'example': {
            'matrix': [[1, 1, 1, 6], [0, 1, -1, 1], [1, -1, 2, 5]],
            'label': 'Example: unique solution (x=7, y=0, z=−1)'
        }
    },
    'gauss-jordan': {
        'title': 'Gauss-Jordan Elimination',
        'subtitle': 'Reduced Row Echelon Form (RREF)',
        'unit': 1,
        'icon': 'RREF',
        'color': 'purple',
        'input_type': 'augmented_matrix',
        'description': (
            'Extend Gaussian Elimination to produce the full Reduced Row Echelon Form (RREF) '
            'by also eliminating entries above each pivot and scaling pivots to 1, '
            'enabling direct solution reading without back-substitution.'
        ),
        'example': {
            'matrix': [[2, 1, -1, 8], [4, -2, 2, 4], [-2, 1, 1, -2]],
            'label': 'Example: x=1, y=4, z=1'
        }
    },
    'vectors': {
        'title': 'Vector Operations',
        'subtitle': 'Dot Product · Cross Product · Angle',
        'unit': 1,
        'icon': '→',
        'color': 'teal',
        'input_type': 'two_vectors',
        'description': (
            'Compute the dot product, cross product (3D only), Euclidean magnitudes, '
            'and angle between two vectors with complete component-wise step-by-step derivation.'
        ),
        'example': {
            'u': [1, 2, 3],
            'v': [4, 5, 6],
            'label': 'Example: u=[1,2,3], v=[4,5,6]'
        }
    },
    'vector-space': {
        'title': 'Vector Spaces',
        'subtitle': 'Linear Independence · Basis · Rank',
        'unit': 1,
        'icon': '∈',
        'color': 'emerald',
        'input_type': 'multi_vectors',
        'description': (
            'Place a set of vectors as columns of a matrix A, compute RREF to identify '
            'pivot columns, determine linear independence/dependence, extract the basis '
            'for Col(A), and compute the dimension (rank).'
        ),
        'example': {
            'vectors': [[1, 0, 2], [0, 1, 3], [1, 1, 5]],
            'label': 'Example: 3 vectors in ℝ³'
        }
    },
    'determinant': {
        'title': 'Determinant',
        'subtitle': 'Minor & Cofactor Expansion',
        'unit': 2,
        'icon': '|A|',
        'color': 'amber',
        'input_type': 'square_matrix',
        'description': (
            'Calculate the determinant of a square matrix (up to 5×5) using recursive '
            'cofactor expansion along the first row, showing all minor submatrices, '
            'cofactor signs (−1)^(i+j), and scalar accumulation at each level.'
        ),
        'example': {
            'matrix': [[1, 2, 3], [4, 5, 6], [7, 2, 9]],
            'label': 'Example: 3×3 matrix'
        }
    },
    'eigenvalues': {
        'title': 'Eigenvalues & Eigenvectors',
        'subtitle': 'Characteristic Equation · det(A − λI) = 0',
        'unit': 2,
        'icon': 'λ',
        'color': 'rose',
        'input_type': 'square_matrix',
        'description': (
            'Form the characteristic polynomial det(A − λI) = 0, find its roots '
            '(eigenvalues λ), then for each λ solve the homogeneous system '
            '(A − λI)v = 0 to compute the corresponding eigenvectors.'
        ),
        'example': {
            'matrix': [[4, 1], [2, 3]],
            'label': 'Example: 2×2 matrix (λ=2, λ=5)'
        }
    },
    'gram-schmidt': {
        'title': 'Gram-Schmidt',
        'subtitle': 'Orthogonalization & Normalization',
        'unit': 2,
        'icon': '⊥',
        'color': 'sky',
        'input_type': 'multi_vectors',
        'description': (
            'Apply the Gram-Schmidt process to convert a set of linearly independent vectors '
            'into an orthogonal set {u_k}, then normalize to produce an orthonormal basis {e_k}, '
            'showing every inner product and projection computation explicitly.'
        ),
        'example': {
            'vectors': [[1, 1, 0], [1, 0, 1], [0, 1, 1]],
            'label': 'Example: 3 vectors in ℝ³'
        }
    },
}

SOLVER_MAP = {
    'gaussian':      solve_gaussian,
    'gauss-jordan':  solve_gauss_jordan,
    'vectors':       solve_vectors,
    'vector-space':  solve_vector_space,
    'determinant':   solve_determinant,
    'eigenvalues':   solve_eigenvalues,
    'gram-schmidt':  solve_gram_schmidt,
}

# ==============================================================================
#  2. FLASK HTTP ROUTES & CONTROLLERS
# ==============================================================================

@app.route('/')
def index():
    """
    Home Page:
    Displays the course overview and module cards grouped by Unit I and Unit II.
    """
    unit1_modules = {k: v for k, v in MODULES.items() if v['unit'] == 1}
    unit2_modules = {k: v for k, v in MODULES.items() if v['unit'] == 2}
    return render_template('index.html', unit1=unit1_modules, unit2=unit2_modules)


@app.route('/solver/<module_name>')
def solver_page(module_name):
    """
    Solver UI Page:
    Renders the interactive matrix/vector input interface for the selected module.
    """
    if module_name not in MODULES:
        abort(404)
    return render_template(
        'solver.html',
        module=module_name,
        meta=MODULES[module_name],
        all_modules=MODULES,
    )


@app.route('/api/solve/<module_name>', methods=['POST'])
def api_solve(module_name):
    """
    Solve API Endpoint (AJAX/Fetch):
    Receives JSON input from the web frontend, passes it to the corresponding
    linear algebra solver function, and returns step-by-step LaTeX math results.
    """
    # 1. Validate that the solver module exists
    if module_name not in MODULES:
        return jsonify({'error': f"Unknown module '{module_name}'.", 'success': False}), 404

    # 2. Parse incoming JSON payload
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.', 'success': False}), 400

    # 3. Execute mathematical solver
    try:
        solver_function = SOLVER_MAP[module_name]
        steps = solver_function(data)
        return jsonify({'steps': steps, 'success': True})
    except ValueError as exc:
        # User input validation errors (e.g. non-invertible matrix, dimension mismatch)
        return jsonify({'error': str(exc), 'success': False}), 400
    except Exception as exc:
        # Catch unexpected runtime exceptions
        traceback.print_exc()
        return jsonify({'error': f'Computation error: {exc}', 'success': False}), 500


@app.errorhandler(404)
def not_found(_e):
    """Fallback 404 error handler: safely redirects back to home template."""
    unit1_modules = {k: v for k, v in MODULES.items() if v['unit'] == 1}
    unit2_modules = {k: v for k, v in MODULES.items() if v['unit'] == 2}
    return render_template('index.html', unit1=unit1_modules, unit2=unit2_modules, error='Page not found.'), 404


if __name__ == '__main__':
    # Run the local Flask development web server
    print("Starting LinAlgo development server on http://localhost:5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)


