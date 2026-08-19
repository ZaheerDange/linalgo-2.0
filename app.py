"""
LinAlgo - Step-by-Step Linear Algebra Solver
Main Flask application entry point.
"""

import traceback
from flask import Flask, render_template, request, jsonify, abort, session, redirect, url_for, flash

from solvers.unit1 import solve_gaussian, solve_gauss_jordan, solve_vectors, solve_vector_space
from solvers.unit2 import solve_determinant, solve_eigenvalues, solve_gram_schmidt
import database as db

app = Flask(__name__)
app.secret_key = 'linalgo_caesar_super_secret_key_2026'
app.config['JSON_SORT_KEYS'] = False


@app.context_processor
def inject_user():
    """Injects current logged-in user into all Jinja2 templates."""
    user_id = session.get('user_id')
    if user_id:
        current_user = db.get_user_by_id(user_id)
        return dict(current_user=current_user)
    return dict(current_user=None)

# ──────────────────────────────────────────────────────────────────────────────
# Module Registry
# ──────────────────────────────────────────────────────────────────────────────

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

# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    unit1 = {k: v for k, v in MODULES.items() if v['unit'] == 1}
    unit2 = {k: v for k, v in MODULES.items() if v['unit'] == 2}
    return render_template('index.html', unit1=unit1, unit2=unit2)


@app.route('/solver/<module_name>')
def solver_page(module_name):
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
    if module_name not in MODULES:
        return jsonify({'error': 'Unknown solver module.', 'success': False}), 404

    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({'error': 'Request body must be valid JSON.', 'success': False}), 400

    user_id = session.get('user_id')
    rem_credits = None
    if user_id:
        success, rem_credits, msg = db.deduct_credit(user_id)
        if not success:
            return jsonify({
                'error': 'INSUFFICIENT_CREDITS',
                'message': 'You have run out of credits! Please top up on the Pricing portal.',
                'success': False
            }), 402

    try:
        steps = SOLVER_MAP[module_name](data)

        # Automatically record calculation in user history if logged in
        if user_id:
            db.save_solution_history(
                user_id=user_id,
                module_name=module_name,
                module_title=MODULES[module_name]['title'],
                input_data=data,
                steps=steps
            )

        return jsonify({'steps': steps, 'remaining_credits': rem_credits, 'success': True})
    except ValueError as exc:
        return jsonify({'error': str(exc), 'success': False}), 400
    except Exception as exc:
        traceback.print_exc()
        return jsonify({'error': f'Computation error: {exc}', 'success': False}), 500


@app.route('/pricing')
def pricing():
    """Pricing & Subscription Upgrade Portal."""
    return render_template('pricing.html')


@app.route('/api/buy-credits', methods=['POST'])
def api_buy_credits():
    """Simulated credit purchase & subscription upgrade handler."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Please sign in to buy credits.', 'success': False}), 401

    payload = request.get_json(force=True, silent=True) or {}
    plan = payload.get('plan')

    if plan == 'weekly':
        updated_user = db.add_credits_to_user(user_id, 200, plan_name='weekly')
        return jsonify({
            'success': True,
            'message': 'Weekly Pro Pass activated! 200 Credits added to your account.',
            'user': updated_user
        })
    elif plan == 'lifetime':
        updated_user = db.set_lifetime_unlimited_user(user_id)
        return jsonify({
            'success': True,
            'message': 'Lifetime Unlimited VIP Pass activated! You now have unlimited calculations forever.',
            'user': updated_user
        })
    else:
        return jsonify({'error': 'Invalid plan selection.', 'success': False}), 400


# ──────────────────────────────────────────────────────────────────────────────
# Authentication Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if password != confirm_password:
            return render_template(
                'register.html',
                error="Passwords do not match. Please try again.",
                username=username,
                email=email,
            )

        user, err = db.create_user(username, email, password)
        if err:
            return render_template(
                'register.html',
                error=err,
                username=username,
                email=email,
            )

        # Automatically log user in upon successful registration
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f"Welcome to LinAlgo, {user['username']}! Your account was created successfully.", "success")
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        user = db.get_user_by_username_or_email(identifier)
        if not user or not db.verify_password(user['password_hash'], password):
            return render_template(
                'login.html',
                error="Invalid username/email or password.",
                identifier=identifier,
            )

        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    username = session.pop('username', None)
    session.pop('user_id', None)
    if username:
        flash(f"You have been signed out successfully.", "info")
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please sign in to view your profile and saved history.", "info")
        return redirect(url_for('login'))

    user = db.get_user_by_id(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))

    history_items = db.get_user_solution_history(user_id, limit=30)
    return render_template('profile.html', user=user, history_items=history_items)


@app.route('/history/<int:history_id>')
def history_detail(history_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("Please sign in to view saved solutions.", "info")
        return redirect(url_for('login'))

    solution = db.get_solution_by_id(history_id, user_id=user_id)
    if not solution:
        flash("Saved solution not found.", "error")
        return redirect(url_for('profile'))

    meta = MODULES.get(solution['module_name'], {
        'title': solution['module_title'],
        'subtitle': 'Saved Calculation',
        'unit': 1,
        'icon': '∑',
        'color': 'burgundy',
        'description': 'Saved linear algebra calculation history record.'
    })

    return render_template(
        'history_detail.html',
        solution=solution,
        meta=meta,
        module=solution['module_name'],
        all_modules=MODULES
    )


@app.route('/api/history/delete/<int:history_id>', methods=['POST', 'DELETE'])
def api_delete_history(history_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized', 'success': False}), 401

    success = db.delete_solution_history(history_id, user_id)
    if success:
        return jsonify({'success': True, 'message': 'Calculation removed from history.'})
    else:
        return jsonify({'success': False, 'error': 'Could not delete item or record not found.'}), 404



@app.errorhandler(404)
def not_found(_e):
    unit1 = {k: v for k, v in MODULES.items() if v['unit'] == 1}
    unit2 = {k: v for k, v in MODULES.items() if v['unit'] == 2}
    return render_template('index.html', unit1=unit1, unit2=unit2, error='Page not found.'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


