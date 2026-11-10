# Campus Eiffel virtuel – ECE / INSEEC (WorkAdventure)

Prototype de campus 2D pour des séances 100 % virtuelles.

## Les cartes
| Carte | Contenu |
|---|---|
| `quartier.tmj` | Point d'arrivée : quai de Seine, rue Sextius Michel, les 4 bâtiments |
| `eiffel1.tmj` | **Eiffel 1 – ECE** (10 rue Sextius Michel) : Amphi Eiffel, TD 1, TD 2, bibliothèque, cafétéria |
| `eiffel2.tmj` | **Eiffel 2 – INSEEC** : Amphi INSEEC, salles 201 et 202, Learning Lab, cafétéria |
| `eiffel3.tmj` | **Eiffel 3 – ECE Labs** : lab informatique, fablab électronique, lab réseaux, salle projets, BDE |
| `eiffel4.tmj` | **Eiffel 4 – ECE · INSEEC** : grand amphi, salle de réunion, TD, scolarité (back-office réservé à l'administration), cafétéria |

⚠️ Seule l'adresse d'Eiffel 1 est réelle. Les noms Eiffel 2 à 4 et **tous les plans intérieurs sont inventés** : les vrais plans ne sont pas publics.
Pour corriger un bâtiment, modifier la liste `BATIMENTS` dans `tools/generate.py` puis relancer le script.
On entre dans un bâtiment par sa porte vitrée et on en ressort par l'allée en bas.

## Contenu
| Fichier | Rôle |
|---|---|
| `tileset.png` | Les tuiles graphiques (générées) |
| `script.js` | Accueil, bannières de salle, bouton « ✋ Lever la main » |
| `infos.html` | Guide affiché par le panneau « i » de l'accueil |
| `tools/generate.py` | Régénère carte + tileset + `apercu.png` |
| `server.js` | Serveur local avec CORS |

## Salles
- **Amphi** : l'estrade est une zone « mégaphone », tout l'amphi entend le prof.
- **TD 1 et 2** : mégaphone au tableau + îlots de groupe (bulles de visio par proximité).
- **Bibliothèque** : zone silencieuse.
- **Accueil** : panneaux interactifs (guide, site de l'ECE).
- **Cafétéria** : discussion libre.

## Tester en local
```bash
node server.js
```
Puis ouvrir http://localhost:5173 et cliquer sur « Entrer sur le campus ».

## Modifier la carte
```bash
python tools/generate.py
```
(ou ouvrir `map.tmj` dans Tiled ; attention, relancer le script écrase les retouches faites dans Tiled).

## Étapes suivantes
1. Héberger la carte en ligne (GitHub Pages ou serveur de l'école).
2. Auto-héberger WorkAdventure avec Docker pour garder les données à l'école (RGPD).
3. Ajouter un bot IA tuteur.

## Connexion et rôles
- Page de connexion : http://localhost:5173 (seuls les mails `@ece.fr` et `@edu.ece.fr` sont acceptés).
- Comptes fictifs de test : `node tools/creer-comptes.js` crée `data/comptes.json` (mots de passe hachés) et `data/comptes-test.md` (identifiants à utiliser). Le dossier `data/` n'est jamais servi par le serveur.
- **Professeur** (contour orange) : seul autorisé sur l'estrade et au tableau, voit les mains levées, bouton 📢 Annonce.
- **Étudiant** (contour bleu) : bouton ✋ Lever la main.
- **Administration** (contour rouge) : 📢 Annonce + 👥 Présents.
- Limite du prototype : la sécurité des rôles est faite côté navigateur. Pour un vrai déploiement, auto-héberger WorkAdventure avec une connexion OpenID (ex. Keycloak ou le compte Microsoft de l'école) et les rôles en « tags ».

## Portes, codes d'accès et tableau
- Chaque salle a une porte et une plaque avec son nom.
- **Amphi, TD 1 et TD 2 sont fermés par un code à 4 chiffres.** Les étudiants le tapent devant la porte ; profs et administration entrent sans code et voient les codes avec le bouton **🔑 Codes**. Les codes sont dans `data/codes-salles.json` (supprimer ce fichier puis relancer le serveur en crée de nouveaux).
- **Tableau de cours** : en entrant dans une salle, le tableau s'ouvre à droite de l'écran. Le prof peut y mettre un PDF, une image ou un lien (Google Slides, Moodle, vidéo…) ; les étudiants le voient apparaître automatiquement.
- Bibliothèque et cafétéria restent en accès libre.

## Installation (après un clone)
Prérequis : Node.js 18+ et Python 3 avec Pillow (`pip install pillow`).
```bash
node tools/creer-comptes.js   # crée les comptes de test fictifs dans data/
node server.js                # puis ouvrir http://localhost:5173
```
Le dossier `data/` (mots de passe, codes des salles, clé de signature) n'est **jamais** publié sur GitHub : il est recréé en local.
