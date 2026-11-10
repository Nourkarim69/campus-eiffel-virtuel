"""Génère le dossier de présentation PDF du Campus Eiffel virtuel.
Usage : python tools/dossier_pdf.py   ->  Dossier-Campus-Eiffel-virtuel.pdf
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parent.parent
SORTIE = ROOT / "Dossier-Campus-Eiffel-virtuel.pdf"

pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", "C:/Windows/Fonts/ariali.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic", boldItalic="Arial-Bold")

NAVY = colors.HexColor("#122652")
CYAN = colors.HexColor("#00AAC8")
GRIS = colors.HexColor("#5B6475")
FOND = colors.HexColor("#F2F5FA")
LIGNE = colors.HexColor("#D5DBE6")
ROUGE = colors.HexColor("#C41E3A")

S = {
    "titre": ParagraphStyle("titre", fontName="Arial-Bold", fontSize=30, leading=36, textColor=NAVY, alignment=TA_CENTER),
    "soustitre": ParagraphStyle("soustitre", fontName="Arial", fontSize=14, leading=20, textColor=GRIS, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=19, leading=24, textColor=NAVY, spaceBefore=4, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=13, leading=17, textColor=NAVY, spaceBefore=10, spaceAfter=5),
    "p": ParagraphStyle("p", fontName="Arial", fontSize=10, leading=14.5, textColor=colors.black, spaceAfter=6),
    "puce": ParagraphStyle("puce", fontName="Arial", fontSize=10, leading=14, leftIndent=12, bulletIndent=2, spaceAfter=3),
    "note": ParagraphStyle("note", fontName="Arial-Italic", fontSize=8.5, leading=11.5, textColor=GRIS, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontName="Arial", fontSize=8.8, leading=11.5),
    "cellb": ParagraphStyle("cellb", fontName="Arial-Bold", fontSize=8.8, leading=11.5, textColor=colors.white),
    "legende": ParagraphStyle("legende", fontName="Arial-Italic", fontSize=8.5, leading=11, textColor=GRIS, alignment=TA_CENTER, spaceAfter=8),
    "encadre": ParagraphStyle("encadre", fontName="Arial", fontSize=10, leading=14, textColor=NAVY),
}


def lien(url, texte=None):
    return f'<a href="{url}" color="#00AAC8"><u>{texte or url}</u></a>'


def P(t, s="p"):
    return Paragraph(t, S[s])


def puces(items):
    return [Paragraph(i, S["puce"], bulletText="•") for i in items]


def tableau(entetes, lignes, largeurs):
    data = [[Paragraph(h, S["cellb"]) for h in entetes]] + [[Paragraph(str(c), S["cell"]) for c in l] for l in lignes]
    t = Table(data, colWidths=largeurs, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FOND]),
        ("GRID", (0, 0), (-1, -1), 0.4, LIGNE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def encadre(texte, couleur=CYAN):
    t = Table([[Paragraph(texte, S["encadre"])]], colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FOND), ("LINEBEFORE", (0, 0), (0, -1), 4, couleur),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def image(fichier, largeur_mm, legende):
    chemin = ROOT / fichier
    from PIL import Image as PILImage
    w, h = PILImage.open(chemin).size
    lw = largeur_mm * mm
    return KeepTogether([Image(str(chemin), width=lw, height=lw * h / w), Spacer(1, 3), P(legende, "legende")])


def pied(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setStrokeColor(LIGNE); canvas.line(20 * mm, 15 * mm, 190 * mm, 15 * mm)
        canvas.setFont("Arial", 8); canvas.setFillColor(GRIS)
        canvas.drawString(20 * mm, 10 * mm, "Campus Eiffel virtuel · ECE / INSEEC · Dossier de présentation")
        canvas.drawRightString(190 * mm, 10 * mm, f"Page {doc.page}")
        canvas.setFillColor(CYAN); canvas.rect(0, 287 * mm, 210 * mm, 10 * mm, stroke=0, fill=1)
    else:
        canvas.setFillColor(NAVY); canvas.rect(0, 0, 210 * mm, 70 * mm, stroke=0, fill=1)
        canvas.setFillColor(CYAN); canvas.rect(0, 70 * mm, 210 * mm, 3 * mm, stroke=0, fill=1)
    canvas.restoreState()


def contenu():
    st = []
    # ------------------------------------------------------------ couverture
    st += [Spacer(1, 30 * mm), P("Campus Eiffel virtuel", "titre"), Spacer(1, 4 * mm),
           P("Un campus 2D pour des séances 100 % virtuelles à l'ECE et à l'INSEEC", "soustitre"), Spacer(1, 3 * mm),
           P("Dossier de présentation du prototype · options 3D et réalité virtuelle · exemples · coûts", "soustitre"),
           Spacer(1, 10 * mm), image("apercu-quartier.png", 150, "Le quartier du Campus Eiffel virtuel (point d'arrivée des étudiants)"),
           Spacer(1, 6 * mm),
           Paragraph("Version prototype – 10 novembre 2026",
                     ParagraphStyle("couv", parent=S["soustitre"], textColor=colors.white, fontName="Arial-Bold")),
           PageBreak()]

    # ------------------------------------------------------------ résumé
    st += [P("1. En résumé", "h1"),
           P("L'objectif est de permettre à l'école d'organiser des <b>séances entièrement à distance</b> qui ressemblent à "
             "une vraie journée sur le campus : on arrive dans le quartier, on entre dans un bâtiment, on rejoint sa salle, "
             "on écoute le prof, puis on travaille en petit groupe, avant de passer à la cafétéria."),
           P("Un <b>prototype fonctionnel</b> a été construit sur <b>WorkAdventure</b>, une plateforme française et open source "
             "qui tourne dans le navigateur. Il comprend :"),
           *puces([
               "un quartier « Campus Eiffel » et <b>4 bâtiments</b> (Eiffel 1 à 4, ECE et INSEEC) avec 20 salles ;",
               "une <b>connexion avec le mail de l'école</b> et trois rôles : professeur, étudiant, administration ;",
               "des <b>salles fermées par un code</b> que seul le prof communique ;",
               "un <b>tableau de cours</b> où le prof affiche un PDF, une image ou un lien, visible de toute la salle ;",
               "la <b>visio intégrée</b> : le prof au tableau est entendu par toute la salle, les étudiants se parlent en s'approchant ;",
               "les outils de classe : <b>lever la main</b>, <b>annonces</b>, <b>liste des présents</b>, zone silencieuse.",
           ]),
           Spacer(1, 4),
           encadre("<b>Recommandation :</b> démarrer avec ce campus 2D (coût très faible, aucun casque, marche sur tout ordinateur), "
                   "le tester sur quelques cours, puis ajouter une salle 3D ou VR seulement pour les usages où elle apporte un vrai plus "
                   "(journées portes ouvertes, travaux pratiques immersifs). Le détail est en partie 7."),
           Spacer(1, 6),
           P("Sommaire", "h2"),
           *puces(["2. Le prototype et son fonctionnement", "3. Les bâtiments et les salles", "4. Les fonctionnalités",
                   "5. Guide de test", "6. Limites et passage en production", "7. Aller plus loin : la 3D et la réalité virtuelle",
                   "8. Des écoles qui l'ont fait", "9. Les coûts", "10. Feuille de route proposée", "11. Liens et sources"]),
           PageBreak()]

    # ------------------------------------------------------------ prototype
    st += [P("2. Le prototype et son fonctionnement", "h1"),
           P("Le campus utilise <b>WorkAdventure</b> : chaque personne est un petit personnage en pixels qui se déplace sur une "
             "carte vue de dessus. Quand deux personnages se rapprochent, une visio démarre automatiquement entre eux. "
             "Tout se passe dans le navigateur (ordinateur, tablette ou téléphone), sans installation."),
           P("Les éléments du projet", "h2"),
           tableau(["Élément", "Rôle"], [
               ["Cartes du campus (format Tiled)", "Le quartier et les 4 bâtiments, générés automatiquement par un script Python et modifiables avec le logiciel gratuit Tiled."],
               ["Script du campus (JavaScript)", "Gère les rôles, les portes à code, le tableau, la main levée, les annonces et les passages entre bâtiments."],
               ["Serveur de l'école (Node.js)", "Vérifie les connexions, garde les comptes (mots de passe chiffrés), les codes des salles et les cours déposés."],
               ["Page de connexion", "L'étudiant ou le prof se connecte avec son mail de l'école, teste son micro et sa caméra, puis entre sur le campus."],
               ["Pages intégrées", "Saisie du code d'une salle, tableau de cours, formulaire d'annonce, guide du campus, page des codes pour le personnel."],
           ], [52 * mm, 118 * mm]),
           Spacer(1, 8),
           P("Le parcours d'un étudiant", "h2"),
           *puces([
               "Il ouvre la page du campus et se connecte avec son adresse <b>@edu.ece.fr</b> (le personnel utilise <b>@ece.fr</b>).",
               "Il arrive dans le <b>quartier</b>, au bord de la Seine, et marche jusqu'à la porte vitrée de son bâtiment.",
               "Devant sa salle, il tape le <b>code donné par le prof</b>. Le tableau du cours s'ouvre à droite de l'écran.",
               "Le prof parle depuis l'estrade : toute la salle l'entend et le voit. Pour les travaux en groupe, chaque îlot de tables "
               "devient une petite visio.",
               "À la pause, il rejoint la cafétéria ou la bibliothèque (zone silencieuse), puis ressort par l'allée pour revenir au quartier.",
           ]),
           PageBreak()]

    # ------------------------------------------------------------ bâtiments
    st += [P("3. Les bâtiments et les salles", "h1"),
           encadre("Seule l'adresse d'Eiffel 1 (10 rue Sextius Michel, Paris 15e) est réelle. Les noms Eiffel 2 à 4 et "
                   "<b>tous les plans intérieurs sont inventés</b>, car les vrais plans ne sont pas publics. Ils se corrigent "
                   "facilement dans le script de génération (liste des bâtiments et type de chaque salle).", ROUGE),
           Spacer(1, 8),
           tableau(["Bâtiment", "Salles à code (avec tableau)", "Espaces libres"], [
               ["<b>Eiffel 1 – ECE</b>", "Amphi Eiffel, TD 1, TD 2", "Bibliothèque (silencieuse), cafétéria"],
               ["<b>Eiffel 2 – INSEEC</b>", "Amphi INSEEC, salle 201, salle 202", "Learning Lab, cafétéria"],
               ["<b>Eiffel 3 – ECE Labs</b>", "Lab informatique, fablab électronique, lab réseaux", "Salle projets, espace BDE"],
               ["<b>Eiffel 4 – ECE · INSEEC</b>", "Grand amphi, salle de réunion, salle de TD", "Scolarité (guichet ; back-office réservé à l'administration), cafétéria"],
           ], [40 * mm, 70 * mm, 60 * mm]),
           Spacer(1, 6),
           P("Au total : 12 salles à code et à tableau, 8 espaces en accès libre, plus le hall d'accueil de chaque bâtiment."),
           image("apercu-eiffel1.png", 150, "Eiffel 1 – ECE : TD 1, amphi, TD 2, bibliothèque, accueil, cafétéria"),
           PageBreak(),
           image("apercu-eiffel2.png", 135, "Eiffel 2 – INSEEC : salles 201 et 202, amphi, Learning Lab, cafétéria"),
           image("apercu-eiffel3.png", 135, "Eiffel 3 – ECE Labs : lab informatique, fablab, lab réseaux, salle projets, BDE"),
           PageBreak(),
           image("apercu-eiffel4.png", 135, "Eiffel 4 – ECE · INSEEC : salle de réunion, grand amphi, TD, scolarité, cafétéria"),
           PageBreak()]

    # ------------------------------------------------------------ fonctionnalités
    st += [P("4. Les fonctionnalités", "h1"),
           P("4.1 Connexion et rôles", "h2"),
           P("Seules les adresses de l'école sont acceptées. Les mots de passe sont stockés chiffrés et la connexion produit "
             "un jeton signé, valable 8 heures, qui suit la personne d'un bâtiment à l'autre."),
           tableau(["Rôle", "Repère visuel", "Ce qu'il peut faire"], [
               ["Professeur", "Contour orange", "Monter sur l'estrade et au tableau, entrer dans toutes les salles sans code, voir les codes, "
                "mettre un cours au tableau, voir les mains levées, faire des annonces."],
               ["Étudiant", "Contour bleu", "Entrer dans une salle avec son code, suivre le cours, travailler en groupe, lever la main. "
                "Il est renvoyé dans la salle s'il essaie de monter sur l'estrade."],
               ["Administration", "Contour rouge", "Mêmes droits que le prof, plus l'accès au back-office de la scolarité et la liste des personnes présentes."],
           ], [30 * mm, 30 * mm, 110 * mm]),
           P("4.2 Portes et codes d'accès", "h2"),
           *puces([
               "Chaque salle a une porte et une plaque avec son nom. Les amphis, salles de cours et labs sont fermés par un <b>code à 4 chiffres</b>.",
               "Devant la porte, l'étudiant est renvoyé dans le couloir et une fenêtre lui demande le code. S'il est bon, il entre directement.",
               "Le personnel voit les codes avec le bouton <b>Codes</b> dans le jeu, ou sur une page web imprimable réservée.",
               "Au-delà de 10 essais faux en une minute, le serveur bloque les tentatives.",
           ]),
           P("4.3 Tableau de cours", "h2"),
           *puces([
               "En entrant dans une salle, le tableau s'ouvre à droite de l'écran.",
               "Le prof y dépose un <b>PDF</b>, une <b>image</b> ou un <b>lien</b> (Google Slides, Moodle, vidéo...), avec un titre. Il peut l'effacer.",
               "Les étudiants voient le nouveau cours apparaître en quelques secondes, sans recharger. Ils ne peuvent pas le modifier.",
           ]),
           P("4.4 Caméras, micro et visio", "h2"),
           *puces([
               "<b>Bulles de proximité</b> : en approchant son personnage d'un autre, une visio démarre (jusqu'à 4 personnes par bulle). "
               "Idéal pour les îlots de travaux dirigés.",
               "<b>Mode conférence</b> : le prof sur l'estrade ou au tableau est vu et entendu par toute la salle.",
               "<b>Zone silencieuse</b> dans la bibliothèque : micro et caméra y sont coupés.",
               "Les vidéos s'affichent en haut de l'écran ; un clic agrandit une vidéo. Le partage d'écran est disponible.",
           ]),
           P("4.5 Outils de classe et de vie du campus", "h2"),
           *puces([
               "<b>Lever la main</b> : un bouton pour les étudiants ; les profs voient la liste des mains levées.",
               "<b>Annonces</b> : profs et administration envoient un message affiché chez tout le monde.",
               "<b>Présents</b> : l'administration voit qui est connecté et avec quel rôle.",
               "<b>Accueil</b> : message de bienvenue, panneaux interactifs (guide du campus, site de l'école), bannière à l'entrée de chaque salle.",
           ]),
           PageBreak()]

    # ------------------------------------------------------------ guide
    st += [P("5. Guide de test", "h1"),
           P("Le prototype tourne sur un ordinateur, avec Node.js et Python installés."),
           tableau(["Étape", "Action"], [
               ["1. Lancer le serveur", "Dans le dossier du projet : <b>node server.js</b>"],
               ["2. Ouvrir la page", "Dans Chrome ou Edge : <b>http://localhost:5173</b>"],
               ["3. Se connecter", "Avec un compte de test (liste dans data/comptes-test.md). Comptes fictifs : 2 profs, 1 administration, 4 étudiants."],
               ["4. Tester micro et caméra", "Bouton « Tester mon micro et ma caméra », puis « Autoriser » dans le navigateur."],
               ["5. Entrer sur le campus", "Bouton « Entrer sur le campus ». WorkAdventure demande un pseudo et ses conditions d'utilisation."],
               ["6. Tester à plusieurs", "Une fenêtre normale avec un prof, une fenêtre privée (Ctrl + Maj + N) avec un étudiant."],
           ], [45 * mm, 125 * mm]),
           P("Comptes de test (fictifs)", "h2"),
           tableau(["Rôle", "Adresse"], [
               ["Professeur", "claire.martin@ece.fr · karim.benali@ece.fr"],
               ["Administration", "sophie.durand@ece.fr"],
               ["Étudiant", "lucas.petit@edu.ece.fr · ines.moreau@edu.ece.fr · yanis.lefevre@edu.ece.fr · emma.garcia@edu.ece.fr"],
           ], [35 * mm, 135 * mm]),
           P("Les mots de passe et les codes des salles ne sont volontairement pas imprimés dans ce dossier. Ils sont dans "
             "data/comptes-test.md et data/codes-salles.json, et sur la page « Codes des salles » réservée au personnel.", "note"),
           P("Si la caméra ne s'allume pas", "h2"),
           *puces([
               "Erreur « NotReadableError » : la webcam est désactivée dans Windows. La réactiver dans Paramètres, puis Bluetooth et appareils, "
               "puis Appareils photo, ou dans le Gestionnaire de périphériques. Vérifier aussi la touche caméra du clavier.",
               "Autoriser la caméra et le micro dans Paramètres, puis Confidentialité et sécurité, y compris pour les « applications de bureau ».",
               "Utiliser Chrome ou Edge et cliquer sur « Autoriser » quand le site le demande. Fermer Teams, Zoom ou Discord, qui peuvent bloquer la caméra.",
           ]),
           PageBreak()]

    # ------------------------------------------------------------ limites
    st += [P("6. Limites et passage en production", "h1"),
           P("Le prototype sert à démontrer l'idée. Avant de l'utiliser en vrai avec des centaines d'étudiants, quatre chantiers sont nécessaires."),
           tableau(["Limite actuelle", "Ce qu'il faut faire"], [
               ["Le campus tourne sur un seul ordinateur : personne d'autre ne peut s'y connecter.",
                "Héberger la carte et le serveur sur un serveur de l'école ou chez un hébergeur, avec une adresse en https."],
               ["Les rôles sont contrôlés en partie dans le navigateur : un utilisateur très technique pourrait les contourner.",
                "Auto-héberger WorkAdventure (Docker) et brancher la connexion sur le compte Microsoft ou l'annuaire de l'école (OpenID Connect), avec les rôles transmis par l'école."],
               ["La visio passe par les serveurs publics de WorkAdventure.",
                "Avec l'auto-hébergement, les données restent à l'école (RGPD). Prévoir un serveur vidéo dimensionné pour les grands amphis."],
               ["Les plans intérieurs sont inventés.",
                "Récupérer les plans réels (plans d'évacuation par étage) et adapter les cartes."],
           ], [75 * mm, 95 * mm]),
           Spacer(1, 6),
           encadre("<b>Le vrai défi n'est pas technique</b> : il faut que les professeurs s'en servent. Prévoir une courte formation, "
                   "une personne référente à l'école, et commencer par 2 ou 3 cours volontaires."),
           PageBreak()]

    # ------------------------------------------------------------ 3D / VR
    st += [P("7. Aller plus loin : la 3D et la réalité virtuelle", "h1"),
           P("Le campus 2D est le plus simple à utiliser au quotidien. La 3D et la réalité virtuelle (VR) apportent plus "
             "d'immersion, mais coûtent plus cher, fatiguent davantage et demandent du matériel. Voici les options réalistes, "
             "de la plus simple à la plus ambitieuse."),
           tableau(["Option", "Ce que c'est", "Matériel", "Points forts / points faibles"], [
               ["<b>A. Campus 2D (ce prototype)</b>", "WorkAdventure dans le navigateur", "Un ordinateur ou un téléphone",
                "Peu cher, peu fatigant, marche partout. / Moins spectaculaire."],
               ["<b>B. Salle 3D web : Hubs Community Edition</b>", "Monde 3D open source dans le navigateur, compatible casques VR",
                "PC ; casque en option", "Gratuit et modifiable, données à l'école. / Hébergement lourd (Kubernetes), demande des développeurs expérimentés."],
               ["<b>C. Plateforme 3D louée</b> (VictoryXR, ENGAGE, Virbela...)", "Campus 3D prêt à l'emploi, sous licence",
                "PC et/ou casques", "Rapide à lancer, accompagnement. / Peu personnalisable, éditeur souvent américain, coût par étudiant."],
               ["<b>D. Campus 3D sur mesure avec un studio</b>", "Modèle de NEOMA (avec Laval Virtual)", "PC ; casque en option",
                "Image très innovante. / Budget élevé, dépendance au prestataire."],
               ["<b>E. Jumeau numérique en VR</b>", "Copie fidèle des vrais bâtiments, à visiter au casque", "Casques VR",
                "Très fort pour la communication. / Le plus cher, gain pédagogique peu démontré."],
           ], [38 * mm, 42 * mm, 28 * mm, 62 * mm]),
           P("Bon à savoir avant de choisir la VR", "h2"),
           *puces([
               "Les séances au casque doivent rester <b>courtes</b> : Stanford limitait les siennes à 30 minutes pour éviter le mal des transports virtuel.",
               "Il faut un <b>casque par étudiant</b> (ou une salle équipée) et une organisation pour les prêter, les charger et les nettoyer.",
               "La 3D peut être <b>combinée</b> au campus 2D : les cours restent en 2D, et un lien ouvre une salle 3D pour un TP ou une visite.",
           ]),
           PageBreak()]

    # ------------------------------------------------------------ exemples
    st += [P("8. Des écoles qui l'ont fait", "h1"),
           tableau(["École", "Ce qu'elle a fait", "Résultats publiés", "Lien"], [
               ["<b>NEOMA Business School</b> (France)",
                "Campus 100 % virtuel ouvert en septembre 2020 avec Laval Virtual, présenté comme son 4e campus. Les étudiants y suivent "
                "des cours et des conférences avec un avatar piloté au clavier et à la souris.",
                "Médaille d'or catégorie Éducation aux Laval Virtual Awards (juillet 2021). L'école garde 60 % de cours en présentiel.",
                lien("https://neoma-bs.com/news/neoma-business-school-opens-first-virtual-campus-europe", "neoma-bs.com")],
               ["<b>Université de Rennes et Rennes 2</b> (France)",
                "Campus WorkAdventure qui reproduit des bâtiments réels ; utilisé pour l'accueil, les portes ouvertes et des escape games pédagogiques.",
                "Selon l'éditeur : jusqu'à 450 utilisateurs simultanés et 70 cartes. Chiffres non vérifiés de façon indépendante.",
                lien("https://workadventu.re/customer-stories/digital-campus-university-rennes-gather-workadventure/", "workadventu.re")],
               ["<b>Stanford University</b> (États-Unis)",
                "Cours « Virtual People » donné presque entièrement en VR en 2021 : un casque prêté à chaque étudiant, plateforme ENGAGE.",
                "Plusieurs centaines d'étudiants ; séances de 30 minutes ; plus de 3 000 heures de données collectées pour la recherche.",
                lien("https://news.stanford.edu/stories/2021/11/new-class-among-first-taught-entirely-virtual-reality", "news.stanford.edu")],
               ["<b>Morehouse College</b> (États-Unis)",
                "« Metaversity » avec VictoryXR : jumeau numérique du campus et cours en VR, financés par des subventions (Meta, Qualcomm, T-Mobile).",
                "Selon l'éditeur, sur un cours d'histoire : note moyenne de 85 % en VR contre 78 % en présentiel et 81 % en ligne. "
                "Passé de 3 à 13 cours par semestre.",
                lien("https://www.insidehighered.com/node/119286", "insidehighered.com")],
               ["<b>IÉSEG</b> (France)",
                "Pas de campus virtuel, mais des avatars de professeurs dopés à l'IA (start-up Compleducation, investissement de 500 000 euros en 2026).",
                "Accès élargi au Programme Grande École ; déploiement prévu pour plus de 5 000 étudiants.",
                lien("https://lexpress-education.com/actualites/ieseg-investit-compleducation/", "lexpress-education.com")],
           ], [32 * mm, 52 * mm, 56 * mm, 30 * mm]),
           Spacer(1, 6),
           P("Les résultats de Morehouse et de Rennes sont publiés par les éditeurs des plateformes : ce sont des indications "
             "intéressantes, pas des études indépendantes.", "note"),
           P("Ce qu'il faut en retenir", "h2"),
           *puces([
               "Les projets qui marchent sont <b>accompagnés</b> : équipe support, formation des profs, usage ciblé.",
               "Le virtuel <b>complète</b> le présentiel plutôt que de le remplacer (cas de NEOMA).",
               "La VR complète est surtout utilisée pour des <b>cours ciblés</b> et souvent <b>financée par des subventions</b> (cas de Morehouse).",
           ]),
           PageBreak()]

    # ------------------------------------------------------------ coûts
    st += [P("9. Les coûts", "h1"),
           P("Les prix ci-dessous viennent des sources citées ou sont des estimations (signalées). Seuls des devis donneraient des montants fermes."),
           tableau(["Poste", "Montant", "Source / remarque"], [
               ["Campus 2D auto-hébergé (ce prototype)", "Logiciel gratuit ; serveur estimé à 100–500 € par mois", "Estimation, selon le nombre d'utilisateurs simultanés"],
               ["WorkAdventure hébergé par l'éditeur", "Gratuit jusqu'à 15 utilisateurs ; événements dès 2 € par utilisateur et par jour ; bureau dès 5 € par utilisateur et par mois",
                "Page tarifs officielle ; devis pour un grand nombre d'utilisateurs"],
               ["Salle 3D Hubs Community Edition", "Logiciel gratuit ; serveurs estimés à 300–1 500 € par mois", "Estimation ; demande des compétences Kubernetes"],
               ["Licence VictoryXR", "Au moins 20 000 $, jusqu'à 100 000 $ pour un jumeau numérique ; environ 200 $ par étudiant et par an",
                "Presse 2022–2023 ; à revérifier"],
               ["Jumeau numérique de campus", "À partir d'environ 50 000 $", "Chiffre cité pour Morehouse (2023)"],
               ["Campus 3D sur mesure avec un studio", "100 000 à 300 000 € au départ ; 20 000 à 50 000 € par an", "Estimation ; à confirmer par devis"],
               ["Casque VR Meta Quest 3S", "Environ 330 € à sa sortie (octobre 2024) ; des hausses de prix sont annoncées en 2026", "Presse française ; tarif éducation à demander"],
           ], [48 * mm, 62 * mm, 60 * mm]),
           P("Exemple de calcul", "h2"),
           tableau(["Scénario pour 300 étudiants", "Première année (ordre de grandeur)"], [
               ["Campus 2D auto-hébergé", "Environ 1 200 à 6 000 € de serveur, plus du temps de développement (projet étudiant)"],
               ["Campus 2D + une salle 3D Hubs", "Environ 5 000 à 25 000 € de serveurs et de mise en place"],
               ["Classe VR équipée de 30 casques", "Environ 10 000 € de casques, plus la licence de la plateforme"],
               ["Tout le monde en VR (300 casques)", "Environ 100 000 € de casques seuls, plus licences (environ 60 000 $ par an à 200 $ par étudiant)"],
           ], [70 * mm, 100 * mm]),
           P("Calculs indicatifs à partir des montants ci-dessus ; hors salaires, formation et support.", "note"),
           PageBreak()]

    # ------------------------------------------------------------ feuille de route
    st += [P("10. Feuille de route proposée", "h1"),
           tableau(["Période", "Objectif", "Livrable"], [
               ["Mois 1 à 2", "Valider le prototype 2D avec 2 ou 3 professeurs volontaires", "Retours des profs et des étudiants, liste d'améliorations"],
               ["Mois 2 à 4", "Mettre en ligne : hébergement à l'école, connexion avec le compte Microsoft de l'école, plans réels des bâtiments",
                "Campus accessible à tous les étudiants concernés"],
               ["Mois 3 à 6", "Tester la 3D : une salle Hubs ou un pilote VictoryXR pour un TP ou une journée portes ouvertes",
                "Mesure de l'intérêt réel pour la 3D et la VR"],
               ["Mois 6 à 12", "Décider : renforcer la solution maison, ou passer par un studio pour un campus 3D ; ajouter un tuteur IA",
                "Décision budgétée pour l'année suivante"],
           ], [28 * mm, 82 * mm, 60 * mm]),
           Spacer(1, 8),
           encadre("<b>Budget de la première année :</b> de l'ordre de 10 000 à 30 000 € en commençant par le 2D puis un test 3D, "
                   "contre plusieurs centaines de milliers d'euros si l'on démarre directement par un campus 3D sur mesure ou par la VR pour tous."),
           PageBreak()]

    # ------------------------------------------------------------ sources
    sources = [
        ("Campus en ligne et plateformes", [
            ("WorkAdventure – tarifs", "https://workadventu.re/pricing"),
            ("WorkAdventure – Université Rennes 2", "https://workadventu.re/universite-de-rennes-2/"),
            ("WorkAdventure – campus numérique de l'Université de Rennes", "https://workadventu.re/customer-stories/digital-campus-university-rennes-gather-workadventure/"),
            ("Mozilla – avenir de Hubs (arrêt le 31 mai 2024)", "https://hubs.mozilla.com/labs/sunset"),
            ("Ryan Schultz – Hubs Community Edition", "https://ryanschultz.com/category/mozilla-hubs/"),
            ("VictoryXR – Metaversity", "https://www.victoryxr.com/metaversity/"),
        ]),
        ("Écoles et universités", [
            ("NEOMA – ouverture du premier campus virtuel en Europe", "https://neoma-bs.com/news/neoma-business-school-opens-first-virtual-campus-europe"),
            ("NEOMA – distinction aux Laval Virtual Awards", "https://neoma-bs.com/news/neomas-virtual-campus-stands-out-laval-virtual-awards"),
            ("AACSB – Virtual Campus, Real Learning (NEOMA)", "https://aacsb.edu/insights/2021/july/virtual-campus-real-learning"),
            ("Stanford News – un cours entièrement en VR", "https://news.stanford.edu/stories/2021/11/new-class-among-first-taught-entirely-virtual-reality"),
            ("Stanford Daily – premier cours entièrement en VR", "https://stanforddaily.com/2021/12/01/stanford-launches-first-class-taught-completely-in-virtual-reality/"),
            ("VictoryXR – résultats de Morehouse", "https://www.victoryxr.com/?p=35999"),
            ("Inside Higher Ed – Morehouse et le métavers", "https://www.insidehighered.com/node/119286"),
            ("CNN via KTVZ – la metaversity, campus du futur ?", "https://ktvz.com/news/national-world/cnn-world/2023/06/27/could-the-metaversity-be-the-college-campus-of-the-future/"),
            ("Technical.ly – les défis de l'université dans le métavers", "https://technical.ly/software-development/challenges-doing-college-in-metaverse/"),
            ("L'Express Éducation – l'IÉSEG investit dans Compleducation", "https://lexpress-education.com/actualites/ieseg-investit-compleducation/"),
            ("ECE – campus de Paris (Eiffel)", "https://ece.fr/?p=9881"),
        ]),
        ("Matériel", [
            ("WatchGeneration – Meta Quest 3S disponible à 330 €", "https://www.watchgeneration.fr/realite-virtuelle/2024/10/le-meta-quest-3s-est-desormais-disponible-pour-330-eu-17437"),
            ("Tech-Insider – Quest 3 ou Quest 3S en 2026", "https://tech-insider.org/fr/meta-quest-3-vs-3s-2026/"),
        ]),
    ]
    st += [P("11. Liens et sources", "h1"),
           P("Tous les liens sont cliquables. Les informations ont été vérifiées le 10 novembre 2026 ; les prix et les offres évoluent souvent.", "note")]
    for titre, liste in sources:
        st.append(P(titre, "h2"))
        st += puces([f"{t} : {lien(u)}" for t, u in liste])
    return st


def main():
    doc = SimpleDocTemplate(str(SORTIE), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=18 * mm, bottomMargin=20 * mm,
                            title="Campus Eiffel virtuel – Dossier de présentation", author="Projet Campus Eiffel virtuel",
                            subject="Campus virtuel 2D, options 3D et VR, exemples et coûts")
    doc.build(contenu(), onFirstPage=pied, onLaterPages=pied)
    print(f"OK : {SORTIE.name}")


if __name__ == "__main__":
    main()
