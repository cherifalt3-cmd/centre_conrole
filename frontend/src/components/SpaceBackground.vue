<script setup>
import { enabledAnimations } from '../animations'
</script>

<template>
  <div class="space-bg" aria-hidden="true">
    <div class="nebula nebula-violet"></div>
    <div class="nebula nebula-blue"></div>
    <div class="nebula nebula-teal"></div>
    <div class="stars stars-far"></div>
    <div class="stars stars-mid"></div>
    <div class="stars stars-near"></div>

    <!-- fusee : traverse en diagonale, du bas a gauche vers le haut a droite -->
    <div v-if="enabledAnimations.rocket" class="craft craft-rocket">
      <svg class="rocket" width="48" height="88" viewBox="0 0 12 22" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
        <!-- coiffe -->
        <rect x="5" y="0" width="2" height="1" fill="#e2564f" />
        <rect x="4" y="1" width="4" height="1" fill="#e2564f" />
        <rect x="4" y="2" width="4" height="1" fill="#eceef3" />
        <!-- corps, eclaire a gauche, ombre a droite -->
        <rect x="3" y="3" width="6" height="12" fill="#eceef3" />
        <rect x="3" y="3" width="1" height="12" fill="#ffffff" />
        <rect x="8" y="3" width="1" height="12" fill="#b8bcc8" />
        <!-- hublot -->
        <rect x="5" y="5" width="2" height="1" fill="#9ccbff" />
        <rect x="5" y="6" width="2" height="1" fill="#3d6fb8" />
        <!-- bande -->
        <rect x="3" y="10" width="6" height="1" fill="#e2564f" />
        <!-- ailerons -->
        <rect x="2" y="12" width="1" height="1" fill="#e2564f" />
        <rect x="9" y="12" width="1" height="1" fill="#e2564f" />
        <rect x="1" y="13" width="2" height="1" fill="#e2564f" />
        <rect x="9" y="13" width="2" height="1" fill="#e2564f" />
        <rect x="0" y="14" width="3" height="1" fill="#b03f3b" />
        <rect x="9" y="14" width="3" height="1" fill="#b03f3b" />
        <!-- tuyere -->
        <rect x="4" y="15" width="4" height="1" fill="#6b6f7a" />
        <!-- flamme -->
        <g class="rocket-flame">
          <rect x="4" y="16" width="4" height="1" fill="#fff1a8" />
          <rect x="4" y="17" width="4" height="1" fill="#ffd166" />
          <rect x="5" y="18" width="2" height="1" fill="#ffa53a" />
          <rect x="5" y="19" width="2" height="1" fill="#ff7a3d" />
          <rect x="5" y="20" width="1" height="1" fill="#e5482f" />
        </g>
      </svg>
    </div>

    <!-- soucoupe : traverse de droite a gauche, en ondulant -->
    <div v-if="enabledAnimations.saucer" class="craft craft-saucer">
      <svg class="saucer" width="100" height="40" viewBox="0 0 20 8" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
        <!-- dome -->
        <rect x="8" y="0" width="4" height="1" fill="#d2ecff" />
        <rect x="7" y="1" width="6" height="1" fill="#a8d8ff" />
        <rect x="6" y="2" width="8" height="1" fill="#74b2ea" />
        <!-- coque -->
        <rect x="3" y="3" width="14" height="1" fill="#c3c7d2" />
        <rect x="1" y="4" width="18" height="1" fill="#e4e7ee" />
        <rect x="0" y="5" width="20" height="1" fill="#9aa1ae" />
        <!-- feux de bord -->
        <g class="saucer-lights">
          <rect x="2" y="5" width="1" height="1" fill="#ffd166" />
          <rect x="7" y="5" width="1" height="1" fill="#7cffc4" />
          <rect x="12" y="5" width="1" height="1" fill="#ffd166" />
          <rect x="17" y="5" width="1" height="1" fill="#7cffc4" />
        </g>
        <!-- dessous -->
        <rect x="3" y="6" width="14" height="1" fill="#6b6f7a" />
        <rect x="6" y="7" width="8" height="1" fill="#4b4f5a" />
      </svg>
    </div>

    <!-- navette lointaine : plus petite, plus pale, de gauche a droite -->
    <div v-if="enabledAnimations.shuttle" class="craft craft-shuttle">
      <svg width="44" height="24" viewBox="0 0 11 6" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
        <rect class="shuttle-engine" x="0" y="2" width="1" height="2" fill="#ffb05c" />
        <rect x="2" y="0" width="2" height="1" fill="#c3ccdb" />
        <rect x="1" y="1" width="5" height="1" fill="#c3ccdb" />
        <rect x="1" y="2" width="8" height="2" fill="#e4e9f2" />
        <rect x="9" y="2" width="2" height="1" fill="#e4e9f2" />
        <rect x="7" y="2" width="2" height="1" fill="#7fb6ff" />
        <rect x="1" y="4" width="5" height="1" fill="#c3ccdb" />
        <rect x="2" y="5" width="2" height="1" fill="#c3ccdb" />
      </svg>
    </div>

    <!-- mini-monstres de feu : meme dessin, trois tailles et trois trajets -->
    <template v-if="enabledAnimations.monsters">
    <div v-for="n in 3" :key="n" :class="['craft', 'craft-monster', `craft-monster-${n}`]">
      <svg class="monster" viewBox="0 0 9 10" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
        <!-- flammes du sommet, qui dansent -->
        <g class="monster-flames">
          <rect x="4" y="0" width="1" height="1" fill="#fff1a8" />
          <rect x="2" y="1" width="1" height="1" fill="#ffd166" />
          <rect x="6" y="1" width="1" height="1" fill="#ffd166" />
          <rect x="2" y="2" width="5" height="1" fill="#ffb03d" />
          <rect x="3" y="2" width="1" height="1" fill="#ffd166" />
          <rect x="5" y="2" width="1" height="1" fill="#ffd166" />
        </g>
        <!-- corps -->
        <rect x="1" y="3" width="7" height="6" fill="#ff8c3a" />
        <rect x="2" y="4" width="5" height="4" fill="#ffb03d" />
        <rect x="1" y="3" width="1" height="6" fill="#e5482f" />
        <rect x="7" y="3" width="1" height="6" fill="#e5482f" />
        <!-- yeux, avec un reflet -->
        <rect x="2" y="5" width="1" height="1" fill="#ffffff" />
        <rect x="2" y="6" width="1" height="1" fill="#1b1030" />
        <rect x="6" y="5" width="1" height="1" fill="#ffffff" />
        <rect x="6" y="6" width="1" height="1" fill="#1b1030" />
        <!-- bouche -->
        <rect x="4" y="7" width="1" height="1" fill="#c2361f" />
        <!-- base de flamme -->
        <rect x="2" y="9" width="5" height="1" fill="#e5482f" />
      </svg>
    </div>

    </template>

    <!-- comete : une tete brillante et sa queue, rapide -->
    <div v-if="enabledAnimations.comet" class="craft craft-comet">
      <div class="comet-tail"></div>
      <div class="comet-head"></div>
    </div>

    <!-- astronaute : derive lentement en tournant sur lui-meme -->
    <div v-if="enabledAnimations.astronaut" class="craft craft-astronaut">
      <svg class="astronaut" width="40" height="48" viewBox="0 0 10 12" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
        <!-- casque et visiere -->
        <rect x="3" y="0" width="4" height="1" fill="#e4e7ee" />
        <rect x="2" y="1" width="6" height="3" fill="#e4e7ee" />
        <rect x="3" y="1" width="4" height="2" fill="#3d6fb8" />
        <rect x="4" y="1" width="1" height="1" fill="#9ccbff" />
        <!-- sac a dos -->
        <rect x="0" y="4" width="2" height="4" fill="#9aa1ae" />
        <!-- combinaison -->
        <rect x="2" y="4" width="6" height="4" fill="#f4f5f8" />
        <rect x="4" y="5" width="2" height="1" fill="#e2564f" />
        <rect x="8" y="4" width="1" height="3" fill="#f4f5f8" />
        <!-- jambes -->
        <rect x="2" y="8" width="2" height="3" fill="#e4e7ee" />
        <rect x="6" y="8" width="2" height="3" fill="#e4e7ee" />
        <rect x="2" y="11" width="2" height="1" fill="#6b6f7a" />
        <rect x="6" y="11" width="2" height="1" fill="#6b6f7a" />
      </svg>
    </div>

    <!-- satellite : corps et panneaux solaires -->
    <div v-if="enabledAnimations.satellite" class="craft craft-satellite">
      <svg width="56" height="24" viewBox="0 0 14 6" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="1" width="4" height="4" fill="#3d6fb8" />
        <rect x="1" y="2" width="2" height="2" fill="#5b8fd6" />
        <rect x="4" y="3" width="1" height="1" fill="#9aa1ae" />
        <rect x="5" y="1" width="4" height="4" fill="#d9a441" />
        <rect x="6" y="0" width="1" height="1" fill="#c3ccdb" />
        <rect class="satellite-light" x="7" y="2" width="1" height="1" fill="#ff6a6a" />
        <rect x="9" y="3" width="1" height="1" fill="#9aa1ae" />
        <rect x="10" y="1" width="4" height="4" fill="#3d6fb8" />
        <rect x="11" y="2" width="2" height="2" fill="#5b8fd6" />
      </svg>
    </div>

    <div class="vignette"></div>
  </div>
</template>

<style scoped>
/* Fond spatial partage par l'application et l'ecran de connexion.

   Lisibilite du texte : c'est l'intensite au CENTRE d'une nebuleuse qui compte,
   car c'est le point le plus clair du fond sous une carte. Elle est verifiee a
   0,55 x 0,20 pour la violette ; la bleue et la turquoise sont plus faibles.
   La visibilite, elle, vient de la taille : des nebuleuses plus etendues se
   voient bien mieux sans eclaircir ce point critique. Elles sont placees loin
   les unes des autres pour que leurs centres ne s'additionnent pas. */
.space-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: var(--bg-base);
  overflow: hidden;
  pointer-events: none;
}

.nebula {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.nebula-violet {
  width: 980px;
  height: 820px;
  top: -320px;
  right: -140px;
  background: radial-gradient(circle, rgba(124, 108, 245, 0.55) 0%, transparent 68%);
  opacity: 0.2;
}

.nebula-blue {
  width: 1040px;
  height: 880px;
  bottom: -380px;
  left: -160px;
  background: radial-gradient(circle, rgba(79, 156, 249, 0.42) 0%, transparent 68%);
  opacity: 0.18;
}

.nebula-teal {
  width: 760px;
  height: 640px;
  top: 38%;
  left: 46%;
  background: radial-gradient(circle, rgba(61, 220, 190, 0.3) 0%, transparent 66%);
  opacity: 0.14;
}

/* Trois couches d'etoiles : de petites et nombreuses au loin, de plus grosses
   et plus rares au premier plan, qui scintillent. Ce sont des points : meme
   brillants, ils ne changent pas le contraste du texte. */
.stars {
  position: absolute;
  inset: 0;
  background-repeat: repeat;
}

.stars-far {
  background-image:
    radial-gradient(1px 1px at 20px 30px, rgba(220, 228, 255, 0.55), transparent),
    radial-gradient(1px 1px at 90px 140px, rgba(200, 210, 255, 0.5), transparent),
    radial-gradient(1px 1px at 170px 60px, rgba(220, 228, 255, 0.55), transparent),
    radial-gradient(1px 1px at 240px 190px, rgba(200, 210, 255, 0.45), transparent),
    radial-gradient(1px 1px at 60px 220px, rgba(220, 228, 255, 0.5), transparent),
    radial-gradient(1px 1px at 280px 100px, rgba(210, 200, 255, 0.5), transparent);
  background-size: 300px 250px;
}

.stars-mid {
  background-image:
    radial-gradient(1.6px 1.6px at 70px 90px, rgba(235, 240, 255, 0.75), transparent),
    radial-gradient(1.6px 1.6px at 310px 40px, rgba(200, 190, 255, 0.7), transparent),
    radial-gradient(1.6px 1.6px at 200px 300px, rgba(235, 240, 255, 0.7), transparent),
    radial-gradient(1.6px 1.6px at 400px 210px, rgba(190, 225, 255, 0.7), transparent);
  background-size: 460px 380px;
  animation: twinkle 7s ease-in-out infinite 1s;
}

.stars-near {
  background-image:
    radial-gradient(2.4px 2.4px at 140px 120px, rgba(255, 255, 255, 0.95), transparent),
    radial-gradient(2.4px 2.4px at 520px 380px, rgba(220, 210, 255, 0.9), transparent),
    radial-gradient(2.4px 2.4px at 380px 60px, rgba(210, 235, 255, 0.9), transparent);
  background-size: 680px 560px;
  animation: twinkle 5s ease-in-out infinite;
}

@keyframes twinkle {
  0%,
  100% {
    opacity: 0.55;
  }
  50% {
    opacity: 1;
  }
}

/* ---------- engins spatiaux ----------
   Chaque engin traverse l'ecran pendant une partie de son cycle, puis reste
   invisible le reste du temps. Les cycles et les delais sont decales pour qu'ils
   ne passent jamais ensemble, et le premier part des 2 s.

   Au repos (animations coupees par le reglage systeme ou par le bouton
   « Reduire les animations »), un engin est invisible : opacity 0 est son style
   de base, l'animation seule le fait apparaitre. Un vaisseau fige au milieu de
   l'ecran serait pire que pas de vaisseau du tout.

   Ils passent derriere les cartes, qu'ils traversent grace au verre peu depoli
   (--blur dans base.css) ; le halo de leurs reacteurs les rend reperables meme
   derriere le verre. Seuls transform et opacity sont animes. */
.craft {
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
  will-change: transform, opacity;
}

.craft-rocket {
  filter: drop-shadow(0 0 10px rgba(255, 170, 80, 0.6));
  animation: rocket-pass 20s linear infinite 2s;
}

/* la fusee pointe dans le sens de sa trajectoire (environ 57 degres) */
.rocket {
  display: block;
  transform: rotate(57deg);
}

.rocket-flame {
  transform-box: fill-box;
  transform-origin: top center;
  animation: flame-flicker 0.24s steps(2, jump-none) infinite;
}

@keyframes rocket-pass {
  0% {
    transform: translate(-8vw, 105vh);
    opacity: 0;
  }
  3% {
    opacity: 0.92;
  }
  52% {
    opacity: 0.92;
  }
  55% {
    transform: translate(108vw, -15vh);
    opacity: 0;
  }
  100% {
    transform: translate(108vw, -15vh);
    opacity: 0;
  }
}

@keyframes flame-flicker {
  0% {
    transform: scaleY(1);
  }
  100% {
    transform: scaleY(0.7);
  }
}

.craft-saucer {
  filter: drop-shadow(0 0 12px rgba(124, 255, 196, 0.45));
  animation: saucer-pass 28s linear infinite 8s;
}

/* l'ondulation est portee par le dessin, la traversee par son conteneur :
   les deux mouvements se combinent sans se contrarier */
.saucer {
  display: block;
  animation: saucer-bob 3.2s ease-in-out infinite;
}

.saucer-lights {
  animation: lights-blink 1.1s steps(1, jump-none) infinite;
}

@keyframes saucer-pass {
  0% {
    transform: translate(104vw, 34vh);
    opacity: 0;
  }
  3% {
    opacity: 0.88;
  }
  47% {
    opacity: 0.88;
  }
  50% {
    transform: translate(-12vw, 24vh);
    opacity: 0;
  }
  100% {
    transform: translate(-12vw, 24vh);
    opacity: 0;
  }
}

@keyframes saucer-bob {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes lights-blink {
  0%,
  49% {
    opacity: 1;
  }
  50%,
  100% {
    opacity: 0.3;
  }
}

.craft-shuttle {
  filter: drop-shadow(0 0 8px rgba(255, 176, 92, 0.5));
  animation: shuttle-pass 36s linear infinite 14s;
}

.shuttle-engine {
  animation: lights-blink 0.4s steps(1, jump-none) infinite;
}

@keyframes shuttle-pass {
  0% {
    transform: translate(-6vw, 62vh);
    opacity: 0;
  }
  3% {
    opacity: 0.7;
  }
  52% {
    opacity: 0.7;
  }
  55% {
    transform: translate(106vw, 56vh);
    opacity: 0;
  }
  100% {
    transform: translate(106vw, 56vh);
    opacity: 0;
  }
}

/* ---------- mini-monstres de feu ----------
   Un seul dessin, trois tailles et trois trajets ondules. Les flammes du sommet
   dansent (fill-box : l'animation part de leur propre base), le corps sautille. */
.craft-monster {
  filter: drop-shadow(0 0 10px rgba(255, 140, 58, 0.65));
}

.monster {
  display: block;
  animation: monster-hop 0.9s ease-in-out infinite;
}

.monster-flames {
  transform-box: fill-box;
  transform-origin: bottom center;
  animation: flames-dance 0.36s steps(2, jump-none) infinite;
}

.craft-monster-1 .monster { width: 44px; height: 48px; }
.craft-monster-2 .monster { width: 34px; height: 38px; }
.craft-monster-3 .monster { width: 26px; height: 29px; }

.craft-monster-1 { animation: monster-pass-1 24s linear infinite 5s; }
.craft-monster-2 { animation: monster-pass-2 30s linear infinite 12s; }
.craft-monster-3 { animation: monster-pass-3 34s linear infinite 20s; }

@keyframes monster-pass-1 {
  0% { transform: translate(-6vw, 72vh); opacity: 0; }
  2% { opacity: 0.9; }
  10% { transform: translate(18vw, 64vh); }
  20% { transform: translate(42vw, 74vh); }
  30% { transform: translate(66vw, 62vh); }
  38% { opacity: 0.9; }
  40% { transform: translate(106vw, 70vh); opacity: 0; }
  100% { transform: translate(106vw, 70vh); opacity: 0; }
}

@keyframes monster-pass-2 {
  0% { transform: translate(104vw, 20vh); opacity: 0; }
  2% { opacity: 0.85; }
  12% { transform: translate(78vw, 12vh); }
  24% { transform: translate(52vw, 22vh); }
  36% { transform: translate(26vw, 14vh); }
  43% { opacity: 0.85; }
  45% { transform: translate(-6vw, 20vh); opacity: 0; }
  100% { transform: translate(-6vw, 20vh); opacity: 0; }
}

@keyframes monster-pass-3 {
  0% { transform: translate(-4vw, 48vh); opacity: 0; }
  2% { opacity: 0.8; }
  14% { transform: translate(24vw, 40vh); }
  28% { transform: translate(52vw, 50vh); }
  42% { transform: translate(80vw, 42vh); }
  48% { opacity: 0.8; }
  50% { transform: translate(104vw, 48vh); opacity: 0; }
  100% { transform: translate(104vw, 48vh); opacity: 0; }
}

@keyframes monster-hop {
  0%, 100% { transform: translateY(0) scale(1, 1); }
  50% { transform: translateY(-6px) scale(0.94, 1.06); }
}

@keyframes flames-dance {
  0% { transform: scaleY(1) skewX(0deg); }
  100% { transform: scaleY(1.25) skewX(-8deg); }
}

/* ---------- comete ----------
   Traversee breve et rapide (3 s sur un cycle de 26 s), en diagonale vers le bas. */
.craft-comet {
  animation: comet-pass 26s ease-in infinite 10s;
}

.comet-head {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 0 12px 4px rgba(180, 220, 255, 0.85);
}

.comet-tail {
  position: absolute;
  top: 3px;
  left: 4px;
  width: 160px;
  height: 2px;
  transform-origin: left center;
  transform: rotate(-19deg);
  background: linear-gradient(90deg, rgba(200, 230, 255, 0.9), rgba(200, 230, 255, 0));
}

@keyframes comet-pass {
  0% { transform: translate(100vw, 4vh); opacity: 0; }
  1% { opacity: 1; }
  10% { opacity: 1; }
  12% { transform: translate(30vw, 42vh); opacity: 0; }
  100% { transform: translate(30vw, 42vh); opacity: 0; }
}

/* ---------- astronaute ----------
   Derive lente de droite a gauche, en tournant sur lui-meme. */
.craft-astronaut {
  filter: drop-shadow(0 0 8px rgba(156, 203, 255, 0.4));
  animation: astronaut-pass 48s linear infinite 16s;
}

.astronaut {
  display: block;
  animation: astronaut-spin 12s linear infinite;
}

@keyframes astronaut-pass {
  0% { transform: translate(104vw, 36vh); opacity: 0; }
  2% { opacity: 0.85; }
  48% { opacity: 0.85; }
  50% { transform: translate(-6vw, 44vh); opacity: 0; }
  100% { transform: translate(-6vw, 44vh); opacity: 0; }
}

@keyframes astronaut-spin {
  to { transform: rotate(360deg); }
}

/* ---------- satellite ---------- */
.craft-satellite {
  animation: satellite-pass 42s linear infinite 26s;
}

.satellite-light {
  animation: lights-blink 1.6s steps(1, jump-none) infinite;
}

@keyframes satellite-pass {
  0% { transform: translate(-6vw, 86vh) rotate(-8deg); opacity: 0; }
  2% { opacity: 0.75; }
  53% { opacity: 0.75; }
  55% { transform: translate(106vw, 80vh) rotate(8deg); opacity: 0; }
  100% { transform: translate(106vw, 80vh) rotate(8deg); opacity: 0; }
}

/* la vignette passe devant les engins : ils s'estompent en approchant des bords */
.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 120% 90% at 50% 40%, transparent 50%, rgba(3, 3, 5, 0.6) 100%);
}
</style>
