# Model Card — Predição de Churn (Telco)

## Visão geral

- **Tarefa:** classificação binária — prever se um cliente vai cancelar o
  serviço (`churn_value = 1`) ou não (`0`).
- **Domínio:** clientes de uma operadora de telecomunicações (dataset
  `data/Telco_customer_churn.xlsx`, 7.043 clientes).
- **Algoritmo campeão:** `RandomForestClassifier` (scikit-learn), dentro de
  um `Pipeline` com `ColumnTransformer` (`StandardScaler` nas features
  numéricas) + classificador.
- **Hiperparâmetros:** `n_estimators=300`, `max_depth=12`,
  `class_weight="balanced"`, `random_state=42`.
- **Artefato treinado:** `models/champion_model.joblib`.
- **Notebook de origem:** `notebooks/model_comparison.ipynb`.
- **Seed fixada:** `RANDOM_STATE = 42` em todo o pipeline de treino/split,
  para reprodutibilidade.

## Dados de treino

- **Split:** 80% treino / 20% teste, estratificado por `churn_value`.
- **Validação cruzada:** `StratifiedKFold` com 5 folds.
- **Features de entrada (20):** dados demográficos (`gender`,
  `senior_citizen`, `partner`, `dependents`), de uso (`tenure_months`,
  `phone_service`, `multiple_lines`, `internet_service` e serviços
  dependentes de internet), contratuais (`contract`, `paperless_billing`,
  `payment_method`) e financeiras (`monthly_charges`, `total_charges`,
  `cltv`).
- **Pré-processamento:** categorias redundantes colapsadas
  (`"No phone service"` → `"No"`, `"No internet service"` → `"No"`),
  one-hot encoding (`drop_first=True`) e padronização (`StandardScaler`)
  das 4 variáveis numéricas. Ver `src/preprocessing.py`.

## Comparação de modelos (conjunto de teste, `models/model_comparison.csv`)

| Modelo | Accuracy | Precisão | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Regressão Logística | 0.8034 | 0.6456 | 0.5749 | 0.6082 | 0.8490 |
| **Random Forest (campeão)** | 0.7722 | 0.5521 | **0.7513** | **0.6365** | 0.8499 |
| MLP (rede neural) | 0.8013 | 0.6320 | 0.6016 | 0.6164 | 0.8505 |

O Random Forest foi escolhido como campeão por ter o maior **F1** no
conjunto de teste, priorizando o equilíbrio entre encontrar clientes que
de fato vão cancelar (recall) e evitar alarmes falsos (precisão). Os três
modelos têm ROC-AUC muito próximo (~0.85), indicando capacidade de
discriminação semelhante entre eles; a escolha do campeão foi decidida
pela métrica de negócio definida (F1).

## Limitações e vieses conhecidos

- **Precisão moderada (0.55):** de cada 10 clientes sinalizados como
  "vai cancelar", cerca de 4 a 5 não cancelariam de fato (falso
  positivo). O modelo foi otimizado para recall (via `class_weight`
  `balanced`), o que é uma escolha de negócio adequada para campanhas de
  retenção (custo de contatar um cliente que não ia sair é menor que
  perder um que ia), mas deve ser considerado ao dimensionar ações
  comerciais baseadas na predição.
- **Dataset estático e de um único período/operadora:** o modelo foi
  treinado com um snapshot histórico de uma base específica. Mudanças de
  mercado, novos planos/produtos ou sazonalidade não são capturadas, e o
  modelo deve ser re-treinado periodicamente.
- **Sem colunas sensíveis explícitas**, mas `gender` e `senior_citizen`
  entram como features; não foi feita uma análise de fairness/viés
  demográfico entre esses grupos, o que é uma limitação a ser endereçada
  antes de qualquer uso que impacte diretamente o cliente (ex.: preço,
  elegibilidade).
- **Ausência de dados temporais/comportamentais recentes** (ex.: tickets
  de suporte, uso de app, NPS) — o modelo enxerga apenas o retrato do
  cliente no momento do snapshot, o que limita a captura de sinais de
  insatisfação recentes.
- **`total_charges` com valores ausentes na fonte original** (11 registros
  com string vazia) foram imputados pela mediana durante o treino; a API
  de inferência não faz essa imputação — espera o valor numérico já
  preenchido pelo chamador.
- **Escopo de validação:** apenas métricas agregadas (accuracy, precisão,
  recall, F1, ROC-AUC) foram avaliadas; não houve análise por segmento
  (ex.: por tipo de contrato ou tempo de casa), o que poderia revelar
  desempenho desigual entre subgrupos de clientes.

## Uso recomendado

- Priorização de clientes para campanhas de retenção proativa.
- Apoio à decisão humana — **não** deve ser usado como critério automático
  único para ações que afetem o cliente (ex.: cancelamento de benefícios).
- Recomenda-se monitorar a distribuição das predições em produção (ver
  métricas Prometheus expostas em `/metrics`) e re-treinar o modelo
  periodicamente à medida que novos dados de churn real forem coletados.
