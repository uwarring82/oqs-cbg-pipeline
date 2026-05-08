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
"${VENV}/bin/python" -m pip install --quiet sphinx myst-parser sphinx-book-theme nbconvert
"${VENV}/bin/python" -m pip install --quiet -e ".[docs]" 2>/dev/null || \
    "${VENV}/bin/python" -m pip install --quiet -e .

echo ">>> Building docs from ${SOURCE_DIR} -> ${OUTPUT_DIR} ..."
rm -rf "${OUTPUT_DIR}"
"${VENV}/bin/sphinx-build" -b html -E -d "${DOCTREE_DIR}" "${SOURCE_DIR}" "${OUTPUT_DIR}"

# Render example notebooks to static HTML alongside the API docs.
# The intro page (docs-site/examples.md) links to these as siblings; their
# outputs reflect the committed-on-disk notebook state (some notebooks are
# checked in without outputs to keep diffs clean — re-execute locally with
# `python -m jupyter nbconvert --to notebook --execute --inplace
# --ExecutePreprocessor.kernel_name=oqs-cbg examples/<nb>.ipynb` before
# rebuilding the docs to populate them; see examples/README.md for the
# kernel-registration step).
EXAMPLES_SRC="${REPO_ROOT}/examples"
EXAMPLES_OUT="${OUTPUT_DIR}/examples"
if compgen -G "${EXAMPLES_SRC}/*.ipynb" > /dev/null; then
    echo ">>> Rendering example notebooks -> ${EXAMPLES_OUT}/ ..."
    mkdir -p "${EXAMPLES_OUT}"
    # Use `python -m jupyter` so the active venv interpreter is used for any
    # in-process plumbing. The render step does NOT execute the notebooks
    # (no --execute flag): notebooks are committed with whatever outputs
    # they have, and re-execution is a separate, explicit step (see
    # examples/README.md and the kernel-registration step it documents).
    # This avoids the kernelspec resolution issue where bare `jupyter`
    # falls through to whatever kernelspec a contributor's local Jupyter
    # has registered.
    "${VENV}/bin/python" -m jupyter nbconvert \
        --to html \
        --output-dir "${EXAMPLES_OUT}" \
        "${EXAMPLES_SRC}"/*.ipynb
fi

# Remove Sphinx's tiny .buildinfo incremental-build manifest from the
# served tree. It is harmless but it is internal Sphinx state and adds
# pure noise to git commits when the only thing changing is its hash.
rm -f "${OUTPUT_DIR}/.buildinfo"

# GitHub Pages applies Jekyll by default and strips any path beginning
# with "_". Sphinx puts assets in _static/, source listings in _modules/,
# etc. — without this marker file at the Pages publishing root, every
# CSS / JS / image referenced by the API site silently 404s once deployed.
# Keep the api-local marker too so the subtree is self-describing when
# opened or copied on its own.
touch "${REPO_ROOT}/.nojekyll"
touch "${OUTPUT_DIR}/.nojekyll"

echo ">>> Done. Open ${OUTPUT_DIR}/index.html or browse via the landing page."
