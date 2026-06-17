import os
import re
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(BASE_DIR, "jtit_submission")

# 1. Regenerate cleanly
print("Regenerating base files...")
subprocess.run(["python", "rebuild_jtit_v2.py"], cwd=BASE_DIR, check=True)

# 2. Fix preamble, URLs, and double end{document}
print("Applying fixes...")
def apply_fixes(filename, is_final):
    filepath = os.path.join(SUB_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Inject natbib before hyperref
    if "\\usepackage[numbers]{natbib}" not in content:
        content = content.replace("\\usepackage{hyperref}", "\\usepackage[numbers]{natbib}\n\\usepackage{hyperref}")

    # Fix URLs
    if is_final:
        content = content.replace("\\url{https://masss.edu.ly}", "\\url{https://www.masss.edu.ly/}")
        content = content.replace("\\url{http://www.supcom.mincom.tn}", "\\url{https://supcom.tn/}")

    # Remove second \end{document} if exists
    parts = content.split("\\end{document}")
    if len(parts) > 2:
        content = parts[0] + "\\end{document}" + "".join(parts[1:-1])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

apply_fixes("manuscript_final.tex", True)
apply_fixes("manuscript_blind.tex", False)

# 3. First pass compile
print("Compiling first pass...")
for f in ["manuscript_final", "manuscript_blind"]:
    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{f}.tex"], cwd=SUB_DIR, stdout=subprocess.DEVNULL)
    subprocess.run(["bibtex", f], cwd=SUB_DIR, stdout=subprocess.DEVNULL)

# 4. Patch BBL and embed
print("Patching BBL and embedding...")
def patch_and_embed(filename):
    bbl_path = os.path.join(SUB_DIR, f"{filename}.bbl")
    with open(bbl_path, "r", encoding="utf-8") as f:
        bbl_content = f.read()

    primary2026a_regex = re.compile(r'\\bibitem\{primary2026a\}(.*?)(?=\\bibitem|\Z)', re.DOTALL)
    new_primary2026a = "\\\\bibitem{primary2026a}\nAnonymous CSP. Service-centric operations transformation: A strategic roadmap to value-based operations aligned with TM forum v2.0 frameworks. Technical Report, Internal Strategic Document v2.0, 2026.\n\n"
    bbl_content = primary2026a_regex.sub(new_primary2026a, bbl_content)

    primary2026b_regex = re.compile(r'\\bibitem\{primary2026b\}(.*?)(?=\\bibitem|\Z)', re.DOTALL)
    new_primary2026b = "\\\\bibitem{primary2026b}\nAnonymous CSP. New-generation intelligent operations: Service-centric operations transformation. Technical Report, Internal Strategic Document v3.3, 2026.\n\n"
    bbl_content = primary2026b_regex.sub(new_primary2026b, bbl_content)

    tex_path = os.path.join(SUB_DIR, f"{filename}.tex")
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the bib block and replace it. Use regex to find it, but standard string replace.
    match = re.search(r'\\bibliographystyle\{[^\}]+\}\s*\\bibliography\{[^\}]+\}', content)
    if match:
        content = content[:match.start()] + bbl_content + content[match.end():]
    
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(content)

patch_and_embed("manuscript_final")
patch_and_embed("manuscript_blind")

# 5. Final compile
print("Final compile...")
for f in ["manuscript_final", "manuscript_blind"]:
    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{f}.tex"], cwd=SUB_DIR, stdout=subprocess.DEVNULL)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"{f}.tex"], cwd=SUB_DIR, stdout=subprocess.DEVNULL)

# 6. Cleanup and ZIP
print("Cleaning up...")
for ext in [".aux", ".bbl", ".blg", ".log", ".out"]:
    for f in ["manuscript_final", "manuscript_blind"]:
        try:
            os.remove(os.path.join(SUB_DIR, f"{f}{ext}"))
        except:
            pass

zip_path = os.path.join(SUB_DIR, "jtit_submission.zip")
if os.path.exists(zip_path):
    os.remove(zip_path)

subprocess.run(["powershell", "-Command", "Compress-Archive -Path * -DestinationPath jtit_submission.zip -Force"], cwd=SUB_DIR)

print("Done!")
