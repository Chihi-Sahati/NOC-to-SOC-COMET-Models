import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(BASE_DIR, "jtit_submission")

with open(os.path.join(SUB_DIR, "manuscript_final.bbl"), "r", encoding="utf-8") as f:
    bbl_content = f.read()

# Replace primary2026a
primary2026a_regex = re.compile(r'\\bibitem\{primary2026a\}(.*?)(?=\\bibitem|\Z)', re.DOTALL)
new_primary2026a = """\\bibitem{primary2026a}
Anonymous CSP. Service-centric operations transformation: A strategic roadmap to value-based operations aligned with TM forum v2.0 frameworks. Technical Report, Internal Strategic Document v2.0, 2026.

"""
bbl_content = primary2026a_regex.sub(new_primary2026a, bbl_content)

# Replace primary2026b
primary2026b_regex = re.compile(r'\\bibitem\{primary2026b\}(.*?)(?=\\bibitem|\Z)', re.DOTALL)
new_primary2026b = """\\bibitem{primary2026b}
Anonymous CSP. New-generation intelligent operations: Service-centric operations transformation. Technical Report, Internal Strategic Document v3.3, 2026.

"""
bbl_content = primary2026b_regex.sub(new_primary2026b, bbl_content)

# Now embed into the tex files
def embed_bbl(filename):
    filepath = os.path.join(SUB_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace \bibliographystyle and \bibliography with bbl_content
    content = re.sub(r'\\bibliographystyle\{[^\}]+\}\s*\\bibliography\{[^\}]+\}', bbl_content.replace('\\', '\\\\'), content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

embed_bbl("manuscript_final.tex")
embed_bbl("manuscript_blind.tex")

print("Bibliography embedded successfully.")
