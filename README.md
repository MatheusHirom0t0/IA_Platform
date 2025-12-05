# Banco Ágil - Sistema de Agentes Bancários Inteligentes

## Visão Geral do Projeto

O Banco Ágil é uma aplicação composta por uma API em FastAPI e uma interface em Streamlit, criada para simular fluxos reais de atendimento bancário usando IA generativa.
O sistema executa três operações principais:
- **Triagem do cliente** (validação de CPF + data de nascimento)
- **Consulta/Aumento de limite de crédito**
- **Entrevista de crédito conduzida por um agente inteligente**
A arquitetura foi pensada para ser modular, expansível e fácil de testar, permitindo que cada parte do fluxo evolua sem quebrar o restante da aplicação.

## Arquitetura do Sistema

### Camadas principais

O backend segue uma arquitetura em camadas:
**Routers** → recebem a requisição HTTP e direcionam ao controller.
**Controllers** → coordenam o fluxo, validam dados e chamam os services.
**Services** → concentram regras de negócio (ex: cálculo de score).
**Repositories** → leitura/escrita no CSV de clientes.
**Agents (IA)** → processam linguagem natural, mantêm estados de conversa e controlam fluxos inteligentes.

### Fluxo de Triagem (Screening Agent)

1. Usuário informa CPF
2. Agente valida e avança para nascimento
3. Autenticação confirmada → libera menu de ações
4. O agente mantém estado entre mensagens (ask_cpf → ask_birthdate → authenticated)

### Fluxo de Entrevista de Crédito
O agente conduz perguntas sobre renda, despesas, emprego e dívidas.
O service calcula score.
O CSV de clientes é atualizado com o novo score.
IA gera respostas naturais para manter a conversa fluida.

### Manipulação de Dados
Todos os clientes são armazenados em data/clientes.csv.
Atualizações (score, limite, status) são feitas pelo Repository.
Nenhum controller manipula arquivos diretamente.

# Funcionalidades Implementadas
- **Backend (FastAPI)**
    - Autenticação via CPF + nascimento
    - Fluxo de triagem inteligente
    - Menu de ações (limite, aumento, entrevista, etc.)
    - IA para respostas naturais (via agente)
    - Cálculo de score de crédito
    - Atualização de dados do cliente no CSV

- **Frontend (Streamlit)**
    - Conversa em tempo real com o agente
    - Controle de sessão para manter o estado da conversa
    - Redirecionamento automático para menu após autenticação
    - Comandos para resetar fluxo quando necessário

# Problemas Encontrados e Como Foram Resolvidos
1. **Manter o estado correto nos agentes de triagem e entrevista**
**Problema:** A aba de ações (menu 1–5) estava sendo exibida antes da autenticação e reaparecendo após qualquer requisição, porque o Streamlit executa toda a aplicação a cada interação e o menu não estava condicionado ao estado correto. Isso causava duplicações e inconsistências no fluxo. Para resolver, o front foi reestruturado para exibir o menu somente quando authenticated == True, usando st.session_state para controlar o estado e evitar renderizações duplicadas ou fora de ordem. Com isso, a aba de ações agora aparece apenas no momento certo e de forma estável.

2. **Respostas da IA vinham com Markdown feio e não formatado**
**Problema:** As respostas da IA apareciam com Markdown bruto (texto, # título, - lista), porque o front exibia o conteúdo diretamente sem realizar formatação, e em alguns momentos a API retornava atributos incorretos. O problema foi resolvido padronizando o acesso ao conteúdo da IA (response.choices[0].message.content) no backend e, no frontend, usando st.markdown(reply, unsafe_allow_html=True) para renderizar corretamente o texto. Assim, todas as respostas agora aparecem limpas, formatadas e com aparência profissional.

3. **Configuração inadequada do front resultava em chamadas duplicadas e fluxo quebrado**
**Problema:** O Streamlit estava executando blocos mais de uma vez, fazendo chamadas repetidas à API, reiniciando o fluxo sem querer e exibindo mensagens duplicadas, porque não havia controle de estado adequado. Para corrigir, o frontend foi reorganizado com uso consistente do st.session_state para armazenar estágios do agente, autenticação, histórico de mensagens e últimas ações. Além disso, o reset foi corrigido para realmente retornar à etapa inicial (digitar CPF), e as chamadas à API foram isoladas para evitar execuções automáticas indesejadas. Agora o fluxo funciona de forma previsível, sem duplicações e com controle total do estado.

# Escolhas Técnicas e Justificativas
## FastAPI
- Escolhido pela capacidade de estruturar APIs de forma clara, tipada e modular.
- Facilita a criação de camadas separadas (Routers, Controllers, Services, Agents).
- A baixa latência do framework garante respostas rápidas mesmo ao integrar IA.
- Ótimo suporte para validação com Pydantic, que ajuda a garantir que o fluxo conversacional receba dados limpos antes de chegar aos agentes de IA.

## Groq
- Utilizado como motor principal para executar inferências de IA devido à velocidade extremamente alta do GroqChip.
- Respostas são muito mais rápidas que em modelos tradicionais, essencial para manter fluidez em conversas.
- Permite usar modelos open-source (como Llama 3) com desempenho similar ou superior a soluções proprietárias.
- Custo reduzido e throughput alto fazem dele uma ótima opção para aplicações de IA interativas.

## LangChain
- Utilizado para organizar a comunicação com o LLM e estruturar prompts de forma mais limpa.
- Facilita a criação de chains reutilizáveis, permitindo padronizar como o agente responde em diferentes etapas.
- Abstrai a complexidade da integração com modelos, permitindo trocar o backend (Groq → OpenAI → Hugging Face) sem alterar a lógica da aplicação.
- Ajuda a implementar controle conversacional, garantindo que o agente siga o fluxo definido (etapas de triagem, entrevista, coleta de dados, etc.).

## Client de IA Padronizado
- Toda comunicação com o modelo passa por um client único (llm_client).
- Torna fácil trocar o provedor de IA sem alterar controllers, services ou lógica de fluxo.
- Resolve problemas de inconsistência no retorno dos modelos, convertendo tudo para texto limpo.
- Implementa tratamento de erros e fallback de forma centralizada, garantindo resiliência.

# Tutorial de Execução
1. Clonar o repositório

git clone https://github.com/MatheusHirom0t0/IA_Platform.git
cd IA_Platform

2. Criar ambiente virtual
    1. python -m venv .venv

    2. source .venv/bin/activate  # Mac/Linux
        .venv\Scripts\activate     # Windows
    
3. Instalar dependências
pip install -r requirements.txt

4. Executar o backend
uvicorn app.main:app --reload

**Backend roda em http://localhost:8000**

5. Executar o frontend (Streamlit)
streamlit run streamlit_app.py

# Estrutura do Código

app/
│
├── agents/
│   ├── screening_agent.py      # fluxo de triagem
│   ├── interview_agent.py      # entrevista de crédito via IA
│
├── controllers/
│   ├── auth_controller.py
│   ├── interview_controller.py
│
├── services/
│   ├── credit_service.py       # regras de negócio
│
├── repositories/
│   ├── client_repository.py    # leitura/escrita CSV
│
├── routers/
│   ├── screening_router.py
│   ├── credit_router.py
│
├── infrastructure/
│   └── schemas/                # Pydantic models
│
└── utils/
    ├── auth_utils.py
    ├── llm_client.py           # integração com IA



# Observação: Trabalho com uma estrutura diferente da feita aqui mas, para evitar overengineering, optei por uma estrutura diferente. Conseguiria trabalhar com erros em camadas diferentes mas visando uma aplicação mais simplificada, optei por essa arquitetura.


# Ferramentas para qualidade de Código:
1. *Pylint* foi utilizado para garantir padronização e boa qualidade do código, 
verificando desde formatação (como limite de caracteres por linha) até possíveis erros estruturais.

2. *Black Formatter* Aplicado para formatar automaticamente todo o código de maneira consistente. 
O Black elimina debates sobre estilo, padroniza espaçamentos, quebras de linha e organização geral do código, tornando o repositório mais legível, uniforme e fácil de manter.