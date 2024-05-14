# Datasets de Teste Cego da Tarefa 2 - 2024 
Nesta pasta, os seguintes arquivos estão disponíveis:
- 'env_vital_signals.txt': utilizado pelo simulador
- 'input.txt': arquivo de entrada para os classificadores
- 'target.txt': arquivo de referência para medir a acurácia dos classificadores

# Datasets de Treino, validação da Tarefa 3 - 2024
- rescue_prior.txt: contém 1280 linhas para treinamento de um regressor que estima a prioridade de salvamento de uma vítima dadas as características:
  - dificuldade de acesso à vítima (soma das dificuldades das células no entorno da vítima + própria célula),
  - nível de gravidade e
  - distância Euclidiana da vítima à base
- 'rescue_prior_preblind.txt': contém 300 linhas para pré-teste cego de um regressor; a estrutura é idêntica ao do rescue_prior.txt, exeto pelo fato de não ter a última coluna que deve ser estimada pelo regressor.
