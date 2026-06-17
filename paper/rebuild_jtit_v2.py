import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBMISSION_DIR = os.path.join(BASE_DIR, "jtit_submission")
INPUT_FILE = os.path.join(BASE_DIR, "comet_paper.tex")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

doc_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', content, re.DOTALL)
if not doc_match:
    exit(1)
body = doc_match.group(1)

# Extract preamble and change geometry margins if needed, but original preamble is good.
preamble = content[:doc_match.start()]

abstract_text = """The migration from Network Operations Centers to Service Operations Centers is a critical transformation in telecommunications, addressing the persistent gap between infrastructure metrics and end-user experience. Despite numerous industry frameworks, theoretical explanations remain fragmented. This paper proposes the Co-evolutionary Operations Maturity and Epistemic Transformation (COMET) theory to resolve these discrepancies. The methodology synthesizes dynamic capabilities, socio-technical systems, and boundary object theories into a unified framework of seven interconnected dimensions. Ten formal mathematical models are established to operationalize key constructs, including demand-capacity gaps, maturity coherence, and automation velocity. Through numerical simulations, the non-linear dynamics of organizational transformation are empirically validated. The results demonstrate that structural inertia triggers measurable maturity regression, and that foundational data unification yields exponential reductions in repair times. Furthermore, the findings prove that balanced cross-dimensional development predicts transformation success more accurately than isolated technological advancement. It is concluded that service graph topology construction must precede large-scale artificial intelligence deployment to achieve sustainable autonomous network orchestration."""

keywords_text = "Autonomous Networks, Digital Twin, Maturity Models, Service Operations Center."

author_final = """
\\begin{center}
{\\LARGE\\bfseries Beyond the Operations Center: A Unified Co-evolutionary Theory of NOC-to-SOC Migration in the Telecommunications Sector}\\\\[1cm]

\\textbf{AlHussein A. AlSahati}, Researcher $\\rightarrow$ Military Academy for Security and Strategic Sciences $\\rightarrow$ \\url{https://orcid.org/0009-0006-7278-4555} hussein.alagore@gmail.com $\\rightarrow$ Military Academy for Security and Strategic Sciences, Benghazi, Libya $\\rightarrow$ \\url{https://masss.edu.ly} \\\\[0.5cm]

\\textbf{Houda Chihi}, Associate Professor $\\rightarrow$ Higher School of Communication of Tunis $\\rightarrow$ \\url{https://orcid.org/0000-0002-0000-0000} houda.chihi@supcom.tn $\\rightarrow$ Higher School of Communication of Tunis (Sup'Com), University of Carthage $\\rightarrow$ \\url{http://www.supcom.mincom.tn}
\\end{center}
\\vspace{1cm}
"""

author_blind = """
\\begin{center}
{\\LARGE\\bfseries Beyond the Operations Center: A Unified Co-evolutionary Theory of NOC-to-SOC Migration in the Telecommunications Sector}\\\\[1cm]

\\textbf{[Anonymous Author 1]}, [Title] $\\rightarrow$ [Institution] $\\rightarrow$ [ORCID] [Email] $\\rightarrow$ [Faculty/University] $\\rightarrow$ [URL] \\\\[0.5cm]

\\textbf{[Anonymous Author 2]}, [Title] $\\rightarrow$ [Institution] $\\rightarrow$ [ORCID] [Email] $\\rightarrow$ [Faculty/University] $\\rightarrow$ [URL]
\\end{center}
\\vspace{1cm}
"""

frontmatter = f"""
\\section*{{Abstract}}
{abstract_text}

\\vspace{{0.3cm}}
\\noindent\\textbf{{Keywords:}} {keywords_text}
"""

# Extract Introduction
intro_match = re.search(r'\\section\{Introduction\}(.*?)\\section\{Theoretical Foundations\}', body, re.DOTALL)
intro_text = intro_match.group(1) if intro_match else ""

# Extract Theoretical Foundations and Critical Synthesis
theory_match = re.search(r'\\section\{Theoretical Foundations\}(.*?)\\section\{The COMET Theory\}', body, re.DOTALL)
theory_text = theory_match.group(1) if theory_match else ""
theory_text = theory_text.replace("\\section{Critical Synthesis of Prior Frameworks}", "\\subsection{Critical Synthesis of Prior Frameworks}")

# Footnotes for GitHub
self_cite_final = """
\\subsection{Authors' Prior Contributions}
The foundation of the COMET framework builds upon our prior work across several telecommunications domains, including unified OSS frameworks\\footnote{\\href{https://github.com/Chihi-Sahati/Unified-OSS-Framework}{Unified OSS Framework for Telecommunications Integration}}, intelligent telemetry and NetOps\\footnote{\\href{https://github.com/Chihi-Sahati/NetOps-Guardian-AI-}{NetOps Guardian AI: Intelligent Telemetry and Network Operations}}, URLLC optimization in V2X architectures\\footnote{\\href{https://github.com/Chihi-Sahati/URLLC_V2X}{URLLC Optimization in V2X Network Architectures}}, 6G RIS mobility\\footnote{\\href{https://github.com/Chihi-Sahati/v2x-6g-ris-mobility}{V2X 6G RIS Mobility: Reconfigurable Intelligent Surfaces for Edge Autonomy}}, and deterministic digital immunity\\footnote{\\href{https://github.com/Chihi-Sahati/6g-digital-immunity}{Deterministic Digital Immunity for Software-Defined 6G Networks}}. These embedded operational logics provide the empirical constraints that inform the mathematical bounds within COMET.
"""

self_cite_blind = """
\\subsection{Authors' Prior Contributions}
The foundation of the COMET framework builds upon prior work across several telecommunications domains, including unified OSS frameworks\\footnote{[Author's Prior Work - Anonymous]}, intelligent telemetry and NetOps\\footnote{[Author's Prior Work - Anonymous]}, URLLC optimization in V2X architectures\\footnote{[Author's Prior Work - Anonymous]}, 6G RIS mobility\\footnote{[Author's Prior Work - Anonymous]}, and deterministic digital immunity\\footnote{[Author's Prior Work - Anonymous]}. These embedded operational logics provide the empirical constraints that inform the mathematical bounds within COMET.
"""

related_work_final = "\\section{Related Work}\n\\subsection{Theoretical Foundations}\n" + theory_text.replace("\\subsection{", "\\subsubsection{") + self_cite_final
related_work_blind = "\\section{Related Work}\n\\subsection{Theoretical Foundations}\n" + theory_text.replace("\\subsection{", "\\subsubsection{") + self_cite_blind

# Extract The COMET Theory and Mathematical Models
research_match = re.search(r'\\section\{The COMET Theory\}(.*?)\\section\{Discussion\}', body, re.DOTALL)
research_text = research_match.group(1) if research_match else ""

# Replace \section{Mathematical Models} with \subsection{The COMET Framework and Mathematical Formulation}
research_text = research_text.replace("\\section{Mathematical Models}", "\\subsection{The COMET Framework and Mathematical Formulation}")
# Also demote \section{The COMET Theory} which is currently implied as the start of the block, but it's not captured. 
# The regex started *after* \section{The COMET Theory}. So we need to add it.
research_text = "\\subsection{The COMET Theory}\n" + research_text
research_text = research_text.replace("\\subsection{", "\\subsubsection{").replace("\\subsubsection{The COMET Theory}", "\\subsection{The COMET Theory}").replace("\\subsubsection{The COMET Framework and Mathematical Formulation}", "\\subsection{The COMET Framework and Mathematical Formulation}")


simulation_narrative = """
\\subsection{Numerical Simulations}

To empirically validate the mathematical formulations of the COMET framework, a 36-month numerical simulation was conducted focusing on three operator archetypes: Advanced, Mid-tier, and Lagging. The simulation results explicitly operationalize the preceding mathematical models.

\\subsubsection{Cumulative EDNS Integration}
Aligning with Equation \\ref{eq:edns}, Figure \\ref{fig:edns} visualizes the cumulative Expected Demand Not Served. The numerical integration over 36 months shows how the gap between expected demand ($D(t)$) and served capacity ($S(t)$) accumulates, reinforcing the paradigm shift from binary availability to demand-weighted impact.

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{figures/edns.png}
\\caption{Cumulative temporal integration of Expected Demand Not Served (EDNS) as formulated in Equation \\ref{eq:edns}.}
\\label{fig:edns}
\\end{figure}

\\subsubsection{Data Fabric and MTTR Exponential Decay}
As formulated in Equation \\ref{eq:mttr}, the relationship between Data Fabric Investment (DFI) and Mean Time to Repair (MTTR) exhibits exponential decay. Figure \\ref{fig:dfi} illustrates this relationship. Foundational data unification yields drastic MTTR drops, validating the exponential parameter $\\lambda$.

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{figures/dfi_vs_mttr.png}
\\caption{Exponential decay of MTTR as a function of Data Fabric Investment (DFI).}
\\label{fig:dfi}
\\end{figure}

\\subsubsection{Maturity Coherence and Transformation Trajectories}
The evolution of the Maturity Coherence Index (MCI) (Equation \\ref{eq:mci}) was simulated using the Markov Transition Model (Equation \\ref{eq:markov}). As shown in Figure \\ref{fig:mci}, operators with a high Cultural Readiness Composite (CRC) successfully prevent backsliding, stabilizing their transformation trajectory. 

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{figures/mci_evolution.png}
\\caption{MCI evolution over a 36-month simulation horizon across three operator archetypes.}
\\label{fig:mci}
\\end{figure}

\\subsubsection{Investment Prioritization and Cost-Benefit}
The economic viability of closed-loop automation is evaluated through the NPV trajectory formulated in Equation \\ref{eq:costbenefit}. Figure \\ref{fig:cost} demonstrates that the Service Graph Maturity Index (SGMI) must reach a critical threshold before large-scale AI deployment to achieve a positive Net Present Value $\\Pi(T)$.

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{figures/cost_benefit_pi.png}
\\caption{Cost-Benefit function $\\Pi(T)$ over time, highlighting break-even points.}
\\label{fig:cost}
\\end{figure}
"""

research_conducted = "\\section{Research Conducted}\n" + research_text + simulation_narrative

# Extract Discussion and Conclusion
discuss_match = re.search(r'\\section\{Discussion\}(.*?)\\newpage', body, re.DOTALL)
discuss_text = "\\section{Discussion}\n" + (discuss_match.group(1) if discuss_match else "")

# References part
refs = """
\\newpage
\\bibliographystyle{unsrt}
\\bibliography{references}
\\end{document}
"""

doc_final = preamble + "\\begin{document}\n" + author_final + frontmatter + "\\section{Introduction}\n" + intro_text + related_work_final + research_conducted + discuss_text + refs
doc_blind = preamble + "\\begin{document}\n" + author_blind + frontmatter + "\\section{Introduction}\n" + intro_text + related_work_blind + research_conducted + discuss_text + refs

with open(os.path.join(SUBMISSION_DIR, "manuscript_final.tex"), "w", encoding="utf-8") as f:
    f.write(doc_final)

with open(os.path.join(SUBMISSION_DIR, "manuscript_blind.tex"), "w", encoding="utf-8") as f:
    f.write(doc_blind)

print("Files generated successfully.")
