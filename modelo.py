"""
Módulo de modelagem preditiva: regressão para valor de mercado de jogadores.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score


FEATURES_NUM = [
    "age",
    "total_appearances",
    "total_goals",
    "total_assists",
    "total_minutes",
    "total_yellow",
    "total_red",
    "goals_per_game",
    "assists_per_game",
    "seasons_active",
]

FEATURES_CAT = ["position_group"]

TARGET = "log_latest_value"


def prepare_xy(master: pd.DataFrame):
    """Filtra linhas válidas e separa X, y."""
    df = master[
        master["latest_market_value"].notna()
        & (master["latest_market_value"] > 0)
        & master["total_appearances"].notna()
        & (master["total_appearances"] >= 5)
    ].copy()

    X = df[FEATURES_NUM + FEATURES_CAT]
    y = df[TARGET]
    return X, y, df


def build_pipeline(model_type: str = "gbr") -> Pipeline:
    num_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer([
        ("num", num_pipe, FEATURES_NUM),
        ("cat", cat_pipe, FEATURES_CAT),
    ])

    if model_type == "gbr":
        regressor = GradientBoostingRegressor(
            n_estimators=300, max_depth=4, learning_rate=0.08,
            subsample=0.8, random_state=42
        )
    else:
        regressor = Ridge(alpha=1.0)

    return Pipeline([("prep", preprocessor), ("model", regressor)])


def train_and_evaluate(master: pd.DataFrame, model_type: str = "gbr") -> dict:
    """Treina o modelo e retorna métricas + predições."""
    X, y, df_filtered = prepare_xy(master)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipe = build_pipeline(model_type)
    pipe.fit(X_train, y_train)

    y_pred_log = pipe.predict(X_test)
    y_pred_eur = np.expm1(y_pred_log)
    y_true_eur = np.expm1(y_test)

    cv_scores = cross_val_score(pipe, X, y, cv=5, scoring="r2")

    # Feature importances (apenas para GBR)
    feature_names = (
        FEATURES_NUM
        + list(
            pipe.named_steps["prep"]
            .named_transformers_["cat"]
            .named_steps["ohe"]
            .get_feature_names_out(FEATURES_CAT)
        )
    )
    if model_type == "gbr":
        importances = pipe.named_steps["model"].feature_importances_
        feat_df = (
            pd.DataFrame({"feature": feature_names, "importance": importances})
            .sort_values("importance", ascending=False)
            .head(10)
        )
    else:
        feat_df = pd.DataFrame()

    return {
        "pipeline": pipe,
        "r2_test": r2_score(y_test, y_pred_log),
        "mae_eur": mean_absolute_error(y_true_eur, y_pred_eur),
        "cv_r2_mean": cv_scores.mean(),
        "cv_r2_std": cv_scores.std(),
        "y_true_eur": y_true_eur.values,
        "y_pred_eur": y_pred_eur,
        "feature_importances": feat_df,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
