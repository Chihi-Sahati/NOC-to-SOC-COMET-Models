#!/bin/bash
# =============================================================================
# build_paper.sh — Build the COMET Framework LaTeX paper
#
# This script compiles the LaTeX source into PDF and exports a DOCX version
# via pandoc. It runs pdflatex three times (to resolve cross-references) with
# a bibtex pass in between for bibliography processing.
#
# Usage:
#   bash scripts/build_paper.sh
#
# Prerequisites:
#   - TeX Live (or MiKTeX) with pdflatex and bibtex on PATH
#   - pandoc (optional; DOCX export will be skipped if not found)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PAPER_DIR="${SCRIPT_DIR}/../paper"
TEX_FILE="comet_paper.tex"
MAIN_NAME="comet_paper"

echo "========================================"
echo "  COMET Framework — Paper Build Script"
echo "========================================"
echo ""

# Navigate to the paper directory
cd "${PAPER_DIR}"

# Verify the main TeX file exists
if [ ! -f "${TEX_FILE}" ]; then
    echo "ERROR: ${TEX_FILE} not found in ${PAPER_DIR}" >&2
    exit 1
fi

# --- Pass 1: Initial pdflatex run (generates .aux for bibtex) ---
echo "[1/5] First pdflatex pass..."
pdflatex -interaction=nonstopmode "${TEX_FILE}" > /dev/null 2>&1 || {
    echo "WARNING: pdflatex pass 1 returned non-zero exit code."
    echo "         Check ${MAIN_NAME}.log for details."
}

# --- Pass 2: bibtex (resolves citations and bibliography) ---
echo "[2/5] Running bibtex..."
if [ -f "${MAIN_NAME}.aux" ]; then
    bibtex "${MAIN_NAME}" > /dev/null 2>&1 || {
        echo "WARNING: bibtex returned non-zero exit code."
        echo "         Check ${MAIN_NAME}.blg for details."
    }
else
    echo "WARNING: ${MAIN_NAME}.aux not found — skipping bibtex."
fi

# --- Pass 3: Second pdflatex run (incorporates bibliography) ---
echo "[3/5] Second pdflatex pass..."
pdflatex -interaction=nonstopmode "${TEX_FILE}" > /dev/null 2>&1 || {
    echo "WARNING: pdflatex pass 2 returned non-zero exit code."
}

# --- Pass 4: Third pdflatex run (resolves all cross-references) ---
echo "[4/5] Third pdflatex pass..."
pdflatex -interaction=nonstopmode "${TEX_FILE}" > /dev/null 2>&1 || {
    echo "WARNING: pdflatex pass 3 returned non-zero exit code."
}

# Verify PDF was produced
if [ -f "${MAIN_NAME}.pdf" ]; then
    echo "      PDF generated: ${MAIN_NAME}.pdf ($(du -h "${MAIN_NAME}.pdf" | cut -f1))"
else
    echo "ERROR: ${MAIN_NAME}.pdf was not generated." >&2
    exit 1
fi

# --- Pass 5: Export to DOCX via pandoc (optional) ---
echo "[5/5] Exporting to DOCX..."
if command -v pandoc &> /dev/null; then
    pandoc "${TEX_FILE}" -o "${MAIN_NAME}.docx" 2>/dev/null || {
        echo "WARNING: pandoc DOCX export returned non-zero exit code."
    }
    if [ -f "${MAIN_NAME}.docx" ]; then
        echo "      DOCX exported: ${MAIN_NAME}.docx ($(du -h "${MAIN_NAME}.docx" | cut -f1))"
    fi
else
    echo "      pandoc not found — skipping DOCX export."
    echo "      (Install pandoc to enable DOCX generation.)"
fi

echo ""
echo "========================================"
echo "  Build complete!"
echo "  Output: ${PAPER_DIR}/${MAIN_NAME}.pdf"
echo "========================================"
