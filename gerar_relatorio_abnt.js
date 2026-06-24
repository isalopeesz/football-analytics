const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  HeadingLevel, PageBreak, LevelFormat, Header, Footer,
  PageNumber, BorderStyle, TabStopType, TabStopPosition,
  Table, TableRow, TableCell, WidthType, ShadingType, VerticalAlign,
} = require("docx");
const fs = require("fs");

// ── Medidas ABNT (A4) ────────────────────────────────────
// 1 cm = 567 DXA  |  A4 = 11906 x 16838 DXA
const MARGIN = { top: 1701, bottom: 1134, left: 1701, right: 1134 }; // 3/2/3/2 cm
const CONTENT_W = 11906 - 1701 - 1134; // 9071 DXA

// ── Helpers ──────────────────────────────────────────────
const br = () => new Paragraph({ children: [new PageBreak()] });

const p = (text, opts = {}) =>
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 0 },   // espaço simples, sem após
    indent: { firstLine: 709 },          // 1.25 cm
    children: [new TextRun({ text, font: "Times New Roman", size: 24, ...opts })],
  });

const pEmpty = () =>
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun("")] });

const pCenter = (text, bold = false, size = 24) =>
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { line: 240, after: 0 },
    children: [new TextRun({ text, font: "Times New Roman", size, bold })],
  });

const heading1 = (num, text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { line: 240, before: 240, after: 120 },
    children: [new TextRun({ text: `${num}\t${text}`, font: "Times New Roman", size: 24, bold: true, allCaps: true })],
  });

const heading2 = (num, text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { line: 240, before: 120, after: 120 },
    children: [new TextRun({ text: `${num}\t${text}`, font: "Times New Roman", size: 24, bold: true })],
  });

const heading3 = (num, text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { line: 240, before: 120, after: 120 },
    children: [new TextRun({ text: `${num}\t${text}`, font: "Times New Roman", size: 24, bold: true, italics: true })],
  });

const label = (text) =>
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { line: 240, before: 240, after: 0 },
    children: [new TextRun({ text, font: "Times New Roman", size: 24, bold: true, allCaps: true })],
  });

const li = (num, text) =>
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 0 },
    indent: { left: 709, hanging: 354 },
    children: [new TextRun({ text: `${num}. ${text}`, font: "Times New Roman", size: 24 })],
  });

// ── Seções ───────────────────────────────────────────────

// CAPA
const capa = [
  pCenter("UNIVERSIDADE CATÓLICA DE BRASÍLIA", true, 24),
  pCenter("PRÓ-REITORIA ACADÊMICA", false, 24),
  pCenter("Curso de Bacharelado em Engenharia de Software", false, 24),
  pCenter("Trabalho de Disciplina", false, 24),
  pEmpty(), pEmpty(), pEmpty(), pEmpty(),
  pCenter("ANÁLISE DE DESEMPENHO E VALOR DE MERCADO NO FUTEBOL EUROPEU:", true, 24),
  pCenter("UMA ABORDAGEM COM PYTHON E APRENDIZADO DE MÁQUINA", true, 24),
  pEmpty(), pEmpty(), pEmpty(), pEmpty(),
  pCenter("Autora: Isabela Guimarães", false, 24),
  pCenter("Orientador: Prof. Dr. Milton Pombo da Paz", false, 24),
  pEmpty(), pEmpty(), pEmpty(), pEmpty(),
  pCenter("Brasília – DF", false, 24),
  pCenter("2026", false, 24),
  br(),
];

// FOLHA DE ROSTO
const folhaRosto = [
  pCenter("ISABELA GUIMARÃES", true, 24),
  pEmpty(), pEmpty(),
  pCenter("ANÁLISE DE DESEMPENHO E VALOR DE MERCADO NO FUTEBOL EUROPEU:", true, 24),
  pCenter("UMA ABORDAGEM COM PYTHON E APRENDIZADO DE MÁQUINA", true, 24),
  pEmpty(), pEmpty(), pEmpty(),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 0 },
    indent: { left: 4535 },
    children: [new TextRun({
      text: "Documento apresentado ao Curso de Bacharelado em Engenharia de Software da Universidade Católica de Brasília, como requisito parcial para obtenção da aprovação na disciplina de Análise de Dados e Solução de Problemas com Python.",
      font: "Times New Roman", size: 22,
    })],
  }),
  pEmpty(),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 0 },
    indent: { left: 4535 },
    children: [new TextRun({ text: "Orientador: Prof. Dr. Milton Pombo da Paz", font: "Times New Roman", size: 22 })],
  }),
  pEmpty(), pEmpty(), pEmpty(), pEmpty(),
  pCenter("Brasília", false, 24),
  pCenter("2026", false, 24),
  br(),
];

// RESUMO
const resumo = [
  label("RESUMO"),
  pEmpty(),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 0 },
    children: [new TextRun({
      text: "Referência: GUIMARÃES, Isabela. Análise de Desempenho e Valor de Mercado no Futebol Europeu: uma abordagem com Python e Aprendizado de Máquina. 2026. Bacharelado em Engenharia de Software – UCB – Universidade Católica de Brasília, Brasília – DF, 2026.",
      font: "Times New Roman", size: 24, italics: true,
    })],
  }),
  pEmpty(),
  p("O futebol europeu movimenta bilhões de euros anualmente em transferências e contratações de atletas. A precificação de jogadores é uma atividade complexa, influenciada por variáveis quantitativas e qualitativas nem sempre mensuráveis objetivamente. O presente trabalho propõe uma análise exploratória de dados de jogadores de futebol das principais ligas europeias, com o objetivo de identificar os fatores que mais influenciam o valor de mercado de um atleta profissional."),
  pEmpty(),
  p("Para tanto, foi utilizado o dataset Player Scores v661, disponível publicamente na plataforma Kaggle, composto por seis arquivos CSV contendo informações sobre jogadores, partidas, aparições, clubes, competições e histórico de valores de mercado. O processamento dos dados foi realizado com as bibliotecas Pandas e NumPy, com etapas de limpeza, transformação de tipos, tratamento de valores nulos, remoção de duplicatas e criação de novas variáveis (engenharia de features). A visualização dos resultados foi implementada por meio de uma interface interativa desenvolvida com Streamlit e Matplotlib. Adicionalmente, foi construído um modelo preditivo de Gradient Boosting para estimativa do valor de mercado dos atletas."),
  pEmpty(),
  p("Os resultados indicam que a posição em campo, a idade e as métricas de eficiência ofensiva (gols e assistências por partida) são os fatores com maior poder preditivo sobre o valor de mercado. A interface Streamlit permite exploração interativa dos dados por meio de filtros e visualizações dinâmicas, tornando a análise acessível a públicos não especializados em ciência de dados."),
  pEmpty(),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 0 },
    children: [new TextRun({ text: "Palavras-chave: ", font: "Times New Roman", size: 24, bold: true }),
               new TextRun({ text: "análise de dados, Python, futebol europeu, valor de mercado, aprendizado de máquina.", font: "Times New Roman", size: 24 })],
  }),
  br(),
];

// ABSTRACT
const abstractSection = [
  label("ABSTRACT"),
  pEmpty(),
  p("European football moves billions of euros annually in player transfers and signings. Player valuation is a complex activity influenced by quantitative and qualitative variables that are not always objectively measurable. This paper proposes an exploratory data analysis of professional football players from the main European leagues, aiming to identify the factors that most influence a player's market value."),
  pEmpty(),
  p("The Player Scores v661 dataset, publicly available on Kaggle, was used, comprising six CSV files containing information on players, matches, appearances, clubs, competitions and market value history. Data processing was carried out using the Pandas and NumPy libraries, with steps of cleaning, type conversion, null value treatment, duplicate removal and creation of new variables (feature engineering). Results were visualized through an interactive interface built with Streamlit and Matplotlib. Additionally, a Gradient Boosting predictive model was built to estimate player market values."),
  pEmpty(),
  p("Findings indicate that field position, age, and offensive efficiency metrics (goals and assists per game) are the most predictive factors for market value. The Streamlit interface enables interactive data exploration through filters and dynamic visualizations, making the analysis accessible to non-specialized audiences."),
  pEmpty(),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 0 },
    children: [new TextRun({ text: "Keywords: ", font: "Times New Roman", size: 24, bold: true }),
               new TextRun({ text: "data analysis, Python, European football, market value, machine learning.", font: "Times New Roman", size: 24 })],
  }),
  br(),
];

// SUMÁRIO
const sumario = [
  label("SUMÁRIO"),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "RESUMO", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "ABSTRACT", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "1\tINTRODUÇÃO", font: "Times New Roman", size: 24, bold: true })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "1.1\tMOTIVAÇÃO", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "1.2\tDIAGNÓSTICO DO TEMA", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "2\tOBJETIVOS", font: "Times New Roman", size: 24, bold: true })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "2.1\tOBJETIVO GERAL", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "2.2\tOBJETIVOS ESPECÍFICOS", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "3\tDESENVOLVIMENTO", font: "Times New Roman", size: 24, bold: true })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "3.1\tDataset e Fonte dos Dados", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "3.2\tPreparação e Limpeza dos Dados", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "3.3\tEngenharia de Features", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "3.4\tAnálise Exploratória e Visualização", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "3.5\tModelo Preditivo de Valor de Mercado", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "3.6\tInterface Interativa com Streamlit", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "4\tCONCLUSÃO", font: "Times New Roman", size: 24, bold: true })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "4.1\tTRABALHOS FUTUROS", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "REFERÊNCIAS", font: "Times New Roman", size: 24, bold: true })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "GLOSSÁRIO", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "ANEXOS", font: "Times New Roman", size: 24, bold: true })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "ANEXO A – Dicionário de Dados do Dataset Player Scores", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "ANEXO B – Features Criadas por Engenharia de Dados", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "ANEXO C – Configuração do Modelo Preditivo", font: "Times New Roman", size: 24 })] }),
  new Paragraph({ spacing: { line: 240, after: 0 }, indent: { left: 709 }, children: [new TextRun({ text: "ANEXO D – Estrutura do Código-Fonte", font: "Times New Roman", size: 24 })] }),
  br(),
];

// INTRODUÇÃO
const introducao = [
  heading1("1", "INTRODUÇÃO"),
  pEmpty(),
  p("A utilização de tecnologias da informação e da computação como suporte à tomada de decisão tem se tornado cada vez mais relevante em diferentes setores da sociedade. No contexto esportivo, a análise de dados — também denominada sports analytics — emerge como uma ferramenta estratégica para clubes, agentes e federações que buscam embasar decisões operacionais e financeiras em evidências quantitativas, reduzindo a subjetividade historicamente associada a avaliações de desempenho e de mercado."),
  pEmpty(),
  p("No futebol europeu, o mercado de transferências de jogadores movimenta montantes bilionários a cada janela, e a avaliação do valor de mercado de um atleta é uma das atividades mais complexas e controversas do setor. Variáveis como posição em campo, faixa etária, volume de partidas disputadas, eficiência ofensiva e tempo de carreira influenciam diretamente essa precificação, mas raramente são analisadas de forma sistemática e integrada. A ausência de uma metodologia objetiva pode resultar em supervalorização ou subvalorização de atletas, gerando prejuízos financeiros e estratégicos aos clubes."),
  pEmpty(),
  p("O presente trabalho propõe uma análise exploratória de dados de jogadores das principais ligas de futebol europeu, utilizando o ecossistema Python de ciência de dados — especificamente as bibliotecas NumPy, Pandas, Matplotlib e Scikit-learn —, com o objetivo de identificar os fatores que mais influenciam o valor de mercado de um atleta profissional e construir um modelo preditivo capaz de estimar esse valor com base em atributos mensuráveis de carreira."),
  pEmpty(),
  p("O documento está estruturado da seguinte forma: a Seção 2 apresenta os objetivos geral e específicos do trabalho; a Seção 3 descreve o desenvolvimento, abrangendo a descrição do dataset, as etapas de preparação e limpeza dos dados, a engenharia de features, a análise exploratória com visualizações, o modelo preditivo e a interface interativa desenvolvida com Streamlit; a Seção 4 apresenta as conclusões e os trabalhos futuros; e, ao final, são listadas as referências bibliográficas utilizadas."),
  pEmpty(),
  heading2("1.1", "MOTIVAÇÃO"),
  pEmpty(),
  p("A motivação para a realização deste trabalho reside na crescente valorização da análise de dados no esporte profissional e na escassez de estudos que combinem, de forma integrada, dados de desempenho em campo com dados históricos de valor de mercado de jogadores. A disponibilidade pública de datasets detalhados sobre ligas europeias — como o Player Scores, disponibilizado na plataforma Kaggle — representa uma oportunidade de aplicar técnicas de ciência de dados a um domínio de grande interesse social e econômico."),
  pEmpty(),
  p("Adicionalmente, o trabalho serve como exercício prático de aplicação dos conceitos lecionados na disciplina de Análise de Dados e Solução de Problemas com Python, demonstrando o domínio das principais ferramentas do ecossistema Python para o ciclo completo de dados: da coleta à geração de insights e à construção de modelos preditivos."),
  pEmpty(),
  heading2("1.2", "DIAGNÓSTICO DO TEMA"),
  pEmpty(),
  p("O futebol europeu é o maior mercado esportivo do mundo, com receitas superiores a 30 bilhões de euros anuais segundo relatórios da UEFA. A avaliação de jogadores é realizada, na maioria dos clubes, por uma combinação de observação técnica, reputação de mercado e dados históricos fragmentados. Plataformas como o Transfermarkt consolidaram estimativas de valor de mercado com base em critérios editoriais colaborativos, mas sem a transparência metodológica necessária para análises científicas."),
  pEmpty(),
  p("O dataset Player Scores, utilizado neste trabalho, agrega dados de aparições em partidas, gols, assistências, minutos jogados, cartões, clubes e histórico de valores de mercado de milhares de jogadores das principais ligas europeias, cobrindo o período de 2008 a 2024. Essa abrangência temporal e geográfica torna o conjunto de dados adequado para uma análise longitudinal do mercado de futebol europeu."),
  br(),
];

// OBJETIVOS
const objetivos = [
  heading1("2", "OBJETIVOS"),
  pEmpty(),
  p("Esta seção apresenta os objetivos que nortearam o desenvolvimento do presente trabalho, divididos em objetivo geral e objetivos específicos."),
  pEmpty(),
  heading2("2.1", "OBJETIVO GERAL"),
  pEmpty(),
  p("Analisar os fatores que influenciam o valor de mercado de jogadores de futebol das principais ligas europeias, por meio de técnicas de análise exploratória de dados, visualização interativa e modelagem preditiva, utilizando o ecossistema Python de ciência de dados."),
  pEmpty(),
  heading2("2.2", "OBJETIVOS ESPECÍFICOS"),
  pEmpty(),
  p("Para alcançar o objetivo geral, foram definidos os seguintes objetivos específicos:"),
  pEmpty(),
  li("a", "Coletar e preparar o dataset Player Scores v661, realizando a limpeza e o tratamento dos dados com as bibliotecas Pandas e NumPy"),
  li("b", "Realizar a engenharia de features, criando variáveis derivadas que enriqueçam a análise, tais como métricas de eficiência por partida, faixas etárias e score de performance ponderado"),
  li("c", "Desenvolver análise exploratória dos dados com visualizações claras e informativas por meio da biblioteca Matplotlib"),
  li("d", "Construir uma interface interativa com Streamlit que permita a exploração dinâmica dos dados e dos resultados"),
  li("e", "Treinar e avaliar um modelo preditivo de Gradient Boosting para estimativa do valor de mercado dos jogadores"),
  li("f", "Identificar as variáveis com maior poder explicativo sobre o valor de mercado dos atletas"),
  br(),
];

// DESENVOLVIMENTO
const desenvolvimento = [
  heading1("3", "DESENVOLVIMENTO"),
  pEmpty(),
  p("Esta seção descreve o processo de desenvolvimento do trabalho, desde a obtenção dos dados até a construção da interface de visualização e do modelo preditivo. Cada subseção corresponde a uma etapa do ciclo de ciência de dados aplicado ao problema proposto."),
  pEmpty(),

  heading2("3.1", "Dataset e Fonte dos Dados"),
  pEmpty(),
  p("O dataset utilizado neste trabalho é o Player Scores, versão 661, disponível publicamente na plataforma Kaggle sob o perfil do usuário davidcariboo. O conjunto de dados é composto por seis arquivos no formato CSV (Comma-Separated Values), descritos a seguir:"),
  pEmpty(),
  li("a", "players.csv: contém informações cadastrais dos jogadores, como nome, data de nascimento, posição, cidadania e valor de mercado atual e histórico máximo"),
  li("b", "appearances.csv: registra as aparições de cada jogador em partidas, com estatísticas individuais de gols, assistências, minutos jogados e cartões recebidos"),
  li("c", "player_valuations.csv: armazena o histórico temporal de valores de mercado de cada jogador"),
  li("d", "games.csv: contém informações sobre as partidas, incluindo data, placar e identificadores dos clubes"),
  li("e", "clubs.csv: descreve os clubes participantes das ligas analisadas"),
  li("f", "competitions.csv: lista as competições cobertas pelo dataset, com países e divisões"),
  pEmpty(),
  p("Os dados abrangem o período de 2008 a 2024 e cobrem as principais ligas europeias, incluindo Premier League (Inglaterra), Bundesliga (Alemanha), La Liga (Espanha), Serie A (Itália) e Ligue 1 (França), além de ligas de segunda divisão e competições continentais."),
  pEmpty(),

  heading2("3.2", "Preparação e Limpeza dos Dados"),
  pEmpty(),
  p("O processamento dos dados foi implementado no módulo data_processor.py, utilizando as bibliotecas Pandas e NumPy. As seguintes etapas de limpeza foram realizadas:"),
  pEmpty(),
  li("a", "Conversão de tipos: colunas de data foram convertidas com pd.to_datetime(errors='coerce') e valores numéricos com pd.to_numeric(errors='coerce'), descartando automaticamente entradas inválidas"),
  li("b", "Remoção de duplicatas: registros duplicados foram eliminados com base nas chaves primárias player_id e appearance_id"),
  li("c", "Tratamento de valores nulos: estatísticas de partida foram preenchidas com zero via fillna(0); linhas sem posição ou data foram removidas com dropna()"),
  li("d", "Filtro de consistência: jogadores com idade fora do intervalo de 15 a 50 anos foram excluídos da análise"),
  li("e", "Padronização de nomenclaturas: países com nomes duplicados no dataset (como Türkiye e Turkey) foram unificados por meio de mapeamento com replace()"),
  pEmpty(),
  p("Ao final do processo de limpeza, o DataFrame principal (master) integrou informações de jogadores, estatísticas agregadas de carreira e valores de mercado mais recentes por meio de operações de merge do Pandas."),
  pEmpty(),

  heading2("3.3", "Engenharia de Features"),
  pEmpty(),
  p("A engenharia de features consistiu na criação de novas variáveis derivadas dos dados brutos, com o objetivo de enriquecer a análise e melhorar o desempenho do modelo preditivo. As principais features criadas foram:"),
  pEmpty(),
  li("a", "age: idade do jogador, calculada em anos com precisão decimal, utilizando a diferença em dias entre a data de nascimento e a data de referência (01/01/2025), dividida por 365,25 com NumPy (np.floor)"),
  li("b", "age_group: faixa etária categorizada com pd.cut() em cinco intervalos: Sub-21, 21-24, 25-28, 29-32 e 33+"),
  li("c", "goal_contributions: soma de gols e assistências por aparição, calculada diretamente com operações vetorizadas do Pandas"),
  li("d", "goals_per_game e assists_per_game: métricas de eficiência ofensiva por partida, calculadas pela divisão dos totais pelo número de aparições"),
  li("e", "red_cards_per_game: taxa de cartões vermelhos por partida, substituindo o total acumulado para eliminar viés de volume de jogos"),
  li("f", "performance_score: score ponderado de performance, calculado como (gols × 2 + assistências) / número de partidas, utilizando np.maximum() para evitar divisão por zero"),
  li("g", "performance_tier: classificação por quartil com pd.qcut() em quatro categorias: Bronze, Prata, Ouro e Elite"),
  li("h", "log_latest_value: transformação logarítmica do valor de mercado com np.log1p(), utilizada como variável alvo no modelo preditivo para normalizar a distribuição assimétrica dos valores"),
  li("i", "value_tier: categorização do valor de mercado em faixas com pd.cut(): abaixo de 1 milhão, entre 1 e 10 milhões, entre 10 e 50 milhões, e acima de 50 milhões de euros"),
  pEmpty(),
  p("Adicionalmente, foi calculada uma matriz de correlação entre as principais variáveis numéricas utilizando o método corr() do Pandas, permitindo identificar relações lineares entre atributos de carreira e valor de mercado."),
  pEmpty(),

  heading2("3.4", "Análise Exploratória e Visualização"),
  pEmpty(),
  p("A análise exploratória foi organizada em cinco eixos principais, cada um implementado como uma aba na interface Streamlit e ilustrado por gráficos gerados com Matplotlib:"),
  pEmpty(),
  li("a", "Distribuição do Valor de Mercado: gráfico de barras empilhadas exibindo a proporção de jogadores em cada faixa de valor por posição; gráfico de barras horizontais com o valor mediano por posição; histograma do log do valor de mercado; e dispersão de idade versus valor de mercado"),
  li("b", "Performance por Posição: conjunto de seis gráficos de barras comparando médias de gols por jogo, assistências por jogo, minutos por jogo, cartões amarelos, cartões vermelhos e temporadas ativas entre as posições; e heatmap da matriz de correlação entre variáveis numéricas"),
  li("c", "Evolução Temporal: gráficos de área e linha mostrando a evolução de gols e assistências totais por temporada (2008–2024); evolução do valor de mercado mediano por ano; e média de gols por aparição ao longo das temporadas"),
  li("d", "Top Jogadores: ranking interativo configurável por métrica (gols totais, assistências, contribuições, gols por jogo ou valor de mercado); e gráfico de barras com a distribuição de jogadores por nacionalidade (Top 20)"),
  li("e", "Modelo Preditivo: gráfico de dispersão entre valores reais e preditos; gráfico de importância das features; e simulador interativo de valor de mercado"),
  pEmpty(),
  p("Todos os gráficos foram formatados com títulos descritivos, rótulos nos eixos, legendas e paleta de cores consistente por posição (vermelho para atacantes, azul para meio-campistas, verde para defensores e laranja para goleiros)."),
  pEmpty(),

  heading2("3.5", "Modelo Preditivo de Valor de Mercado"),
  pEmpty(),
  p("O modelo preditivo foi implementado no módulo modelo.py, utilizando o algoritmo Histogram Gradient Boosting Regressor da biblioteca Scikit-learn. Esse algoritmo foi escolhido por sua eficiência computacional em datasets de grande volume e por sua capacidade de lidar nativamente com valores ausentes nas features."),
  pEmpty(),
  p("As features utilizadas no treinamento foram: idade, total de aparições, total de gols, total de assistências, total de minutos, total de cartões amarelos, taxa de cartões vermelhos por jogo, gols por jogo, assistências por jogo, temporadas ativas e posição (variável categórica codificada com OneHotEncoder). A variável alvo foi o logaritmo natural do valor de mercado mais recente (log_latest_value)."),
  pEmpty(),
  p("O dataset foi dividido em 80% para treino e 20% para teste, de forma aleatória com semente fixada (random_state=42) para reprodutibilidade. O pipeline de pré-processamento incluiu imputação de valores ausentes com SimpleImputer e codificação das variáveis categóricas com OneHotEncoder. O modelo foi avaliado pelo coeficiente de determinação R² no conjunto de teste e pelo erro absoluto médio (MAE) na escala original de euros."),
  pEmpty(),
  p("A substituição do total de cartões vermelhos pela taxa por partida (red_cards_per_game) foi uma decisão metodológica relevante: o total acumulado criava uma correlação espúria com o valor de mercado — jogadores mais valiosos, por disputarem mais partidas, acumulavam mais cartões, o que levava o modelo a interpresar incorretamente os cartões como fator de valorização. A taxa por partida elimina esse viés ao normalizar pelo volume de jogos."),
  pEmpty(),

  heading2("3.6", "Interface Interativa com Streamlit"),
  pEmpty(),
  p("A interface de visualização foi desenvolvida com a biblioteca Streamlit, no arquivo app.py. A aplicação é estruturada com uma barra lateral de filtros globais e cinco abas de análise, conforme descrito na Seção 3.4."),
  pEmpty(),
  p("A barra lateral exibe a cobertura temporal do dataset (datas de início e fim das partidas e dos registros de valor de mercado), além de filtros por temporada, posição, faixa etária e número mínimo de partidas disputadas. Os gráficos e métricas da interface se atualizam automaticamente em resposta à alteração dos filtros, proporcionando uma experiência de análise interativa."),
  pEmpty(),
  p("O carregamento dos dados e o treinamento do modelo são armazenados em cache com o decorador @st.cache_data do Streamlit, evitando reprocessamento a cada interação do usuário e garantindo desempenho adequado mesmo em datasets de grande volume."),
  br(),
];

// CONCLUSÃO
const conclusao = [
  heading1("4", "CONCLUSÃO"),
  pEmpty(),
  p("O presente trabalho demonstrou que é possível extrair insights relevantes e construir modelos preditivos confiáveis sobre o valor de mercado de jogadores de futebol europeu a partir de dados públicos, utilizando o ecossistema Python de ciência de dados de forma integrada."),
  pEmpty(),
  p("O objetivo geral foi plenamente atendido: a análise identificou que posição em campo, idade, gols por partida e assistências por partida são os atributos com maior poder preditivo sobre o valor de mercado de um atleta. Os objetivos específicos também foram alcançados: o dataset foi preparado e limpo com Pandas e NumPy; foram criadas nove novas features; foram geradas visualizações claras e informativas com Matplotlib; foi construída uma interface interativa com Streamlit; e o modelo de Gradient Boosting apresentou desempenho satisfatório (R² entre 0,70 e 0,80 no conjunto de teste)."),
  pEmpty(),
  p("Entre as principais descobertas, destacam-se: a distribuição fortemente assimétrica dos valores de mercado, com a maioria dos jogadores avaliados em menos de 1 milhão de euros e poucos superastros concentrando valores superiores a 50 milhões; o pico de valor de mercado entre os 22 e 27 anos de idade; o Brasil como a nacionalidade mais representada no dataset; e o crescimento consistente dos valores de mercado medianos ao longo da última década, reflexo da inflação no mercado futebolístico europeu."),
  pEmpty(),
  p("As principais limitações identificadas são: o modelo não captura fatores subjetivos como forma recente, lesões, prestígio do clube ou popularidade midiática; os dados históricos podem não refletir as dinâmicas mais recentes do mercado; e a variância elevada dos valores na escala original resulta em erros absolutos medianos significativos, mesmo com bom desempenho em escala logarítmica."),
  pEmpty(),
  heading2("4.1", "TRABALHOS FUTUROS"),
  pEmpty(),
  p("Como extensões naturais deste trabalho, sugere-se:"),
  pEmpty(),
  li("a", "Incorporar dados de redes sociais (seguidores, engajamento) e métricas físicas (velocidade, aceleração) para ampliar o poder preditivo do modelo"),
  li("b", "Aplicar modelos de séries temporais (como LSTM ou Prophet) para prever a trajetória futura do valor de mercado de jogadores individuais"),
  li("c", "Desenvolver um sistema de recomendação de jogadores para clubes, considerando critérios de custo-benefício e perfil tático"),
  li("d", "Expandir a análise para ligas da América do Sul e da Ásia, verificando padrões globais de valorização de atletas"),
  li("e", "Implementar o deploy da aplicação Streamlit em plataforma de nuvem pública, tornando-a acessível sem necessidade de instalação local"),
  br(),
];

// REFERÊNCIAS
const referencias = [
  label("REFERÊNCIAS"),
  pEmpty(),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 240 },
    children: [new TextRun({ text: "CARIBOO, David. Player Scores. Kaggle, 2024. Dataset version 661. Disponível em: https://www.kaggle.com/datasets/davidcariboo/player-scores/versions/661. Acesso em: jun. 2026.", font: "Times New Roman", size: 24 })],
  }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 240 },
    children: [new TextRun({ text: "GÉRON, Aurélien. Mãos à Obra: Aprendizado de Máquina com Scikit-Learn, Keras & TensorFlow. 2. ed. Rio de Janeiro: Alta Books, 2021.", font: "Times New Roman", size: 24 })],
  }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 240 },
    children: [new TextRun({ text: "MCKINNEY, Wes. Python para Análise de Dados: Tratamento de Dados com Pandas, NumPy e IPython. 2. ed. São Paulo: Novatec, 2019.", font: "Times New Roman", size: 24 })],
  }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 240 },
    children: [new TextRun({ text: "PEDREGOSA, F. et al. Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, v. 12, p. 2825-2830, 2011.", font: "Times New Roman", size: 24 })],
  }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 240 },
    children: [new TextRun({ text: "STREAMLIT INC. Streamlit Documentation. Disponível em: https://docs.streamlit.io. Acesso em: jun. 2026.", font: "Times New Roman", size: 24 })],
  }),
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 240, after: 240 },
    children: [new TextRun({ text: "UEFA. The European Club Footballing Landscape: Club Licensing Benchmarking Report. Nyon: UEFA, 2023.", font: "Times New Roman", size: 24 })],
  }),
  br(),
];

// GLOSSÁRIO
const glossario = [
  label("GLOSSÁRIO"),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "CSV (Comma-Separated Values):", font: "Times New Roman", size: 24, bold: true }), new TextRun({ text: " formato de arquivo de texto simples para armazenamento de dados tabulares, em que os valores são separados por vírgulas.", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "DataFrame:", font: "Times New Roman", size: 24, bold: true }), new TextRun({ text: " estrutura de dados bidimensional da biblioteca Pandas, similar a uma planilha, com linhas e colunas nomeadas.", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "Feature Engineering (Engenharia de Features):", font: "Times New Roman", size: 24, bold: true }), new TextRun({ text: " processo de criação e transformação de variáveis a partir dos dados brutos para melhorar o desempenho de modelos de aprendizado de máquina.", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "Gradient Boosting:", font: "Times New Roman", size: 24, bold: true }), new TextRun({ text: " algoritmo de aprendizado de máquina do tipo conjunto (ensemble), que combina múltiplas árvores de decisão para produzir previsões mais precisas.", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "IQR (Intervalo Interquartil):", font: "Times New Roman", size: 24, bold: true }), new TextRun({ text: " medida estatística de dispersão calculada como a diferença entre o terceiro quartil (Q3) e o primeiro quartil (Q1), utilizada para detectar outliers.", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "MAE (Mean Absolute Error — Erro Absoluto Médio):", font: "Times New Roman", size: 24, bold: true }), new TextRun({ text: " métrica de avaliação de modelos de regressão que calcula a média das diferenças absolutas entre os valores reais e os valores preditos.", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "R² (Coeficiente de Determinação):", font: "Times New Roman", size: 24, bold: true }), new TextRun({ text: " métrica que indica a proporção da variância da variável alvo explicada pelo modelo preditivo; varia de 0 a 1, sendo 1 o ajuste perfeito.", font: "Times New Roman", size: 24 })] }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, children: [new TextRun({ text: "Streamlit:", font: "Times New Roman", size: 24, bold: true }), new TextRun({ text: " biblioteca Python de código aberto para criação de aplicações web interativas voltadas para análise e visualização de dados.", font: "Times New Roman", size: 24 })] }),
];

// ── Helpers de tabela ────────────────────────────────────
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const cell = (text, bold = false, shade = null, w = 4535) =>
  new TableCell({
    borders,
    width: { size: w, type: WidthType.DXA },
    shading: shade ? { fill: shade, type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [new Paragraph({
      spacing: { line: 240, after: 0 },
      children: [new TextRun({ text, font: "Times New Roman", size: 20, bold })],
    })],
  });

const tableRow = (cols, header = false) =>
  new TableRow({ children: cols.map((c, i) => cell(c, header, header ? "D6E4F0" : null, [2000, 2500, 4571][i] || 3000)) });

// ── ANEXOS ───────────────────────────────────────────────
const anexos = [
  label("ANEXOS"),
  pEmpty(),
  p("Os anexos a seguir apresentam informações complementares que auxiliam na compreensão do dataset utilizado, das variáveis analisadas, dos resultados estatísticos e da configuração do modelo preditivo desenvolvido neste trabalho."),
  br(),

  // ANEXO A
  new Paragraph({
    spacing: { line: 240, before: 0, after: 120 },
    children: [new TextRun({ text: "ANEXO A – DICIONÁRIO DE DADOS DO DATASET PLAYER SCORES", font: "Times New Roman", size: 24, bold: true })],
  }),
  pEmpty(),
  p("O Quadro A.1 apresenta a descrição de todas as colunas relevantes dos seis arquivos CSV que compõem o dataset Player Scores v661, utilizado neste trabalho."),
  pEmpty(),
  pCenter("Quadro A.1 – Dicionário de dados do dataset Player Scores v661", false, 22),
  pEmpty(),

  // Tabela players.csv
  new Paragraph({ spacing: { line: 240, after: 60 }, children: [new TextRun({ text: "players.csv", font: "Times New Roman", size: 22, bold: true, italics: true })] }),
  new Table({
    width: { size: 9071, type: WidthType.DXA },
    columnWidths: [2000, 2500, 4571],
    rows: [
      tableRow(["Coluna", "Tipo", "Descrição"], true),
      tableRow(["player_id", "Inteiro", "Identificador único do jogador"]),
      tableRow(["name", "Texto", "Nome completo do jogador"]),
      tableRow(["date_of_birth", "Data", "Data de nascimento"]),
      tableRow(["position", "Texto", "Posição em campo (Attack, Midfield, Defender, Goalkeeper)"]),
      tableRow(["country_of_citizenship", "Texto", "Nacionalidade (cidadania) do jogador"]),
      tableRow(["country_of_birth", "Texto", "País de nascimento"]),
      tableRow(["market_value_in_eur", "Decimal", "Valor de mercado atual em euros"]),
      tableRow(["highest_market_value_in_eur", "Decimal", "Valor de mercado histórico máximo em euros"]),
      tableRow(["last_season", "Inteiro", "Última temporada registrada no dataset"]),
    ],
  }),
  pEmpty(),

  // Tabela appearances.csv
  new Paragraph({ spacing: { line: 240, after: 60 }, children: [new TextRun({ text: "appearances.csv", font: "Times New Roman", size: 22, bold: true, italics: true })] }),
  new Table({
    width: { size: 9071, type: WidthType.DXA },
    columnWidths: [2000, 2500, 4571],
    rows: [
      tableRow(["Coluna", "Tipo", "Descrição"], true),
      tableRow(["appearance_id", "Texto", "Identificador único da aparição"]),
      tableRow(["player_id", "Inteiro", "Referência ao jogador (chave estrangeira)"]),
      tableRow(["game_id", "Inteiro", "Referência à partida"]),
      tableRow(["date", "Data", "Data da partida"]),
      tableRow(["goals", "Inteiro", "Gols marcados na partida"]),
      tableRow(["assists", "Inteiro", "Assistências realizadas na partida"]),
      tableRow(["minutes_played", "Inteiro", "Minutos em campo"]),
      tableRow(["yellow_cards", "Inteiro", "Cartões amarelos recebidos"]),
      tableRow(["red_cards", "Inteiro", "Cartões vermelhos recebidos"]),
    ],
  }),
  pEmpty(),

  // Tabela player_valuations.csv
  new Paragraph({ spacing: { line: 240, after: 60 }, children: [new TextRun({ text: "player_valuations.csv", font: "Times New Roman", size: 22, bold: true, italics: true })] }),
  new Table({
    width: { size: 9071, type: WidthType.DXA },
    columnWidths: [2000, 2500, 4571],
    rows: [
      tableRow(["Coluna", "Tipo", "Descrição"], true),
      tableRow(["player_id", "Inteiro", "Referência ao jogador"]),
      tableRow(["date", "Data", "Data do registro do valor"]),
      tableRow(["market_value_in_eur", "Decimal", "Valor de mercado registrado naquela data em euros"]),
    ],
  }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Fonte: Kaggle — Player Scores v661 (davidcariboo, 2024).", font: "Times New Roman", size: 20, italics: true })] }),
  br(),

  // ANEXO B
  new Paragraph({
    spacing: { line: 240, before: 0, after: 120 },
    children: [new TextRun({ text: "ANEXO B – FEATURES CRIADAS POR ENGENHARIA DE DADOS", font: "Times New Roman", size: 24, bold: true })],
  }),
  pEmpty(),
  p("O Quadro B.1 apresenta todas as variáveis derivadas criadas durante a etapa de engenharia de features, com a fórmula de cálculo, a biblioteca utilizada e a finalidade de cada uma."),
  pEmpty(),
  pCenter("Quadro B.1 – Features criadas por engenharia de dados", false, 22),
  pEmpty(),
  new Table({
    width: { size: 9071, type: WidthType.DXA },
    columnWidths: [2200, 2200, 1671, 3000],
    rows: [
      new TableRow({ children: [
        cell("Feature", true, "D6E4F0", 2200),
        cell("Fórmula / Método", true, "D6E4F0", 2200),
        cell("Biblioteca", true, "D6E4F0", 1671),
        cell("Finalidade", true, "D6E4F0", 3000),
      ]}),
      new TableRow({ children: [cell("age", false, null, 2200), cell("(data_ref - date_of_birth).days / 365.25", false, null, 2200), cell("Pandas / NumPy", false, null, 1671), cell("Idade atual do jogador", false, null, 3000)] }),
      new TableRow({ children: [cell("age_group", false, null, 2200), cell("pd.cut() em 5 faixas", false, null, 2200), cell("Pandas", false, null, 1671), cell("Categoria etária (Sub-21 a 33+)", false, null, 3000)] }),
      new TableRow({ children: [cell("position_group", false, null, 2200), cell("map() com dicionário", false, null, 2200), cell("Pandas", false, null, 1671), cell("Agrupamento em 4 posições", false, null, 3000)] }),
      new TableRow({ children: [cell("goal_contributions", false, null, 2200), cell("goals + assists", false, null, 2200), cell("Pandas", false, null, 1671), cell("Total de participações em gols", false, null, 3000)] }),
      new TableRow({ children: [cell("goals_per_game", false, null, 2200), cell("total_goals / total_appearances", false, null, 2200), cell("Pandas", false, null, 1671), cell("Eficiência ofensiva por partida", false, null, 3000)] }),
      new TableRow({ children: [cell("assists_per_game", false, null, 2200), cell("total_assists / total_appearances", false, null, 2200), cell("Pandas", false, null, 1671), cell("Eficiência criativa por partida", false, null, 3000)] }),
      new TableRow({ children: [cell("red_cards_per_game", false, null, 2200), cell("total_red / total_appearances", false, null, 2200), cell("Pandas", false, null, 1671), cell("Taxa de cartões vermelhos (sem viés de volume)", false, null, 3000)] }),
      new TableRow({ children: [cell("performance_score", false, null, 2200), cell("(gols×2 + assists) / np.maximum(apps,1)", false, null, 2200), cell("NumPy", false, null, 1671), cell("Score ponderado de desempenho ofensivo", false, null, 3000)] }),
      new TableRow({ children: [cell("performance_tier", false, null, 2200), cell("pd.qcut() em 4 quartis", false, null, 2200), cell("Pandas", false, null, 1671), cell("Nível de desempenho (Bronze a Elite)", false, null, 3000)] }),
      new TableRow({ children: [cell("log_latest_value", false, null, 2200), cell("np.log1p(latest_market_value)", false, null, 2200), cell("NumPy", false, null, 1671), cell("Variável alvo normalizada para o modelo", false, null, 3000)] }),
      new TableRow({ children: [cell("value_tier", false, null, 2200), cell("pd.cut() em 4 faixas de valor", false, null, 2200), cell("Pandas", false, null, 1671), cell("Classificação por faixa de mercado", false, null, 3000)] }),
      new TableRow({ children: [cell("value_to_peak_ratio", false, null, 2200), cell("market_value / highest_market_value", false, null, 2200), cell("NumPy", false, null, 1671), cell("Proporção entre valor atual e pico histórico", false, null, 3000)] }),
    ],
  }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Fonte: elaboração própria, 2026.", font: "Times New Roman", size: 20, italics: true })] }),
  br(),

  // ANEXO C
  new Paragraph({
    spacing: { line: 240, before: 0, after: 120 },
    children: [new TextRun({ text: "ANEXO C – CONFIGURAÇÃO DO MODELO PREDITIVO", font: "Times New Roman", size: 24, bold: true })],
  }),
  pEmpty(),
  p("O Quadro C.1 descreve os hiperparâmetros utilizados no modelo Histogram Gradient Boosting Regressor e o pipeline de pré-processamento configurado com a biblioteca Scikit-learn."),
  pEmpty(),
  pCenter("Quadro C.1 – Hiperparâmetros do modelo preditivo", false, 22),
  pEmpty(),
  new Table({
    width: { size: 9071, type: WidthType.DXA },
    columnWidths: [2800, 2000, 4271],
    rows: [
      new TableRow({ children: [cell("Parâmetro", true, "D6E4F0", 2800), cell("Valor", true, "D6E4F0", 2000), cell("Justificativa", true, "D6E4F0", 4271)] }),
      new TableRow({ children: [cell("Algoritmo", false, null, 2800), cell("HistGradientBoostingRegressor", false, null, 2000), cell("Eficiência computacional superior ao GBR clássico em grandes volumes", false, null, 4271)] }),
      new TableRow({ children: [cell("max_iter", false, null, 2800), cell("100", false, null, 2000), cell("Equilibra qualidade e tempo de treino (< 10 segundos)", false, null, 4271)] }),
      new TableRow({ children: [cell("max_depth", false, null, 2800), cell("4", false, null, 2000), cell("Controla a complexidade das árvores e evita overfitting", false, null, 4271)] }),
      new TableRow({ children: [cell("learning_rate", false, null, 2800), cell("0,10", false, null, 2000), cell("Taxa de aprendizado moderada para convergência estável", false, null, 4271)] }),
      new TableRow({ children: [cell("random_state", false, null, 2800), cell("42", false, null, 2000), cell("Semente fixa para reprodutibilidade dos resultados", false, null, 4271)] }),
      new TableRow({ children: [cell("Variável alvo", false, null, 2800), cell("log_latest_value", false, null, 2000), cell("Log do valor de mercado para normalizar distribuição assimétrica", false, null, 4271)] }),
      new TableRow({ children: [cell("Divisão treino/teste", false, null, 2800), cell("80% / 20%", false, null, 2000), cell("Holdout aleatório com random_state=42", false, null, 4271)] }),
      new TableRow({ children: [cell("Imputação de nulos", false, null, 2800), cell("SimpleImputer (mediana)", false, null, 2000), cell("Preserva a distribuição central sem distorções por outliers", false, null, 4271)] }),
      new TableRow({ children: [cell("Encoder categórico", false, null, 2800), cell("OneHotEncoder", false, null, 2000), cell("Converte posição em variáveis binárias para o modelo", false, null, 4271)] }),
    ],
  }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Fonte: elaboração própria, 2026.", font: "Times New Roman", size: 20, italics: true })] }),
  br(),

  // ANEXO D
  new Paragraph({
    spacing: { line: 240, before: 0, after: 120 },
    children: [new TextRun({ text: "ANEXO D – ESTRUTURA DO CÓDIGO-FONTE", font: "Times New Roman", size: 24, bold: true })],
  }),
  pEmpty(),
  p("O Quadro D.1 apresenta a estrutura de arquivos do projeto, com a descrição da responsabilidade de cada módulo."),
  pEmpty(),
  pCenter("Quadro D.1 – Estrutura do código-fonte do projeto", false, 22),
  pEmpty(),
  new Table({
    width: { size: 9071, type: WidthType.DXA },
    columnWidths: [2800, 6271],
    rows: [
      new TableRow({ children: [cell("Arquivo", true, "D6E4F0", 2800), cell("Responsabilidade", true, "D6E4F0", 6271)] }),
      new TableRow({ children: [cell("app.py", false, null, 2800), cell("Interface principal Streamlit: sidebar, KPIs, cinco abas de análise e simulador de valor de mercado", false, null, 6271)] }),
      new TableRow({ children: [cell("data_processor.py", false, null, 2800), cell("Carregamento dos CSVs, limpeza, engenharia de features, construção do DataFrame mestre e matriz de correlação", false, null, 6271)] }),
      new TableRow({ children: [cell("modelo.py", false, null, 2800), cell("Pipeline de pré-processamento, treinamento do HistGradientBoostingRegressor e retorno de métricas e importâncias", false, null, 6271)] }),
      new TableRow({ children: [cell("gerar_relatorio.py", false, null, 2800), cell("Geração do relatório auxiliar em PDF com a biblioteca ReportLab", false, null, 6271)] }),
      new TableRow({ children: [cell("gerar_relatorio_abnt.js", false, null, 2800), cell("Geração do relatório completo em formato ABNT (.docx) com a biblioteca docx para Node.js", false, null, 6271)] }),
      new TableRow({ children: [cell("requirements.txt", false, null, 2800), cell("Dependências Python do projeto (Streamlit, Pandas, NumPy, Matplotlib, Scikit-learn)", false, null, 6271)] }),
      new TableRow({ children: [cell("data/", false, null, 2800), cell("Pasta destinada aos seis arquivos CSV do dataset Player Scores v661 (não versionados no repositório)", false, null, 6271)] }),
    ],
  }),
  pEmpty(),
  new Paragraph({ spacing: { line: 240, after: 0 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Fonte: elaboração própria, 2026.", font: "Times New Roman", size: 20, italics: true })] }),
  pEmpty(),
  p("O repositório do projeto está disponível publicamente em: https://github.com/isalopeesz/football-analytics."),
];

// ── Monta o documento ────────────────────────────────────
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Times New Roman", size: 24 },
        paragraph: { spacing: { line: 240 } },
      },
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
        run: { size: 24, bold: true, font: "Times New Roman", color: "000000" },
        paragraph: { spacing: { before: 240, after: 120, line: 240 }, outlineLevel: 0 },
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
        run: { size: 24, bold: true, font: "Times New Roman", color: "000000" },
        paragraph: { spacing: { before: 120, after: 60, line: 240 }, outlineLevel: 1 },
      },
      {
        id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal",
        run: { size: 24, bold: true, italics: true, font: "Times New Roman", color: "000000" },
        paragraph: { spacing: { before: 120, after: 60, line: 240 }, outlineLevel: 2 },
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: MARGIN,
      },
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [new TextRun({ children: [PageNumber.CURRENT], font: "Times New Roman", size: 22 })],
        })],
      }),
    },
    children: [
      ...capa,
      ...folhaRosto,
      ...resumo,
      ...abstractSection,
      ...sumario,
      ...introducao,
      ...objetivos,
      ...desenvolvimento,
      ...conclusao,
      ...referencias,
      ...glossario,
      ...anexos,
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("Relatorio_ABNT_Football_Analytics_v2.docx", buffer);
  console.log("Documento gerado com sucesso!");
});
