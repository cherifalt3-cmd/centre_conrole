<script setup>
import { ref } from 'vue'
import { login } from '../auth'

const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  error.value = ''
  try {
    await login(username.value, password.value)
  } catch (e) {
    error.value = e.message
  }
}
</script>

<template>
  <div class="page">
    <!-- fond galaxie -->
    <div class="galaxy">
      <div class="nebula nebula-a"></div>
      <div class="nebula nebula-b"></div>
      <div class="stars stars-1"></div>
      <div class="stars stars-2"></div>
      <div class="stars stars-3"></div>

      <!-- étoiles filantes -->
      <div class="shooting shooting-1"></div>
      <div class="shooting shooting-2"></div>
      <div class="shooting shooting-3"></div>

      <!-- système solaire -->
      <div class="solar-system">
        <div class="sun"></div>
        <div class="orbit orbit-1"><span class="planet planet-1"></span></div>
        <div class="orbit orbit-2"><span class="planet planet-2"></span></div>
        <div class="orbit orbit-3"><span class="planet planet-3"><span class="ring"></span></span></div>
        <div class="orbit orbit-4"><span class="planet planet-4"></span></div>
      </div>
    </div>

    <div class="card">
      <form @submit.prevent="handleLogin">
        <p class="eyebrow">Centre de contrôle</p>
        <h1>Connexion</h1>

        <div class="field">
          <label for="username">Nom d'utilisateur</label>
          <input id="username" v-model="username" type="text" autocomplete="username" />
        </div>

        <div class="field">
          <label for="password">Mot de passe</label>
          <input id="password" v-model="password" type="password" autocomplete="current-password" />
        </div>

        <button class="btn" type="submit">Se connecter</button>

        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.page {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: radial-gradient(ellipse at 50% 40%, #241546 0%, #120a2c 45%, #06040f 100%);
}

/* ---------- galaxie ---------- */
.galaxy {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.nebula {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.5;
  mix-blend-mode: screen;
}

.nebula-a {
  width: 620px;
  height: 620px;
  top: -140px;
  left: -120px;
  background: radial-gradient(circle, #7b3fe4 0%, transparent 70%);
  animation: drift-a 26s ease-in-out infinite;
}

.nebula-b {
  width: 520px;
  height: 520px;
  bottom: -160px;
  right: -100px;
  background: radial-gradient(circle, #2f6ad0 0%, transparent 70%);
  animation: drift-b 32s ease-in-out infinite;
}

@keyframes drift-a {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(40px, 30px); }
}

@keyframes drift-b {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-40px, -30px); }
}

/* ---------- étoiles (3 couches) ---------- */
.stars {
  position: absolute;
  inset: 0;
  background-repeat: repeat;
}

.stars-1 {
  background-image:
    radial-gradient(1px 1px at 20px 30px, #fff, transparent),
    radial-gradient(1px 1px at 90px 70px, #fff, transparent),
    radial-gradient(1px 1px at 160px 40px, #cfe0ff, transparent),
    radial-gradient(1px 1px at 50px 150px, #fff, transparent),
    radial-gradient(1px 1px at 130px 190px, #fff, transparent),
    radial-gradient(1px 1px at 200px 120px, #dfe8ff, transparent),
    radial-gradient(1px 1px at 240px 60px, #fff, transparent),
    radial-gradient(1px 1px at 280px 180px, #fff, transparent);
  background-size: 300px 300px;
  animation: twinkle 4s ease-in-out infinite, scroll-slow 140s linear infinite;
}

.stars-2 {
  background-image:
    radial-gradient(1.5px 1.5px at 60px 50px, #fff, transparent),
    radial-gradient(1.5px 1.5px at 180px 120px, #bcd4ff, transparent),
    radial-gradient(1.5px 1.5px at 300px 80px, #fff, transparent),
    radial-gradient(1.5px 1.5px at 120px 260px, #fff, transparent),
    radial-gradient(1.5px 1.5px at 350px 220px, #fff, transparent),
    radial-gradient(1.5px 1.5px at 260px 320px, #d8e4ff, transparent);
  background-size: 400px 400px;
  animation: twinkle 6s ease-in-out infinite 1s, scroll-slow 200s linear infinite;
}

.stars-3 {
  background-image:
    radial-gradient(2px 2px at 100px 100px, #fff, transparent),
    radial-gradient(2px 2px at 380px 200px, #fff, transparent),
    radial-gradient(2px 2px at 220px 400px, #c8dcff, transparent),
    radial-gradient(2px 2px at 460px 320px, #fff, transparent);
  background-size: 520px 520px;
  animation: twinkle 5s ease-in-out infinite 2s;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.35; }
  50% { opacity: 1; }
}

@keyframes scroll-slow {
  from { background-position: 0 0; }
  to { background-position: 300px 0; }
}

/* ---------- étoiles filantes ---------- */
.shooting {
  position: absolute;
  width: 120px;
  height: 2px;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0), #fff);
  border-radius: 2px;
  opacity: 0;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.8));
}

.shooting::after {
  content: '';
  position: absolute;
  right: 0;
  top: -1px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 8px 2px rgba(255, 255, 255, 0.9);
}

/* coin haut-gauche vers le bas-droite */
.shooting-1 {
  top: 8%;
  left: -140px;
  transform: rotate(28deg);
  animation: shoot-1 7s ease-in infinite;
}

/* coin haut-droit vers le bas-gauche */
.shooting-2 {
  top: 4%;
  right: -140px;
  transform: rotate(150deg);
  animation: shoot-2 9s ease-in infinite 3s;
}

/* coin bas-gauche vers le haut-droite */
.shooting-3 {
  bottom: 12%;
  left: -140px;
  transform: rotate(-24deg);
  animation: shoot-3 11s ease-in infinite 5.5s;
}

@keyframes shoot-1 {
  0% { opacity: 0; transform: translate(0, 0) rotate(28deg); }
  6% { opacity: 1; }
  18% { opacity: 1; }
  30% { opacity: 0; transform: translate(70vw, 40vh) rotate(28deg); }
  100% { opacity: 0; transform: translate(70vw, 40vh) rotate(28deg); }
}

@keyframes shoot-2 {
  0% { opacity: 0; transform: translate(0, 0) rotate(150deg); }
  6% { opacity: 1; }
  18% { opacity: 1; }
  30% { opacity: 0; transform: translate(-70vw, 45vh) rotate(150deg); }
  100% { opacity: 0; transform: translate(-70vw, 45vh) rotate(150deg); }
}

@keyframes shoot-3 {
  0% { opacity: 0; transform: translate(0, 0) rotate(-24deg); }
  6% { opacity: 1; }
  18% { opacity: 1; }
  30% { opacity: 0; transform: translate(75vw, -35vh) rotate(-24deg); }
  100% { opacity: 0; transform: translate(75vw, -35vh) rotate(-24deg); }
}

/* ---------- système solaire ---------- */
.solar-system {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 0;
  height: 0;
}

.sun {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 46px;
  height: 46px;
  margin: -23px 0 0 -23px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 35%, #fff3b0, #ffb43d 45%, #ff7a1a 80%);
  box-shadow: 0 0 30px 10px rgba(255, 160, 40, 0.55), 0 0 70px 30px rgba(255, 120, 20, 0.25);
  animation: sun-pulse 5s ease-in-out infinite;
}

@keyframes sun-pulse {
  0%, 100% { box-shadow: 0 0 30px 10px rgba(255, 160, 40, 0.55), 0 0 70px 30px rgba(255, 120, 20, 0.25); }
  50% { box-shadow: 0 0 38px 14px rgba(255, 170, 50, 0.7), 0 0 90px 40px rgba(255, 120, 20, 0.32); }
}

.orbit {
  position: absolute;
  top: 50%;
  left: 50%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.orbit-1 { width: 220px; height: 220px; animation: spin 14s linear infinite; }
.orbit-2 { width: 360px; height: 360px; animation: spin 24s linear infinite; }
.orbit-3 { width: 520px; height: 520px; animation: spin 40s linear infinite; }
.orbit-4 { width: 700px; height: 700px; animation: spin 60s linear infinite; }

@keyframes spin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.planet {
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 50%;
}

.planet-1 {
  width: 10px;
  height: 10px;
  background: radial-gradient(circle at 35% 30%, #ffd9a8, #c86b3a);
  box-shadow: 0 0 8px rgba(200, 107, 58, 0.6);
}

.planet-2 {
  width: 14px;
  height: 14px;
  top: -7px;
  background: radial-gradient(circle at 35% 30%, #9fe0ff, #2f7ad0);
  box-shadow: 0 0 10px rgba(47, 122, 208, 0.6);
}

.planet-3 {
  width: 18px;
  height: 18px;
  top: -9px;
  background: radial-gradient(circle at 35% 30%, #ffe6b0, #d9a441);
  box-shadow: 0 0 10px rgba(217, 164, 65, 0.55);
}

.planet-3 .ring {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 30px;
  height: 10px;
  margin: -5px 0 0 -15px;
  border: 1px solid rgba(255, 230, 176, 0.6);
  border-radius: 50%;
  transform: rotate(-20deg);
}

.planet-4 {
  width: 12px;
  height: 12px;
  top: -6px;
  background: radial-gradient(circle at 35% 30%, #c8b6ff, #6a4fd0);
  box-shadow: 0 0 10px rgba(106, 79, 208, 0.6);
}

/* ---------- carte (verre sombre) ---------- */
.card {
  position: relative;
  z-index: 1;
  background: rgba(14, 16, 26, 0.6);
  backdrop-filter: var(--blur);
  -webkit-backdrop-filter: var(--blur);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-3), 0 0 80px rgba(124, 108, 245, 0.14);
  padding: 38px 34px;
  width: 100%;
  max-width: 376px;
}

/* liseré lumineux sur l'arête haute */
.card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(160deg, rgba(124, 108, 245, 0.6), rgba(255, 255, 255, 0) 45%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 8px;
}

h1 {
  font-size: 1.62rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  margin: 0 0 30px;
  color: #fff;
}

.field {
  margin-bottom: 18px;
}

label {
  display: block;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--text-muted);
  margin-bottom: 7px;
}

input {
  width: 100%;
  padding: 11px 13px;
  background: var(--glass-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.93rem;
  color: var(--text);
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

input:focus {
  outline: none;
  background: var(--glass-3);
  border-color: var(--accent-line);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

.btn {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  background: linear-gradient(135deg, var(--accent), #6355d6);
  color: #fff;
  border: 1px solid var(--accent-line);
  border-radius: var(--radius-sm);
  font-size: 0.92rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 6px 24px rgba(124, 108, 245, 0.3);
  transition: filter 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.btn:hover {
  filter: brightness(1.12);
  box-shadow: 0 8px 32px rgba(124, 108, 245, 0.45);
  transform: translateY(-1px);
}

.error {
  margin-top: 14px;
  margin-bottom: 0;
  color: var(--danger);
  font-size: 0.86rem;
}
</style>
