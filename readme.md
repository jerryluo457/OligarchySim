# Oligarchy Simulator

### [**Launch Live Simulation**](https://jerryluo457-oligarchysim-filesapp-spzxtc.streamlit.app/)

A computational model exploring **Economic Elite Domination theory**. This interactive simulation visualizes how democratic responsiveness decays when policy outcomes systematically favor elite interests over the public will. It draws on theoretical frameworks from **Gilens & Page (2014)** and **Jeffrey Winters (2011)** to model the tension between electoral democracy and oligarchic capture.

---

## User Guide

### 1. Setup Phase
Before the simulation begins, you configure the initial state of the world:
* **Public Opinion:** Set the starting position of the Median Voter ($M$) on the Economic (X) and Social (Y) axes.
* **Add Elites:** Manually place elite actors (e.g., "Wall St", "Unions", "Tech Moguls") on the compass and assign them an **Influence Weight**.
    * *Tip:* Placing elites far from the public creates higher tension and faster erosion of democracy.

### 2. Simulation Phase
Once started, the simulation runs for $T$ cycles. You can watch the dynamics unfold in real-time:
* **The Chart:**
    * **Public ($M$):** Moves slowly, adapting to policy outcomes (or propaganda).
    * **Policy ($O$):** The actual law of the land. Its position is a weighted tug-of-war between the Public and the Elites.
    * **Elite Consensus ($E$):** The weighted average position of all elite actors.
* **The Gauges:**
    * **Democracy Score ($\theta$):** How much the government cares about the public. (1.0 = Pure Democracy, 0.0 = Total Oligarchy).
    * **Elite Capture ($ECI$):** A measure of how far policy has drifted from the public relative to the elites.

---

## Theoretical & Mathematical Specifications

### Core Logic
The simulation models the **Policy Outcome ($O$)** as a convex combination of the Public's preference ($M$) and the Elite's preference ($E$), weighted by the current level of **Democratic Responsiveness ($\theta$)**.

$$O_t = \theta_t M_t + (1 - \theta_t) E_t$$

* If $\theta = 1$, policy matches public opinion (Majoritarian Democracy).
* If $\theta = 0$, policy matches elite opinion (Economic Elite Domination).

### The Evolution of Democracy (Mean-Reverting Decay)
Unlike static models, this simulation treats democracy as a dynamic variable that evolves over time. It follows a **Mean-Reverting Decay** process:

$$\theta_{t+1} = \theta_t + \alpha(\theta^* - \theta_t) - \lambda \cdot ECI_t$$

Where:
* **$\theta^*$ (Baseline Democracy):** The natural capacity of the state to be democratic (e.g., strength of the constitution).
* **$\alpha$ (Recovery Rate):** The speed at which institutions heal from corruption.
* **$\lambda$ (Erosion Rate):** The damage caused by elite capture per cycle.
* **$ECI$ (Elite Capture Index):** The normalized distance the policy has moved away from the public toward the elites.

### Known Limitations & Theoretical Flaws

1.  **The "Manufactured Consent" Illusion**
    * **Phenomenon:** If the **Public Learning Rate ($\eta$)** is set very high, the public rapidly updates its preferences to match the new policy status quo (cognitive dissonance reduction or effective propaganda).
    * **The Flaw:** As the public moves toward the elite-controlled policy, the distance $\|O - M\|$ shrinks to near zero. The system interprets this as "low elite capture," causing the Democracy Score ($\theta$) to recover.
    * **Result:** The simulation may declare a "Healthy Democracy" because the government is doing what the public "wants"—even if the public only wants it because they were manipulated. This effectively models **Gramscian Hegemony** but can be confusing if interpreted strictly as institutional health.

2.  **The "Leak" Dynamics**
    * Because the Erosion term ($-\lambda \cdot ECI$) is always negative (or zero), democracy is under constant pressure. Without a sufficiently high Recovery Rate ($\alpha$) or Baseline ($\theta^*$), the system has a deterministic tendency to drift toward oligarchy over long time horizons.

---

## Technical Specifications

### Tech Stack
* **Language:** Python 3.12+
* **Frontend:** [Streamlit](https://streamlit.io/) (Reactive Web Framework)
* **Visualization:** [Plotly Graph Objects](https://plotly.com/python/) (Interactive SVG/Canvas rendering)
* **Computation:** NumPy (Vectorized linear algebra for centroid/distance calculations)

### File Structure
```bash
oligarchy-sim/
├── app.py             # Main entry point; handles UI, animation loop, and state
├── simulation.py      # Orchestrator; manages the time-step loop
├── dynamics.py        # Core Math; implements the evolution equations for Theta and Policy
├── elites.py          # Logic for weighted centroid calculation and influence updates
├── metrics.py         # Calculation of Elite Capture Index (ECI)
├── state.py           # Data class for storing snapshots of each cycle
├── utils.py           # Helper functions (Gaussian noise generation)
└── requirements.txt   # Dependency manifest for deployment