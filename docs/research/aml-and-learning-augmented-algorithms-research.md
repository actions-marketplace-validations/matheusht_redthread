# AML and Learning-Augmented Algorithms Research Map

Status: curated research map  
Scope: adversarial machine learning, learning-augmented algorithms, and robust algorithms with untrusted predictions  
Source policy: this file stores metadata, summaries, links, and research opportunities only. It does not copy full paper text.

## 1. Executive summary

Two research streams are starting to rhyme:

1. **Adversarial machine learning (AML)** studies what happens when model inputs, training data, context, labels, or deployment surfaces are controlled by an attacker.
2. **Learning-augmented algorithms** study what happens when a classical algorithm receives ML advice that may be good, stale, noisy, or wrong.

The shared question is simple:

> What should a system do when prediction helps in normal cases but can fail under error, drift, or attack?

This creates a strong paper direction: treat untrusted ML advice as an algorithmic input-corruption problem. The AML side gives threat models. The algorithms side gives worst-case guarantees, fallback logic, and consistency/robustness tradeoffs.

Best near-term topics:

1. **Adversarial Prediction Models for Learning-Augmented Algorithms**
2. **Robust ML Advice in Online Algorithms**
3. **Poisoning the Data Supply Chain of Generative Models**
4. **Distillation as an Amplifier for Adversarial Bias**
5. **Benchmarking Algorithms Under Wrong Predictions**

## 2. Paper map: adversarial machine learning

### 2.1 Adversarial Machine Learning: Attacks, Defenses, and Open Challenges

- URL: https://arxiv.org/html/2502.05637v1
- Area: AML survey
- Paper type: survey / taxonomy
- Main contribution: gives a broad map of evasion attacks, poisoning attacks, defense mechanisms, adaptive threat models, and open challenges around certified robustness, scalability, and deployment.
- Threat model: adversary manipulates model inputs, training data, or deployment conditions to reduce model reliability or force targeted behavior.
- Methods covered: evasion attacks, poisoning attacks, adversarial training, detection, certified defenses, adaptive attacks.
- Limits / gaps: broad survey framing; needs concrete cross-domain benchmarks for modern agentic, generative, and tool-using systems.
- Research subtopics enabled:
  - certified robustness under adaptive attackers
  - deployment-time AML evaluation
  - AML for agentic systems
  - robustness metrics that combine accuracy, safety, and operational cost

### 2.2 A Comprehensive Review of Adversarial Attacks on Machine Learning

- URL: https://arxiv.org/abs/2412.11384
- Area: AML survey and practice
- Paper type: review with practical simulation focus
- Main contribution: reviews adversarial attack types, business implications, mitigation strategies, and uses the Adversarial Robustness Toolbox to simulate attacks in practical settings such as self-driving use cases.
- Threat model: adversary crafts malicious inputs or conditions to exploit model weaknesses.
- Methods covered: attack comparisons, ART-based simulations, mitigation overview.
- Limits / gaps: appears practice-oriented and broad; does not by itself settle which defenses hold against adaptive real-world attackers.
- Research subtopics enabled:
  - practitioner-facing AML benchmark design
  - translating AML attacks into business risk
  - evaluating defense claims with reproducible attack harnesses

### 2.3 Data Poisoning in Deep Learning: A Survey

- URL: https://arxiv.org/abs/2503.22759
- Area: data poisoning
- Paper type: survey
- Main contribution: focused survey on data poisoning attacks in deep learning, including attack categories, design principles, LLM poisoning, open challenges, and a companion resource repository.
- Threat model: adversary inserts or manipulates training data to degrade accuracy, create targeted behavior, or induce anomalous model behavior.
- Methods covered: poisoning categories across deep learning, LLM-focused poisoning, attack design principles.
- Limits / gaps: survey of attacks more than a unified defense benchmark; needs connection to data supply-chain governance.
- Research subtopics enabled:
  - poisoning-resistant training pipelines
  - provenance-aware dataset curation
  - LLM poisoning and downstream model behavior
  - data supply-chain security for foundation models

### 2.4 On the Feasibility of Poisoning Text-to-Image AI Models via Adversarial Mislabeling

- URL: https://arxiv.org/html/2506.21874v1
- Area: poisoning, generative models, vision-language labeling
- Paper type: empirical attack paper
- Main contribution: shows that adversarial perturbations can cause VLM-based captioning or labeling systems to mislabel images, enabling dirty-label poisoning of text-to-image training data. Reported black-box success is over 73% against commercial VLMs in the extracted summary.
- Threat model: attacker modifies images so automated data-captioning or labeling pipelines assign attacker-shaped labels while images remain usable in the training set.
- Methods covered: adversarial perturbations against VLM labeling, dirty-label poisoning setup, black-box evaluation, defense stress testing.
- Limits / gaps: needs careful replication across datasets, caption pipelines, filtering systems, and model families. Defense results depend on adaptive attacker assumptions.
- Research subtopics enabled:
  - adversarial mislabeling as data supply-chain attack
  - robust captioning for model training data
  - dataset filtering under adaptive perturbations
  - provenance and audit trails for generative model corpora

### 2.5 Stealthy Cross-Origin Context Poisoning Attacks against AI Coding Assistants

- URL: https://arxiv.org/html/2503.14281v4
- Area: coding assistant security, context poisoning
- Paper type: empirical attack paper
- Main contribution: introduces the XOXO attack, where semantics-preserving transformations poison cross-origin context used by AI coding assistants. The extracted summary reports Greedy Cayley Graph Search and average attack success of 73.20% across eight models, with vulnerability injection up to 66.67% and a GitHub Copilot demo.
- Threat model: attacker controls or influences code/context from another origin that is later consumed by a coding assistant, causing insecure suggestions while preserving apparent semantics.
- Methods covered: semantics-preserving transformations, search over transformed code/context, coding assistant vulnerability injection tests.
- Limits / gaps: results may vary by model, IDE context policy, prompt construction, and user review behavior. Needs defenses at context ingestion and provenance boundaries.
- Research subtopics enabled:
  - context poisoning as input-corruption problem
  - provenance-aware coding agents
  - robust retrieval/context selection for developer tools
  - benchmark design for secure code assistant context handling

### 2.6 Cascading Adversarial Bias from Injection to Distillation in Language Models

- URL: https://arxiv.org/html/2505.24842v2
- Area: poisoning, distillation, bias propagation
- Paper type: empirical attack / measurement paper
- Main contribution: shows that small poisoning of a teacher model can propagate and amplify in a distilled student. Extracted details include 25 poisoned samples / 0.25% poisoning rate, targeted student bias at 76.9% vs 69.4% teacher, and untargeted propagation 5.7x to 29.2x more frequent in students on unseen tasks.
- Threat model: adversary poisons or biases teacher behavior or training examples, then distillation transfers and amplifies the bias into student models.
- Methods covered: targeted and untargeted poisoning, teacher-student distillation evaluation, defense checks with perplexity filtering, bias detection, and LLM autoraters.
- Limits / gaps: needs broader replication across model families, distillation recipes, and defense stacks. Also needs operational guidance for model supply chains.
- Research subtopics enabled:
  - distillation as adversarial amplification
  - model supply-chain security
  - bias propagation metrics
  - defense failure analysis for weak poisoning signals

## 3. Topic 1 map: Learning-Augmented Algorithms: When ML Advice Helps Classical Algorithms

Learning-augmented algorithms use predictions to improve average-case performance while trying to preserve worst-case guarantees. The core tension is this:

> If the prediction is good, the algorithm should exploit it. If the prediction is bad, the algorithm should not collapse.

### 3.1 Prediction-specific online algorithm design

Key source:

- **Prediction-Specific Design of Learning-Augmented Algorithms**
- URL: https://arxiv.org/abs/2510.14887

Summary:

The paper argues that many existing algorithms with predictions are too conservative. Instead of only optimizing coarse consistency/robustness tradeoffs, it proposes prediction-specific performance criteria and strongly-optimal algorithms. It introduces a bi-level optimization framework and applies it to ski rental, randomized ski rental, and one-max search, with case studies in dynamic power management and volatility-based index trading.

Research questions:

- Can prediction-specific algorithms outperform generic robust algorithms in real workloads?
- Which online problems have exploitable prediction structure?
- Can prediction-specific design survive adversarial predictions?
- Can the bi-level framework be used for scheduling, caching, routing, or resource allocation?

Possible article angle:

> Learning-augmented algorithms should not treat all wrong predictions equally. The structure of the prediction error matters.

### 3.2 Tradeoffs: consistency, robustness, smoothness, and average performance

Key source:

- **On Tradeoffs in Learning-Augmented Algorithms**
- URL: https://arxiv.org/abs/2501.12770

Summary:

The paper studies how learning-augmented algorithms balance consistency, robustness, smoothness, and expected performance. It argues that Pareto-optimal consistency/robustness tradeoffs can harm smoothness in some settings, and that multiple tradeoffs must be considered together.

Research questions:

- When does better consistency make robustness worse?
- When does better robustness make algorithm behavior unstable or less smooth?
- What metrics should be reported beyond competitive ratio?
- How should distributional prediction information be used without losing worst-case safety?

Possible article angle:

> The classic consistency-vs-robustness story is incomplete. Smoothness and expected performance matter too.

### 3.3 Advice-augmented caching, scheduling, and streaming

This is a strong subtopic family because online decisions are common in real systems.

Research questions:

- Caching: how should a cache use predicted next access times when predictions are stale or adversarial?
- Scheduling: how should a scheduler use predicted job sizes or deadlines when predictions are biased?
- Streaming: how should streaming algorithms use learned sketches, priors, or forecasts under drift?
- Resource allocation: how should systems use ML demand forecasts without creating failure cliffs?

Possible article angle:

> ML advice is most valuable when the algorithm can use it locally, measure error, and fall back safely.

### 3.4 Benchmark design for ML-advised algorithms

Many papers report strong results under chosen error models. A useful research contribution would be a benchmark suite that varies the trust model.

Benchmark axes:

- perfect predictions
- random noise
- stale predictions
- biased predictions
- distribution shift
- adversarial predictions
- strategically corrupted predictions
- missing predictions

Metrics:

- consistency
- robustness
- smoothness
- average performance
- tail failure
- recovery time after bad advice
- cost of fallback
- sensitivity to prediction error

Possible article angle:

> Learning-augmented algorithm benchmarks should test prediction failure as a first-class workload, not as an appendix.

## 4. Topic 2 map: Robust Algorithms with Untrusted Predictions

This topic is the sharper and more security-relevant version of topic 1.

Core thesis:

> A prediction should be treated like an untrusted input. Good algorithms can benefit from it, but must bound harm when it is wrong or malicious.

### 4.1 Robustness-consistency tradeoff under adversarial prediction

The basic promise of learning-augmented algorithms is:

- **consistency:** near-optimal behavior when predictions are accurate
- **robustness:** bounded damage when predictions are wrong

Security framing adds:

- predictions may be attacker-controlled
- prediction errors may be targeted, not random
- the attacker may know the fallback rule
- bad advice may be rare but high-impact

Research questions:

- What competitive ratios are possible against adaptive adversarial predictions?
- Can algorithms detect when predictions are strategically wrong?
- Which fallback rules are robust to targeted manipulation?
- Is there a formal bridge between AML threat models and learning-augmented algorithms?

### 4.2 Learning-Augmented Robust Algorithmic Recourse

Key source:

- **Learning-Augmented Robust Algorithmic Recourse**
- URL: https://arxiv.org/abs/2410.01580

Summary:

The paper applies learning-augmented design to algorithmic recourse. Recourse should help people change outcomes under a model, but models get updated. Robust recourse handles adversarial model changes at higher cost. This paper studies how predictions of the future model can reduce cost when accurate while bounding cost when inaccurate.

Algorithmic model:

- A decision system changes over time.
- A designer has a prediction of the future model.
- The algorithm chooses recourse that trades lower cost under good prediction against protection under bad prediction.

Research questions:

- Can recourse systems expose a tunable consistency/robustness parameter?
- What happens if the predicted future model is strategically manipulated?
- Can learning-augmented recourse be audited for fairness and safety?
- How should recourse systems report uncertainty to affected users?

Possible article angle:

> Recourse is a human-facing example of untrusted predictions: wrong advice creates real cost.

### 4.3 Graceful degradation and fallback design

Good robust algorithms should not have cliffs. Bad predictions should cause bounded degradation, not catastrophic failure.

Fallback mechanisms:

- ignore prediction after error threshold
- blend predicted and classical policy
- use confidence-weighted advice
- maintain a safe baseline in parallel
- audit prediction drift before use
- cap the maximum influence of one prediction

Research questions:

- How much performance should be sacrificed for safe fallback?
- Can fallback rules be learned without becoming another attack surface?
- What is the right unit of trust: prediction, model, source, time window, or workload?

### 4.4 Trust calibration for ML advice

The algorithm should ask: how much should this prediction matter?

Trust signals:

- historical prediction error
- source provenance
- uncertainty estimates
- distribution shift indicators
- adversarial anomaly signals
- agreement between independent predictors

Security risk:

If trust calibration is itself learned, it can be attacked. This creates a second-order problem: robust algorithms need robust trust estimators.

Research questions:

- Can trust be calibrated with formal worst-case bounds?
- Can AML detection feed into algorithmic fallback rules?
- When should a system prefer a worse but trusted baseline over a better but untrusted prediction?

### 4.5 Robust predictions as a bridge between AML and algorithms

AML papers often focus on attacks and defenses around models. Learning-augmented algorithm papers often focus on prediction error and competitive analysis. The gap is useful.

Bridge model:

1. A predictor gives advice to an algorithm.
2. The advice may be wrong due to noise, drift, poisoning, or evasion.
3. The algorithm has a baseline safe policy.
4. The algorithm chooses how much to trust advice.
5. The evaluation measures both normal-case gain and worst-case damage.

Possible formal models:

- random error model
- bounded error model
- stale prediction model
- biased prediction model
- oblivious adversary
- adaptive adversary
- poisoned predictor
- strategic data-source adversary

## 5. Cross-cutting research opportunities

### 5.1 Adversarial Prediction Models for Learning-Augmented Algorithms

Why it is strong:

- Combines AML and algorithms cleanly.
- Has a clear thesis.
- Can be written as a survey + position paper first.
- Later can become empirical with benchmark tasks.

Core question:

> How should algorithms use ML advice when the advice may be adversarial?

### 5.2 Robust ML Advice in Online Algorithms

Why it is strong:

- Online algorithms already have mature theory.
- Predictions are useful in caching, scheduling, routing, and resource allocation.
- Failure under bad advice is easy to explain.

Core question:

> Can online algorithms exploit predictions without creating new attack surfaces?

### 5.3 Poisoning the Data Supply Chain of Generative Models

Why it is strong:

- Backed by recent poisoning, mislabeling, and distillation papers.
- Practical relevance is high.
- Connects data provenance, model training, and downstream harm.

Core question:

> How can small upstream corruptions survive filtering and shape downstream models?

### 5.4 Distillation as an Amplifier for Adversarial Bias

Why it is strong:

- Clear mechanism: poisoned teacher → amplified student.
- Important for model compression and supply chains.
- Strong empirical story from extracted paper summary.

Core question:

> When does distillation preserve safety, and when does it amplify hidden failure modes?

### 5.5 Context Poisoning as Algorithmic Input Corruption

Why it is strong:

- Bridges agent/coding-assistant security and classical robustness.
- Context is basically an input stream.
- Provenance and fallback can be analyzed algorithmically.

Core question:

> Can context ingestion be designed like a robust online algorithm under adversarial inputs?

## 6. More possible topics

1. **Prediction Firewalls for Learning-Augmented Algorithms**  
   Formal guards that cap how much ML advice can influence classical decisions.

2. **Consistency Is Not Enough: Smoothness Metrics for ML-Advised Systems**  
   Study why algorithms need stable behavior under small prediction errors.

3. **The Security of Learned Heuristics in Combinatorial Optimization**  
   Treat heuristic suggestions as attackable inputs to solvers.

4. **Adversarial Benchmarks for Algorithms with Predictions**  
   A benchmark suite with perfect, noisy, stale, biased, and adversarial advice.

5. **Trust Calibration for Online Algorithms with ML Advice**  
   Methods for estimating when predictions should be ignored.

6. **Data Poisoning as Algorithmic Supply-Chain Risk**  
   Unify poisoned labels, poisoned context, and poisoned teacher models.

7. **Fallback Policy Design for AI-Augmented Infrastructure**  
   How systems should degrade when demand forecasts, routing predictions, or schedulers fail.

8. **Robust Recourse Under Model Drift and Strategic Prediction Error**  
   Human-facing robust algorithms where wrong predictions create real cost.

9. **Certified Robustness vs Adaptive Attack Reality**  
   Why formal guarantees can fail if the attacker model is too weak.

10. **From AML to Robust Algorithms: A Shared Language for Untrusted Predictions**  
   A survey/position paper that maps AML threat models into algorithm design terms.

## 7. Recommended top 5 topics

### 1. Adversarial Prediction Models for Learning-Augmented Algorithms

Best first paper. It is novel, clean, and bridges AML with algorithms.

Likely format: survey + position paper.  
Possible later proof: benchmark with online algorithm tasks and corrupted predictions.

### 2. Robust ML Advice in Online Algorithms

Best technical algorithms topic. Focus on caching, scheduling, routing, and resource allocation.

Likely format: systematization + benchmark proposal.

### 3. Poisoning the Data Supply Chain of Generative Models

Best AML/security topic. Strong source base from data poisoning, adversarial mislabeling, and distillation papers.

Likely format: survey + threat model paper.

### 4. Context Poisoning as Algorithmic Input Corruption

Best bridge to AI coding assistants and agentic security.

Likely format: conceptual paper with empirical examples from coding assistant research.

### 5. Benchmarking Algorithms Under Wrong Predictions

Best practical contribution. Could become a reusable benchmark paper.

Likely format: benchmark design + empirical evaluation.

## 8. Source table

| Area | Title | URL |
|---|---|---|
| AML survey | Adversarial Machine Learning: Attacks, Defenses, and Open Challenges | https://arxiv.org/html/2502.05637v1 |
| AML survey | A Comprehensive Review of Adversarial Attacks on Machine Learning | https://arxiv.org/abs/2412.11384 |
| Data poisoning | Data Poisoning in Deep Learning: A Survey | https://arxiv.org/abs/2503.22759 |
| Generative model poisoning | On the Feasibility of Poisoning Text-to-Image AI Models via Adversarial Mislabeling | https://arxiv.org/html/2506.21874v1 |
| Coding assistant context poisoning | Stealthy Cross-Origin Context Poisoning Attacks against AI Coding Assistants | https://arxiv.org/html/2503.14281v4 |
| Distillation poisoning | Cascading Adversarial Bias from Injection to Distillation in Language Models | https://arxiv.org/html/2505.24842v2 |
| Learning-augmented algorithms | Prediction-Specific Design of Learning-Augmented Algorithms | https://arxiv.org/abs/2510.14887 |
| Learning-augmented algorithms | On Tradeoffs in Learning-Augmented Algorithms | https://arxiv.org/abs/2501.12770 |
| Robust recourse | Learning-Augmented Robust Algorithmic Recourse | https://arxiv.org/abs/2410.01580 |

## 9. Safety notes

- This map discusses AML attacks at research-summary level only.
- It avoids procedural exploit steps, runnable attack code, or target-specific abuse instructions.
- Any future empirical work should use controlled lab datasets, local fixtures, synthetic targets, or explicitly authorized benchmarks.
- For coding assistant or agentic-security experiments, do not test against real users, private repositories, production systems, or third-party services without authorization.
