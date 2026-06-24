import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
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
    "red_cards_per_game",
    "goals_per_game",
    "assists_per_game",
    "seasons_active",
]

FEATURES_CAT = ["position_group"]

TARGET = "log_latest_value"


def prepare_xy(master: pd.DataFrame):
    df = master[
        master["latest_market_value"].notna()
        & (master["latest_market_value"] > 0)
        & master["total_appearances"].notna()
        & (master["total_appearances"] >= 5)
    ].copy()

    X = df[FEATURES_NUM + FEATURES_CAT]
    y = df[TARGET]
    return X, y


def build_pipeline() -> Pipeline:
    # HistGradientBoosting lida nativamente com nulos — só precisa do encoder categórico
    cat_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer([
        ("cat", cat_pipe, FEATURES_CAT),
        ("num", "passthrough", FEATURES_NUM),
    ])

    regressor = HistGradientBoostingRegressor(
        max_iter=100, max_depth=4, learning_rate=0.1, random_state=42
    )

    return Pipeline([("prep", preprocessor), ("model", regressor)])


def train_and_evaluate(master: pd.DataFrame, model_type: str = "gbr") -> dict:
    X, y = prepare_xy(master)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    y_pred_log = pipe.predict(X_test)
    y_pred_eur = np.expm1(y_pred_log)
    y_true_eur = np.expm1(y_test)

    importances = pipe.named_steps["model"].feature_importances_
    # Nomes: primeiro as colunas OHE, depois as numéricas (passthrough)
    ohe_names = list(
        pipe.named_steps["prep"]
        .named_transformers_["cat"]
        .named_steps["ohe"]
        .get_feature_names_out(FEATURES_CAT)
    )
    feature_names = ohe_names + FEATURES_NUM
    feat_df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .head(10)
    )

    return {
        "pipeline": pipe,
        "r2_test": r2_score(y_test, y_pred_log),
        "mae_eur": mean_absolute_error(y_true_eur, y_pred_eur),
        "y_true_eur": y_true_eur.values,
        "y_pred_eur": y_pred_eur,
        "feature_importances": feat_df,
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
