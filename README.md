# Banco Ágil - Sistema de Agentes Bancários Inteligentes

## Visão Geral do Projeto

O Banco Ágil é um projeto criado para simular como seria um atendimento bancário moderno, rápido e conduzido por agentes de IA.
A ideia foi construir algo que parecesse uma conversa real com um atendente, mas com regras claras, estados conversacionais e decisões baseadas em dados.

- Uma API em FastAPI (onde ficam os fluxos, regras e agentes)
- Uma interface em Streamlit
- Agentes de IA que controlam a triagem, consulta de limite e entrevista de crédito

## Objetivo do projeto:
1. Criação de agentes conversacionais
2. Integração de IA em fluxos de manipulações de dados em CSV 
3. Boas práticas de arquitetura de software
4. Usar IA de forma controlada e segura, evitando que tenha contato direto com arquivos

## Conceito de Agentes de IA no Projeto.
Este projeto não usa IA apenas para “responder mensagens”.
Os agentes têm estado, memória e lógica própria de decisão.

**Agente de Triagem**
*Fluxo*
ask_cpf → ask_birthdate → authenticated

**Agente de Entrevista de Crédito**
Coleta renda, despesas, emprego, dependentes e dívidas.
Calcula score via service e retorna resposta natural via IA.

## Ideia do uso de IA
Uma escolha intencional da arquitetura foi não permitir que a IA acesse dados sensíveis diretamente.
Quem faz a leitura, escrita e decisões é o backend Python.
A IA tem contato apenas com o contexto necessário para montar a resposta humanizada.

**Por que isso é importante?**
- A IA não entende muito privacidade e questões de LGPD.
- Podem interferir incorretamente em dados.
- Podem gerar dados imprecisos se caso receberem valores brutos.
Esse é o mesmo padrão utilizado por plataformas grandes, como o Nubank e outros bancos digitais.

**Isso garante:**
*Segurança dos dados* 
*Previsibilidade*

## Arquitetura do Sistema
Optei por uma arquitetura simples, modular e fácil de testar, evitando overengineering sem perder boas práticas.

### Camadas principais
O backend segue uma arquitetura em camadas:
**Routers** → recebem requisições, chamam os controllers
**Controllers** → coordenam o fluxo, validam dados e chamam os services.
**Services** → concentram regras de negócio (ex: cálculo de score).
**Repositories** → leitura/escrita no CSV de clientes.
**Agents (IA)** → controlam conversa + IA.

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
    - triagem (CPF + data de nascimento)
    - agente de autenticação
    - menu de ações inteligente
    - entrevista de crédito
    - cálculo de score de crédito
    - atualização de dados do cliente no .csv
    - logs em arquivo .csv
    - retorno de valor cambial


- **Frontend (Streamlit)**
    - experiência conversacional
    - controle de estado
    - reset de fluxo
    - formatação limpa das respostas

# Problemas Encontrados e Como Foram Resolvidos
1. **Estado no Streamlit**
Resolvido reorganizando o fluxo e usando session_state.

2. **Markdown feio vindo da IA**
Resolvido com st.markdown(..., unsafe_allow_html=True) e padronização no backend.

3. **Chamadas duplicadas**
Resolvido isolando chamadas e controlando melhor o fluxo.

# Escolhas Técnicas e Justificativas
## FastAPI
- rápido, simples e fácil de testar
- ótima separação de camadas
- validações com Pydantic
- ideal para fluxos conversacionais

## Groq
- latência extremamente baixa
- suporte a modelos open-source
- experiência conversacional fluida

## LangChain
- organiza prompts
- padroniza chamadas ao LLM
- permite troca de modelos sem refatorar nada

## Client de IA Padronizado
- ponto único de comunicação com o LLM
- centraliza tratamento de erros
- garante consistência e evita retornos imprevisíveis

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

```text
# Estrutura do Código
app/
├── agents/
│   ├── screening_agent.py         # fluxo de triagem
│   └── interview_agent.py         # entrevista de crédito via IA
├── controllers/
│   ├── auth_controller.py
│   └── interview_controller.py
├── services/
│   └── credit_service.py          # regras de negócio
├── repositories/
│   └── client_repository.py       # leitura/escrita CSV
├── routers/
│   ├── screening_router.py
│   └── credit_router.py
├── infrastructure/
│   └── schemas/                   # Pydantic models
└── utils/
    ├── auth_utils.py
    └── llm_client.py              # integração com IA
```



### Ferramentas para qualidade de Código:
1. *Pylint* foi utilizado para garantir padronização e boa qualidade do código, 
verificando desde formatação (como limite de caracteres por linha) até possíveis erros estruturais.

2. *Black Formatter* Aplicado para formatar automaticamente todo o código de maneira consistente. 
O Black elimina debates sobre estilo, padroniza espaçamentos, quebras de linha e organização geral do código, tornando o repositório mais legível, uniforme e fácil de manter.

### Observação: Trabalho com uma estrutura diferente da feita aqui mas, para evitar overengineering, optei por uma estrutura diferente. Conseguiria trabalhar com erros em camadas diferentes mas visando uma aplicação mais simplificada, optei por essa arquitetura.