/// <reference types="@workadventure/iframe-api-typings" />
// Script commun à toutes les cartes du Campus Eiffel (quartier + bâtiments).
// Il lit les zones de la carte (propriétés posées par tools/generate.py) :
//   message          bannière affichée en entrant dans la zone
//   reserve          "staff" (profs + admin) ou "admin" ; sortieX/sortieY = où renvoyer les autres
//   codeSalle        porte à code ; sortieX/Y (couloir) et entreeX/Y (dans la salle)
//   tableau          ouvre le tableau de cours de la salle
//   versCarte        passage vers une autre carte (bâtiment <-> quartier)
//   arrivee-<cle>    point d'arrivée quand on vient de la carte <cle>

const ROLES = {
  prof: { libelle: "Professeur", couleur: [230, 126, 34] },
  admin: { libelle: "Administration", couleur: [192, 57, 43] },
  etudiant: { libelle: "Étudiant", couleur: [41, 128, 185] },
  invite: { libelle: "Invité", couleur: null },
};

function banniere(id, texte, duree = 5, fond = "#122652") {
  try {
    WA.ui.banner.openBanner({ id, text: texte, bgColor: fond, textColor: "#ffffff", closable: true, timeToClose: duree * 1000 });
  } catch (e) {
    console.log("[ECE]", texte);
  }
}

const props = (o) => Object.fromEntries((o.properties || []).map((p) => [p.name, p.value]));

WA.onInit().then(async () => {
  const hash = WA.room.hashParameters || {};
  const jeton = hash.jeton || "";
  const origine = new URL(WA.room.mapURL).origin;

  // --- Lecture de la carte -------------------------------------------------
  const carte = await WA.room.getTiledMap();
  const cleCarte = props(carte).cle || "carte";
  const zones = carte.layers
    .filter((l) => l.type === "objectgroup")
    .flatMap((l) => l.objects)
    .map((o) => ({ ...o, p: props(o) }));
  const zone = (nom) => zones.find((z) => z.name === nom);

  // --- Identité ------------------------------------------------------------
  let profil = null;
  if (jeton) {
    try {
      const r = await fetch(`${origine}/api/verify?jeton=${encodeURIComponent(jeton)}`);
      if (r.ok) profil = await r.json();
    } catch (e) { console.error("[ECE] vérification", e); }
  }
  profil = profil || { nom: WA.player.name, role: "invite" };
  const role = ROLES[profil.role] ? profil.role : "invite";
  const estStaff = role === "prof" || role === "admin";

  WA.player.state.saveVariable("role", role, { public: true, persist: false });
  WA.player.state.saveVariable("nomEcole", profil.nom, { public: true, persist: false });
  if (ROLES[role].couleur) {
    try { WA.player.setOutlineColor(...ROLES[role].couleur); } catch (e) { /* ancienne version */ }
  }

  // --- Arrivée depuis une autre carte ---------------------------------------
  const arrivee = hash.depuis && zone(`arrivee-${hash.depuis}`);
  if (arrivee) {
    WA.player.teleport(arrivee.x + arrivee.width / 2, arrivee.y + arrivee.height / 2);
  }
  if (role === "invite") {
    banniere("identite", "⚠️ Non connecté : passe par la page de connexion avec ton mail de l'école.", 15, "#c0392b");
  } else {
    banniere("identite", `${props(carte).mapName || ""} · ${profil.nom} (${ROLES[role].libelle})`, 6);
  }
  if (cleCarte === "quartier" && !hash.depuis && zone("popupAccueil")) {
    WA.ui.openPopup("popupAccueil",
      `Bienvenue sur le Campus Eiffel, ${profil.nom} !\n` +
      "• Eiffel 1 : ECE (amphi, TD, bibliothèque)\n• Eiffel 2 : INSEEC\n" +
      "• Eiffel 3 : labs ECE\n• Eiffel 4 : grand amphi et scolarité\n" +
      "Marche jusqu'à une porte vitrée pour entrer.",
      [{ label: "C'est parti !", className: "primary", callback: (p) => { try { p.close(); } catch (e) {} } }]);
  }

  // --- Passages entre cartes -------------------------------------------------
  const baseSalle = new URL(WA.room.id).pathname.replace(/[^/]+$/, "");
  for (const z of zones.filter((z) => z.p.versCarte)) {
    WA.room.area.onEnter(z.name).subscribe(() => {
      const h = new URLSearchParams({ jeton, depuis: cleCarte }).toString();
      WA.nav.goToRoom(`${baseSalle}${z.p.versCarte}#${h}`);
    });
  }

  // --- Bannières et zones réservées ----------------------------------------
  for (const z of zones.filter((z) => z.p.message || z.p.reserve)) {
    WA.room.area.onEnter(z.name).subscribe(() => {
      const r = z.p.reserve;
      const autorise = !r || (r === "staff" && estStaff) || (r === "admin" && role === "admin");
      if (!autorise) {
        WA.player.teleport(z.p.sortieX * 32, z.p.sortieY * 32);
        banniere("salle", r === "admin" ? "⛔ Réservé à l'administration." : "⛔ Réservé aux professeurs.", 4, "#c0392b");
        return;
      }
      if (z.p.message && !z.p.versCarte) banniere("salle", z.p.message);
    });
  }

  // --- Portes à code ---------------------------------------------------------
  const deverrouillees = new Set();
  const portes = Object.fromEntries(zones.filter((z) => z.p.codeSalle).map((z) => [z.p.codeSalle, z.p]));
  for (const z of zones.filter((z) => z.p.codeSalle)) {
    WA.room.area.onEnter(z.name).subscribe(() => {
      if (estStaff || deverrouillees.has(z.p.codeSalle)) return;
      WA.player.teleport(z.p.sortieX * 32, z.p.sortieY * 32);
      WA.ui.modal.openModal({
        title: "Code d'accès", position: "center", allowApi: true,
        src: `${origine}/code.html?salle=${encodeURIComponent(z.p.codeSalle)}&nom=${encodeURIComponent(z.p.nomSalle)}`,
      });
    });
  }
  WA.player.state.onVariableChange("codeOk").subscribe((v) => {
    const p = v && portes[v.salle];
    if (!p) return;
    deverrouillees.add(v.salle);
    WA.ui.modal.closeModal();
    WA.player.teleport(p.entreeX * 32, p.entreeY * 32);
    banniere("salle", `🔓 Code correct, bienvenue : ${p.nomSalle}`, 4, "#27ae60");
  });

  // --- Tableau de cours --------------------------------------------------------
  let tableau = null;
  for (const z of zones.filter((z) => z.p.tableau)) {
    WA.room.area.onEnter(z.name).subscribe(async () => {
      const url = `${origine}/tableau.html?salle=${encodeURIComponent(z.p.tableau)}&nom=${encodeURIComponent(z.p.nomSalle)}` +
        (estStaff ? `&jeton=${encodeURIComponent(jeton)}` : "");
      try { tableau = await WA.nav.openCoWebSite(url, false, "fullscreen", 55); } catch (e) { console.error("[ECE] tableau", e); }
    });
    WA.room.area.onLeave(z.name).subscribe(() => { if (tableau) { tableau.close(); tableau = null; } });
  }

  // --- Autres joueurs : mains levées, annonces --------------------------------
  await WA.players.configureTracking({ players: true, movement: false });
  const mains = new Map();
  function afficherMains() {
    if (!estStaff) return;
    if (mains.size === 0) { try { WA.ui.banner.closeBanner(); } catch (e) {} return; }
    banniere("mains", `✋ Mains levées : ${[...mains.values()].join(", ")}`, 30, "#e67e22");
  }
  WA.players.onVariableChange("mainLevee").subscribe(({ player, value }) => {
    if (value) mains.set(player.playerId, player.state.nomEcole || player.name); else mains.delete(player.playerId);
    afficherMains();
  });
  WA.players.onPlayerLeaves.subscribe((p) => { mains.delete(p.playerId); afficherMains(); });
  WA.players.onVariableChange("annonce").subscribe(({ player, value }) => {
    const r = player.state.role;
    if (!value || (r !== "prof" && r !== "admin")) return;
    banniere("annonce", `📢 ${player.state.nomEcole || player.name} (${ROLES[r].libelle}) : ${value.texte}`, 20, "#c0392b");
  });

  // --- Boutons selon le rôle -------------------------------------------------------
  if (!estStaff) {
    let levee = false;
    const boutonMain = () => {
      WA.ui.actionBar.removeButton("main");
      WA.ui.actionBar.addButton({
        id: "main", label: levee ? "✋ Baisser la main" : "✋ Lever la main",
        callback: () => {
          levee = !levee;
          WA.player.state.saveVariable("mainLevee", levee, { public: true, persist: false });
          banniere("mamain", levee ? "Ta main est levée, le prof la voit." : "Tu as baissé la main.", 3);
          boutonMain();
        },
      });
    };
    boutonMain();
  } else {
    WA.ui.actionBar.addButton({
      id: "annonce", label: "📢 Annonce",
      callback: () => WA.ui.modal.openModal({ title: "Faire une annonce", position: "center", allowApi: true, src: `${origine}/annonce.html` }),
    });
    WA.player.state.onVariableChange("brouillonAnnonce").subscribe((texte) => {
      if (!texte) return;
      WA.player.state.saveVariable("annonce", { texte, t: Date.now() }, { public: true, persist: false });
      banniere("annonce", `📢 Annonce envoyée : ${texte}`, 6, "#c0392b");
      WA.ui.modal.closeModal();
    });
    if (Object.keys(portes).length) {
      WA.ui.actionBar.addButton({
        id: "codes", label: "🔑 Codes",
        callback: async () => {
          const r = await fetch(`${origine}/api/codes?jeton=${encodeURIComponent(jeton)}`);
          if (!r.ok) return banniere("codes", "Impossible de lire les codes.", 5, "#c0392b");
          const c = await r.json();
          const ici = Object.entries(portes).map(([id, p]) => `${p.nomSalle} ${c[id]}`).join(" · ");
          banniere("codes", `🔑 Codes de ce bâtiment : ${ici}`, 25, "#e67e22");
        },
      });
    }
  }
  if (role === "admin") {
    WA.ui.actionBar.addButton({
      id: "presents", label: "👥 Présents",
      callback: () => {
        const liste = [...WA.players.list()].map((p) => `${p.state.nomEcole || p.name} (${(ROLES[p.state.role] || ROLES.invite).libelle})`);
        banniere("presents", `👥 ${liste.length + 1} présent(s) ici : toi, ${liste.join(", ") || "personne d'autre"}`, 20);
      },
    });
  }
}).catch((e) => console.error("[ECE] Erreur du script", e));
