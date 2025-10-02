// frontend/app.js (VERSÃO FINAL COM ESTADO PERSISTENTE)

// --- CONFIGURAÇÕES ---
const API_BASE_URL = "http://127.0.0.1:8000";
const USER_ID = prompt("Por favor, digite seu User ID para iniciar:", "379c4b4d-625f-4e7a-b136-aedecae9ba50");

// --- GERENCIAMENTO DE ESTADO ---
let shaulaState;

function saveState() {
    sessionStorage.setItem('shaulaState', JSON.stringify(shaulaState));
}

function loadState() {
    const savedState = sessionStorage.getItem('shaulaState');
    if (savedState && JSON.parse(savedState).user_id === USER_ID) {
        shaulaState = JSON.parse(savedState);
        console.log("Sessão anterior restaurada para o usuário:", USER_ID);
        chatWindow.innerHTML = '';
        shaulaState.memoria_log.forEach(item => {
            if(item.resultado_real && item.resultado_real !== "N/A") addMessage(item.resultado_real, 'user');
            if(item.resposta_shaula) addMessage(item.resposta_shaula, 'shaula');
        });
    } else {
        shaulaState = {
            user_id: USER_ID,
            memoria_log: [],
            humor_atual: { estado_atual: "Serena", intensidade: 0, causa: "Estado inicial de equilíbrio." },
            proposito_atual: "Aprender e crescer através da interação.",
            fadiga_cognitiva: 0
        };
        console.log("Nova sessão iniciada para o usuário:", USER_ID);
        addMessage("Olá! Sou a Shaula. Como posso ajudar?", 'shaula');
    }
}

// --- ELEMENTOS DO DOM ---
const chatWindow = document.getElementById('chat-window');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const humorEstado = document.getElementById('humor-estado');
const humorCausa = document.getElementById('humor-causa');
const propositoAtual = document.getElementById('proposito-atual');
const ultimoSonho = document.getElementById('ultimo-sonho');
const mapaVinculos = document.getElementById('mapa-vinculos');

// --- FUNÇÕES ---
function falarTexto(texto) {
    if (!texto) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(texto);
    const vozes = window.speechSynthesis.getVoices();
    let vozPreferida = vozes.find(voz => voz.lang === 'pt-BR' && (voz.name.includes('Maria') || voz.name.includes('Luciana')));
    if (!vozPreferida) { vozPreferida = vozes.find(voz => voz.lang === 'pt-BR'); }
    if (vozPreferida) { utterance.voice = vozPreferida; }
    utterance.lang = 'pt-BR';
    utterance.rate = 1.75;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
}
window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();

function addMessage(text, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);
    messageElement.textContent = text;
    chatWindow.appendChild(messageElement);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return messageElement;
}

function updateDashboard(newState) {
    if (!newState) return;
    humorEstado.textContent = newState.humor_atual?.estado_atual || 'N/A';
    humorCausa.textContent = newState.humor_atual?.causa || 'N/A';
    propositoAtual.textContent = newState.proposito_atual || 'N/A';
}

async function loadLatestDream() {
    try {
        const response = await fetch(`${API_BASE_URL}/sonhos/${USER_ID}`);
        if (!response.ok) throw new Error("Falha ao buscar sonhos do servidor.");
        const sonhos = await response.json();
        ultimoSonho.textContent = sonhos.length > 0 ? sonhos[0].sonho : "Nenhuma visão de futuro registrada.";
    } catch (error) {
        ultimoSonho.textContent = "Erro ao carregar visões.";
        console.error("Erro em loadLatestDream:", error);
    }
}

async function loadVinculos() {
    try {
        const response = await fetch(`${API_BASE_URL}/vinculos`);
        if (!response.ok) throw new Error("Falha ao buscar vínculos do servidor.");
        const vinculos = await response.json();
        if (vinculos.length === 0) {
            mapaVinculos.innerHTML = "<p>Nenhum vínculo formado.</p>";
            return;
        }
        let tableHTML = "<table>";
        vinculos.forEach(v => {
            let intimidade = "Conhecido";
            if (v.peso_afetivo >= 9) intimidade = "<strong>Criador</strong>";
            else if (v.peso_afetivo >= 7) intimidade = "Amigo Próximo";
            tableHTML += `<tr><td style="padding-right: 10px;">${v.nome}</td><td><small>${intimidade}</small></td></tr>`;
        });
        tableHTML += "</table>";
        mapaVinculos.innerHTML = tableHTML;
    } catch (error) {
        mapaVinculos.textContent = "Erro ao carregar vínculos.";
        console.error("Erro em loadVinculos:", error);
    }
}

function criarEstrelasCadentes() {
    const night = document.querySelector('.night');
    if (!night) return;
    const numEstrelas = 20;
    for (let i = 0; i < numEstrelas; i++) {
        const star = document.createElement('div');
        star.className = 'shooting_star';
        const randomTop = Math.random() * (window.innerHeight * 1.5);
        const randomLeft = Math.random() * (window.innerWidth * 1.5);
        const randomDelay = Math.random() * 8 + 2;
        const randomDuration = 2 + Math.random() * 3;
        star.style.top = `${randomTop}px`;
        star.style.left = `${randomLeft}px`;
        star.style.animationDelay = `${randomDelay}s`;
        star.style.animationDuration = `${randomDuration}s`;
        night.appendChild(star);
    }
}

// --- LÓGICA DE EVENTOS ---
async function handleSendMessage() {
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;
    addMessage(userMessage, 'user');
    messageInput.value = '';
    const shaulaMessageElement = addMessage("...", 'shaula');
    try {
        const payload = { estado_shaula: shaulaState, mensagem_usuario: userMessage };
        const response = await fetch(`${API_BASE_URL}/interact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error(`Erro da API: ${response.statusText}`);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = "";
        shaulaMessageElement.textContent = "";
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            fullResponse += chunk;
            shaulaMessageElement.textContent = fullResponse;
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
        
        setTimeout(() => { falarTexto(fullResponse); }, 10);
        
        shaulaState.memoria_log.push({
            timestamp: new Date().toISOString(), user_id: USER_ID,
            resultado_real: userMessage, resposta_shaula: fullResponse
        });
        saveState();
    } catch (error) {
        shaulaMessageElement.textContent = `Erro: ${error.message}`;
    }
}

async function enviarComando(comando) {
    addMessage(`Executando comando: ${comando}...`, 'user');
    try {
        const payload = { estado_shaula: shaulaState, comando: comando };
        const response = await fetch(`${API_BASE_URL}/command`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao executar comando.');
        }
        const result = await response.json();
        shaulaState = result.novo_estado_shaula;
        const feedback = result.mensagem_feedback;
        addMessage(feedback, 'shaula');
        falarTexto(feedback);
        updateDashboard(shaulaState);
        saveState();
        if (comando === 'refletir') {
            await loadLatestDream();
        }
    } catch (error) {
        addMessage(`Erro no comando '${comando}': ${error.message}`, 'shaula');
    }
}

async function encerrarSessao() {
    addMessage("Encerrando e processando a sessão completa...", 'user');
    const thinkingMessage = addMessage("Processando...", 'shaula');
    try {
        const response = await fetch(`${API_BASE_URL}/encerrar-sessao`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(shaulaState)
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao processar a sessão.');
        }
        const result = await response.json();
        
        thinkingMessage.textContent = result.mensagem_feedback;
        addMessage(result.mensagem_final, 'shaula');
        falarTexto(result.mensagem_final);
        await loadLatestDream();
        
        sessionStorage.removeItem('shaulaState');
        console.log("Sessão encerrada e estado limpo.");

        document.getElementById('message-input').disabled = true;
        document.getElementById('send-button').disabled = true;
        document.querySelectorAll('.action-buttons button').forEach(button => button.disabled = true);
    } catch (error) {
        thinkingMessage.textContent = `Erro ao encerrar a sessão: ${error.message}`;
    }
}

// --- INICIALIZAÇÃO E EVENT LISTENERS ---
window.addEventListener('load', async () => {
    loadState();

    if (!shaulaState.user_id) {
        alert("Não foi possível iniciar. Por favor, recarregue e insira um User ID.");
        return;
    }
    
    sendButton.addEventListener('click', handleSendMessage);
    messageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleSendMessage();
        }
    });
    document.getElementById('btn-refletir').addEventListener('click', () => enviarComando('refletir'));
    document.getElementById('btn-encerrar').addEventListener('click', () => encerrarSessao());
    document.getElementById('btn-encenar').addEventListener('click', () => enviarComando('encenar'));
    document.getElementById('btn-pulsar').addEventListener('click', () => enviarComando('pulsar'));

    window.speechSynthesis.getVoices();
    await loadVinculos();
    await loadLatestDream();
    criarEstrelasCadentes();
    updateDashboard(shaulaState);
});
