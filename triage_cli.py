from app.core.agent_triage import TriageAgent

if __name__ == "__main__":
    agent = TriageAgent()

    print("=== Agente de Triagem - Banco Ágil ===")
    while True:
        user = input("Você: ")
        if user.lower() in {"sair", "exit", "quit"}:
            print("Agente: Atendimento encerrado. Até logo!")
            break

        answer = agent.ask(user)
        print(f"Agente: {answer}")
