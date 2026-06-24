"""
Módulo de carregamento, limpeza e engenharia de features dos dados de futebol.
Dataset: https://www.kaggle.com/datasets/davidcariboo/player-scores/versions/661/data
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)


def load_raw() -> dict[str, pd.DataFrame]:
    """Carrega todos os CSVs do dataset bruto."""
    files = {
        "appearances": "appearances.csv",
        "clubs": "clubs.csv",
        "competitions": "competitions.csv",
        "games": "games.csv",
        "player_valuations": "player_valuations.csv",
        "players": "players.csv",
    }
    dfs = {}
    for key, fname in files.items():
        full = _path(fname)
        if not os.path.exists(full):
            raise FileNotFoundError(
                f"Arquivo '{fname}' não encontrado em '{DATA_DIR}'.\n"
                "Faça o download do dataset em:\n"
                "https://www.kaggle.com/datasets/davidcariboo/player-scores/versions/661/data\n"
                "e coloque os CSVs na pasta 'data/'."
            )
        dfs[key] = pd.read_csv(full, low_memory=False)
    return dfs


def clean_players(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Conversão de tipos
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")
    df["last_season"] = pd.to_numeric(df["last_season"], errors="coerce")
    df["market_value_in_eur"] = pd.to_numeric(df["market_value_in_eur"], errors="coerce")
    df["highest_market_value_in_eur"] = pd.to_numeric(
        df["highest_market_value_in_eur"], errors="coerce"
    )

    # Remove duplicatas pelo ID
    df = df.drop_duplicates(subset="player_id")

    # Idade calculada com NumPy (dias / 365.25)
    hoje = pd.Timestamp("2025-01-01")
    df["age"] = np.floor((hoje - df["date_of_birth"]).dt.days / 365.25).astype("Int64")

    # Remove jogadores sem posição ou com idade fora do intervalo válido
    df = df.dropna(subset=["position"])
    df = df[df["age"].between(15, 50)]

    # Simplifica posições para 4 grupos
    position_map = {
        "Attack": "Atacante",
        "Midfield": "Meio-Campo",
        "Defender": "Defensor",
        "Goalkeeper": "Goleiro",
    }
    df["position_group"] = df["position"].map(position_map).fillna(df["position"])

    # Faixa etária com pd.cut (engenharia de feature categórica)
    df["age_group"] = pd.cut(
        df["age"].astype(float),
        bins=[14, 20, 24, 28, 32, 50],
        labels=["Sub-21", "21-24", "25-28", "29-32", "33+"],
    )

    # Log do valor de mercado para análise (NumPy)
    df["log_market_value"] = np.log1p(df["market_value_in_eur"].fillna(0))

    # Proporção entre valor atual e valor histórico máximo
    df["value_to_peak_ratio"] = np.where(
        df["highest_market_value_in_eur"] > 0,
        df["market_value_in_eur"] / df["highest_market_value_in_eur"],
        np.nan,
    ).round(3)

    return df


def clean_appearances(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    numeric_cols = ["goals", "assists", "minutes_played", "yellow_cards", "red_cards"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "player_id"])
    df = df.drop_duplicates(subset=["appearance_id"])

    # Contribuições diretas (Pandas)
    df["goal_contributions"] = df["goals"] + df["assists"]

    # Minutos por contribuição — evita divisão por zero (NumPy)
    df["minutes_per_contribution"] = np.where(
        df["goal_contributions"] > 0,
        df["minutes_played"] / df["goal_contributions"],
        np.nan,
    )

    # Temporada derivada da data (julho = início da temporada europeia)
    df["season"] = df["date"].dt.year.where(
        df["date"].dt.month >= 7, df["date"].dt.year - 1
    )

    return df


def clean_valuations(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["market_value_in_eur"] = pd.to_numeric(df["market_value_in_eur"], errors="coerce")
    df = df.dropna(subset=["date", "market_value_in_eur", "player_id"])
    df = df.sort_values(["player_id", "date"])
    return df


def clean_games(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in ["home_club_goals", "away_club_goals"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["date"])
    df["total_goals"] = df["home_club_goals"] + df["away_club_goals"]
    return df


def build_player_stats(appearances: pd.DataFrame) -> pd.DataFrame:
    """Agrega estatísticas por jogador ao longo de toda a carreira."""
    agg = (
        appearances.groupby("player_id")
        .agg(
            total_appearances=("appearance_id", "count"),
            total_goals=("goals", "sum"),
            total_assists=("assists", "sum"),
            total_minutes=("minutes_played", "sum"),
            total_yellow=("yellow_cards", "sum"),
            total_red=("red_cards", "sum"),
            total_contributions=("goal_contributions", "sum"),
            seasons_active=("season", "nunique"),
            avg_minutes_per_contribution=("minutes_per_contribution", "mean"),
        )
        .reset_index()
    )

    # Métricas por jogo (Pandas + NumPy)
    agg["goals_per_game"]   = (agg["total_goals"]   / agg["total_appearances"]).round(3)
    agg["assists_per_game"] = (agg["total_assists"]  / agg["total_appearances"]).round(3)
    agg["minutes_per_game"] = (agg["total_minutes"]  / agg["total_appearances"]).round(1)
    agg["red_cards_per_game"] = (agg["total_red"]    / agg["total_appearances"]).round(4)

    # Score de performance ponderado (NumPy): gols valem 2x, assistências 1x, normalizado por jogo
    agg["performance_score"] = np.round(
        (agg["total_goals"] * 2 + agg["total_assists"]) / np.maximum(agg["total_appearances"], 1),
        3,
    )

    # Quartis de performance com pd.qcut (Pandas)
    try:
        agg["performance_tier"] = pd.qcut(
            agg["performance_score"],
            q=4,
            labels=["Bronze", "Prata", "Ouro", "Elite"],
            duplicates="drop",
        )
    except ValueError:
        agg["performance_tier"] = "Prata"

    return agg


def detect_value_outliers(master: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta outliers de valor de mercado usando o método IQR (NumPy).
    Adiciona coluna booleana 'is_value_outlier'.
    """
    vals = master["latest_market_value"].dropna().values
    q1 = np.percentile(vals, 25)
    q3 = np.percentile(vals, 75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr

    master = master.copy()
    master["is_value_outlier"] = master["latest_market_value"] > upper
    return master


def build_master(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Constrói DataFrame mestre combinando jogadores, estatísticas agregadas
    e valor de mercado mais recente.
    """
    players  = clean_players(dfs["players"])
    appearances = clean_appearances(dfs["appearances"])
    valuations  = clean_valuations(dfs["player_valuations"])

    # Valor de mercado mais recente por jogador (Pandas groupby + last)
    latest_val = (
        valuations.sort_values("date")
        .groupby("player_id")["market_value_in_eur"]
        .last()
        .reset_index()
        .rename(columns={"market_value_in_eur": "latest_market_value"})
    )

    stats = build_player_stats(appearances)

    master = (
        players
        .merge(stats, on="player_id", how="left")
        .merge(latest_val, on="player_id", how="left")
    )

    # Preenche nulos nas colunas numéricas com 0 (Pandas)
    zero_cols = ["total_appearances", "total_goals", "total_assists",
                 "total_minutes", "total_contributions"]
    master[zero_cols] = master[zero_cols].fillna(0)

    # Log do valor de mercado (NumPy)
    master["log_latest_value"] = np.log1p(master["latest_market_value"].fillna(0))

    # Faixa de valor de mercado com pd.cut (Pandas)
    master["value_tier"] = pd.cut(
        master["latest_market_value"].fillna(0),
        bins=[0, 1_000_000, 10_000_000, 50_000_000, np.inf],
        labels=["< €1M", "€1M–€10M", "€10M–€50M", "> €50M"],
    )

    # Detecta outliers de valor (NumPy IQR)
    master = detect_value_outliers(master)

    return master


def get_correlation_matrix(master: pd.DataFrame) -> pd.DataFrame:
    """Retorna matriz de correlação entre as principais variáveis numéricas."""
    cols = [
        "age", "total_appearances", "total_goals", "total_assists",
        "goals_per_game", "assists_per_game", "minutes_per_game",
        "performance_score", "seasons_active", "latest_market_value",
    ]
    available = [c for c in cols if c in master.columns]
    return master[available].corr(numeric_only=True).round(2)


def load_all() -> dict[str, pd.DataFrame]:
    """Ponto de entrada principal: retorna dict com todos os DataFrames limpos."""
    raw = load_raw()
    master = build_master(raw)
    return {
        "master": master,
        "appearances": clean_appearances(raw["appearances"]),
        "valuations": clean_valuations(raw["player_valuations"]),
        "games": clean_games(raw["games"]),
        "clubs": raw["clubs"],
        "competitions": raw["competitions"],
        "corr_matrix": get_correlation_matrix(master),
    }
