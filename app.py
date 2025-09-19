# app.py — Évaluateur GIR (conversationnel, corrigé)
# -------------------------------------------------
import streamlit as st

st.set_page_config(page_title="Évaluation GIR (indicative)", page_icon="🧭", layout="centered")

# ---- Style plus doux (gris ardoise) -----------------------------------------
st.markdown("""
<style>
:root {
  --primary-color: #64748b;              /* slate-500 */
}
button[kind="primary"] {
  background: #64748b !important;
  border-color: #64748b !important;
}
button[kind="primary"]:hover {
  background: #475569 !important;        /* slate-600 */
  border-color: #475569 !important;
}
div[data-testid="stRadio"] label { font-weight: 500; color:#374151; } /* text-gray-700 */
.small { font-size: 0.92rem; color: #5b5b5b; }
.muted { color:#6b7280; }
.card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 1rem 1.1rem; background: #fff; }
.step { font-weight: 600; color:#374151; font-size: 0.95rem; margin-bottom: 0.2rem; }
.emph { font-weight: 600; color:#111827; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

# ---- Intro -------------------------------------------------------------------
st.title("🧭 Évaluation de l’autonomie — GIR (version indicative)")
st.caption("Un repère pour ouvrir la discussion — seule une **évaluation à domicile** réalisée par un(e) professionnel(le) médico-social(e) fait foi.")

with st.expander("ℹ️ La grille AGGIR, en deux mots", expanded=True):
    st.markdown(
        "- La **grille AGGIR** permet d'apprécier l’autonomie au quotidien et classe en **GIR 1 à 6**.\n"
        "- **GIR 1–4** : pertes d’autonomie ouvrant en général droit à l’**APA**.\n"
        "- **GIR 5–6** : autonomie globalement préservée, avec possibilités d’**aides de prévention**.\n\n"
        "Ressources officielles :\n"
        "- Explications grand public : "
        "https://www.pour-les-personnes-agees.gouv.fr/preserver-son-autonomie/perte-d-autonomie-evaluation-et-droits/comment-fonctionne-la-grille-aggir\n"
        "- Faire une **demande d’aides à l’autonomie à domicile** : "
        "https://www.pour-les-personnes-agees.gouv.fr/vivre-a-domicile/beneficier-d-aide-a-domicile/faire-une-demande-d-aides-a-l-autonomie-a-domicile\n"
    )
    st.markdown(
        "💡 *Ici, on pose des questions simples, comme le ferait un proche ou un(e) travailleur(se) social(e). "
        "Répondez spontanément; il n’y a pas de « bonne » réponse.*"
    )

# ---- Questions (formulation humaine) -----------------------------------------
QUESTIONS = [
    ("Cohérence", "🧠", "Au quotidien, est-ce que vous vous sentez clair(e) dans vos idées, "
     "capable de faire des choix et de vous faire comprendre sans difficulté ?"),
    ("Orientation", "🧭", "Vous repérer dans le temps et les lieux est-il facile (date, rendez-vous, trajet connu) ?"),
    ("Toilette", "🚿", "Pour la toilette (se laver, se sécher), vous débrouillez-vous sans aide ?"),
    ("Habillage", "👕", "Pour vous habiller (choix des vêtements, fermetures, chaussures), ça va tout seul ?"),
    ("Alimentation", "🍽️", "Pour préparer/prendre vos repas et boire suffisamment, avez-vous besoin d’un coup de main ?"),
    ("Élimination", "🚻", "Aller aux toilettes (y aller, s’installer, se rhabiller) est-ce gérable seul(e) ?"),
    ("Transferts", "🧍‍♀️", "Vous lever, vous asseoir, vous coucher — pouvez-vous le faire sans assistance ?"),
    ("Déplacements intérieurs", "🏠", "Vous déplacer **dans le logement** (avec ou sans aide technique), est-ce aisé ?"),
    ("Déplacements extérieurs", "🚶", "Sortir **à l’extérieur** pour de petites courses/rendez-vous : le faites-vous sans aide humaine ?"),
    ("Communication", "☎️", "Téléphone, sonnette, alarme : êtes-vous à l’aise pour **joindre quelqu’un** en cas de besoin ?"),
]
CHOICES = { 0: "Je fais seul(e) sans difficulté", 1: "J’ai parfois besoin d’un coup de main", 2: "J’ai souvent besoin d’aide" }

VARS7 = [
    ("activité_physique", "🤸", "Bouger un peu chaque jour (marche, étirements) vous est-il facile en ce moment ?"),
    ("nutrition_hydratation", "🥤", "Buvez-vous suffisamment et vos repas sont-ils réguliers et équilibrés ?"),
    ("sommeil", "🌙", "Votre sommeil est-il plutôt réparateur ?"),
    ("vision_audition", "👓", "Vision et audition : êtes-vous bien équipé(e) (lunettes, appareil) et à jour des contrôles ?"),
    ("sécurité_logement", "🛠️", "Votre logement est-il sécurisé (éclairage, tapis antidérapants, barres d’appui) ?"),
    ("liens_sociaux", "🤝", "Avez-vous des contacts réguliers (famille, voisins, associations) ?"),
    ("administratif_budget", "📄", "Vous sentez-vous à l’aise avec les démarches administratives et le budget ?"),
]
VARS_CHOICES = { 0: "Oui, plutôt", 1: "Ça pourrait aller mieux", 2: "C’est difficile en ce moment" }

# ---- État & navigation -------------------------------------------------------
if "step" not in st.session_state: st.session_state.step = 0
if "answers" not in st.session_state: st.session_state.answers = {}
if "vars7" not in st.session_state: st.session_state.vars7 = {}

total_steps = len(QUESTIONS) + len(VARS7)

def next_step(): st.session_state.step = min(st.session_state.step + 1, total_steps)
def prev_step(): st.session_state.step = max(st.session_state.step - 1, 0)

# ---- Progression -------------------------------------------------------------
st.progress(st.session_state.step / total_steps, text=f"Étape {st.session_state.step} / {total_steps}")

# Helper pour un radio “obligatoire” (avec sentinelle)
def required_radio(key: str, options_map: dict, sentinel_label="— Choisir une réponse —"):
    """
    Affiche un radio avec une première option sentinelle (-1).
    Retourne (valeur, is_selected)
    """
    opts = [-1] + list(options_map.keys())
    fmt = lambda v: sentinel_label if v == -1 else options_map[v]
    # index par défaut = 0 (sentinelle) si pas de state antérieur
    index = 0
    if key in st.session_state:
        try:
            index = opts.index(st.session_state[key])
        except ValueError:
            index = 0
    val = st.radio(" ", options=opts, index=index, format_func=fmt,
                   key=key, label_visibility="collapsed")
    return val, (val != -1)

# ---- Corps -------------------------------------------------------------------
with st.container():
    # 0..9 : items AGGIR
    if st.session_state.step < len(QUESTIONS):
        idx = st.session_state.step
        code, icon, prompt = QUESTIONS[idx]

        st.markdown(f"<div class='card'><div class='step'>{icon} {code}</div>{prompt}</div>", unsafe_allow_html=True)

        val, ok = required_radio(f"q_{code}", CHOICES)
        if ok:
            st.session_state.answers[code] = int(val)

        c1, c2 = st.columns(2)
        with c1:
            st.button("Précédent", use_container_width=True, on_click=prev_step, disabled=(idx == 0), key=f"prev_q_{idx}")
        with c2:
            st.button("Continuer", use_container_width=True, on_click=next_step, disabled=not ok, key=f"next_q_{idx}")

    # 10..16 : 7 variables illustratives
    elif st.session_state.step < len(QUESTIONS) + len(VARS7):
        idx = st.session_state.step - len(QUESTIONS)
        code, icon, prompt = VARS7[idx]

        st.markdown(f"<div class='card'><div class='step'>{icon} Prévention — {code.replace('_',' ').title()}</div>{prompt}</div>", unsafe_allow_html=True)

        val, ok = required_radio(f"v_{code}", VARS_CHOICES)
        if ok:
            st.session_state.vars7[code] = int(val)

        is_last = (idx == len(VARS7) - 1)
        c1, c2 = st.columns(2)
        with c1:
            st.button("Précédent", use_container_width=True, on_click=prev_step, key=f"prev_v_{idx}")
        with c2:
            st.button("Voir mon résultat" if is_last else "Continuer",
                      use_container_width=True, on_click=next_step, disabled=not ok, key=f"next_v_{idx}")

    # Résultat final
    else:
        st.header("Votre résultat (indicatif)")

        # -- calcul GIR simplifié
        ans = st.session_state.answers
        vals = list(ans.values())
        severe = sum(1 for v in vals if v == 2)
        partial = sum(1 for v in vals if v == 1)
        sev_keys = {k for k, v in ans.items() if v == 2}

        if severe >= 4 and ("Cohérence" in sev_keys or "Orientation" in sev_keys):
            gir = 1
        elif severe >= 2:
            gir = 2
        elif severe >= 1 and partial >= 2:
            gir = 3
        elif partial >= 1:
            gir = 4
        else:
            gir = 6 if severe == 0 and partial == 0 else 5

        DESCR = {
            1: "Dépendance très lourde, besoin d’aide continue.",
            2: "Aide importante (confinement ou altérations cognitives marquées).",
            3: "Aide pluri-quotidienne pour l’autonomie corporelle.",
            4: "Aide ponctuelle pour certains actes (transferts, toilette, repas…).",
            5: "Autonomie globale, possibles aides ménagères / prévention.",
            6: "Autonomie pour les actes essentiels.",
        }

        c1, c2 = st.columns([1,1])
        with c1:
            st.metric("**GIR estimé**", f"{gir}")
            st.write(f"<span class='muted'>{DESCR[gir]}</span>", unsafe_allow_html=True)
        with c2:
            if gir in (1,2,3,4):
                st.success("**Prochaine étape** : déposer une **demande d’aide à l’autonomie** (dossier **commun APA + aides des caisses de retraite**) auprès de **votre Département**.")
            else:
                st.info("**Prévention** : en **GIR 5–6**, pensez aux **aides de prévention** via votre **caisse de retraite** (CARSAT le plus souvent).")

        st.markdown(
            "Ressources :\n"
            "- Demande d’aides à l’autonomie à domicile : "
            "https://www.pour-les-personnes-agees.gouv.fr/vivre-a-domicile/beneficier-d-aide-a-domicile/faire-une-demande-d-aides-a-l-autonomie-a-domicile\n"
            "- Comprendre la grille AGGIR : "
            "https://www.pour-les-personnes-agees.gouv.fr/preserver-son-autonomie/perte-d-autonomie-evaluation-et-droits/comment-fonctionne-la-grille-aggir"
        )

        st.divider()

        # -- Points d’attention (AGGIR)
        need_help = [k for k, v in ans.items() if v in (1,2)]
        st.subheader("Points d’attention repérés")
        if need_help:
            for k in need_help:
                st.write(f"• **{k}** — {CHOICES[ans[k]]}")
        else:
            st.write("Aucun besoin particulier signalé. Restez à l’écoute de votre ressenti, c’est le meilleur indicateur.")

        # -- Conseils de prévention ciblés
        PREV_TIPS_AGGIR = {
            "Cohérence": "Parler chaque jour avec un proche, tenir un petit carnet de repères (rendez-vous, médicaments), consulter si des troubles apparaissent.",
            "Orientation": "Affichage visible du calendrier et de l’horloge, routines quotidiennes stables, accompagnement ponctuel si nouveaux trajets.",
            "Toilette": "Installer **barres d’appui**, tapis antidérapant, siège de douche. Préparer le nécessaire à portée de main.",
            "Habillage": "Vêtements faciles à enfiler (scratch, fermetures simples), s’asseoir pour s’habiller.",
            "Alimentation": "Repas réguliers, hydratation tout au long de la journée, portage de repas si besoin.",
            "Élimination": "Accès WC dégagé, rehausseur/poignées, éclairage nocturne, surveillance des épisodes de fuites/infections.",
            "Transferts": "Chaise stable, lit à bonne hauteur, gestes sécurisés. Évaluer une aide technique (cannes, verticalisateur).",
            "Déplacements intérieurs": "Dégager les passages, supprimer les tapis glissants, éclairage automatique (détecteurs).",
            "Déplacements extérieurs": "Sorties accompagnées si besoin, parcours connus, canne ou déambulateur, carte de priorité si éligible.",
            "Communication": "Téléphone simplifié, numéros d’urgence en favori, médaillon/bracelet d’alerte si isolement.",
        }
        tips = [f"• **{k}** — {PREV_TIPS_AGGIR[k]}" for k in need_help if k in PREV_TIPS_AGGIR]
        if tips:
            for t in tips: st.write(t)

        st.divider()

        # -- 7 variables -> priorités
        st.subheader("Conseils d’autonomie — vos priorités du moment")
        v = st.session_state.vars7
        VARS_TIPS = {
            "activité_physique": "Bouger un peu chaque jour (marche douce, exercices assis/debout), même 10–15 min, est très utile.",
            "nutrition_hydratation": "Fractionner les repas, varier les textures, penser aux boissons chaudes/froides, soupes, compotes.",
            "sommeil": "Rythme régulier, lumière naturelle en journée, limiter les écrans le soir, tisane si besoin.",
            "vision_audition": "Contrôle annuel, nettoyer lunettes/appareils, bon éclairage et contrastes au domicile.",
            "sécurité_logement": "Éliminer obstacles, tapis antidérapants, barres d’appui, veilleuses de nuit.",
            "liens_sociaux": "Appeler un proche, passer à l’association ou au club local, visites de convivialité.",
            "administratif_budget": "Mettre en place des **prélèvements automatiques**, ranger les papiers au même endroit, demander un **accompagnement social** si besoin.",
        }
        any_prio = False
        for code, _, label in VARS7:
            if v.get(code, 0) >= 1:
                any_prio = True
                st.write(f"• **{label}** — {VARS_TIPS[code]}")
        if not any_prio:
            st.write("Rien de particulier à signaler. Continuez sur cette bonne dynamique ✅")

        st.divider()
        st.markdown(
            "🔗 Pour une **première estimation financière** (participation, aides, heures possibles), "
            "essayez le **simulateur** : "
            "[habitat-intermediaire.fr/aides](https://habitat-intermediaire.fr/aides)"
        )

        st.button("🔁 Refaire l’évaluation", on_click=lambda: (st.session_state.clear(), None), type="secondary")
