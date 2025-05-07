# QRQ-ML-flagging

A Python-based machine learning project designed to detect and flag outliers in the QRQ dataset, which is instrumental in calculating the Rule of Law Index. The project employs various sampling techniques to balance the training data and explores multiple classification algorithms, including ensemble methods, to enhance outlier detection accuracy.

## Project Overview

The QRQ-ML-flagging project aims to improve the integrity of the Rule of Law Index by identifying anomalous entries within the QRQ dataset. By leveraging machine learning techniques, the project seeks to automate the detection of outliers that may skew the index's calculations.

## Features

- **Data Balancing**: Implements oversampling and undersampling techniques to address class imbalance in the training dataset.
- **Algorithm Exploration**: Evaluates various classification algorithms, including:
    - Logistic Regression
    - Support Vector Classifier (SVC)
    - Decision Tree Classifier
    - Ensemble Methods:
        - Bagging
        - Random Forest
        - AdaBoost
        - XGBoost

- **Modular Design**: Structured codebase with separate modules for data processing and model training/testing.
- **Reproducibility**: Managed using the [uv project manager](https://github.com/astral-sh/uv) to ensure consistent environments.

## Project Structure

```bash
QRQ-ML-flagging/
├── data/
│   ├── features/               # Processed feature datasets
│   └── historic-data/          # Historical QRQ data
├── inputs/                     # Raw input data
├── main.py                     # Entry point for training and evaluation
├── models/                     # Saved machine learning models
├── notebooks/                  # Jupyter notebooks for exploration and analysis
├── pyproject.toml              # Project dependencies and configurations
├── README.md                   # Project documentation
├── src/
│   ├── data/
│   │   ├── build_features.py   # Script for feature engineering
│   │   └── gen_historic_data.R # R script for generating historical data
│   └── models/                 # Model training and evaluation scripts
└── uv.lock                     # Lock file for uv package manager
```

## Getting Started

1. Clone the Git repository:

```bash
git clone https://github.com/ctoruno/QRQ-ML-flagging.git
cd QRQ-ML-flagging
```

2. Ensure you have uv installed. If not, install it using pip:

```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Generate the historic data:

```bash
Rscript src/data/gen_historic_data.R
```

4. Build the features:

```bash
uv run main.py --data
```

5. Train and evaluate models:

```bash
uv run main.py --classifiers
```

## Modeling Approach

The project follows a systematic approach to outlier detection:

1. **Data Preprocessing:**
    - Handle missing values and normalize features.
    - Apply oversampling (e.g., SMOTE) and undersampling techniques to balance the dataset.

2. **Model Training:**

    - Train various classifiers, including logistic regression, SVC, decision trees, and ensemble methods.

3. **Model Evaluation**:

    - Assess model performance using metrics such as accuracy, precision, recall, - and F1-score.
    Compare results across different algorithms to select the best-performing model.

4. **Outlier Detection**:

    - Use the selected model to identify and flag outliers in the QRQ dataset.

## Contact

For inqueries please contact Carlos Toruño (ctoruno@worldjusticeproject.org).