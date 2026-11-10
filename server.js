// Serveur local (sans dépendance) : sert la carte avec CORS + connexion par mail de l'école.
// Lancer :  node server.js   puis ouvrir http://localhost:5173
const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const PORT = process.env.PORT || 5173;
const ROOT = __dirname;
const DATA = path.join(ROOT, "data");
const DOMAINES = ["ece.fr", "edu.ece.fr"];   // seuls les mails de l'école sont acceptés
const DUREE_SESSION = 8 * 3600 * 1000;       // 8 h

const TYPES = {
  ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".tmj": "application/json; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".png": "image/png", ".css": "text/css; charset=utf-8",
};

// Secret de signature des jetons (créé une fois, gardé dans data/)
const fichierSecret = path.join(DATA, ".secret");
if (!fs.existsSync(fichierSecret)) {
  fs.mkdirSync(DATA, { recursive: true });
  fs.writeFileSync(fichierSecret, crypto.randomBytes(32).toString("hex"));
}
const SECRET = fs.readFileSync(fichierSecret, "utf8").trim();

function comptes() {
  try { return JSON.parse(fs.readFileSync(path.join(DATA, "comptes.json"), "utf8")); }
  catch { return []; }
}

function signer(donnees) {
  const corps = Buffer.from(JSON.stringify(donnees)).toString("base64url");
  const sig = crypto.createHmac("sha256", SECRET).update(corps).digest("base64url");
  return `${corps}.${sig}`;
}

function verifier(jeton) {
  const [corps, sig] = String(jeton || "").split(".");
  if (!corps || !sig) return null;
  const attendu = crypto.createHmac("sha256", SECRET).update(corps).digest("base64url");
  if (sig.length !== attendu.length || !crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(attendu))) return null;
  const d = JSON.parse(Buffer.from(corps, "base64url").toString());
  return d.exp > Date.now() ? d : null;
}

// --- Salles : codes d'accès et cours affiché au tableau -------------------
// Liste des salles produite par tools/generate.py (ex. "eiffel1-amphi")
const SALLES = Object.keys(JSON.parse(fs.readFileSync(path.join(ROOT, "salles.json"), "utf8")));
const fichierCodes = path.join(DATA, "codes-salles.json");
{
  let codes = {};
  try { codes = JSON.parse(fs.readFileSync(fichierCodes, "utf8")); } catch {}
  const nouveaux = Object.fromEntries(SALLES.map((s) => [s, codes[s] || String(crypto.randomInt(1000, 10000))]));
  fs.writeFileSync(fichierCodes, JSON.stringify(nouveaux, null, 2));
}
const lireCodes = () => JSON.parse(fs.readFileSync(fichierCodes, "utf8"));

const DOSSIER_COURS = path.join(ROOT, "cours");
fs.mkdirSync(DOSSIER_COURS, { recursive: true });
const fichierCours = path.join(DATA, "cours.json");
const lireCours = () => { try { return JSON.parse(fs.readFileSync(fichierCours, "utf8")); } catch { return {}; } };
const EXT_COURS = { "application/pdf": ".pdf", "image/png": ".png", "image/jpeg": ".jpg" };

const essais = new Map(); // anti-devinette : nb d'essais de code par IP
function staff(req) {
  const d = verifier(new URL(req.url, "http://x").searchParams.get("jeton"));
  return d && (d.role === "prof" || d.role === "admin") ? d : null;
}
function lireBrut(req, max) {
  return new Promise((ok, ko) => {
    const morceaux = []; let taille = 0;
    req.on("data", (c) => { taille += c.length; if (taille > max) { ko(new Error("trop gros")); req.destroy(); } else morceaux.push(c); });
    req.on("end", () => ok(Buffer.concat(morceaux)));
  });
}

function json(res, code, obj) {
  res.writeHead(code, { "Content-Type": "application/json; charset=utf-8" });
  res.end(JSON.stringify(obj));
}

function lireCorps(req) {
  return new Promise((ok) => {
    let b = "";
    req.on("data", (c) => { b += c; if (b.length > 1e4) req.destroy(); });
    req.on("end", () => { try { ok(JSON.parse(b)); } catch { ok({}); } });
  });
}

http.createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Private-Network", "true");
  if (req.method === "OPTIONS") {
    res.writeHead(204, { "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "GET, POST" });
    return res.end();
  }
  const url = decodeURIComponent(req.url.split("?")[0]);

  // --- API ---------------------------------------------------------------
  if (url === "/api/login" && req.method === "POST") {
    const { email = "", motDePasse = "" } = await lireCorps(req);
    const mail = email.trim().toLowerCase();
    if (!DOMAINES.some((d) => mail.endsWith("@" + d))) {
      return json(res, 400, { erreur: "Utilise ton adresse mail de l'ECE (@ece.fr ou @edu.ece.fr)." });
    }
    const c = comptes().find((x) => x.email === mail);
    const ok = c && crypto.timingSafeEqual(
      Buffer.from(crypto.scryptSync(motDePasse, c.sel, 32).toString("hex")), Buffer.from(c.hash));
    if (!ok) return json(res, 401, { erreur: "Email ou mot de passe incorrect." });
    const profil = { email: c.email, nom: c.nom, role: c.role };
    return json(res, 200, { ...profil, jeton: signer({ ...profil, exp: Date.now() + DUREE_SESSION }) });
  }
  if (url === "/api/verify") {
    const jeton = new URL(req.url, "http://x").searchParams.get("jeton");
    const d = verifier(jeton);
    return d ? json(res, 200, { email: d.email, nom: d.nom, role: d.role }) : json(res, 401, { erreur: "Jeton invalide" });
  }

  // Code d'accès d'une salle (étudiants)
  if (url === "/api/code" && req.method === "POST") {
    const ip = req.socket.remoteAddress;
    const n = (essais.get(ip) || 0) + 1;
    essais.set(ip, n);
    setTimeout(() => essais.set(ip, Math.max(0, (essais.get(ip) || 1) - 1)), 60000);
    if (n > 10) return json(res, 429, { erreur: "Trop d'essais, attends une minute." });
    const { salle, code } = await lireCorps(req);
    const ok = SALLES.includes(salle) && String(code).trim() === lireCodes()[salle];
    return ok ? json(res, 200, { ok: true }) : json(res, 403, { erreur: "Code incorrect." });
  }
  // Liste des codes (profs et administration uniquement)
  if (url === "/api/codes") {
    return staff(req) ? json(res, 200, lireCodes()) : json(res, 403, { erreur: "Réservé aux profs" });
  }
  // Tableau de cours : lecture (tout le monde) / modification (profs et administration)
  const m = url.match(/^\/api\/cours\/([a-z0-9-]+)$/);
  if (m && SALLES.includes(m[1])) {
    const salle = m[1];
    if (req.method === "GET") return json(res, 200, lireCours()[salle] || null);
    const prof = staff(req);
    if (!prof) return json(res, 403, { erreur: "Seuls les profs peuvent modifier le tableau." });
    const tous = lireCours();
    const type = (req.headers["content-type"] || "").split(";")[0];
    if (EXT_COURS[type]) {                      // envoi d'un fichier (PDF ou image)
      let contenu;
      try { contenu = await lireBrut(req, 25 * 1024 * 1024); } catch { return json(res, 413, { erreur: "Fichier trop gros (25 Mo max)." }); }
      const nomFichier = `${salle}-${Date.now()}${EXT_COURS[type]}`;
      fs.writeFileSync(path.join(DOSSIER_COURS, nomFichier), contenu);
      const titre = decodeURIComponent(req.headers["x-titre"] || "Cours");
      tous[salle] = { titre, type: type === "application/pdf" ? "pdf" : "image", url: `/cours/${nomFichier}`, auteur: prof.nom, date: Date.now() };
    } else {                                    // lien, ou effacer le tableau
      const { titre = "Cours", lien, effacer } = await lireCorps(req);
      if (effacer) delete tous[salle];
      else if (/^https?:\/\//.test(lien || "")) tous[salle] = { titre, type: "lien", url: lien, auteur: prof.nom, date: Date.now() };
      else return json(res, 400, { erreur: "Lien invalide (doit commencer par http:// ou https://)." });
    }
    fs.writeFileSync(fichierCours, JSON.stringify(tous, null, 2));
    return json(res, 200, tous[salle] || null);
  }

  // --- Fichiers statiques ------------------------------------------------
  const file = path.normalize(path.join(ROOT, url === "/" ? "index.html" : url));
  const interdit = [DATA, path.join(ROOT, "tools"), path.join(ROOT, ".claude")];
  if (!file.startsWith(ROOT) || interdit.some((d) => file.startsWith(d))) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end("Introuvable"); }
    res.writeHead(200, { "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
    res.end(data);
  });
}).listen(PORT, () => {
  console.log(`Campus ECE : http://localhost:${PORT}`);
});
