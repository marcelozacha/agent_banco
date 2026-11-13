# tools.py
# Este arquivo define as ferramentas (tools) que o agente bancário pode utilizar para interagir com o banco de dados, incluindo consultas de saldo, saques, depósitos e transferências.

from langchain_core.tools import tool
from database import CONTAS_DB, obter_usuario_logado, salvar_banco

#para logar operações bancárias
from logger import registrar_operacao_bancaria

@tool
def consultar_saldo() -> str:
    """Consulta o saldo atual, agência, conta e dados do usuário logado."""
    user = obter_usuario_logado()
    return (
        f"Titular: {user['nome']} | Código: {user['codigo']}\n"
        f"Agência: {user['agencia']} | Conta: {user['conta']}-{user['digito']}\n"
        f"Saldo Atual: R$ {user['saldo']:.2f}"
    )

@tool
def realizar_saque(valor: float) -> str:
    """Realiza um saque na conta do usuário logado, validando o saldo, atualizando o montante e salvando."""
    user = obter_usuario_logado()
    if valor <= 0:
        return "Erro: O valor do saque deve ser maior que zero."
    
    if user["saldo"] < valor:
        return f"Erro: Saldo insuficiente. Saldo atual: R$ {user['saldo']:.2f}, Tentativa de saque: R$ {valor:.2f}."
    
    user["saldo"] -= valor
    salvar_banco()  # Salva permanentemente no JSON

    #logar a operação de saque
    registrar_operacao_bancaria("saque", user["nome"], valor, f"Conta: {user['conta']}")

    return f"Sucesso! Saque de R$ {valor:.2f} realizado. Saldo atualizado da conta {user['conta']}-{user['digito']}: R$ {user['saldo']:.2f}."

@tool
def realizar_deposito(valor: float) -> str:
    """Realiza um depósito na conta do usuário logado, atualiza o saldo e salva."""
    user = obter_usuario_logado()
    if valor <= 0:
        return "Erro: O valor do depósito deve ser maior que zero."
    
    user["saldo"] += valor
    salvar_banco()  # Salva permanentemente no JSON

    #logar a operação de depósito
    registrar_operacao_bancaria("depósito", user["nome"], valor, f"Conta: {user['conta']}")

    return f"Sucesso! Depósito de R$ {valor:.2f} realizado. Saldo atualizado da conta {user['conta']}-{user['digito']}: R$ {user['saldo']:.2f}."

@tool
def transferir_valor(valor: float, destinatario_nome: str, agencia: str, conta: str, digito: str) -> str:
    """Transfere um valor da conta do usuário logado para outro usuário identificando por nome, agência, conta e dígito, atualiza os saldos e salva."""
    origem = obter_usuario_logado()
    
    # Encontrar o destinatário combinando nome, agência, conta e dígito
    destino = None
    for u in CONTAS_DB.values():
        if (
            u["nome"].lower() == destinatario_nome.lower() and
            u["agencia"] == agencia and
            u["conta"] == conta and
            u["digito"] == digito and
            u["id"] != origem["id"]
        ):
            destino = u
            break
            
    if not destino:
        return f"Erro: Destinatário '{destinatario_nome}' (Ag: {agencia}, CC: {conta}-{digito}) não encontrado ou dados incorretos."
        
    if valor <= 0:
        return "Erro: O valor da transferência deve ser maior que zero."
        
    if origem["saldo"] < valor:
        return f"Erro: Saldo insuficiente para transferência. Saldo atual: R$ {origem['saldo']:.2f}."
        
    # Efetivar a transferência atualizando ambos os saldos
    origem["saldo"] -= valor
    destino["saldo"] += valor
    
    salvar_banco()  # Salva permanentemente no JSON

    #logar a operação de transferência
    registrar_operacao_bancaria("transferência", origem["nome"], valor, f"Para: {destino['nome']} (Ag: {destino['agencia']}, CC: {destino['conta']}-{destino['digito']})")
    
    return (
        f"Sucesso! Transferência de R$ {valor:.2f} para {destino['nome']} "
        f"(Ag: {destino['agencia']} | Conta: {destino['conta']}-{destino['digito']}) realizada.\n"
        f"Seu saldo atualizado: R$ {origem['saldo']:.2f}"
    )

# Lista de tools disponíveis para o agente
ALL_TOOLS = [consultar_saldo, realizar_saque, realizar_deposito, transferir_valor]