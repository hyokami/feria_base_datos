// Navegación entre pestañas
function mostrarSeccion(idSeccion, boton) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  
  document.getElementById(idSeccion).classList.add('active');
  if (boton) boton.classList.add('active');
}

function irDesdeTarjeta(idSeccion) {
  const botones = document.querySelectorAll('.nav-btn');
  const mapa = { hub: 0, champions: 1, gachapon: 2, grammy: 3 };
  mostrarSeccion(idSeccion, botones[mapa[idSeccion]]);
}

// --- DEMO VISUAL CHAMPIONS (Luego se conecta a /api/champions/simular) ---
function guardarPrediccionChampions() {
  const alias = document.getElementById('aliasInput').value || 'Visitante';
  const equipo = document.getElementById('equipoUsuario').value;
  document.getElementById('msgChampions').textContent = 
    `✓ Predicción guardada para ${alias}: ${equipo}.`;
}

function simularChampionsDemo() {
  const temp = document.getElementById('temporadaSelect').value;
  const bracket = document.getElementById('bracketResultado');
  bracket.innerHTML = `
    <div class="bracket-col">
      <h4>Semifinales (${temp})</h4>
      <div class="match-card">Real Madrid (54%) vs Bayern (46%)</div>
      <div class="match-card">Man. City (58%) vs Arsenal (42%)</div>
    </div>
    <div class="bracket-col">
      <h4>Campeón Simulado (${temp})</h4>
      <div class="match-card highlight">🏆 Real Madrid (Prob. Monte Carlo: 31.4%)</div>
    </div>
  `;
}

// --- DEMO VISUAL GACHAPÓN (Luego se conecta al backend de inventario) ---
let intentos = 3;
let pity = 14;

function abrirCofreDemo() {
  if (intentos <= 0) {
    alert('Ya usaste tus 3 tiradas gratuitas en el stand.');
    return;
  }

  intentos--;
  pity++;
  document.getElementById('intentosUser').textContent = intentos;
  
  const cofre = document.getElementById('cofreVisual');
  const texto = document.getElementById('premioTexto');
  cofre.style.transform = 'scale(1.15)';
  texto.textContent = 'Abriendo cofre...';

  setTimeout(() => {
    cofre.style.transform = 'scale(1)';
    let premio = 'Sticker Común (Común)';
    
    if (pity >= 20) {
      premio = '🏆 Llavero Edición Feria (LEGENDARIO - Garantía)';
      pity = 0;
    } else {
      const rand = Math.floor(Math.random() * 100) + 1;
      if (rand > 97) { premio = '🏆 Llavero Edición Feria (LEGENDARIO)'; pity = 0; }
      else if (rand > 85) { premio = '✨ Pin Metálico (Épico)'; }
      else if (rand > 60) { premio = '🍀 Pulsera (Especial)'; }
    }

    document.getElementById('pityCount').textContent = `${pity} / 20`;
    texto.textContent = `¡Ganaste: ${premio}!`;

    const alias = document.getElementById('aliasInput').value || 'Visitante';
    const lista = document.getElementById('historialGacha');
    const item = document.createElement('li');
    item.textContent = `${alias} ganó: ${premio}`;
    lista.prepend(item);
  }, 600);
}

// --- DEMO VISUAL LATIN GRAMMY (Luego se conecta a /api/latingrammy/predecir) ---
function votarGrammy(artista) {
  const alias = document.getElementById('aliasInput').value || 'Visitante';
  document.getElementById('msgGrammy').textContent = 
    `✓ ${alias} apostó por ${artista}. Comparando con el Teorema de Bayes...`;
}