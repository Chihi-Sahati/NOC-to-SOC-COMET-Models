import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUB_DIR = os.path.join(BASE_DIR, "jtit_submission")

def fix_tex_file(filepath, is_final):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Fix syntax error
    content = content.replace("\\usepackage[numbers]{natbib}`n\\usepackage{hyperref}", "\\usepackage[numbers]{natbib}\n\\usepackage{hyperref}")
    
    # Also handle standard \usepackage[numbers]{natbib}\n\usepackage{hyperref} if it was mangled differently
    content = re.sub(r'\\usepackage\[numbers\]\{natbib\}[^\\\n]*\\usepackage\{hyperref\}', '\\\\usepackage[numbers]{natbib}\n\\\\usepackage{hyperref}', content)

    # 2. Fix URLs (only in final)
    if is_final:
        content = content.replace("\\url{https://masss.edu.ly}", "\\url{https://www.masss.edu.ly/}")
        content = content.replace("\\url{http://www.supcom.mincom.tn}", "\\url{https://supcom.tn/}")

    # 3. Ensure exactly one \end{document}
    parts = content.split("\\end{document}")
    if len(parts) > 2:
        content = parts[0] + "\\end{document}" + "".join(parts[1:-1])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

fix_tex_file(os.path.join(SUB_DIR, "manuscript_final.tex"), True)
fix_tex_file(os.path.join(SUB_DIR, "manuscript_blind.tex"), False)

print("Fixed tex files.")
