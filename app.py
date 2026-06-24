import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec

from data_processor import load_all
from modelo import train_and_evaluate

# Config da página
st.set_page_config(
    page_title="Football Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta de cores consistente
COLORS = {
    "Atacante": "#e74c3c",
    "Meio-Campo": "#3498db",
    "Defensor": "#2ecc71",
    "Goleiro": "#f39c12",
    "primary": "#1a1a2e",
    "accent": "#e94560",
}
POSITION_ORDER = ["Atacante", "Meio-Campo", "Defensor", "Goleiro"]

# Cache de dados
@st.cache_data(show_spinner="Carregando e processando dados...")
def get_data():
    return load_all()


@st.cache_data(show_spinner="Treinando modelo de ML...")
def get_model_results(_master):
    return train_and_evaluate(_master, model_type="gbr")


# Helpers de formatação
def fmt_eur(value: float) -> str:
    if value >= 1_000_000:
        return f"€{value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"€{value/1_000:.0f}K"
    return f"€{value:.0f}"


def style_axes(ax, title="", xlabel="", ylabel="", grid=True):
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.tick_params(labelsize=9)
    if grid:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
        ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines[["top", "right"]].set_visible(False)


# Carrega dados
try:
    data = get_data()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

from data_processor import get_correlation_matrix

master = data["master"]
appearances = data["appearances"]
valuations = data["valuations"]
games = data["games"]
corr_matrix = data.get("corr_matrix") or get_correlation_matrix(master)

# Metadados temporais do dataset
app_date_min = appearances["date"].min()
app_date_max = appearances["date"].max()
val_date_min = valuations["date"].min()
val_date_max = valuations["date"].max()

season_min = int(appearances["season"].min())
season_max = int(appearances["season"].max())

# Sidebar — filtros globais
with st.sidebar:
    st.title("⚽ Football Analytics")
    st.markdown("**Dataset:** Kaggle — Player Scores v661")
    st.divider()

    st.subheader("Cobertura dos Dados")
    st.markdown(
        f"**Partidas:** {app_date_min.strftime('%d/%m/%Y')} → {app_date_max.strftime('%d/%m/%Y')}"
    )
    st.markdown(
        f"**Valores de Mercado:** {val_date_min.strftime('%d/%m/%Y')} → {val_date_max.strftime('%d/%m/%Y')}"
    )
    st.divider()

    st.subheader("Filtros Globais")

    season_range = st.slider(
        "Temporada",
        min_value=season_min,
        max_value=season_max,
        value=(season_min, season_max),
        help="Filtra a aba Evolução Temporal e estatísticas de aparições",
    )

    posicoes_disponiveis = [p for p in POSITION_ORDER if p in master["position_group"].unique()]
    posicoes_sel = st.multiselect(
        "Posições",
        options=posicoes_disponiveis,
        default=posicoes_disponiveis,
    )

    age_min, age_max = int(master["age"].min()), int(master["age"].max())
    age_range = st.slider("Faixa etária", age_min, age_max, (18, 38))

    min_apps = st.slider("Mínimo de partidas disputadas", 0, 100, 10)

    st.divider()

# Aplica filtros ao master
mask = (
    master["position_group"].isin(posicoes_sel)
    & master["age"].between(*age_range)
    & (master["total_appearances"] >= min_apps)
)
df = master[mask].copy()

# KPIs no topo
st.title("Análise de Desempenho e Valor de Mercado no Futebol Europeu")
st.markdown(
    "> **Pergunta de negócio:** Quais fatores — posição, idade, volume de jogo e estatísticas "
    "ofensivas — mais influenciam o valor de mercado de um jogador profissional?"
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Jogadores Analisados", f"{len(df):,}")
k2.metric("Gols Totais", f"{int(df['total_goals'].sum()):,}")
k3.metric("Assistências Totais", f"{int(df['total_assists'].sum()):,}")
k4.metric(
    "Valor Mediano",
    fmt_eur(df["latest_market_value"].median()) if df["latest_market_value"].notna().any() else "N/A",
)
k6.metric("Período dos Dados", f"{app_date_min.year} – {app_date_max.year}")
k5.metric(
    "Idade Média",
    f"{df['age'].mean():.1f} anos",
)

st.divider()

# Abas da interface
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Distribuição de Valor",
    "⚡ Performance por Posição",
    "📈 Evolução Temporal",
    "🏆 Top Jogadores",
    "🤖 Modelo Preditivo",
])


# ABA 1 — DISTRIBUIÇÃO DE VALOR DE MERCADO
with tab1:
    st.subheader("Distribuição do Valor de Mercado por Posição")
    st.markdown(
        "Jogadores de ataque concentram os maiores valores, mas a dispersão é alta — "
        "poucos superastros elevam a média de forma significativa."
    )

    df_val = df.dropna(subset=["latest_market_value"])
    df_val = df_val[df_val["latest_market_value"] > 0]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    fig.subplots_adjust(bottom=0.18)

    # --- Barras empilhadas: proporção por faixa de valor ---
    ax = axes[0]
    pos_order = [p for p in POSITION_ORDER if p in df_val["position_group"].unique()]

    faixas = {
        "< €1M":      (0,          1_000_000),
        "€1M – €10M": (1_000_000,  10_000_000),
        "€10M – €50M":(10_000_000, 50_000_000),
        "> €50M":     (50_000_000, float("inf")),
    }
    faixa_cores = ["#b0bec5", "#64b5f6", "#42a5f5", "#1565c0"]

    proporcoes = {}
    for pos in pos_order:
        sub = df_val[df_val["position_group"] == pos]["latest_market_value"]
        total = len(sub)
        proporcoes[pos] = [
            100 * ((sub >= lo) & (sub < hi)).sum() / total
            for lo, hi in faixas.values()
        ]

    bottoms = [0] * len(pos_order)
    for (faixa, _), cor in zip(faixas.items(), faixa_cores):
        vals = [proporcoes[p][list(faixas.keys()).index(faixa)] for p in pos_order]
        bars = ax.bar(pos_order, vals, bottom=bottoms, color=cor,
                      label=faixa, edgecolor="white", linewidth=0.5)
        for bar, v, b in zip(bars, vals, bottoms):
            if v > 6:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    b + v / 2,
                    f"{v:.0f}%",
                    ha="center", va="center", fontsize=8.5,
                    fontweight="bold", color="white",
                )
        bottoms = [b + v for b, v in zip(bottoms, vals)]

    ax.set_title("Distribuição por Faixa de Valor", fontsize=13, fontweight="bold")
    ax.set_xlabel("Posição")
    ax.set_ylabel("% de Jogadores")
    ax.set_ylim(0, 105)
    ax.legend(loc="upper left", bbox_to_anchor=(0, -0.15), ncol=2, fontsize=8, framealpha=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    # --- Barras com valor mediano ---
    ax2 = axes[1]
    medians = (
        df_val.groupby("position_group")["latest_market_value"]
        .median()
        .reindex(pos_order)
    )
    max_median = medians.max()
    # Usa €K se todos os medianos forem abaixo de 1M, caso contrário €M
    if max_median < 1_000_000:
        divisor, ylabel, tick_fmt = 1_000, "€ Mil (K)", lambda x, _: f"€{x:,.0f}K"
    else:
        divisor, ylabel, tick_fmt = 1_000_000, "€ Milhões", lambda x, _: f"€{x:.1f}M"

    bars = ax2.bar(
        pos_order,
        medians.values / divisor,
        color=[COLORS.get(p, "#888") for p in pos_order],
        alpha=0.85,
        edgecolor="white",
        width=0.5,
    )
    y_max = (medians.values / divisor).max()
    for bar, val in zip(bars, medians.values):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + y_max * 0.02,
            fmt_eur(val),
            ha="center", va="bottom", fontsize=10, fontweight="bold",
        )
    ax2.set_title("Valor Mediano por Posição", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Posição")
    ax2.set_ylabel(ylabel)
    ax2.set_ylim(0, y_max * 1.18)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(tick_fmt))
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # --- Histograma + densidade ---
    st.markdown("---")
    st.markdown("#### Histograma do Valor de Mercado (escala log)")
    fig2, ax3 = plt.subplots(figsize=(12, 4))
    for pos in pos_order:
        subset = df_val[df_val["position_group"] == pos]["log_latest_value"]
        ax3.hist(
            subset, bins=40, alpha=0.55, label=pos,
            color=COLORS.get(pos, "#888"), edgecolor="none",
        )
    ax3.set_title("Distribuição do log(Valor de Mercado) por Posição", fontsize=13, fontweight="bold")
    ax3.set_xlabel("log(€ + 1)")
    ax3.set_ylabel("Quantidade de Jogadores")
    ax3.legend()
    ax3.spines[["top", "right"]].set_visible(False)
    ax3.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # --- Scatter: Idade × Valor ---
    st.markdown("---")
    st.markdown("#### Relação Idade × Valor de Mercado")
    fig3, ax4 = plt.subplots(figsize=(12, 5))
    for pos in pos_order:
        sub = df_val[df_val["position_group"] == pos]
        ax4.scatter(
            sub["age"], sub["latest_market_value"] / 1e6,
            alpha=0.25, s=12, label=pos, color=COLORS.get(pos, "#888"),
        )
    ax4.set_title("Idade vs. Valor de Mercado", fontsize=13, fontweight="bold")
    ax4.set_xlabel("Idade (anos)")
    ax4.set_ylabel("Valor de Mercado (€M)")
    ax4.set_ylim(bottom=0)
    ax4.legend(markerscale=2)
    ax4.spines[["top", "right"]].set_visible(False)
    ax4.grid(linestyle="--", alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    with st.expander("Insight"):
        st.markdown(
            "- A maioria dos jogadores profissionais vale **menos de €1M** — "
            "o mercado é concentrado no topo.\n"
            "- **Atacantes** têm a maior proporção de jogadores acima de €10M.\n"
            "- O pico de valor ocorre tipicamente entre **22 e 27 anos**, declinando após os 30.\n"
            "- Poucos superastros (> €50M) concentram grande parte do valor total do mercado."
        )



# ABA 2 — PERFORMANCE POR POSIÇÃO
with tab2:
    st.subheader("Métricas de Performance por Posição")

    # Médias por posição
    perf = (
        df.groupby("position_group")[
            ["goals_per_game", "assists_per_game", "minutes_per_game",
             "total_yellow", "total_red", "seasons_active"]
        ]
        .mean()
        .reindex([p for p in POSITION_ORDER if p in df["position_group"].unique()])
        .round(3)
    )

    fig, axes = plt.subplots(2, 3, figsize=(16, 9))

    metrics = [
        ("goals_per_game", "Gols por Jogo", "Média de Gols"),
        ("assists_per_game", "Assistências por Jogo", "Média de Assistências"),
        ("minutes_per_game", "Minutos por Jogo", "Minutos"),
        ("total_yellow", "Total de Cartões Amarelos", "Média de Amarelos"),
        ("total_red", "Total de Cartões Vermelhos", "Média de Vermelhos"),
        ("seasons_active", "Temporadas Ativas", "Média de Temporadas"),
    ]

    for ax, (col, title, ylabel) in zip(axes.flat, metrics):
        pos_list = perf.index.tolist()
        vals = perf[col].values
        colors = [COLORS.get(p, "#888") for p in pos_list]
        bars = ax.bar(pos_list, vals, color=colors, alpha=0.85, edgecolor="white")
        for bar, v in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(vals) * 0.01,
                f"{v:.2f}",
                ha="center", va="bottom", fontsize=8.5,
            )
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.tick_params(labelsize=8.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.suptitle("Métricas Médias por Posição", fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Tabela resumo
    st.markdown("#### Tabela de Estatísticas por Posição")
    st.dataframe(
        perf.rename(columns={
            "goals_per_game": "Gols/Jogo",
            "assists_per_game": "Assistências/Jogo",
            "minutes_per_game": "Minutos/Jogo",
            "total_yellow": "Amarelos (média)",
            "total_red": "Vermelhos (média)",
            "seasons_active": "Temporadas Ativas",
        }).style.background_gradient(cmap="Blues", axis=0),
        use_container_width=True,
    )

    with st.expander("Insight"):
        st.markdown(
            "- **Atacantes** lideram em gols por jogo, enquanto **Meio-Campistas** "
            "dominam em assistências.\n"
            "- **Defensores** apresentam mais cartões amarelos, reflexo do estilo de jogo.\n"
            "- **Goleiros** têm a maior média de minutos por jogo (quase sempre jogam o tempo todo)."
        )

    # --- Heatmap de Correlação ---
    st.markdown("---")
    st.markdown("#### Correlação entre Variáveis Numéricas")
    st.caption("Valores próximos de 1 indicam correlação positiva forte; próximos de -1, correlação negativa.")

    fig_corr, ax_corr = plt.subplots(figsize=(10, 7))
    corr_data = corr_matrix.values
    labels = [
        c.replace("_", " ").replace("total ", "").title()
        for c in corr_matrix.columns
    ]
    im = ax_corr.imshow(corr_data, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax_corr, fraction=0.03)
    ax_corr.set_xticks(range(len(labels)))
    ax_corr.set_yticks(range(len(labels)))
    ax_corr.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax_corr.set_yticklabels(labels, fontsize=8)
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = corr_data[i, j]
            if not np.isnan(val):
                ax_corr.text(j, i, f"{val:.2f}", ha="center", va="center",
                             fontsize=7, color="black" if abs(val) < 0.7 else "white")
    ax_corr.set_title("Matriz de Correlação — Atributos dos Jogadores",
                      fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    st.pyplot(fig_corr)
    plt.close()

    with st.expander("Como ler este gráfico"):
        st.markdown(
            "- **Verde escuro** → correlação positiva forte (as duas variáveis crescem juntas)\n"
            "- **Vermelho** → correlação negativa (quando uma sobe, a outra tende a cair)\n"
            "- **Amarelo/branco** → pouca ou nenhuma correlação\n\n"
            "Por exemplo: **gols totais** e **valor de mercado** tendem a ter correlação positiva, "
            "enquanto **idade** e **valor** podem apresentar correlação negativa a partir de certo ponto."
        )


# ABA 3 — EVOLUÇÃO TEMPORAL
with tab3:
    s_ini, s_fim = season_range
    st.subheader(f"Evolução Temporal de Gols e Valores de Mercado — Temporadas {s_ini}/{s_ini+1} a {s_fim}/{s_fim+1}")

    st.caption(
        f"Cobertura completa do dataset: partidas de **{app_date_min.strftime('%d/%m/%Y')}** "
        f"até **{app_date_max.strftime('%d/%m/%Y')}** · "
        f"Valores de mercado de **{val_date_min.strftime('%d/%m/%Y')}** "
        f"até **{val_date_max.strftime('%d/%m/%Y')}**"
    )

    # Gols por temporada (respeita filtro de temporada da sidebar)
    apps_season = (
        appearances[appearances["season"].between(s_ini, s_fim)]
        .groupby("season")
        .agg(total_goals=("goals", "sum"), total_assists=("assists", "sum"),
             total_games=("appearance_id", "count"))
        .reset_index()
    )

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    ax = axes[0]
    ax.fill_between(apps_season["season"], apps_season["total_goals"],
                    alpha=0.3, color="#e74c3c")
    ax.plot(apps_season["season"], apps_season["total_goals"],
            color="#e74c3c", marker="o", lw=2, label="Gols")
    ax.fill_between(apps_season["season"], apps_season["total_assists"],
                    alpha=0.3, color="#3498db")
    ax.plot(apps_season["season"], apps_season["total_assists"],
            color="#3498db", marker="s", lw=2, label="Assistências")
    ax.set_title(f"Gols e Assistências por Temporada ({s_ini}–{s_fim})", fontsize=13, fontweight="bold")
    ax.set_xlabel("Temporada")
    ax.set_ylabel("Total")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(linestyle="--", alpha=0.4)

    # Evolução mediana do valor de mercado por ano (respeita filtro)
    val_year = (
        valuations[valuations["date"].dt.year.between(s_ini, s_fim + 1)]
        .assign(year=lambda x: x["date"].dt.year)
        .groupby("year")["market_value_in_eur"]
        .median()
        .reset_index()
    )

    ax2 = axes[1]
    ax2.fill_between(val_year["year"], val_year["market_value_in_eur"] / 1e6,
                     alpha=0.3, color="#f39c12")
    ax2.plot(val_year["year"], val_year["market_value_in_eur"] / 1e6,
             color="#f39c12", marker="o", lw=2)
    ax2.set_title(f"Valor de Mercado Mediano por Ano (€M) — {s_ini}–{s_fim+1}", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Ano")
    ax2.set_ylabel("€ Milhões")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(linestyle="--", alpha=0.4)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Gols por jogo (média) ao longo das temporadas
    st.markdown("---")
    st.markdown(f"#### Gols por Partida (média) — Temporadas {s_ini} a {s_fim}")
    apps_season["goals_per_game"] = apps_season["total_goals"] / apps_season["total_games"]

    fig2, ax3 = plt.subplots(figsize=(12, 4))
    ax3.bar(
        apps_season["season"], apps_season["goals_per_game"],
        color="#e74c3c", alpha=0.75, edgecolor="white"
    )
    ax3.set_title("Média de Gols por Aparição por Temporada", fontsize=13, fontweight="bold")
    ax3.set_xlabel("Temporada")
    ax3.set_ylabel("Gols / Aparição")
    ax3.spines[["top", "right"]].set_visible(False)
    ax3.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    with st.expander("Insight"):
        st.markdown(
            "- O volume de gols e assistências cresceu consistentemente até ~2019, "
            "com queda em 2020 (pandemia, menos jogos registrados).\n"
            "- O **valor de mercado mediano** dobrou entre 2012 e 2023, refletindo a "
            "inflação no futebol europeu."
        )

# ABA 4 — TOP JOGADORES
with tab4:
    st.subheader("Ranking de Jogadores")

    col_left, col_right = st.columns(2)

    with col_left:
        n_top = st.slider("Quantidade de jogadores no ranking", 5, 30, 15)
        metrica = st.selectbox(
            "Ordenar por",
            ["total_goals", "total_assists", "total_contributions",
             "goals_per_game", "latest_market_value"],
            format_func=lambda x: {
                "total_goals": "Total de Gols",
                "total_assists": "Total de Assistências",
                "total_contributions": "Contribuições (G+A)",
                "goals_per_game": "Gols por Jogo",
                "latest_market_value": "Valor de Mercado",
            }[x],
        )

    df_rank = (
        df.dropna(subset=["name"])
        .sort_values(metrica, ascending=False)
        .head(n_top)[["name", "position_group", "age", "country_of_citizenship",
                       "total_goals", "total_assists", "total_contributions",
                       "goals_per_game", "total_appearances", "latest_market_value"]]
    )

    fig, ax = plt.subplots(figsize=(12, max(4, n_top * 0.4)))
    colors = [COLORS.get(p, "#888") for p in df_rank["position_group"]]
    valores = df_rank[metrica].values

    if metrica == "latest_market_value":
        label_fmt = [fmt_eur(v) for v in valores]
        x_vals = valores / 1e6
        xlabel = "€ Milhões"
    else:
        label_fmt = [f"{v:.2f}" if "per_game" in metrica else f"{int(v)}" for v in valores]
        x_vals = valores
        xlabel = metrica.replace("_", " ").title()

    bars = ax.barh(df_rank["name"], x_vals, color=colors, alpha=0.85, edgecolor="white")
    for bar, label in zip(bars, label_fmt):
        ax.text(
            bar.get_width() + max(x_vals) * 0.005,
            bar.get_y() + bar.get_height() / 2,
            label, va="center", fontsize=8.5,
        )

    ax.invert_yaxis()
    ax.set_title(f"Top {n_top} — {xlabel}", fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=COLORS[p], label=p) for p in POSITION_ORDER if p in df_rank["position_group"].values]
    ax.legend(handles=legend_elements, loc="lower right")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Distribuição de nacionalidades
    st.markdown("---")
    st.markdown("#### Distribuição por Nacionalidade (Top 20)")
    nac_col = "country_of_citizenship" if "country_of_citizenship" in df.columns else "country_of_birth"

    # Normaliza nomes duplicados de países no dataset
    country_aliases = {
        "Türkiye": "Turkey",
        "Czech Republic": "Czechia",
        "Korea, South": "South Korea",
        "Korea, North": "North Korea",
        "IR Iran": "Iran",
        "Côte d'Ivoire": "Ivory Coast",
        "UdSSR": "União Soviética (ex-URSS)",
        "Soviet Union": "União Soviética (ex-URSS)",
        "Jugoslawien (SFR)": "Iugoslávia (ex-SFR)",
        "Yugoslavia": "Iugoslávia (ex-SFR)",
    }
    nac_series = df[nac_col].replace(country_aliases)
    nac = nac_series.value_counts().head(20)

    fig2, ax2 = plt.subplots(figsize=(12, 5))
    ax2.bar(nac.index, nac.values, color="#3498db", alpha=0.8, edgecolor="white")
    ax2.set_title("Top 20 Nacionalidades dos Jogadores", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Nacionalidade")
    ax2.set_ylabel("Quantidade")
    ax2.tick_params(axis="x", rotation=45)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    top1 = nac.index[0]
    top2 = nac.index[1]
    top3 = nac.index[2]
    pct_top3 = round(nac.values[:3].sum() / nac.values.sum() * 100)

    with st.expander("Insight"):
        st.markdown(
            f"- **{top1}**, **{top2}** e **{top3}** são os países com mais jogadores "
            f"no futebol europeu, representando juntos cerca de **{pct_top3}%** do Top 20.\n"
            "- O Brasil é o único país não europeu no topo do ranking, reflexo de décadas "
            "de exportação de talento para as ligas europeias.\n"
            "- A forte presença de países como Espanha, França e Alemanha reflete o tamanho "
            "e a profundidade das suas ligas nacionais — que formam e retêm jogadores.\n"
            "- A coluna utilizada é **`country_of_citizenship`** (cidadania), portanto "
            "jogadores com dupla nacionalidade são contados pelo passaporte declarado no dataset."
        )


# ABA 5 — MODELO PREDITIVO
with tab5:
    st.subheader("Modelo Preditivo: Estimativa do Valor de Mercado")
    st.markdown(
        "Usamos um **Histogram Gradient Boosting Regressor** para estimar o valor de mercado "
        "com base em atributos do jogador e estatísticas acumuladas de carreira. "
        "O modelo é treinado automaticamente na primeira vez que esta aba é acessada."
    )

    try:
        with st.spinner("Treinando modelo — aguarde alguns segundos..."):
            results = get_model_results(master)
    except Exception as e:
        st.error(f"Erro ao treinar modelo: {e}")
        st.stop()

    # Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("R² (teste)", f"{results['r2_test']:.3f}")
    m2.metric("MAE médio (€)", fmt_eur(results["mae_eur"]))
    m3.metric("Amostras treino / teste", f"{results['n_train']} / {results['n_test']}")

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Predito × Real
    ax = axes[0]
    y_true = results["y_true_eur"] / 1e6
    y_pred = results["y_pred_eur"] / 1e6
    lim = max(y_true.max(), y_pred.max())
    ax.scatter(y_true, y_pred, alpha=0.25, s=10, color="#3498db")
    ax.plot([0, lim], [0, lim], "r--", lw=1.5, label="Ideal")
    ax.set_title("Valor Real vs. Predito (€M)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Valor Real (€M)")
    ax.set_ylabel("Valor Predito (€M)")
    ax.legend()
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(linestyle="--", alpha=0.3)

    # Feature importance
    ax2 = axes[1]
    if not results["feature_importances"].empty:
        fi = results["feature_importances"]
        ax2.barh(fi["feature"], fi["importance"], color="#e74c3c", alpha=0.8, edgecolor="white")
        ax2.invert_yaxis()
        ax2.set_title("Top 10 Features por Importância", fontsize=13, fontweight="bold")
        ax2.set_xlabel("Importância")
        ax2.spines[["top", "right"]].set_visible(False)
        ax2.grid(axis="x", linestyle="--", alpha=0.4)
    else:
        ax2.set_visible(False)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Preditor interativo
    st.markdown("---")
    st.markdown("#### Simulador de Valor de Mercado")
    st.markdown("Insira as características de um jogador hipotético para estimar seu valor:")

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sim_age = st.number_input("Idade", 16, 45, 24)
        sim_pos = st.selectbox("Posição", POSITION_ORDER)
        sim_apps = st.number_input("Total de Partidas", 0, 800, 80)
    with sc2:
        sim_goals = st.number_input("Total de Gols", 0, 500, 30)
        sim_assists = st.number_input("Total de Assistências", 0, 500, 20)
        sim_minutes = st.number_input("Total de Minutos", 0, 80000, 6500)
    with sc3:
        sim_yellow = st.number_input("Cartões Amarelos", 0, 100, 8)
        sim_red = st.number_input("Cartões Vermelhos (total)", 0, 20, 0)
        sim_seasons = st.number_input("Temporadas Ativas", 1, 25, 4)

    gpg = round(sim_goals / sim_apps, 3) if sim_apps > 0 else 0
    apg = round(sim_assists / sim_apps, 3) if sim_apps > 0 else 0
    mpg = round(sim_minutes / sim_apps, 1) if sim_apps > 0 else 0
    rpg = round(sim_red / sim_apps, 4) if sim_apps > 0 else 0

    sim_df = pd.DataFrame([{
        "age": sim_age, "position_group": sim_pos,
        "total_appearances": sim_apps, "total_goals": sim_goals,
        "total_assists": sim_assists, "total_minutes": sim_minutes,
        "total_yellow": sim_yellow, "red_cards_per_game": rpg,
        "goals_per_game": gpg, "assists_per_game": apg,
        "minutes_per_game": mpg, "seasons_active": sim_seasons,
    }])

    log_pred = results["pipeline"].predict(sim_df)[0]
    valor_pred = np.expm1(log_pred)

    st.success(f"**Valor de Mercado Estimado: {fmt_eur(valor_pred)}**")

    with st.expander("Interpretação do Modelo"):
        st.markdown(
            f"- R² de **{results['r2_test']:.3f}** indica que o modelo explica ~"
            f"{results['r2_test']*100:.0f}% da variância do log do valor de mercado.\n"
            "- O erro absoluto mediano está na casa dos milhões de euros — esperado "
            "dado a enorme variância dos valores no futebol.\n"
            "- **Limitações:** o modelo não captura fatores subjetivos (prestígio do clube, "
            "forma recente, lesões) que têm grande impacto no valor real.\n"
            "- Features mais relevantes: **total de aparições**, **gols por jogo** e **idade**."
        )
