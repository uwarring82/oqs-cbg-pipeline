#!/usr/bin/env bash
# Build the API documentation site.
#
# Sources live under docs-site/ (Sphinx + MyST + sphinx-book-theme); output
# goes to api/ at the repository root, which is served by GitHub Pages
# alongside the hand-curated landing page index.html.
#
# This script is the canonical doc-build entry point. It is idempotent and
# rebuilds from scratch (-E) so stale references cannot accumulate.
#
# Behaviour:
#   1. If a local .venv/ does not exist, create one.
#   2. Install / refresh the docs dependencies declared in pyproject.toml
#      under [project.optional-dependencies] docs.
#   3. Install the project itself in editable mode so autodoc can import
#      cbg / models / numerical / reporting.
#   4. Run sphinx-build with the project's conf.py.
#
# Usage: scripts/build_docs.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${REPO_ROOT}/.venv"
SOURCE_DIR="${REPO_ROOT}/docs-site"
OUTPUT_DIR="${REPO_ROOT}/api"
# Sphinx incremental-build cache (.doctrees, environment.pickle, .buildinfo).
# Kept inside .venv/ so it's gitignored alongside the venv itself; it must
# live OUTSIDE the served tree so the committed api/ contains only files
# meant to be served by GitHub Pages.
DOCTREE_DIR="${VENV}/.sphinx-doctrees"

cd "${REPO_ROOT}"

if [[ ! -d "${VENV}" ]]; then
    echo ">>> Creating local venv at ${VENV} ..."
    python3 -m venv "${VENV}"
fi

echo ">>> Installing docs dependencies ..."
"${VENV}/bin/python" -m pip install --quiet --upgrade pip
"${VENV}/bin/python" -m pip install --quiet sphinx myst-parser sphinx-book-theme
"${VENV}/bin/python" -m pip install --quiet -e ".[docs]" 2>/dev/null || \
    "${VENV}/bin/python" -m pip install --quiet -e .

echo ">>> Building docs from ${SOURCE_DIR} -> ${OUTPUT_DIR} ..."
rm -rf "${OUTPUT_DIR}"
"${VENV}/bin/sphinx-build" -b html -E -d "${DOCTREE_DIR}" "${SOURCE_DIR}" "${OUTPUT_DIR}"

# Remove Sphinx's tiny .buildinfo incremental-build manifest from the
# served tree. It is harmless but it is internal Sphinx state and adds
# pure noise to git commits when the only thing changing is its hash.
rm -f "${OUTPUT_DIR}/.buildinfo"

# GitHub Pages applies Jekyll by default and strips any path beginning
# with "_". Sphinx puts assets in _static/, source listings in _modules/,
# etc. — without this marker file, every CSS / JS / image referenced by
# the API site would silently 404 once deployed. Empty file is the
# canonical "disable Jekyll processing" signal documented by GitHub.
touch "${OUTPUT_DIR}/.nojekyll"

echo ">>> Done. Open ${OUTPUT_DIR}/index.html or browse via the landing page."
