"""
================================================================================
  AKIR-IAO — MODULE MÉMOIRE SCIENCES INFIRMIÈRES v2.0
  Développeur exclusif : Ismail Ibn-Daifa
================================================================================
  Question de recherche :
  "Dans quelle mesure un outil informatisé d'aide au triage conforme à la grille
  FRENCH V1.1 améliore-t-il la concordance des décisions de triage entre
  infirmiers IAO expérimentés et infirmiers moins expérimentés aux urgences
  du Hainaut ?"

  Design : étude croisée (crossover) à deux facteurs
    Facteur 1 : Expérience (>= 3 ans IAO / < 3 ans IAO)
    Facteur 2 : Outil (avec / sans AKIR-IAO)
    → 4 cellules : Exp+Outil | Exp-Outil | Déb+Outil | Déb-Outil

  Hypothèses :
    H1 — L'outil améliore le kappa des débutants
    H2 — L'outil n'améliore pas significativement les expérimentés
    H3 — L'outil réduit l'écart de concordance entre les deux groupes

  Mesure : kappa de Cohen pondéré linéaire (Cohen J. Psychol Bull. 1968)
  RGPD : aucun nom ni prénom stocké — code participant anonyme uniquement
  Localisation : Hainaut, Wallonie, Belgique
  Référence clinique : FRENCH Triage SFMU V1.1 — Juin 2018
================================================================================
"""

import streamlit as st
import json
import os
import csv
import io
from datetime import datetime

st.set_page_config(
    page_title="AKIR-IAO — Mémoire Sciences Infirmières",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# CSS
# ==============================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap');
:root {
    --fond:#0A0E14; --fond-carte:#141A22; --fond-input:#1C2430; --bord:#2D3748;
    --txt:#E2E8F0; --txt-aide:#718096; --txt-titre:#F7FAFC;
    --bleu:#63B3ED; --vert:#48BB78; --rouge:#FC8181; --orange:#F6AD55; --violet:#B794F4;
    --exp-color:#63B3ED; --deb-color:#F6AD55;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="st-"]{font-family:'IBM Plex Sans',sans-serif;font-size:15px;color:var(--txt);background:var(--fond);}
.app-header{background:linear-gradient(135deg,#0A0E14 0%,#141A22 60%,#1a2236 100%);border:1px solid var(--bord);border-left:5px solid var(--bleu);border-radius:8px;padding:20px 26px;margin-bottom:20px;}
.app-titre{font-family:'IBM Plex Mono',monospace;font-size:1.05rem;font-weight:600;color:var(--bleu);letter-spacing:.08em;}
.app-question{font-size:.95rem;font-weight:500;color:var(--txt-titre);margin:8px 0 4px 0;line-height:1.5;}
.app-sous{font-size:.72rem;color:var(--txt-aide);}
.sec{font-size:.6rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--bleu);border-bottom:1px solid var(--bord);padding-bottom:5px;margin:18px 0 10px 0;}
.carte{background:var(--fond-carte);border:1px solid var(--bord);border-radius:8px;padding:18px 22px;margin-bottom:12px;}
.badge-exp{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:.72rem;font-weight:600;padding:3px 10px;border-radius:3px;letter-spacing:.06em;}
.badge-exp-exp{background:#1A365D;color:var(--exp-color);border:1px solid var(--exp-color);}
.badge-exp-deb{background:#7B341E;color:var(--orange);border:1px solid var(--orange);}
.vignette-num{font-family:'IBM Plex Mono',monospace;font-size:.65rem;color:var(--txt-aide);letter-spacing:.1em;margin-bottom:8px;}
.vignette-motif{font-size:1.08rem;font-weight:600;color:var(--txt-titre);margin-bottom:14px;line-height:1.4;}
.const-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:.79rem;background:var(--fond-input);border:1px solid var(--bord);border-radius:4px;padding:4px 10px;margin:3px 3px 3px 0;color:var(--txt);}
.const-alerte{border-color:var(--rouge)!important;color:var(--rouge)!important;}
.contexte-box{background:var(--fond-input);border-left:3px solid var(--bleu);border-radius:4px;padding:10px 14px;margin-top:12px;font-size:.84rem;color:var(--txt);line-height:1.6;}
.atcd-line{font-size:.79rem;color:var(--txt-aide);font-style:italic;margin-top:10px;}
.niveau-badge{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:.88rem;font-weight:700;padding:6px 20px;border-radius:4px;letter-spacing:.06em;}
.niv-M{background:#2D1F47;color:var(--violet);border:1px solid var(--violet);}
.niv-1{background:#3D1217;color:var(--rouge);border:1px solid var(--rouge);}
.niv-2{background:#3A2A0A;color:var(--orange);border:1px solid var(--orange);}
.niv-3A,.niv-3B{background:#1A2E4A;color:var(--bleu);border:1px solid var(--bleu);}
.niv-4{background:#1A3A22;color:var(--vert);border:1px solid var(--vert);}
.niv-5{background:#1C2430;color:var(--txt-aide);border:1px solid var(--bord);}
.res-correct{background:#1A3A22;border:1px solid var(--vert);border-left:4px solid var(--vert);border-radius:6px;padding:12px 16px;margin:5px 0;}
.res-surtriage{background:#1A2E4A;border:1px solid var(--bleu);border-left:4px solid var(--bleu);border-radius:6px;padding:12px 16px;margin:5px 0;}
.res-soustriage{background:#3D1217;border:1px solid var(--rouge);border-left:4px solid var(--rouge);border-radius:6px;padding:12px 16px;margin:5px 0;}
.kappa-box{background:var(--fond-carte);border:2px solid var(--bleu);border-radius:8px;padding:18px 16px;text-align:center;}
.kappa-val{font-family:'IBM Plex Mono',monospace;font-size:2.2rem;font-weight:700;color:var(--bleu);}
.kappa-lbl{font-size:.62rem;color:var(--txt-aide);text-transform:uppercase;letter-spacing:.1em;margin-top:3px;}
.kappa-interp{font-size:.82rem;color:var(--txt);margin-top:7px;font-weight:600;}
.kappa-group{font-size:.65rem;color:var(--txt-aide);margin-top:4px;}
.hypo-box{background:var(--fond-input);border:1px solid var(--bord);border-radius:6px;padding:14px 18px;margin:8px 0;font-size:.84rem;}
.hypo-label{font-family:'IBM Plex Mono',monospace;font-size:.7rem;color:var(--bleu);font-weight:600;margin-bottom:4px;}
.hypo-ok{border-left:4px solid var(--vert);}
.hypo-fail{border-left:4px solid var(--rouge);}
.al-crit{background:#3D1217;border-left:4px solid var(--rouge);border-radius:4px;padding:10px 14px;margin:6px 0;font-size:.82rem;color:var(--rouge);}
.al-warn{background:#2A200A;border-left:4px solid var(--orange);border-radius:4px;padding:10px 14px;margin:6px 0;font-size:.82rem;color:var(--orange);}
.al-ok{background:#1A3A22;border-left:4px solid var(--vert);border-radius:4px;padding:10px 14px;margin:6px 0;font-size:.82rem;color:var(--vert);}
.al-info{background:#1A2E4A;border-left:4px solid var(--bleu);border-radius:4px;padding:10px 14px;margin:6px 0;font-size:.82rem;color:var(--bleu);}
.chrono{font-family:'IBM Plex Mono',monospace;font-size:1.9rem;color:var(--vert);text-align:center;font-weight:600;}
.chrono-lbl{font-size:.6rem;color:var(--txt-aide);text-align:center;text-transform:uppercase;letter-spacing:.1em;}
.prog-fond{background:var(--fond-input);border-radius:4px;height:6px;margin:8px 0;}
.prog-fill{border-radius:4px;height:6px;transition:width .4s ease;}
.tableau-comp{width:100%;border-collapse:collapse;font-size:.82rem;margin:10px 0;}
.tableau-comp th{background:var(--fond-input);color:var(--txt-aide);font-size:.65rem;letter-spacing:.08em;text-transform:uppercase;padding:8px 12px;text-align:left;border-bottom:2px solid var(--bord);}
.tableau-comp td{padding:8px 12px;border-bottom:1px solid var(--bord);font-family:'IBM Plex Mono',monospace;font-size:.8rem;}
.td-bon{color:var(--vert);} .td-moy{color:var(--orange);} .td-fai{color:var(--rouge);}
.diff-pos{color:var(--vert);font-weight:600;} .diff-neg{color:var(--rouge);font-weight:600;} .diff-neu{color:var(--txt-aide);}
.likert-q{font-size:.86rem;font-weight:600;color:var(--txt-titre);margin:14px 0 4px 0;}
.disclaimer{background:var(--fond-carte);border:1px solid var(--bord);border-radius:4px;padding:14px 18px;margin-top:24px;font-size:.68rem;color:var(--txt-aide);line-height:1.8;}
.disclaimer-sig{font-size:.72rem;font-weight:600;color:var(--bleu);border-top:1px solid var(--bord);padding-top:8px;margin-top:8px;}
@media(max-width:768px){.kappa-val{font-size:1.7rem;}.chrono{font-size:1.5rem;}.stButton>button{min-height:48px!important;font-size:.95rem!important;}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ==============================================================================
# CONSTANTES
# ==============================================================================

LABELS_TRI = {
    "M":"Tri M — Engagement vital","1":"Tri 1 — Urgence absolue",
    "2":"Tri 2 — Urgence","3A":"Tri 3A — Urgence relative rapide",
    "3B":"Tri 3B — Urgence relative","4":"Tri 4 — Semi-urgence","5":"Tri 5 — Non-urgent",
}
CSS_TRI = {"M":"niv-M","1":"niv-1","2":"niv-2","3A":"niv-3A","3B":"niv-3B","4":"niv-4","5":"niv-5"}
ORD_NIV = {"M":0,"1":1,"2":2,"3A":3,"3B":4,"4":5,"5":6}
SEUIL_EXP_ANNEES = 3
FICHIER_RESULTATS = "akir_memoire_v2_resultats.json"
SESSION_1_IDS = [1,3,5,7,9,11,13,15,17,19]
SESSION_2_IDS = [2,4,6,8,10,12,14,16,18,20]

# ==============================================================================
# VIGNETTES
# ==============================================================================

VIGNETTES = [
    {"id":1,"categorie":"Cardio-circulatoire","difficulte":"Facile","piege":False,
     "motif_declare":"J'ai une douleur dans la poitrine depuis 1 heure",
     "age":58,"sexe":"H","age_mois":None,"fc":102,"pas":118,"spo2":97,"fr":18,"temp":37.1,"gcs":15,
     "atcd":["HTA","Diabete","Tabagisme"],"allergies":"RAS",
     "contexte":"ECG realise a l'arrivee : sus-decalage ST en V1-V4. Douleur constrictive bras gauche.",
     "reponse_french":"1",
     "justification":"ECG typique de SCA — Tri 1 selon FRENCH p.1.",
     "reference":"FRENCH SFMU V1.1 p.1 — Douleur thoracique / SCA",
     "enseignement":"Tout sus-decalage ST = Tri 1 immediat. Activation filiere STEMI sans attendre le medecin.",
     "point_differentiel":None},
    {"id":2,"categorie":"Neurologie","difficulte":"Facile","piege":False,
     "motif_declare":"Mon bras gauche ne repond plus depuis 2 heures",
     "age":71,"sexe":"F","age_mois":None,"fc":88,"pas":162,"spo2":96,"fr":16,"temp":37.0,"gcs":14,
     "atcd":["HTA","Fibrillation auriculaire"],"allergies":"Penicilline",
     "contexte":"Deficit moteur bras gauche, deviation de la commissure labiale. Debut brutal. Delai 2h.",
     "reponse_french":"1",
     "justification":"Deficit neurologique focal, delai <= 4h30 — filiere Stroke. Tri 1 selon FRENCH p.3.",
     "reference":"FRENCH SFMU V1.1 p.3 — Deficit moteur / AVC",
     "enseignement":"Delai <= 4h30 = activation filiere Stroke immediate. Ne pas faire baisser la TA sauf si > 220 mmHg.",
     "point_differentiel":None},
    {"id":3,"categorie":"Traumatologie","difficulte":"Facile","piege":False,
     "motif_declare":"Accident de voiture — douleur thoracique",
     "age":34,"sexe":"H","age_mois":None,"fc":124,"pas":88,"spo2":93,"fr":28,"temp":36.8,"gcs":13,
     "atcd":[],"allergies":"RAS",
     "contexte":"Choc frontal 90 km/h. Plaie thoracique penetrante visible cote droit.",
     "reponse_french":"1",
     "justification":"Traumatisme penetrant haute velocite — Tri 1 selon FRENCH p.7. NEWS2 = 7.",
     "reference":"FRENCH SFMU V1.1 p.7 — Traumatisme abdomen/thorax/cervical",
     "enseignement":"Tout traumatisme penetrant = Tri 1. Shock Index = 1,41. 2 VVP gros calibre immediat.",
     "point_differentiel":None},
    {"id":4,"categorie":"Cardio-circulatoire","difficulte":"Moyenne","piege":False,
     "motif_declare":"Palpitations depuis ce matin, je suis essoufflee",
     "age":45,"sexe":"F","age_mois":None,"fc":185,"pas":112,"spo2":97,"fr":18,"temp":37.0,"gcs":15,
     "atcd":["ATCD familial coronarien"],"allergies":"RAS",
     "contexte":"Palpitations regulieres. Legere sensation de malaise. ECG non encore realise.",
     "reponse_french":"1",
     "justification":"FC >= 180/min — Tri 1 selon FRENCH p.1.",
     "reference":"FRENCH SFMU V1.1 p.1 — Tachycardie / tachyarythmie",
     "enseignement":"FC >= 180 = Tri 1 meme si etat general correct. Monitoring cardiaque immediat.",
     "point_differentiel":None},
    {"id":5,"categorie":"Infectiologie","difficulte":"Difficile","piege":True,
     "motif_declare":"Fievre depuis 3 jours, je me sens fatigue",
     "age":28,"sexe":"H","age_mois":None,"fc":108,"pas":96,"spo2":97,"fr":23,"temp":39.2,"gcs":15,
     "atcd":[],"allergies":"RAS",
     "contexte":"Retour du Senegal il y a 8 jours. Frissons intenses. Taches rouges non effacables au verre sur les membres inferieurs.",
     "reponse_french":"1",
     "justification":"Purpura non effacable = Tri 1 absolu. Ceftriaxone 2g IV IMMEDIAT.",
     "reference":"SPILF / SFP — Purpura fulminans 2017 — critere transversal Tri 1",
     "enseignement":"PIEGE : la fievre seule = Tri 2. Le purpura non effacable impose Tri 1. Test du verre OBLIGATOIRE.",
     "point_differentiel":"Les experimente(e)s reconnaissent immediatement le purpura fulminans. Les debutant(e)s restent sur Tri 2 (fievre)."},
    {"id":6,"categorie":"Gynecologie","difficulte":"Difficile","piege":True,
     "motif_declare":"Douleur abdominale basse depuis ce matin",
     "age":24,"sexe":"F","age_mois":None,"fc":98,"pas":104,"spo2":99,"fr":16,"temp":36.9,"gcs":15,
     "atcd":[],"allergies":"RAS",
     "contexte":"Douleur abdominale basse droite irradiant dans l'epaule droite. Dernieres regles il y a 6 semaines. Test grossesse non realise.",
     "reponse_french":"2",
     "justification":"GEU probable : amenorrhee 6 sem + douleur abdominale + irradiation epaule. Beta-hCG systematique. Tri 2.",
     "reference":"FRENCH SFMU V1.1 p.2 — Douleur abdominale + alerte GEU",
     "enseignement":"PIEGE : constantes sub-normales mais GEU = urgence chirurgicale. Choc possible brutalement.",
     "point_differentiel":"Les experimente(e)s pensent immediatement a la GEU. Les debutant(e)s s'arretent a Tri 3B ou 4."},
    {"id":7,"categorie":"Neurologie","difficulte":"Moyenne","piege":False,
     "motif_declare":"J'ai eu une crise d'epilepsie dans la rue",
     "age":32,"sexe":"H","age_mois":None,"fc":94,"pas":128,"spo2":98,"fr":16,"temp":37.1,"gcs":15,
     "atcd":["Epilepsie"],"allergies":"RAS",
     "contexte":"Crise tonico-clonique de 2 min selon temoins. Recuperation neurologique complete a l'arrivee.",
     "reponse_french":"3B",
     "justification":"Convulsion avec recuperation complete — Tri 3B selon FRENCH p.3.",
     "reference":"FRENCH SFMU V1.1 p.3 — Convulsions",
     "enseignement":"Recuperation complete post-critique = Tri 3B. Crise en cours ou confusion = Tri 2. Glycemie capillaire systematique.",
     "point_differentiel":None},
    {"id":8,"categorie":"Traumatologie","difficulte":"Moyenne","piege":False,
     "motif_declare":"Je suis tombe et je me suis cogne la tete",
     "age":78,"sexe":"H","age_mois":None,"fc":72,"pas":134,"spo2":98,"fr":14,"temp":36.7,"gcs":14,
     "atcd":["HTA","Anticoagulants / AOD"],"allergies":"RAS",
     "contexte":"Chute de sa hauteur. Plaie occipitale. GCS 14 (Y4V4M6). Sous Xarelto 20mg.",
     "reponse_french":"2",
     "justification":"TC + AOD + GCS 14 — Tri 2 selon FRENCH p.7.",
     "reference":"FRENCH SFMU V1.1 p.7 — Traumatisme cranien",
     "enseignement":"AOD/AVK = risque d'hematome intracranien differe. TDM cerebral URGENT.",
     "point_differentiel":None},
    {"id":9,"categorie":"Cardiologie","difficulte":"Moyenne","piege":False,
     "motif_declare":"Ma tension est tres haute",
     "age":62,"sexe":"F","age_mois":None,"fc":88,"pas":192,"spo2":97,"fr":16,"temp":36.9,"gcs":15,
     "atcd":["HTA"],"allergies":"RAS",
     "contexte":"PAS 192 mmHg. Pas de cephalee, pas de trouble visuel, pas de douleur thoracique.",
     "reponse_french":"3B",
     "justification":"PAS 180-220 mmHg sans signes fonctionnels — Tri 3B selon FRENCH p.1.",
     "reference":"FRENCH SFMU V1.1 p.1 — Hypertension arterielle",
     "enseignement":"HTA sans signe fonctionnel = Tri 3B. Tri 2 si PAS >= 220 ou signes associes.",
     "point_differentiel":None},
    {"id":10,"categorie":"Pediatrie","difficulte":"Difficile","piege":False,
     "motif_declare":"Mon bebe a de la fievre et pleure depuis hier",
     "age":0,"sexe":"H","age_mois":2,"fc":162,"pas":72,"spo2":98,"fr":42,"temp":38.8,"gcs":15,
     "atcd":[],"allergies":"RAS",
     "contexte":"Nourrisson de 2 mois. Fievre 38,8 degres C rectale. Pleurs incessants. Fontanelle normale.",
     "reponse_french":"2",
     "justification":"Fievre chez nourrisson <= 3 mois = Tri 2 SYSTEMATIQUE selon FRENCH p.5.",
     "reference":"FRENCH SFMU V1.1 p.5 — Pediatrie <= 2 ans — Fievre <= 3 mois",
     "enseignement":"REGLE ABSOLUE : fievre chez nourrisson < 3 mois = Tri 2 sans exception.",
     "point_differentiel":"Les debutant(e)s peuvent attribuer Tri 3B si l'etat apparent semble correct. Regle memorisee plus solidement par les experimente(e)s."},
    {"id":11,"categorie":"Respiratoire","difficulte":"Facile","piege":False,
     "motif_declare":"Je n'arrive plus a respirer depuis ce matin",
     "age":55,"sexe":"H","age_mois":None,"fc":118,"pas":134,"spo2":84,"fr":38,"temp":37.2,"gcs":14,
     "atcd":["BPCO"],"allergies":"RAS",
     "contexte":"Exacerbation aigue de BPCO. Ne peut pas finir ses phrases. Tirage intercostal visible.",
     "reponse_french":"1",
     "justification":"Detresse respiratoire : SpO2 < 86% ET FR >= 40/min — Tri 1 selon FRENCH p.6.",
     "reference":"FRENCH SFMU V1.1 p.6 — Dyspnee / insuffisance cardiaque",
     "enseignement":"NEWS2 = 10. Engagement vital immediat.",
     "point_differentiel":None},
    {"id":12,"categorie":"Psychiatrie","difficulte":"Facile","piege":False,
     "motif_declare":"J'ai avale des medicaments pour en finir",
     "age":22,"sexe":"F","age_mois":None,"fc":92,"pas":118,"spo2":99,"fr":16,"temp":36.8,"gcs":15,
     "atcd":["Depression"],"allergies":"RAS",
     "contexte":"Ingestion de paracetamol dose inconnue il y a 1 heure. Patiente consciente. Intention suicidaire exprimee.",
     "reponse_french":"2",
     "justification":"Intoxication medicamenteuse avec intention suicidaire — Tri 2 selon FRENCH p.3.",
     "reference":"FRENCH SFMU V1.1 p.3 — Intoxication medicamenteuse",
     "enseignement":"Intention suicidaire = Tri 2 systematique. Paracetamolemie + charbon active si < 1h.",
     "point_differentiel":None},
    {"id":13,"categorie":"Digestif","difficulte":"Moyenne","piege":False,
     "motif_declare":"J'ai vomi du sang ce matin",
     "age":67,"sexe":"H","age_mois":None,"fc":114,"pas":98,"spo2":97,"fr":18,"temp":36.6,"gcs":15,
     "atcd":["Cirrhose hepatique","Anticoagulants / AOD"],"allergies":"RAS",
     "contexte":"Hematemese abondante en jet. Patient pale, sueurs froides. Abdomen souple.",
     "reponse_french":"2",
     "justification":"Hematemese abondante + Shock Index 1,16 — Tri 2 selon FRENCH p.2.",
     "reference":"FRENCH SFMU V1.1 p.2 — Hematemese",
     "enseignement":"Shock Index > 1 = etat de choc probable. Cirrhose + hematemese = rupture de varices.",
     "point_differentiel":None},
    {"id":14,"categorie":"Urologie","difficulte":"Facile","piege":False,
     "motif_declare":"Douleur terrible dans le rein droit",
     "age":38,"sexe":"H","age_mois":None,"fc":98,"pas":132,"spo2":99,"fr":20,"temp":37.0,"gcs":15,
     "atcd":[],"allergies":"AINS",
     "contexte":"Douleur lombaire droite intense en colique, irradiant vers l'aine. Agitation importante.",
     "reponse_french":"2",
     "justification":"Douleur lombaire intense avec agitation — Tri 2 selon FRENCH p.2.",
     "reference":"FRENCH SFMU V1.1 p.2 — Douleur lombaire / colique nephretique",
     "enseignement":"Allergie AINS : pas de Taradyl ni Diclofenac. Dipidolor ou Morphine IV.",
     "point_differentiel":None},
    {"id":15,"categorie":"Infectiologie","difficulte":"Difficile","piege":True,
     "motif_declare":"Je me sens pas bien, un peu fatiguee",
     "age":82,"sexe":"F","age_mois":None,"fc":102,"pas":108,"spo2":94,"fr":22,"temp":37.6,"gcs":14,
     "atcd":["Diabete de type 2","Insuffisance renale chronique","Immunodepression"],"allergies":"RAS",
     "contexte":"Confusion legere selon la famille. Brulures urinaires depuis 3 jours non traitees. Reside en EHPAD.",
     "reponse_french":"2",
     "justification":"qSOFA = 3 (FR >= 22, GCS < 15, PAS <= 100) + contexte infectieux — sepsis probable. Tri 2.",
     "reference":"FRENCH SFMU V1.1 + qSOFA Singer et al. JAMA 2016",
     "enseignement":"PIEGE MAJEUR : presentation masquee chez la personne agee immunodeprimee.",
     "point_differentiel":"Les experimente(e)s reconnaissent le profil geriatrique septique. Les debutant(e)s attribuent Tri 3B ou 4."},
    {"id":16,"categorie":"Traumatologie","difficulte":"Facile","piege":False,
     "motif_declare":"Je me suis tordu la cheville en jouant au foot",
     "age":19,"sexe":"H","age_mois":None,"fc":78,"pas":126,"spo2":99,"fr":14,"temp":36.8,"gcs":15,
     "atcd":[],"allergies":"RAS",
     "contexte":"Entorse cheville droite. Boiterie. Pas de deformation. Douleur 5/10. Regles d'Ottawa positives.",
     "reponse_french":"4",
     "justification":"Traumatisme distal, impotence moderee, pas de deformation — Tri 4 selon FRENCH p.7.",
     "reference":"FRENCH SFMU V1.1 p.7 — Traumatisme distal de membre",
     "enseignement":"Regles d'Ottawa = necessite d'une radio, pas d'un Tri urgent. Impotence moderee = Tri 4.",
     "point_differentiel":None},
    {"id":17,"categorie":"Metabolique","difficulte":"Moyenne","piege":False,
     "motif_declare":"Je suis diabetique et je me sens bizarre",
     "age":44,"sexe":"F","age_mois":None,"fc":94,"pas":122,"spo2":98,"fr":16,"temp":36.9,"gcs":13,
     "atcd":["Diabete de type 1"],"allergies":"RAS",
     "contexte":"Glycemie capillaire a l'arrivee : 28 mg/dl (1,6 mmol/l). GCS 13. Sueurs profuses.",
     "reponse_french":"2",
     "justification":"Hypoglycemie avec GCS 9-13 — Tri 2 selon FRENCH p.8.",
     "reference":"FRENCH SFMU V1.1 p.8 — Hypoglycemie",
     "enseignement":"Glycemie 28 mg/dl = hypoglycemie severe. Glucose 30% 50ml IV en bolus immediat.",
     "point_differentiel":None},
    {"id":18,"categorie":"ORL","difficulte":"Moyenne","piege":False,
     "motif_declare":"J'ai du sang qui coule du nez depuis une heure",
     "age":71,"sexe":"H","age_mois":None,"fc":88,"pas":158,"spo2":98,"fr":16,"temp":36.8,"gcs":15,
     "atcd":["HTA","Anticoagulants / AOD"],"allergies":"RAS",
     "contexte":"Epistaxis anterieure droite active abondante. Sous Eliquis 5mg. Saignement non controle.",
     "reponse_french":"3B",
     "justification":"Epistaxis abondante sous AOD — Tri 3B selon FRENCH p.4.",
     "reference":"FRENCH SFMU V1.1 p.4 — Epistaxis",
     "enseignement":"Epistaxis + AOD = surveillance hemodynamique. Mechage anterieur urgent.",
     "point_differentiel":None},
    {"id":19,"categorie":"Gynecologie","difficulte":"Moyenne","piege":False,
     "motif_declare":"J'ai des saignements vaginaux abondants",
     "age":31,"sexe":"F","age_mois":None,"fc":108,"pas":102,"spo2":99,"fr":18,"temp":36.7,"gcs":15,
     "atcd":["Grossesse en cours"],"allergies":"RAS",
     "contexte":"Grossesse de 8 semaines. Saignements abondants avec caillots depuis 3 heures.",
     "reponse_french":"3A",
     "justification":"Grossesse T1 avec metrorragies — Tri 3A selon FRENCH p.3.",
     "reference":"FRENCH SFMU V1.1 p.3 — Grossesse 1er trimestre",
     "enseignement":"Grossesse T1 + metrorragies = Tri 3A. Alerte equipe obstetricale. Beta-hCG + echo.",
     "point_differentiel":None},
    {"id":20,"categorie":"Divers","difficulte":"Facile","piege":False,
     "motif_declare":"Je voudrais renouveler mon ordonnance pour ma tension",
     "age":54,"sexe":"H","age_mois":None,"fc":76,"pas":138,"spo2":99,"fr":14,"temp":36.8,"gcs":15,
     "atcd":["HTA"],"allergies":"RAS",
     "contexte":"Patient venu pour renouvellement d'ordonnance antihypertensive. Aucun symptome aigu.",
     "reponse_french":"5",
     "justification":"Renouvellement d'ordonnance — Tri 5 selon FRENCH p.8.",
     "reference":"FRENCH SFMU V1.1 p.8 — Renouvellement ordonnance",
     "enseignement":"Tri 5 = consultation non urgente. Reorienter vers medecin generaliste.",
     "point_differentiel":None},
]

# ==============================================================================
# MOTEUR STATISTIQUE
# ==============================================================================

def kappa_pondere(reps_iao, reps_french):
    niveaux = ["M","1","2","3A","3B","4","5"]
    k = len(niveaux)
    n = len(reps_iao)
    if n == 0:
        return 0.0, "Donnees insuffisantes"
    def w(a,b):
        return 1 - abs(ORD_NIV.get(a,3) - ORD_NIV.get(b,3)) / (k-1)
    po = sum(w(reps_iao[i], reps_french[i]) for i in range(n)) / n
    fi = {niv: reps_iao.count(niv)/n for niv in niveaux}
    fj = {niv: reps_french.count(niv)/n for niv in niveaux}
    pe = sum(fi[a]*fj[b]*w(a,b) for a in niveaux for b in niveaux)
    if pe >= 1.0:
        return 1.0, "Accord parfait"
    kappa = round((po-pe)/(1-pe), 3)
    if   kappa < 0.20: interp = "Concordance faible"
    elif kappa < 0.40: interp = "Concordance mediocre"
    elif kappa < 0.60: interp = "Concordance moderee"
    elif kappa < 0.80: interp = "Concordance bonne"
    else:              interp = "Concordance excellente"
    return kappa, interp


def analyser(resultats):
    reps_iao, reps_fr = [], []
    correct = surtriage = soustriage = pieges_rates = 0
    temps = []
    for r in resultats:
        iao = r.get("reponse_iao")
        fr  = r.get("reponse_french")
        if not iao or not fr:
            continue
        reps_iao.append(iao)
        reps_fr.append(fr)
        ecart = ORD_NIV.get(iao,3) - ORD_NIV.get(fr,3)
        if   ecart == 0: correct += 1
        elif ecart < 0:  surtriage += 1
        else:
            soustriage += 1
            if r.get("piege"): pieges_rates += 1
        if r.get("temps_sec"): temps.append(r["temps_sec"])
    n = len(reps_iao)
    kappa, interp = kappa_pondere(reps_iao, reps_fr)
    return {
        "n": n, "kappa": kappa, "interpretation": interp,
        "correct": correct, "sur_triage": surtriage, "sous_triage": soustriage,
        "taux_correct": round(correct/n*100,1) if n else 0,
        "taux_sous": round(soustriage/n*100,1) if n else 0,
        "temps_moyen": round(sum(temps)/len(temps),1) if temps else 0,
        "pieges_rates": pieges_rates,
    }


def tester_hypotheses(sc):
    res = {}
    if sc.get("deb_sans") and sc.get("deb_avec"):
        delta = sc["deb_avec"]["kappa"] - sc["deb_sans"]["kappa"]
        res["H1"] = {"titre":"L'outil ameliore la concordance des infirmiers debutants",
                     "delta": delta, "valide": delta > 0.10,
                     "detail": f"delta kappa debutants : {'+' if delta>=0 else ''}{delta:.3f}"}
    if sc.get("exp_sans") and sc.get("exp_avec"):
        delta = sc["exp_avec"]["kappa"] - sc["exp_sans"]["kappa"]
        res["H2"] = {"titre":"L'outil n'ameliore pas significativement les experimente(e)s",
                     "delta": delta, "valide": abs(delta) < 0.10,
                     "detail": f"delta kappa experimente(e)s : {'+' if delta>=0 else ''}{delta:.3f}"}
    if sc.get("exp_avec") and sc.get("deb_avec") and sc.get("exp_sans") and sc.get("deb_sans"):
        ecart_avec = sc["exp_avec"]["kappa"] - sc["deb_avec"]["kappa"]
        ecart_sans = sc["exp_sans"]["kappa"] - sc["deb_sans"]["kappa"]
        delta = ecart_sans - ecart_avec
        res["H3"] = {"titre":"L'outil reduit l'ecart de concordance entre les deux groupes",
                     "delta": delta, "valide": ecart_avec < ecart_sans,
                     "detail": f"Ecart sans outil : {ecart_sans:.3f} — avec outil : {ecart_avec:.3f}"}
    return res

# ==============================================================================
# PERSISTANCE
# ==============================================================================

def charger():
    if os.path.exists(FICHIER_RESULTATS):
        try:
            with open(FICHIER_RESULTATS,"r",encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def sauvegarder(data):
    try:
        with open(FICHIER_RESULTATS,"w",encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def exporter_csv(resultats):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["code_participant","experience_groupe","annees_iao","service","groupe",
                "session","mode_outil","vignette_id","categorie","difficulte","piege",
                "niveau_iao","niveau_french","concordance","ecart_ordinal","type_ecart","temps_sec"])
    for r in resultats:
        if r.get("type") == "likert":
            continue
        ecart = ORD_NIV.get(r.get("reponse_iao","5"),5) - ORD_NIV.get(r.get("reponse_french","5"),5)
        te = "Correct" if ecart==0 else ("Sur-triage" if ecart<0 else "Sous-triage")
        w.writerow([r.get("code_participant","ANON"), r.get("experience_groupe","?"),
                    r.get("annees_iao","?"), r.get("service","?"), r.get("groupe","?"),
                    r.get("session","?"), r.get("mode_outil","?"), r.get("vignette_id","?"),
                    r.get("categorie","?"), r.get("difficulte","?"), r.get("piege",False),
                    r.get("reponse_iao","?"), r.get("reponse_french","?"),
                    ecart==0, ecart, te, r.get("temps_sec","")])
    return out.getvalue()

# ==============================================================================
# SESSION STATE
# ==============================================================================

DEFAULTS = {
    "memoire_etape":"accueil","code_participant":"","experience_groupe":"",
    "annees_iao":0,"service":"","groupe":"A","session_num":1,"mode_outil":False,
    "vignettes_session":[],"index_vignette":0,"reponse_en_cours":None,
    "heure_debut_vignette":None,"resultats_session":[],"revelation":False,"consentement":False,
}
for k,v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def ui_al(msg, typ="info"):
    css={"crit":"al-crit","warn":"al-warn","ok":"al-ok","info":"al-info"}.get(typ,"al-info")
    st.markdown(f'<div class="{css}">{msg}</div>',unsafe_allow_html=True)

def ui_sec(titre):
    st.markdown(f'<div class="sec">{titre}</div>',unsafe_allow_html=True)

def vig_by_id(vid):
    return next((v for v in VIGNETTES if v["id"]==vid), None)

def badge_exp(g):
    if g == "experimente":
        return '<span class="badge-exp badge-exp-exp">EXPERIMENTE >= 3 ans</span>'
    return '<span class="badge-exp badge-exp-deb">DEBUTANT < 3 ans</span>'

def kappa_color(k):
    if isinstance(k,float):
        return "var(--vert)" if k>=0.61 else ("var(--orange)" if k>=0.41 else "var(--rouge)")
    return "var(--txt-aide)"

def kappa_td(k):
    if isinstance(k,float):
        return "td-bon" if k>=0.61 else ("td-moy" if k>=0.41 else "td-fai")
    return ""

def const_badge(val, seuil_bas, seuil_haut):
    try:
        return "const-alerte" if float(val)<seuil_bas or float(val)>seuil_haut else ""
    except Exception:
        return ""

# ==============================================================================
# EN-TETE
# ==============================================================================

st.markdown(
    '<div class="app-header">'
    '<div class="app-titre">AKIR-IAO — MODULE MEMOIRE SCIENCES INFIRMIERES v2.0</div>'
    '<div class="app-question">'
    '"Dans quelle mesure un outil informatise d\'aide au triage conforme a la grille FRENCH V1.1 '
    'ameliore-t-il la concordance des decisions de triage entre infirmiers IAO experimentes '
    'et infirmiers moins experimentes aux urgences du Hainaut ?"'
    '</div>'
    '<div class="app-sous">Ismail Ibn-Daifa  |  Design crossover 4 cellules  |  '
    'Kappa de Cohen pondere  |  Hainaut, Wallonie, Belgique  |  FRENCH SFMU V1.1</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ==============================================================================
# ACCUEIL
# ==============================================================================

if st.session_state.memoire_etape == "accueil":
    c1,c2 = st.columns(2)
    with c1:
        st.markdown(
            '<div class="carte"><div class="sec">Question de recherche et hypotheses</div>'
            'L\'etude compare la concordance au referentiel FRENCH V1.1 entre :<br><br>'
            '<span class="badge-exp badge-exp-exp">EXPERIMENTES</span> >= 3 ans IAO<br>'
            '<span class="badge-exp badge-exp-deb">DEBUTANTS</span> &lt; 3 ans IAO<br><br>'
            '<b>H1</b> — L\'outil ameliore le kappa des debutants<br>'
            '<b>H2</b> — L\'outil n\'ameliore pas significativement les experimentes<br>'
            '<b>H3</b> — L\'outil reduit l\'ecart de concordance entre les deux groupes'
            '</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="carte"><div class="sec">Design crossover — 4 cellules</div>'
            '<table class="tableau-comp">'
            '<tr><th>Groupe</th><th>Sans outil</th><th>Avec outil</th></tr>'
            '<tr><td><span class="badge-exp badge-exp-exp">Experimentes</span></td>'
            '<td>Session 1 ou 2</td><td>Session 2 ou 1</td></tr>'
            '<tr><td><span class="badge-exp badge-exp-deb">Debutants</span></td>'
            '<td>Session 1 ou 2</td><td>Session 2 ou 1</td></tr>'
            '</table><br>'
            '20 vignettes standardisees FRENCH — 10 par session<br>'
            'Wash-out 2 semaines entre les sessions<br>'
            'Mesure : kappa de Cohen pondere lineaire'
            '</div>',
            unsafe_allow_html=True,
        )
    ui_al("RGPD — Aucun nom ni prenom collecte. Code participant anonyme uniquement. Participation volontaire.","info")
    b1,b2 = st.columns(2)
    if b1.button("Commencer une session participant", use_container_width=True, type="primary"):
        st.session_state.memoire_etape = "consentement"; st.rerun()
    if b2.button("Espace administrateur / resultats", use_container_width=True):
        st.session_state.memoire_etape = "admin"; st.rerun()

# ==============================================================================
# CONSENTEMENT
# ==============================================================================

elif st.session_state.memoire_etape == "consentement":
    st.markdown("### Formulaire de consentement eclaire")
    st.markdown(
        '<div class="carte"><div class="sec">Information du participant</div>'
        'Vous etes invite(e) a participer a une etude dans le cadre d\'un memoire en sciences infirmieres.<br><br>'
        '<b>Ce que vous allez faire :</b> trier 10 vignettes cliniques fictives et standardisees, avec ou sans l\'outil AKIR-IAO.<br><br>'
        '<b>Ce que nous mesurons :</b> la concordance de vos decisions avec le referentiel FRENCH Triage SFMU V1.1. '
        'Votre performance individuelle n\'est PAS evaluee.<br><br>'
        '<b>Vos droits :</b><br>'
        '— Participation volontaire et sans contrainte<br>'
        '— Retrait possible a tout moment<br>'
        '— Aucun nom ni prenom collecte<br>'
        '— Donnees stockees localement, aucune transmission a des tiers'
        '</div>',
        unsafe_allow_html=True,
    )
    consent = st.checkbox("J'ai lu et compris les informations. Je consens a participer de maniere volontaire et anonyme.")
    c1,c2 = st.columns(2)
    if c1.button("Continuer", use_container_width=True, type="primary", disabled=not consent):
        st.session_state.consentement = True; st.session_state.memoire_etape = "configuration"; st.rerun()
    if c2.button("Annuler", use_container_width=True):
        st.session_state.memoire_etape = "accueil"; st.rerun()

# ==============================================================================
# CONFIGURATION
# ==============================================================================

elif st.session_state.memoire_etape == "configuration":
    st.markdown("### Votre profil — Configuration de la session")
    with st.form("config_form"):
        ui_sec("Identification anonyme")
        code = st.text_input("Code participant (attribue par le chercheur, ex: IAO_01)", max_chars=10)
        ui_sec("Profil professionnel")
        annees = st.number_input(
            f"Annees d'exercice en poste IAO uniquement (seuil etude : >= {SEUIL_EXP_ANNEES} ans = experimente)",
            min_value=0, max_value=40, value=2, step=1
        )
        service = st.text_input("Service / institution (ex: CHU Ambroise Pare, EpiCURA...)", max_chars=60)
        formation = st.radio(
            "Formation specifique au referentiel FRENCH Triage ?",
            ["Oui, formation complete","Oui, formation partielle / autoformation","Non"],
        )
        ui_sec("Protocole crossover")
        groupe = st.radio("Groupe d'appartenance (attribue par le chercheur)", ["A","B"], horizontal=True,
                          help="Groupe A : session 1 sans outil | Groupe B : session 1 avec outil")
        session = st.radio("Numero de session", [1,2], horizontal=True,
                           help="Session 1 = premiere participation | Session 2 = apres wash-out de 2 semaines")
        soumis = st.form_submit_button("Valider et commencer", use_container_width=True)

    if soumis:
        if not code.strip():
            ui_al("Veuillez saisir votre code participant.","crit")
        else:
            exp_grp = "experimente" if annees >= SEUIL_EXP_ANNEES else "debutant"
            if groupe == "A":
                avec_outil  = (session==2)
                ids_session = SESSION_1_IDS if session==1 else SESSION_2_IDS
            else:
                avec_outil  = (session==1)
                ids_session = SESSION_2_IDS if session==1 else SESSION_1_IDS
            st.session_state.update({
                "code_participant": code.strip().upper(),
                "experience_groupe": exp_grp,
                "annees_iao": annees,
                "service": service.strip(),
                "formation_french": formation,
                "groupe": groupe, "session_num": session,
                "mode_outil": avec_outil,
                "vignettes_session": ids_session,
                "index_vignette": 0, "resultats_session": [],
                "revelation": False, "reponse_en_cours": None,
                "heure_debut_vignette": datetime.now(),
                "memoire_etape": "session",
            })
            st.rerun()

    if st.button("Retour a l'accueil"):
        st.session_state.memoire_etape = "accueil"; st.rerun()

# ==============================================================================
# SESSION
# ==============================================================================

elif st.session_state.memoire_etape == "session":
    ids   = st.session_state.vignettes_session
    idx   = st.session_state.index_vignette
    n_tot = len(ids)

    if idx >= n_tot:
        st.session_state.memoire_etape = "resultats"; st.rerun()

    vig = vig_by_id(ids[idx])
    if not vig:
        st.error("Vignette introuvable."); st.stop()

    pct = round(idx/n_tot*100)
    bar_col = "var(--vert)" if pct<70 else "var(--orange)"
    exp_html = badge_exp(st.session_state.experience_groupe)
    mode_lbl = "AVEC outil" if st.session_state.mode_outil else "SANS outil"
    st.markdown(
        f'<div class="prog-fond"><div class="prog-fill" style="width:{pct}%;background:{bar_col};"></div></div>'
        f'<div style="display:flex;justify-content:space-between;font-size:.68rem;color:var(--txt-aide);margin-bottom:8px;">'
        f'<span>Vignette {idx+1} / {n_tot}</span>'
        f'<span>{st.session_state.code_participant} | {exp_html} | {mode_lbl}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.heure_debut_vignette:
        elapsed = (datetime.now() - st.session_state.heure_debut_vignette).total_seconds()
        m,s = divmod(int(elapsed),60)
        cc = "var(--rouge)" if elapsed>180 else ("var(--orange)" if elapsed>120 else "var(--vert)")
        st.markdown(f'<div class="chrono" style="color:{cc};">{m:02d}:{s:02d}</div><div class="chrono-lbl">Temps — objectif 3 min</div>',unsafe_allow_html=True)

    age_lbl = f"{vig.get('age_mois')} mois" if vig.get("age_mois") else f"{vig['age']} ans"
    atcd_lbl = ", ".join(vig["atcd"]) if vig["atcd"] else "Aucun antecedent notable"
    fc_c   = const_badge(vig["fc"],40,130)
    pas_c  = const_badge(vig["pas"],90,180)
    spo2_c = const_badge(vig["spo2"],94,100)
    fr_c   = const_badge(vig["fr"],12,20)
    temp_c = const_badge(vig["temp"],36.0,38.0)
    gcs_c  = "const-alerte" if vig["gcs"]<15 else ""

    st.markdown(
        f'<div class="carte">'
        f'<div class="vignette-num">VIGNETTE {idx+1:02d} / {n_tot}  —  {vig["categorie"]}'
        f'{"  [VIGNETTE PIEGE]" if vig["piege"] else ""}</div>'
        f'<div class="vignette-motif">"{vig["motif_declare"]}"</div>'
        f'<span class="const-badge">Age : {age_lbl} {vig["sexe"]}</span>'
        f'<span class="const-badge {fc_c}">FC : {vig["fc"]} bpm</span>'
        f'<span class="const-badge {pas_c}">PAS : {vig["pas"]} mmHg</span>'
        f'<span class="const-badge {spo2_c}">SpO2 : {vig["spo2"]} %</span>'
        f'<span class="const-badge {fr_c}">FR : {vig["fr"]} /min</span>'
        f'<span class="const-badge {temp_c}">T : {vig["temp"]} deg C</span>'
        f'<span class="const-badge {gcs_c}">GCS : {vig["gcs"]}/15</span>'
        f'<div class="atcd-line">Antecedents : {atcd_lbl} | Allergies : {vig["allergies"]}</div>',
        unsafe_allow_html=True,
    )
    if vig.get("contexte"):
        st.markdown(f'<div class="contexte-box"><b>Contexte clinique :</b> {vig["contexte"]}</div></div>',unsafe_allow_html=True)
    else:
        st.markdown('</div>',unsafe_allow_html=True)

    if st.session_state.mode_outil:
        ui_al("Mode AVEC outil : utilisez l'application AKIR-IAO principale pour vous aider, puis saisissez votre niveau final ci-dessous.","info")

    # Phase 1 — Reponse cachee
    if not st.session_state.revelation:
        ui_sec("Votre decision de triage")
        reponse = st.radio(
            "Quel niveau de tri attribuez-vous a ce patient ?",
            ["M","1","2","3A","3B","4","5"],
            format_func=lambda x: f"Tri {x}  —  {LABELS_TRI[x]}",
            key=f"rep_{idx}",
        )
        cv, cp = st.columns(2)
        if cv.button("Valider ma reponse", use_container_width=True, type="primary"):
            elapsed = (datetime.now()-st.session_state.heure_debut_vignette).total_seconds()
            st.session_state.reponse_en_cours = reponse
            st.session_state.revelation = True
            st.session_state.resultats_session.append({
                "code_participant":  st.session_state.code_participant,
                "experience_groupe": st.session_state.experience_groupe,
                "annees_iao":        st.session_state.annees_iao,
                "service":           st.session_state.service,
                "groupe":            st.session_state.groupe,
                "session":           st.session_state.session_num,
                "mode_outil":        "avec" if st.session_state.mode_outil else "sans",
                "vignette_id":       vig["id"],
                "categorie":         vig["categorie"],
                "difficulte":        vig["difficulte"],
                "piege":             vig["piege"],
                "reponse_iao":       reponse,
                "reponse_french":    vig["reponse_french"],
                "temps_sec":         round(elapsed,1),
                "heure":             datetime.now().strftime("%H:%M:%S"),
            })
            st.rerun()
        if cp.button("Passer cette vignette", use_container_width=True):
            st.session_state.index_vignette += 1
            st.session_state.revelation = False
            st.session_state.heure_debut_vignette = datetime.now()
            st.rerun()

    # Phase 2 — Revelation
    else:
        iao    = st.session_state.reponse_en_cours
        french = vig["reponse_french"]
        ecart  = ORD_NIV.get(iao,3) - ORD_NIV.get(french,3)
        ui_sec("Revelation — Reponse FRENCH officielle")
        ca,cb = st.columns(2)
        with ca:
            st.markdown(f'<div style="text-align:center;"><div style="font-size:.65rem;color:var(--txt-aide);margin-bottom:6px;">VOTRE REPONSE</div><span class="niveau-badge {CSS_TRI.get(iao,"niv-5")}">Tri {iao}</span></div>',unsafe_allow_html=True)
        with cb:
            st.markdown(f'<div style="text-align:center;"><div style="font-size:.65rem;color:var(--txt-aide);margin-bottom:6px;">FRENCH SFMU V1.1</div><span class="niveau-badge {CSS_TRI.get(french,"niv-5")}">Tri {french}</span></div>',unsafe_allow_html=True)
        if ecart==0:
            ui_al(f"Reponse correcte — {vig['justification']}","ok")
        elif ecart<0:
            ui_al(f"Sur-triage (niveau plus urgent qu'attendu) — {vig['justification']}","info")
        else:
            ui_al(f"SOUS-TRIAGE — Erreur potentiellement dangereuse pour le patient — {vig['justification']}","crit")

        with st.expander("Enseignement clinique + point differentiel experience", expanded=(ecart!=0)):
            st.markdown(f"**Reference :** {vig['reference']}")
            st.markdown(f"**Point cle :** {vig['enseignement']}")
            if vig.get("point_differentiel"):
                ui_al(f"Point differentiel experience : {vig['point_differentiel']}","warn")
            if vig["piege"]:
                ui_al("VIGNETTE PIEGE : concu pour tester les presentations atypiques differenciant experimentes et debutants.","warn")

        if st.button("Vignette suivante", use_container_width=True, type="primary"):
            st.session_state.index_vignette += 1
            st.session_state.revelation = False
            st.session_state.heure_debut_vignette = datetime.now()
            st.rerun()

# ==============================================================================
# RESULTATS
# ==============================================================================

elif st.session_state.memoire_etape == "resultats":
    resultats = st.session_state.resultats_session
    stats = analyser(resultats)
    exp_lbl  = st.session_state.experience_groupe
    mode_lbl = "avec outil" if st.session_state.mode_outil else "sans outil"

    tous = charger()
    tous.extend(resultats)
    sauvegarder(tous)

    st.markdown(f"### Resultats — Session {st.session_state.session_num} — {mode_lbl.upper()}")
    st.markdown(badge_exp(exp_lbl), unsafe_allow_html=True)

    kc = kappa_color(stats["kappa"])
    st.markdown(
        f'<div class="kappa-box">'
        f'<div class="kappa-val" style="color:{kc};">{stats["kappa"]}</div>'
        f'<div class="kappa-lbl">Kappa de Cohen pondere lineaire</div>'
        f'<div class="kappa-interp">{stats["interpretation"]}</div>'
        f'<div class="kappa-group">{badge_exp(exp_lbl)} — {mode_lbl} — {stats["n"]} vignettes</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Reponses",stats["n"])
    c2.metric("Correctes",stats["correct"],delta=f'{stats["taux_correct"]} %')
    c3.metric("Sur-triage",stats["sur_triage"])
    c4.metric("Sous-triage",stats["sous_triage"],delta=f'-{stats["taux_sous"]} %',delta_color="inverse")
    c5.metric("Temps moyen",f'{stats["temps_moyen"]} s')

    if stats["sous_triage"]>0:
        ui_al(f"{stats['sous_triage']} sous-triage(s) — Le sous-triage est l'erreur la plus dangereuse cliniquement.","crit")
    if stats.get("pieges_rates",0)>0:
        ui_al(f"{stats['pieges_rates']} vignette(s) piege(s) sous-triee(s) — Ces cas sont cibles pour differencier les deux groupes.","warn")

    ui_sec("Detail vignette par vignette")
    for r in resultats:
        iao    = r.get("reponse_iao","?")
        french = r.get("reponse_french","?")
        ecart  = ORD_NIV.get(iao,3) - ORD_NIV.get(french,3)
        if ecart==0: rcss,rlbl = "res-correct","CORRECT"
        elif ecart<0: rcss,rlbl = "res-surtriage","SUR-TRIAGE"
        else: rcss,rlbl = "res-soustriage","SOUS-TRIAGE"
        v2 = vig_by_id(r.get("vignette_id",0))
        ml = (v2["motif_declare"][:55]+"...") if v2 and len(v2["motif_declare"])>55 else (v2["motif_declare"] if v2 else "?")
        st.markdown(
            f'<div class="{rcss}"><b>V{r.get("vignette_id","?")} — {r.get("categorie","?")}</b>'
            f'{"  [PIEGE]" if r.get("piege") else ""}  |  {ml}<br>'
            f'Tri {iao} -> FRENCH Tri {french}  |  {rlbl}  |  {r.get("temps_sec","?")} s</div>',
            unsafe_allow_html=True,
        )

    # Likert (mode avec outil uniquement)
    if st.session_state.mode_outil:
        ui_sec("Questionnaire de satisfaction — AKIR-IAO (10 items)")
        st.caption("1 = Pas du tout d'accord  |  5 = Tout a fait d'accord")
        likert_items = [
            ("L'outil est intuitif et facile a utiliser en situation d'urgence.","facilite"),
            ("L'outil m'a permis de trier plus rapidement.","rapidite"),
            ("L'outil a ameliore la precision de mes decisions.","precision"),
            ("Les alertes cliniques (purpura, GEU, sepsis...) etaient pertinentes.","alertes"),
            ("L'outil reduit la charge cognitive en situation de flux eleve.","charge_cog"),
            ("Je ferais confiance a cet outil dans ma pratique quotidienne.","confiance"),
            ("L'outil compense un manque d'experience en triage.","compensation_exp"),
            ("Je le recommanderais a un collegue debutant en IAO.","recommande_deb"),
            ("Je le recommanderais a un collegue experimente en IAO.","recommande_exp"),
            ("L'outil serait un support de formation utile pour les nouveaux IAO.","formation"),
        ]
        with st.form("likert_form"):
            lreps = {}
            for q,cle in likert_items:
                st.markdown(f'<div class="likert-q">{q}</div>',unsafe_allow_html=True)
                lreps[cle] = st.slider(q,1,5,3,label_visibility="collapsed",key=f"lk_{cle}")
            commentaire = st.text_area("Commentaire libre — differences percues selon votre experience ?",key="lk_com")
            if st.form_submit_button("Envoyer le questionnaire",use_container_width=True):
                tous2 = charger()
                tous2.append({
                    "type":"likert",
                    "code_participant": st.session_state.code_participant,
                    "experience_groupe": st.session_state.experience_groupe,
                    "annees_iao": st.session_state.annees_iao,
                    "groupe": st.session_state.groupe,
                    "session": st.session_state.session_num,
                    "heure": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "reponses": lreps, "commentaire": commentaire,
                })
                sauvegarder(tous2)
                ui_al("Questionnaire enregistre. Merci pour votre participation.","ok")

    csv_data = exporter_csv(resultats)
    st.download_button(
        label="Telecharger mes resultats (CSV)",
        data=csv_data,
        file_name=f"akir_memoire_{st.session_state.code_participant}_S{st.session_state.session_num}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
    if st.button("Retour a l'accueil",use_container_width=True):
        for k,v in DEFAULTS.items(): st.session_state[k]=v
        st.session_state.memoire_etape = "accueil"; st.rerun()

# ==============================================================================
# ADMIN
# ==============================================================================

elif st.session_state.memoire_etape == "admin":
    st.markdown("### Espace administrateur — Resultats agregés")
    mdp = st.text_input("Mot de passe",type="password",key="admin_mdp")
    if mdp != "memoire2025":
        ui_al("Saisir le mot de passe administrateur.","info")
        if st.button("Retour a l'accueil"):
            st.session_state.memoire_etape = "accueil"; st.rerun()
        st.stop()

    tous        = charger()
    triage_data = [r for r in tous if r.get("type")!="likert"]
    likert_data = [r for r in tous if r.get("type")=="likert"]
    participants= list(set(r.get("code_participant","") for r in triage_data))
    c1,c2,c3 = st.columns(3)
    c1.metric("Reponses triage",len(triage_data))
    c2.metric("Questionnaires Likert",len(likert_data))
    c3.metric("Participants",len(participants))

    if not triage_data:
        ui_al("Aucune donnee enregistree.","info")
    else:
        exp_sans = [r for r in triage_data if r.get("experience_groupe")=="experimente" and r.get("mode_outil")=="sans"]
        exp_avec = [r for r in triage_data if r.get("experience_groupe")=="experimente" and r.get("mode_outil")=="avec"]
        deb_sans = [r for r in triage_data if r.get("experience_groupe")=="debutant"    and r.get("mode_outil")=="sans"]
        deb_avec = [r for r in triage_data if r.get("experience_groupe")=="debutant"    and r.get("mode_outil")=="avec"]
        sc = {}
        if exp_sans: sc["exp_sans"] = analyser(exp_sans)
        if exp_avec: sc["exp_avec"] = analyser(exp_avec)
        if deb_sans: sc["deb_sans"] = analyser(deb_sans)
        if deb_avec: sc["deb_avec"] = analyser(deb_avec)

        ui_sec("Tableau comparatif — 4 cellules crossover")
        rows = [
            ("Experimentes (>= 3 ans)","exp_sans","exp_avec"),
            ("Debutants (< 3 ans)",    "deb_sans","deb_avec"),
        ]
        html = ('<table class="tableau-comp"><tr><th>Groupe</th><th>N sans / avec</th>'
                '<th>Kappa sans outil</th><th>Kappa avec outil</th><th>Delta kappa</th>'
                '<th>% correct sans</th><th>% correct avec</th>'
                '<th>Sous-triage sans</th><th>Sous-triage avec</th></tr>')
        for lbl,ks,ka in rows:
            ss = sc.get(ks,{}); sa = sc.get(ka,{})
            k_s = ss.get("kappa","-") if ss else "-"
            k_a = sa.get("kappa","-") if sa else "-"
            if isinstance(k_s,float) and isinstance(k_a,float):
                delta = round(k_a-k_s,3)
                dcss = "diff-pos" if delta>0 else ("diff-neg" if delta<0 else "diff-neu")
                dlbl = f'{("+" if delta>0 else "")}{delta}'
            else:
                delta=None; dcss="diff-neu"; dlbl="-"
            ns = ss.get("n",0) if ss else 0; na = sa.get("n",0) if sa else 0
            html += (f'<tr><td><b>{lbl}</b></td><td>{ns} / {na}</td>'
                     f'<td class="{kappa_td(k_s)}">{k_s}</td>'
                     f'<td class="{kappa_td(k_a)}">{k_a}</td>'
                     f'<td class="{dcss}">{dlbl}</td>'
                     f'<td>{ss.get("taux_correct","?") if ss else "-"} %</td>'
                     f'<td>{sa.get("taux_correct","?") if sa else "-"} %</td>'
                     f'<td>{ss.get("sous_triage","-") if ss else "-"}</td>'
                     f'<td>{sa.get("sous_triage","-") if sa else "-"}</td></tr>')
        html += '</table>'
        st.markdown(html,unsafe_allow_html=True)

        ui_sec("Evaluation des hypotheses de recherche")
        hypo = tester_hypotheses(sc)
        if hypo:
            for cle,h in hypo.items():
                ok_css = "hypo-ok" if h["valide"] else "hypo-fail"
                ok_lbl = "CONFIRMEE (donnees preliminaires)" if h["valide"] else "NON CONFIRMEE (donnees preliminaires)"
                ok_icn = "+" if h["valide"] else "-"
                st.markdown(
                    f'<div class="hypo-box {ok_css}">'
                    f'<div class="hypo-label">{cle} — {ok_icn} {ok_lbl}</div>'
                    f'{h["titre"]}<br>'
                    f'<small style="color:var(--txt-aide);">{h["detail"]}</small>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            ui_al("Donnees insuffisantes pour tester les hypotheses (les 4 cellules doivent contenir des donnees).","warn")

        if likert_data:
            ui_sec("Satisfaction Likert — Comparaison experimentes / debutants")
            items_lk = [
                ("facilite","Facilite d'utilisation"),("rapidite","Rapidite decision"),
                ("precision","Precision decision"),("alertes","Pertinence alertes"),
                ("charge_cog","Reduction charge cognitive"),("confiance","Confiance en l'outil"),
                ("compensation_exp","Compensation manque experience"),
                ("recommande_deb","Recommande pour debutants"),
                ("recommande_exp","Recommande pour experimentes"),
                ("formation","Support de formation"),
            ]
            lk_exp = [r for r in likert_data if r.get("experience_groupe")=="experimente"]
            lk_deb = [r for r in likert_data if r.get("experience_groupe")=="debutant"]
            html_lk = ('<table class="tableau-comp"><tr><th>Item Likert</th>'
                       '<th>Experimentes (moy/5)</th><th>Debutants (moy/5)</th><th>Ecart D-E</th></tr>')
            for cle,lbl in items_lk:
                ve = [r["reponses"].get(cle,3) for r in lk_exp if "reponses" in r]
                vd = [r["reponses"].get(cle,3) for r in lk_deb if "reponses" in r]
                me = round(sum(ve)/len(ve),2) if ve else "-"
                md = round(sum(vd)/len(vd),2) if vd else "-"
                if isinstance(me,float) and isinstance(md,float):
                    ec = round(md-me,2)
                    ecss = "diff-pos" if ec>0.3 else ("diff-neg" if ec<-0.3 else "diff-neu")
                    elbl = f'{("+" if ec>0 else "")}{ec}'
                else:
                    ecss="diff-neu"; elbl="-"
                html_lk += f'<tr><td>{lbl}</td><td>{me} (n={len(ve)})</td><td>{md} (n={len(vd)})</td><td class="{ecss}">{elbl}</td></tr>'
            html_lk += '</table>'
            st.markdown(html_lk,unsafe_allow_html=True)

        ui_sec("Export des donnees")
        csv_global = exporter_csv(triage_data)
        st.download_button(
            label="Exporter toutes les donnees triage (CSV — R / SPSS / Excel)",
            data=csv_global,
            file_name=f"akir_memoire_global_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True,
        )
        commentaires = [r.get("commentaire","").strip() for r in likert_data if r.get("commentaire","").strip()]
        if commentaires:
            ui_sec("Commentaires libres des participants")
            for i,c in enumerate(commentaires,1):
                grp = ([r.get("experience_groupe","?") for r in likert_data if r.get("commentaire","").strip()] + ["?"])[i-1]
                st.markdown(f'<div class="carte" style="font-size:.84rem;font-style:italic;">Participant {i} ({grp}) : "{c}"</div>',unsafe_allow_html=True)

    if st.button("Retour a l'accueil"):
        st.session_state.memoire_etape = "accueil"; st.rerun()

# ==============================================================================
# DISCLAIMER
# ==============================================================================

st.markdown(
    '<div class="disclaimer">'
    'Outil developpe dans le cadre d\'un memoire en sciences infirmieres. '
    'Vignettes cliniques fictives et standardisees a partir du referentiel FRENCH Triage SFMU V1.1 (Juin 2018). '
    'Donnees anonymisees — aucun nom ni prenom collecte — stockage local uniquement. '
    'Participation volontaire — droit de retrait a tout moment sans consequence.'
    '<div class="disclaimer-sig">'
    'AKIR-IAO Project — Module Memoire Sciences Infirmieres v2.0 — Ismail Ibn-Daifa<br>'
    'FRENCH Triage SFMU V1.1 — Wallonie, Belgique<br>'
    'Question de recherche : concordance IAO experimentes vs debutants — effet outil informatise'
    '</div></div>',
    unsafe_allow_html=True,
)