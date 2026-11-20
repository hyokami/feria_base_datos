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

// --- CONEXIÓN REAL CHAMPIONS (FastAPI + SQLite + Monte Carlo) ---
const API_CHAMPIONS = "http://127.0.0.1:8000/api/champions";

// Cargar los 16 equipos reales desde SQLite al abrir la página
document.addEventListener("DOMContentLoaded", async () => {
  const selectEquipo = document.getElementById("equipoUsuario");
  if (!selectEquipo) return;

  try {
    const res = await fetch(`${API_CHAMPIONS}/equipos`);
    if (!res.ok) return;
    const equipos = await res.json();

    selectEquipo.innerHTML = "";
    equipos.forEach(eq => {
      const opt = document.createElement("option");
      opt.value = eq.id_equipo;
      opt.textContent = `${eq.nombre} (Elo: ${Math.round(eq.puntaje_poder)})`;
      selectEquipo.appendChild(opt);
    });
  } catch (error) {
    console.warn("Backend de Champions apagado; se mantienen los equipos del HTML.");
  }
});

async function guardarPrediccionChampions() {
  const alias = document.getElementById("aliasInput").value.trim() || "Visitante";
  const selectEquipo = document.getElementById("equipoUsuario");
  const idEquipo = parseInt(selectEquipo.value) || 1;
  const nombreEquipo = selectEquipo.options[selectEquipo.selectedIndex]?.text || "Equipo";
  const temporada = parseInt(document.getElementById("temporadaSelect").value) || 2027;
  const msg = document.getElementById("msgChampions");

  try {
    const res = await fetch(`${API_CHAMPIONS}/predecir`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id_usuario_global: alias,
        id_equipo_campeon: idEquipo,
        temporada: temporada
      })
    });

    const data = await res.json();
    msg.textContent = `✓ ${data.mensaje} (#${data.id_prediccion}) para ${alias}: ${nombreEquipo}.`;
  } catch (error) {
    msg.textContent = "⚠️ No se pudo conectar con la API de Champions (verifica que uvicorn esté encendido).";
  }
}

async function simularChampionsDemo() {
  const temp = parseInt(document.getElementById("temporadaSelect").value) || 2027;
  const bracket = document.getElementById("bracketResultado");
  bracket.innerHTML = `<div class="bracket-col"><div class="match-card">Ejecutando 5,000 simulaciones Monte Carlo...</div></div>`;

  try {
    const res = await fetch(`${API_CHAMPIONS}/simular`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        temporada: temp,
        n_simulaciones: 5000
      })
    });

    const data = await res.json();
    let html = "";

    // Recorre automáticamente Octavos, Cuartos, Semis y Final
    for (const [fase, partidos] of Object.entries(data.arbol)) {
      html += `<div class="bracket-col"><h4>${fase} (${temp})</h4>`;
      partidos.forEach(p => {
        const probB = (100 - p.prob_a).toFixed(1);
        html += `
          <div class="match-card">
            ${p.equipo_a.nombre} (${p.prob_a}%) vs ${p.equipo_b.nombre} (${probB}%)
            <br><small><strong>Avanza:</strong> ${p.ganador.nombre}</small>
          </div>
        `;
      });
      html += `</div>`;
    }

    // Columna del campeón
    html += `
      <div class="bracket-col">
        <h4>Campeón Simulado (${temp})</h4>
        <div class="match-card highlight">
          🏆 ${data.campeon.nombre}<br>
          <small>Elo: ${data.campeon.puntaje_poder}</small>
        </div>
      </div>
    `;

    bracket.innerHTML = html;
  } catch (error) {
    bracket.innerHTML = `<div class="bracket-col"><div class="match-card">⚠️ Error conectando con http://127.0.0.1:8000</div></div>`;
  }
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