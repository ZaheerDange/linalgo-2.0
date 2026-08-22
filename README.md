# 🧮 LinAlgo — Step-by-Step Linear Algebra Solver

**LinAlgo** is a production-grade, full-stack Python Flask web application designed for solving complex linear algebra problems with complete, human-readable, step-by-step mathematical derivations.

---

## ✨ Features

- **Exact Rational Arithmetic**: Uses Python's `fractions.Fraction` — 0 floating-point drift or rounding errors.
- **TeX MathJax 3 Rendering**: All matrices, row operations, cofactor expansions, and vectors are rendered in textbook-quality LaTeX.
- **7 Solver Modules**:
  1. **Gaussian Elimination**: Row Echelon Form (REF) + Back-Substitution.
  2. **Gauss-Jordan Elimination**: Reduced Row Echelon Form (RREF).
  3. **Vector Operations**: Dot product, 3D cross product, Euclidean magnitudes, and angles.
  4. **Vector Spaces**: Linear independence, basis extraction, and column space rank.
  5. **Determinant**: Submatrix minor & cofactor expansion step-by-step.
  6. **Eigenvalues & Eigenvectors**: Characteristic polynomial $\det(A - \lambda I) = 0$ solving.
  7. **Gram-Schmidt**: Orthogonalization and orthonormal basis normalization.
- **Open & Direct Access**: No logins, subscriptions, or credit barriers needed.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/linalgo.git
cd linalgo
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Flask Web Application
```bash
python app.py
```

### 4. Open in Browser
Navigate to `http://localhost:5000` in your browser.

---

## 🛠️ Project Architecture

```
linalgo/
├── app.py                # Main Flask application & API routes
├── database.py           # SQLite database manager & credit balance handlers
├── requirements.txt      # Python dependencies (Flask, SymPy, NumPy)
├── solvers/              # Pure Python step-by-step linear algebra solvers
│   ├── unit1.py          # Gaussian, Gauss-Jordan, Vectors, Vector Spaces
│   └── unit2.py          # Determinant, Eigenvalues, Gram-Schmidt
├── static/               # Frontend assets
│   ├── css/style.css     # Glassmorphic Caesar dark theme
│   └── js/solver.js      # Dynamic form building, API handling & MathJax
└── templates/            # Jinja2 HTML templates
    ├── base.html         # Navbar, layout & user context
    ├── index.html        # Home page & module grid
    ├── login.html        # Sign In portal
    ├── register.html     # Account registration
    ├── profile.html      # User dashboard
    ├── pricing.html      # Upgrade & Credit portal
    └── solver.html       # Dynamic solver page
```

---

## 📜 License
This project is open-source under the MIT License.
