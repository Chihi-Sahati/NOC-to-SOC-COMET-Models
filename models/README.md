# COMET Framework — Mathematical Models

Implementation of the core equations from the **COMET Framework** (NOC-to-SOC Unified Theory of Intelligent Service Transformation in Telecommunications).

Each file is self-contained, type-hinted, and runnable via `python <file>.py`.

---

## Model Files

| # | File | Equation | Description |
|---|------|----------|-------------|
| 1 | `edns.py` | EDNS = ∫₀ᵀ [D(t) − S(t)] · w(t) dt | **Expected Demand Not Served** — cumulative unserved demand over an evaluation period, computed via Simpson's rule numerical integration. |
| 2 | `service_graph_maturity.py` | SGMI = (1/K) Σ wₖ · (1 − exp(−α · Cₖ)) | **Service Graph Maturity Index** — measures service-graph connectivity maturity with exponential saturation. Accepts connectivity arrays or adjacency matrices. |
| 3 | `automation_velocity.py` | AV = (N_auto/N_total) · (1/t_avg) · SGMI^β · (1 − ρ) | **Automation Velocity** — rate of effective automation, combining automation ratio, speed, service graph maturity, and a sedimentation drag factor. |
| 4 | `maturity_coherence.py` | MCI = 1 − σ_L / μ_L | **Maturity Coherence Index** — coefficient-of-variation approach measuring balance across maturity dimensions. Includes a diagnostic analyzer. |
| 5 | `cultural_readiness.py` | CRC = w₁·MS + w₂·CN + w₃·ET + w₄·ES | **Cultural Readiness Coefficient** — weighted sum across mindset shift, collaboration norms, experimentation tolerance, and executive sponsorship. |
| 6 | `contextual_maturity.py` | CMF = β₁·CI + β₂·RE + β₃·CP + β₄·DG | **Contextual Maturity Factor** — external readiness via competitive intensity, regulatory enablement, customer sophistication, and digital ecosystem gap. Includes scenario analysis. |
| 7 | `regression_model.py` | TS = γ₁·MCI + γ₂·CRC + γ₃·CMF + γ₄·AV + γ₅·(CRC×TM) + γ₆·(CMF×TM) + ε | **Transformation Success regression** — OLS estimation and prediction with interaction terms. Supports `fit()` and `predict()`. |
| 8 | `mttr_decay.py` | MTTR(DFI) = MTTR₀ · exp(−λ · DFI) | **MTTR Decay** — exponential decay of Mean Time To Repair with Data Fabric Investment. Includes breakeven and curve generation utilities. |
| 9 | `cost_benefit.py` | Π(T) = ∫₀ᵀ [V_auto − C_impl] · e^{−rt} dt − C₀ | **Cost-Benefit (NPV)** — net present value of transformation investment with discounted cash flows and breakeven analysis. |
| 10 | `markov_transition.py` | P(j|i, X) = exp(X·β_ij) / Σ_l exp(X·β_il) | **Markov Transition Model** — multinomial-logit parameterised stochastic maturity evolution across discrete levels. Multi-dimensional simulation with Monte Carlo expectations. |

---

## Dependencies

- Python ≥ 3.10
- `numpy`
- `scipy`

Install with:

```bash
pip install numpy scipy
```

---

## Usage

Run any model directly for a built-in demonstration:

```bash
python models/edns.py
python models/service_graph_maturity.py
python models/automation_velocity.py
python models/maturity_coherence.py
python models/cultural_readiness.py
python models/contextual_maturity.py
python models/regression_model.py
python models/mttr_decay.py
python models/cost_benefit.py
python models/markov_transition.py
```

Or import as a module:

```python
from models.edns import compute_edns
from models.service_graph_maturity import compute_sgmi
from models.automation_velocity import compute_automation_velocity
from models.maturity_coherence import compute_mci
from models.cultural_readiness import compute_crc
from models.contextual_maturity import compute_cmf
from models.regression_model import TransformationSuccessModel
from models.mttr_decay import MTTRDecayModel
from models.cost_benefit import CostBenefitModel
from models.markov_transition import MarkovMaturityModel
```