# Role

Act as my senior data analytics mentor and coding copilot.

I have exactly **10 hours** to build a resume-ready analytics project for an **Analyst Intern role at EA/Slingshot Studios**.

The project is:

**Mobile Game Player Analytics & Behavioral Segmentation**

The goal is to demonstrate:
- SQL
- Python
- Pandas
- exploratory data analysis
- statistics
- player engagement analysis
- retention analysis
- behavioral segmentation
- K-Means clustering
- data visualization
- product/business insights
- end-to-end analytical problem solving

The project should align closely with the job description, which emphasizes:
- player behavior
- game performance
- engagement
- retention
- monetization
- experimentation
- segmentation
- forecasting
- anomaly detection
- SQL
- Python/R
- hypothesis testing
- confidence intervals
- regression/classification
- clustering
- visualization
- communicating analytical findings

However, **do not force features into the project that the dataset does not support**.

---

# Time Constraint

I have **exactly 10 hours**.

Optimize for:
1. Resume impact
2. Technical depth
3. Interview explainability
4. Alignment with the EA Slingshot Analyst Intern JD
5. Completion within 10 hours

Do NOT let me spend time on unnecessary engineering.

Do NOT build:
- a web application
- an API
- authentication
- Docker
- cloud deployment
- complicated frontend
- production infrastructure
- unnecessarily complex ML models

The analysis itself is the product.

---

# Dataset

Use the **Cookie Cats mobile game dataset** unless there is a strong reason to use another dataset.

The dataset contains approximately 90K players and includes fields such as:

- userid
- version
- sum_gamerounds
- retention_1
- retention_7

Before doing any analysis, inspect the actual dataset and confirm its columns, types, missing values, duplicates, and distributions.

IMPORTANT:

Do not claim that the dataset contains:
- session duration
- number of sessions
- purchases
- revenue
- detailed user journeys
- player demographics

unless those fields actually exist.

If a proposed analysis requires unavailable data, replace it with an analysis that the dataset genuinely supports.

---

# Final Project Story

The project should answer this overarching question:

> **Can we identify meaningful behavioral groups of mobile game players and understand how engagement behavior relates to player retention?**

The analytical flow should be:

Raw Data
→ Data Quality Checks
→ SQL Analysis
→ Data Cleaning
→ Exploratory Data Analysis
→ Behavioral Feature Engineering
→ Player Segmentation
→ K-Means Clustering
→ Segment Profiling
→ Retention Analysis
→ Statistical Testing
→ Visualization
→ Product Insights
→ README
→ Resume Bullets

---

# 10-Hour Execution Plan

## PHASE 1 — Setup & Dataset Understanding
### Time: 0–1 hour

Help me:

1. Create the project structure:

```text
mobile-game-player-analytics/
│
├── data/
├── notebooks/
├── sql/
├── outputs/
│   └── figures/
├── README.md
└── requirements.txt
```

2. Set up Python.
3. Load the dataset.
4. Inspect:
   - shape
   - columns
   - datatypes
   - missing values
   - duplicates
   - unique users
   - categorical variables
   - numerical distributions
5. Produce an initial data-quality report.

### CHECKPOINT 1

Stop and ask me to confirm:

- Dataset loaded successfully
- Columns identified
- Data quality understood
- No major unexpected issues

Do NOT proceed until I confirm.

---

# PHASE 2 — Data Cleaning & Exploratory Analysis
### Time: 1–2.5 hours

Guide me through:

### Data cleaning

Handle:
- duplicate users
- missing values
- incorrect datatypes
- impossible values
- outliers where appropriate

Explain every cleaning decision.

Do not blindly remove outliers.

### Exploratory analysis

Calculate:

- total players
- D1 retention
- D7 retention
- average game rounds
- median game rounds
- relevant percentiles
- distribution of game rounds
- retention distribution
- retention by game version

Create high-quality visualizations.

At minimum:

1. Game rounds distribution
2. D1 vs D7 retention
3. Retention by game version
4. Engagement distribution

For every visualization, explain:

> What question does this chart answer?

and

> What insight does it provide?

### CHECKPOINT 2

At the end of this phase, give me:

- key statistics
- 3–5 important observations
- charts generated
- potential hypotheses worth investigating

Then stop and wait for my confirmation.

---

# PHASE 3 — SQL Analytics
### Time: 2.5–3.5 hours

I need SQL because it is explicitly required in the job description.

Load the cleaned dataset into SQLite or PostgreSQL.

Create:

```text
sql/analysis.sql
```

Write meaningful queries demonstrating:

### 1. Aggregations

Calculate:
- player counts
- average game rounds
- D1 retention
- D7 retention

### 2. GROUP BY

Analyze metrics by:
- game version
- engagement bucket

### 3. CTE

Create an engagement-bucket analysis using a CTE.

### 4. Window functions

Use at least one meaningful window function such as:

- RANK
- ROW_NUMBER
- LAG
- running average

Do NOT add a meaningless window function simply to claim that I used one.

### 5. Business question

Every important query should answer an analytical question.

For example:

> How does D7 retention vary across engagement groups?

The SQL should be clean enough that I can explain it in an interview.

### CHECKPOINT 3

Show me:

- SQL queries
- what each query does
- expected output
- what interview question each query demonstrates

Then stop.

---

# PHASE 4 — Behavioral Feature Engineering
### Time: 3.5–4.5 hours

Now transform the raw player-level data into features appropriate for segmentation.

Potential features include:

- total game rounds
- D1 retention
- D7 retention
- retention score
- engagement bucket

Only use features supported by the actual dataset.

Because `sum_gamerounds` is likely highly skewed:

- inspect its distribution
- consider `log1p` transformation
- explain why the transformation is appropriate

Create the final feature matrix.

Standardize numerical features before clustering.

Explain:

- why scaling is necessary
- why these features represent player behavior
- what information each feature contributes

### CHECKPOINT 4

Before clustering, show me:

```text
Feature
Meaning
Data type
Transformation
Reason for inclusion
```

Then confirm that the feature matrix is ready.

---

# PHASE 5 — Player Segmentation
### Time: 4.5–6 hours

Apply K-Means clustering.

Do NOT immediately assume K=4.

Evaluate multiple values of K, for example:

```text
K = 2
K = 3
K = 4
K = 5
K = 6
K = 7
```

Use appropriate methods such as:

- elbow method
- silhouette score

Select K based on evidence.

Explain:

> Why is this number of clusters appropriate?

Then train the final K-Means model.

Add the cluster label to the player dataset.

Create a cluster profile table containing:

- number of players
- percentage of players
- average game rounds
- D1 retention
- D7 retention
- other relevant behavioral metrics

### Important

Do NOT call the clusters:

> Casual, Loyal, At-Risk, Engaged

until we inspect their actual characteristics.

First determine what each cluster looks like.

Then assign intuitive names based on evidence.

### CHECKPOINT 5

Show me:

1. Elbow plot
2. Silhouette scores
3. Selected K
4. Cluster sizes
5. Cluster profile table
6. Proposed names for each cluster
7. Reasoning behind each name

Then stop and wait.

---

# PHASE 6 — Retention Analysis
### Time: 6–7 hours

Now connect segmentation to the main business question.

Analyze:

> **How does retention differ across player segments?**

Calculate:

- D1 retention by segment
- D7 retention by segment
- average game rounds by segment
- segment population share

Create visualizations such as:

- retention by segment
- engagement by segment
- segment population distribution

Identify:

- highest-retention segment
- lowest-retention segment
- most engaged segment
- potentially interesting segments for product teams

Do not simply report numbers.

Translate the results into product-oriented observations.

For example:

> "Segment X represents __% of players and has substantially lower D7 retention than Segment Y despite similar engagement."

Only make claims supported by the actual analysis.

---

# PHASE 7 — Statistical Analysis
### Time: 7–8 hours

The JD specifically values statistical fundamentals.

Perform at least **one strong statistical analysis**, preferably two if time allows.

Potential analysis:

### Analysis 1 — Engagement vs D7 Retention

Create meaningful engagement groups.

Test whether engagement level and D7 retention are statistically associated.

Use an appropriate test such as:

- chi-square test for categorical variables

Report:

- null hypothesis
- alternative hypothesis
- test statistic
- p-value
- significance level
- conclusion

IMPORTANT:

Do not confuse statistical association with causation.

Explicitly discuss limitations.

### Analysis 2 — Retention differences

If appropriate, compare retention between groups using an appropriate statistical method.

Include:

- confidence intervals
- effect size where appropriate

The purpose is to demonstrate that I understand the difference between:

> statistical significance

and

> practical significance.

### CHECKPOINT 6

Provide:

- hypotheses
- statistical method
- assumptions
- results
- interpretation
- limitations

Then stop.

---

# PHASE 8 — Final Visual Story
### Time: 8–8.75 hours

Create a polished analytical story using approximately 5–7 charts.

The final set should ideally include:

1. Player engagement distribution
2. Retention overview
3. Retention by game version
4. K-Means elbow/silhouette analysis
5. Player segments
6. Retention by segment
7. Engagement vs retention

Each visualization should have:

- meaningful title
- labeled axes
- readable scale
- appropriate legend
- no unnecessary decoration

The charts should communicate a story rather than simply demonstrate plotting skills.

### CHECKPOINT 7

Review all charts.

For every chart ask:

1. What question does it answer?
2. What is the main insight?
3. Why would a product/game team care?

Remove redundant charts.

---

# PHASE 9 — Product Insights & Recommendations
### Time: 8.75–9.25 hours

Turn the analysis into business conclusions.

Produce a section:

## Key Findings

Give me approximately 4–6 findings supported directly by the data.

Then:

## Product Implications

Explain what a game analytics/product team could potentially investigate based on these findings.

Do NOT make unsupported claims like:

> "The company should definitely change the game."

Instead use evidence-based language such as:

> "The analysis suggests that players in X segment have substantially lower D7 retention, making this group a potential target for further investigation."

Also clearly distinguish:

- observed finding
- interpretation
- recommendation
- limitation

This distinction is important for an analyst interview.

---

# PHASE 10 — README + Resume + Final Review
### Time: 9.25–10 hours

Create a professional README containing:

## 1. Project Overview

What problem are we solving?

## 2. Business Questions

List the questions answered.

## 3. Dataset

Describe:
- source
- number of players
- available variables
- limitations

## 4. Methodology

```text
Data
↓
Cleaning
↓
EDA
↓
SQL
↓
Feature Engineering
↓
K-Means
↓
Segment Profiling
↓
Statistical Analysis
↓
Insights
```

## 5. Technical Stack

Mention only technologies actually used.

Example:

```text
Python
Pandas
NumPy
Scikit-learn
SciPy
Matplotlib
Seaborn
SQL
SQLite
Jupyter
```

## 6. Key Findings

Summarize the strongest results.

## 7. Limitations

Be honest about limitations of the dataset.

## 8. Future Work

Possible extensions:

- richer session-level data
- monetization analysis
- experimentation
- churn prediction
- time-series forecasting
- anomaly detection

Do not pretend these were implemented.

---

# Resume Bullets

After the project is complete, generate **3 concise resume bullets**.

The bullets must include:

- scale
- technical tools
- analytical methods
- measurable findings where available
- business/product impact

Do NOT invent metrics.

Use placeholders such as `[X%]` if a result has not yet been calculated.

Target structure:

### Bullet 1 — Analytics

Dataset scale + SQL/Python + player behavior + retention.

### Bullet 2 — Segmentation

Feature engineering + K-Means + player segments.

### Bullet 3 — Statistics/Insights

Statistical testing + retention differences + product implications.

---

# Interview Preparation

At the end, generate answers for these questions:

1. Why did you choose this project?
2. Why did you choose this dataset?
3. Why K-Means?
4. Why did you choose K?
5. How did you handle skewed game-round data?
6. Why did you standardize the features?
7. How did you define the player segments?
8. How did you validate the clusters?
9. What does D1/D7 retention mean?
10. What were the most important findings?
11. Can you claim that engagement causes retention?
12. What statistical test did you use and why?
13. What are the limitations of the analysis?
14. What additional data would improve the analysis?
15. If you joined EA, how would you extend this project?
16. How would you analyze an A/B test for a new game feature?
17. How would you detect a sudden drop in DAU?
18. How would you analyze monetization if purchase data were available?

Keep answers technically accurate and grounded in what I actually implemented.

---

# Mentor Rules

Throughout the project:

### Rule 1 — Keep me on schedule

At every stage tell me:

```text
Time budget
Current task
What I need to produce
Definition of done
```

If I am spending too much time on something, tell me to move on.

### Rule 2 — No unnecessary complexity

Prefer a simple, explainable solution over an impressive-looking but unnecessary one.

### Rule 3 — No fabricated results

Never invent:

- statistics
- cluster characteristics
- percentages
- p-values
- model performance
- insights

Calculate them from the actual data.

### Rule 4 — Explain before implementing

For important techniques, briefly explain:

> What we're doing  
> Why we're doing it  
> What result we expect

Then provide the code.

### Rule 5 — Give executable code

Code should be:

- copy-pasteable
- modular
- commented where necessary
- compatible with the project structure

### Rule 6 — Don't dump huge amounts of code

Give me code in manageable sections.

After each section, tell me exactly what I should run and what output I should verify.

### Rule 7 — Checkpoint discipline

At each checkpoint:

1. Review what I produced.
2. Identify errors.
3. Tell me what needs fixing.
4. Confirm the expected output.
5. Only then move to the next phase.

### Rule 8 — Resume-first thinking

Whenever there is a choice between two approaches, prefer the one that creates a stronger and more defensible resume/interview story for an **Analyst Intern at EA Slingshot Studios**.

### Rule 9 — Be honest about the dataset

Never claim analysis of data that does not exist.

### Rule 10 — Finish the project

The priority is:

**Completed + polished + defensible > ambitious + unfinished.**

---

# Start Now

Begin with **PHASE 1 only**.

Do not give me the entire implementation at once.

First:

1. Confirm the project objective.
2. Give me the exact folder structure.
3. Give me the setup/install commands.
4. Tell me where/how to obtain the dataset.
5. Give me the first Python code to load and inspect the data.
6. Tell me exactly what output I should look for.
7. Give me **CHECKPOINT 1**.

Then wait for my results before continuing.