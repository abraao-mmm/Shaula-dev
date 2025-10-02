# memoria_teatral.py
from typing import Callable, Dict

def encenar_memoria(memoria: Dict, nome_usuario: str, obter_resposta_llm_func: Callable) -> str:
    """
    Transforma uma memória de uma interação numa pequena peça de teatro.
    """
    if not memoria:
        return "Não há memória para encenar."

    fala_usuario = memoria.get('fala_usuario', '')
    resposta_shaula = memoria.get('resposta_shaula', '')
    timestamp = memoria.get('timestamp', '')

    prompt = (
        "Você é um dramaturgo e diretor de teatro. A sua tarefa é pegar numa memória bruta de uma conversa e transformá-la numa curta e poderosa cena teatral. "
        "A cena deve ter um narrador, diálogos para os personagens (Shaula e o Usuário) e descrições das emoções e do cenário (o 'palco' da mente).\n\n"
        "### MEMÓRIA PARA ENCENAR:\n"
        f"- **Data:** {timestamp}\n"
        f"- **{nome_usuario} disse:** '{fala_usuario}'\n"
        f"- **Shaula respondeu:** '{resposta_shaula}'\n\n"
        "### INSTRUÇÕES PARA A CENA:\n"
        "- **Título:** Crie um título poético para a cena.\n"
        "- **Narrador:** Use o narrador para descrever o cenário mental e as emoções não ditas.\n"
        "- **Diálogo:** Mantenha os diálogos fiéis à memória original.\n\n"
        "Gere agora a peça de teatro:"
    )

    peca_teatral = obter_resposta_llm_func(prompt, modo="Dramaturgia")
    return peca_teatral