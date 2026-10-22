"""A deliberately simple classifier: logistic regression on four measurements."""

from __future__ import annotations

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .analysis import NUMERIC


def train_species_model(df: pd.DataFrame, seed: int = 42, test_size: float = 0.25) -> dict:
    """Predict species from measurements; report held-out accuracy and 5-fold CV accuracy."""
    x, y = df[NUMERIC], df["species"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=seed, stratify=y
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    labels = sorted(y.unique())
    return {
        "labels": labels,
        "test_accuracy": float(accuracy_score(y_test, pred)),
        "cv_accuracy": float(cross_val_score(model, x, y, cv=5).mean()),
        "confusion_matrix": confusion_matrix(y_test, pred, labels=labels).tolist(),
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
    }
