// Crée des comptes FICTIFS de test (prof, étudiant, administration).
// Usage : node tools/creer-comptes.js
// Écrit data/comptes.json (mots de passe hachés) et data/comptes-test.md (identifiants en clair, pour tester).
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const DATA = path.join(__dirname, "..", "data");
fs.mkdirSync(DATA, { recursive: true });

// Personnes fictives. Domaines : @ece.fr pour le personnel, @edu.ece.fr pour les étudiants.
const PERSONNES = [
  { nom: "Claire Martin", email: "claire.martin@ece.fr", role: "prof" },
  { nom: "Karim Benali", email: "karim.benali@ece.fr", role: "prof" },
  { nom: "Sophie Durand", email: "sophie.durand@ece.fr", role: "admin" },
  { nom: "Lucas Petit", email: "lucas.petit@edu.ece.fr", role: "etudiant" },
  { nom: "Inès Moreau", email: "ines.moreau@edu.ece.fr", role: "etudiant" },
  { nom: "Yanis Lefèvre", email: "yanis.lefevre@edu.ece.fr", role: "etudiant" },
  { nom: "Emma Garcia", email: "emma.garcia@edu.ece.fr", role: "etudiant" },
];

const ROLES = { prof: "Professeur", etudiant: "Étudiant", admin: "Administration" };

function motDePasse() {
  return crypto.randomBytes(6).toString("base64url"); // 8 caractères aléatoires
}

const comptes = [];
let md = "# Comptes de test (fictifs)\n\nÀ utiliser uniquement en local. Relancer `node tools/creer-comptes.js` régénère de nouveaux mots de passe.\n\n| Rôle | Nom | Email | Mot de passe |\n|---|---|---|---|\n";
for (const p of PERSONNES) {
  const mdp = motDePasse();
  const sel = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(mdp, sel, 32).toString("hex");
  comptes.push({ ...p, sel, hash });
  md += `| ${ROLES[p.role]} | ${p.nom} | ${p.email} | \`${mdp}\` |\n`;
}

fs.writeFileSync(path.join(DATA, "comptes.json"), JSON.stringify(comptes, null, 2));
fs.writeFileSync(path.join(DATA, "comptes-test.md"), md);
console.log(`${comptes.length} comptes créés. Identifiants : data/comptes-test.md`);
