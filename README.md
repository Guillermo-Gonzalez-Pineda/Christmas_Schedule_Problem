# 🎄 Santa Workshop Optimizer (Model A)

**Strategy:** Happiness Maximization & Strict Operational Efficiency.

This project implements an **Operations Research (MIP)** solution to solve the Santa Claus Workshop Scheduling Problem. The goal is to assign 5,000 families across 100 working days, maximizing their personal satisfaction.

---

## 🧠 Model A Philosophy

Unlike coverage-focused approaches that prioritize filling slots at any cost, this model follows a **"Quality over Quantity"** policy:

1.  **Top 10 or Nothing:** Families are strictly assigned to one of their Top 10 preferred days. If assignment is not possible within their preferences, they remain unassigned (avoiding assignments to days families dislike).
2.  **Smart Facility Management:** A workshop day only opens if it is efficient to do so.
    * **Rule:** A workshop must have either **0 people** (Closed) OR between **100 and 300 people** (Open).
    * This prevents operational waste by avoiding opening large facilities for just a few families.

---

## 📐 Mathematical Formulation

This project models the challenge as a **Generalized Assignment Problem with Semicontinuous Constraints**. Below is the formal formulation used in `solver_engine.py`.

### 1. Sets and Indices
* $F$: Set of families ($i \in \{0, \dots, 4999\}$).
* $D$: Set of days ($d \in \{1, \dots, 100\}$).
* $P_i$: Set of preferred days for family $i$ (Top 10).
* $m_i$: Number of members in family $i$.
* $h_{i,d}$: Happiness points awarded if family $i$ is assigned to day $d$ (based on preference rank).

### 2. Decision Variables

**$x_{i,d}$ (Binary): Assignment**
$$
x_{i,d} = \begin{cases} 
1 & \text{if family } i \text{ is assigned to day } d \\
0 & \text{otherwise}
\end{cases}
$$

**$z_d$ (Binary): Workshop Opening**
$$
z_d = \begin{cases} 
1 & \text{if day } d \text{ is OPEN (activity > 0)} \\
0 & \text{if day } d \text{ is CLOSED (activity = 0)}
\end{cases}
$$

### 3. Objective Function

The goal is to **Maximize Global Happiness**:

$$
\text{Max } Z = \sum_{i \in F} \sum_{d \in P_i} h_{i,d} \cdot x_{i,d}
$$

### 4. Constraints

#### A. Single Assignment (or None)
Each family can be assigned to at most one day from their preference list. The inequality ($\le$) allows a family to remain unassigned if it is not feasible to accommodate them.

$$
\sum_{d \in P_i} x_{i,d} \le 1 \quad \forall i \in F
$$

#### B. Semicontinuous Capacity (Opening Rule)

**Lower Bound (Opening Link):**
If the day is open ($z_d=1$), occupancy must be at least 100. If closed ($z_d=0$), occupancy must be at least 0.

$$
\sum_{i \in F} m_i \cdot x_{i,d} \ge 100 \cdot z_d \quad \forall d \in D
$$

**Upper Bound (Capacity Limit):**
If the day is open ($z_d=1$), max occupancy is 300. If closed ($z_d=0$), occupancy must be 0.

$$
\sum_{i \in F} m_i \cdot x_{i,d} \le 300 \cdot z_d \quad \forall d \in D
$$

#### C. Variable Integrity

$$
x_{i,d} \in \{0, 1\}, \quad z_d \in \{0, 1\}
$$

---

## 🛠️ Technical Challenges & Solutions

During development, I addressed several combinatorial optimization challenges:

### 1. The "Infeasibility Trap"
* **Challenge:** The original constraint required `Occupancy >= 100` at all times. If a specific day was requested by only a few families (e.g., 20 people), the model would become infeasible because 20 < 100.
* **Solution:** Implemented **Semicontinuous Constraints** using binary variables ($z_d$). The solver can now decide: *"I cannot reach 100, so I'll close the day ($z=0$) and reject the demand."*

### 2. Combinatorial Explosion
* **Challenge:** 5,000 families × 100 days creates a search space of 500,000 decision variables.
* **Solution:** Implemented **Sparse Sets** to only generate decision variables for days in each family's preference list. This reduced the problem size by ~90%, achieving optimal solutions in seconds.

## 📂 Project Structure

* `main.py`: Entry point. Validates input data and runs the pipeline.
* `solver_engine.py`: The mathematical core. Implements the MIP model using **Pyomo** and the **CBC** solver. Defines the binary opening logic.
* `solution_manager.py`: Orchestrator. Handles data loading, solver execution, and reporting.
* `family.py` / `workshop.py`: Domain entities.

## 🚀 How to Run

1.  Ensure Python and the CBC solver are installed:
    ```bash
    sudo apt-get install coinor-cbc  # Linux
    pip install pandas pyomo
    ```

2.  Run the optimizer:
    ```bash
    python main.py
    ```

3.  Check results in `submission_modelA.csv` and the console report.

---
**Author:** Guillermo González Pineda