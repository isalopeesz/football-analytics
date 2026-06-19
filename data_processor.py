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

    # Tipos
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce")
    df["last_season"] = pd.to_numeric(df["last_season"], errors="coerce")
    df["market_value_in_eur"] = pd.to_numeric(df["market_value_in_eur"], errors="coerce")
    df["highest_market_value_in_eur"] = pd.to_numeric(
        df["highest_market_value_in_eur"], errors="coerce"
    )

    # Remove duplicatas pelo ID
    df = df.drop_duplicates(subset="player_id")

    # Cria coluna de idade atual
    hoje = pd.Timestamp("2025-01-01")
    df["age"] = ((hoje - df["date_of_birth"]).dt.days / 365.25).round(1)

    # Remove jogadores sem posição ou com idade absurda
    df = df.dropna(subset=["position"])
    df = df[df["age"].between(15, 50, inclusive="both")]

    # Simplifica posições para categoria principal
    position_map = {
        "Attack": "Atacante",
        "Midfield": "Meio-Campo",
        "Defender": "Defensor",
        "Goalkeeper": "Goleiro",
    }
    df["position_group"] = df["position"].map(position_map).fillna(df["position"])

    # Log do valor de mercado (útil para regressão)
    df["log_market_value"] = np.log1p(df["market_value_in_eur"].fillna(0))

    return df


def clean_appearances(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    numeric_cols = ["goals", "assists", "minutes_played", "yellow_cards", "red_cards"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "player_id"])
    df = df.drop_duplicates(subset=["appearance_id"])

    # Feature: contribuições diretas (gols + assistências)
    df["goal_contributions"] = df["goals"] + df["assists"]

    # Feature: minutos por contribuição (evita divisão por zero)
    df["minutes_per_contribution"] = np.where(
        df["goal_contributions"] > 0,
        df["minutes_played"] / df["goal_contributions"],
        np.nan,
    )

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
        )
        .reset_index()
    )
    agg["goals_per_game"] = (agg["total_goals"] / agg["total_appearances"]).round(3)
    agg["assists_per_game"] = (agg["total_assists"] / agg["total_appearances"]).round(3)
    agg["minutes_per_game"] = (agg["total_minutes"] / agg["total_appearances"]).round(1)
    return agg


def build_master(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Constrói DataFrame mestre combinando jogadores, estatísticas agregadas
    e valor de mercado mais recente.
    """
    players = clean_players(dfs["players"])
    appearances = clean_appearances(dfs["appearances"])
    valuations = clean_valuations(dfs["player_valuations"])

    # Valor de mercado mais recente por jogador
    latest_val = (
        valuations.sort_values("date")
        .groupby("player_id")["market_value_in_eur"]
        .last()
        .reset_index()
        .rename(columns={"market_value_in_eur": "latest_market_value"})
    )

    stats = build_player_stats(appearances)

    master = (
        players.merge(stats, on="player_id", how="left")
        .merge(latest_val, on="player_id", how="left")
    )

    master["total_appearances"] = master["total_appearances"].fillna(0)
    master["total_goals"] = master["total_goals"].fillna(0)
    master["total_assists"] = master["total_assists"].fillna(0)
    master["log_latest_value"] = np.log1p(master["latest_market_value"].fillna(0))

    return master


def load_all() -> dict[str, pd.DataFrame]:
    """Ponto de entrada principal: retorna dict com todos os DataFrames limpos."""
    raw = load_raw()
    return {
        "master": build_master(raw),
        "appearances": clean_appearances(raw["appearances"]),
        "valuations": clean_valuations(raw["player_valuations"]),
        "games": clean_games(raw["games"]),
        "clubs": raw["clubs"],
        "competitions": raw["competitions"],
    }
