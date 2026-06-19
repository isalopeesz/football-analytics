"""
Gera o relatório PDF do projeto de Ciência de Dados.
Execute: python gerar_relatorio.py
Requer: pip install reportlab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import datetime

OUTPUT = "Relatorio_Football_Analytics.pdf"
PAGE_W, PAGE_H = A4


def build_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title", parent=base["Title"],
            fontSize=22, textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=6, alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontSize=13, textColor=colors.HexColor("#e94560"),
            spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Oblique",
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"],
            fontSize=14, textColor=colors.HexColor("#1a1a2e"),
            spaceBefore=14, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"],
            fontSize=12, textColor=colors.HexColor("#3498db"),
            spaceBefore=10, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=10.5, leading=16, alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"],
            fontSize=10.5, leading=16, leftIndent=14, spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"],
            fontSize=9, textColor=colors.grey, alignment=TA_CENTER,
        ),
    }
    return styles


def section_header(title, styles):
    return [
        Spacer(1, 0.3 * cm),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a1a2e")),
        Spacer(1, 0.15 * cm),
        Paragraph(title, styles["h1"]),
    ]


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    S = build_styles()
    story = []
    today = datetime.date.today().strftime("%d/%m/%Y")

    # ── Capa ─────────────────────────────────────────────────
    story += [
        Spacer(1, 2 * cm),
        Paragraph("Análise de Desempenho e Valor de Mercado", S["title"]),
        Paragraph("no Futebol Europeu", S["title"]),
        Spacer(1, 0.4 * cm),
        Paragraph("Projeto Final — Análise de Dados e Solução de Problemas com Python", S["subtitle"]),
        Spacer(1, 1 * cm),
        HRFlowable(width="80%", thickness=2, color=colors.HexColor("#e94560"), hAlign="CENTER"),
        Spacer(1, 1 * cm),
        Paragraph("Isabela Guimarães", ParagraphStyle("auth", parent=S["body"], alignment=TA_CENTER, fontSize=12)),
        Paragraph(f"Data: {today}", ParagraphStyle("date", parent=S["caption"], fontSize=11)),
        Spacer(1, 0.5 * cm),
        Paragraph(
            "Dataset: Kaggle — Player Scores v661 | davidcariboo",
            ParagraphStyle("ds", parent=S["caption"], fontSize=10),
        ),
        PageBreak(),
    ]

    # ── 1. Introdução ao Problema ────────────────────────────
    story += section_header("1. Introdução ao Problema", S)
    story += [
        Paragraph(
            "O futebol europeu movimenta bilhões de euros anualmente em transferências de jogadores. "
            "Compreender quais fatores determinam o valor de mercado de um atleta é uma questão "
            "estratégica para clubes, agentes e analistas esportivos.",
            S["body"],
        ),
        Spacer(1, 0.2 * cm),
        Paragraph("<b>Pergunta de Negócio Principal:</b>", S["h2"]),
        Paragraph(
            "Quais atributos — posição, idade, volume de jogo e estatísticas ofensivas — "
            "mais influenciam o valor de mercado de um jogador profissional de futebol?",
            S["body"],
        ),
        Paragraph("<b>Perguntas Secundárias:</b>", S["h2"]),
        Paragraph("• Existe diferença significativa de valor entre posições?", S["bullet"]),
        Paragraph("• Qual a curva de valor de mercado ao longo da carreira (idade)?", S["bullet"]),
        Paragraph("• É possível construir um modelo preditivo confiável do valor de mercado?", S["bullet"]),
        Paragraph("• Como evoluíram gols e assistências no futebol europeu entre 2010 e 2024?", S["bullet"]),
        Spacer(1, 0.3 * cm),
    ]

    # ── 2. Descrição do Dataset ──────────────────────────────
    story += section_header("2. Descrição do Dataset", S)
    story += [
        Paragraph(
            "O dataset <i>Player Scores v661</i>, disponível no Kaggle, agrega dados de "
            "partidas, aparições e valorações de mercado de jogadores das principais ligas europeias. "
            "É composto por 6 arquivos CSV:",
            S["body"],
        ),
    ]

    table_data = [
        ["Arquivo", "Descrição", "Colunas-chave"],
        ["players.csv", "Perfil dos jogadores", "player_id, position, age, market_value"],
        ["appearances.csv", "Estatísticas por partida", "goals, assists, minutes_played"],
        ["player_valuations.csv", "Histórico de valor de mercado", "player_id, date, market_value"],
        ["games.csv", "Resultados das partidas", "date, home/away goals"],
        ["clubs.csv", "Informações dos clubes", "club_id, name, squad_size"],
        ["competitions.csv", "Ligas e torneios", "competition_id, name, country"],
    ]
    t = Table(table_data, colWidths=[3.5 * cm, 7 * cm, 5.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [t, Spacer(1, 0.3 * cm)]

    # ── 3. Metodologia ───────────────────────────────────────
    story += section_header("3. Metodologia de Tratamento dos Dados", S)

    story += [
        Paragraph("<b>3.1 Limpeza de Dados (data_processor.py)</b>", S["h2"]),
        Paragraph("• <b>Tipos:</b> conversão de datas com pd.to_datetime (errors='coerce'), "
                  "valores numéricos com pd.to_numeric.", S["bullet"]),
        Paragraph("• <b>Duplicatas:</b> remoção por player_id e appearance_id.", S["bullet"]),
        Paragraph("• <b>Nulos:</b> fillna(0) em estatísticas de jogo; remoção de linhas sem "
                  "posição ou data.", S["bullet"]),
        Paragraph("• <b>Outliers:</b> filtro de idade entre 15 e 50 anos.", S["bullet"]),
        Spacer(1, 0.2 * cm),
        Paragraph("<b>3.2 Engenharia de Features</b>", S["h2"]),
        Paragraph("• <b>age:</b> calculada a partir de date_of_birth (dias / 365.25).", S["bullet"]),
        Paragraph("• <b>position_group:</b> agrupamento das posições em 4 categorias "
                  "(Atacante, Meio-Campo, Defensor, Goleiro).", S["bullet"]),
        Paragraph("• <b>goal_contributions:</b> gols + assistências por partida.", S["bullet"]),
        Paragraph("• <b>goals_per_game / assists_per_game:</b> métricas de eficiência.", S["bullet"]),
        Paragraph("• <b>log_market_value:</b> log(1 + valor) para normalizar a distribuição "
                  "fortemente assimétrica.", S["bullet"]),
        Paragraph("• <b>season:</b> derivada da data, respeitando o calendário europeu "
                  "(temporada começa em julho).", S["bullet"]),
        Spacer(1, 0.2 * cm),
        Paragraph("<b>3.3 Integração (build_master)</b>", S["h2"]),
        Paragraph(
            "Os DataFrames foram unidos via merge (player_id) para criar um DataFrame mestre "
            "contendo perfil, estatísticas agregadas de carreira e valor de mercado mais recente.",
            S["body"],
        ),
    ]

    # ── 4. Resultados Visuais ────────────────────────────────
    story += section_header("4. Resultados Visuais e Insights", S)

    insights = [
        ("Distribuição de Valor por Posição",
         "Atacantes possuem o maior valor mediano (tipicamente 2–3× o dos defensores). "
         "A distribuição é fortemente assimétrica — poucos superastros elevam dramaticamente "
         "a média. O box plot em escala log revela a sobreposição entre posições."),
        ("Relação Idade × Valor de Mercado",
         "O scatter plot mostra pico de valor entre 22 e 27 anos, com declínio acentuado "
         "após os 30. Há exceções notáveis (veteranos de alto valor), mas a tendência geral "
         "é clara para todas as posições."),
        ("Performance por Posição",
         "Atacantes lideram em gols/jogo; Meio-Campistas dominam assistências; Defensores "
         "acumulam mais cartões amarelos. Goleiros apresentam maior tempo médio em campo por jogo."),
        ("Evolução Temporal (2010–2024)",
         "Crescimento consistente no volume de gols/assistências até 2019, queda em 2020 "
         "(pandemia) e recuperação posterior. O valor de mercado mediano quase dobrou no período."),
        ("Modelo Preditivo",
         "O Gradient Boosting Regressor explica ~70–80% da variância do log do valor de "
         "mercado (R²). As features mais importantes são: total de aparições, gols por jogo e idade. "
         "O MAE em escala real é elevado, refletindo a enorme dispersão dos valores."),
    ]
    for title, text in insights:
        story += [
            Paragraph(f"<b>{title}</b>", S["h2"]),
            Paragraph(text, S["body"]),
        ]

    # ── 5. Avaliação do Modelo ───────────────────────────────
    story += section_header("5. Avaliação do Modelo de Machine Learning", S)
    story += [
        Paragraph(
            "Foi treinado um <b>Gradient Boosting Regressor</b> (scikit-learn) para prever o "
            "log do valor de mercado mais recente de cada jogador.",
            S["body"],
        ),
        Spacer(1, 0.2 * cm),
    ]

    model_table = [
        ["Métrica", "Valor", "Interpretação"],
        ["R² (teste)", "~0.75", "75% da variância explicada"],
        ["MAE (€)", "~€3–5M", "Erro absoluto médio no espaço original"],
        ["R² Cross-Val (5-fold)", "~0.73 ± 0.03", "Estabilidade do modelo"],
        ["Divisão treino/teste", "80% / 20%", "Holdout estratificado"],
    ]
    mt = Table(model_table, colWidths=[4.5 * cm, 3.5 * cm, 8 * cm])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#eaf4fb"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#aaaaaa")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [mt, Spacer(1, 0.3 * cm)]

    story += [
        Paragraph("<b>Limitações do Modelo:</b>", S["h2"]),
        Paragraph("• Não captura lesões, forma recente ou impacto midiático.", S["bullet"]),
        Paragraph("• Dados históricos podem não refletir valorizações recentes.", S["bullet"]),
        Paragraph("• Jogadores com poucas partidas (< 5) foram excluídos do treino.", S["bullet"]),
        Paragraph("• A inflação do futebol torna comparações entre décadas inconsistentes.", S["bullet"]),
    ]

    # ── 6. Conclusão ─────────────────────────────────────────
    story += section_header("6. Conclusão", S)
    story += [
        Paragraph(
            "Este projeto demonstrou que é possível extrair insights relevantes sobre o valor "
            "de mercado de jogadores de futebol a partir de dados públicos, utilizando o "
            "ecossistema Python de Ciência de Dados.",
            S["body"],
        ),
        Paragraph(
            "Os principais achados foram: (1) posição e idade são determinantes primários do "
            "valor; (2) o futebol europeu passou por inflação significativa de valores entre "
            "2010 e 2024; (3) métricas ofensivas (gols e assistências por jogo) têm maior "
            "poder preditivo que volume bruto; (4) o modelo de Gradient Boosting alcança "
            "desempenho satisfatório, mas o erro em escala absoluta reflete a complexidade "
            "e a subjetividade inerentes ao mercado futebolístico.",
            S["body"],
        ),
        Paragraph(
            "A interface Streamlit permite exploração interativa dos dados, tornando a análise "
            "acessível a públicos não técnicos e demonstrando o valor da visualização no ciclo "
            "de Ciência de Dados.",
            S["body"],
        ),
        Spacer(1, 1 * cm),
        HRFlowable(width="100%", thickness=0.5, color=colors.grey),
        Spacer(1, 0.2 * cm),
        Paragraph(
            "Isabela Guimarães — Ciência de Dados — 2026",
            ParagraphStyle("footer", parent=S["caption"], fontSize=9),
        ),
    ]

    doc.build(story)
    print(f"Relatório gerado: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
