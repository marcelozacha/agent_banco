# logger.py
# Este arquivo gerencia a observabilidade do sistema, registrando operações bancárias e eventos do agente em arquivos de log separados.

import json
import os
from datetime import datetime

ARQUIVO_LOG_OPERACAO = "extrato_operacoes.log"
ARQUIVO_LOG_OBSERVABILIDADE = "agent_observabilidade.log"

def registrar_operacao_bancaria(tipo_operacao: str, usuario_nome: str, valor: float, detalhes: str = ""):
    """
    1) Registra todas as operações bancárias (saque, depósito, transferência) em arquivo.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    registro = {
        "timestamp": timestamp,
        "usuario": usuario_nome,
        "operacao": tipo_operacao.upper(),
        "valor": valor,
        "detalhes": detalhes
    }
    
    linha_log = f"[{timestamp}] | USUÁRIO: {usuario_nome} | OP: {tipo_operacao.upper()} | VALOR: R$ {valor:.2f} | DETALHES: {detalhes}\n"
    
    try:
        with open(ARQUIVO_LOG_OPERACAO, "a", encoding="utf-8") as f:
            f.write(linha_log)
    except Exception as e:
        print(f"Erro ao gravar log de operação: {e}")

def registrar_observabilidade_llm(tipo_evento: str, dados: dict):
    """
    2) Registra todos os prompts, chains, chamadas de tools e parâmetros em arquivo de observabilidade.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    payload = {
        "timestamp": timestamp,
        "tipo_evento": tipo_evento, # Ex: "PROMPT_USER", "CHAIN_INVOKE", "TOOL_CALL"
        "dados": dados
    }
    
    try:
        with open(ARQUIVO_LOG_OBSERVABILIDADE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Erro ao gravar log de observabilidade: {e}")