import os
from flask import Flask, render_template, request
from supabase import create_client

app = Flask(__name__)

# Ces informations seront lues directement depuis les réglages de Render
# pour ne pas que vos mots de passe soient publics sur GitHub
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    # 1. On récupère tous les motifs pour afficher les cases à cocher
    response = supabase.table("comptes_rendus").select("*").execute()
    return render_template('index.html', motifs=response.data)

@app.route('/fusionner', methods=['POST'])
def fusionner():
    # 2. On récupère les IDs cochés par l'utilisateur
    ids = request.form.getlist('motif_ids')
    
    # 3. On va chercher le texte de ces IDs dans Supabase
    response = supabase.table("comptes_rendus").select("*").in_("id", ids).execute()
    selection = response.data

    # 4. LA FUSION
    sections = [
        ("DIAGNOSTIC", "diagnostic"),
        ("SIGNES DE GRAVITÉ", "signes_gravite"),
        ("SOINS", "soins_urgences"),
        ("SORTIE", "conduite_a_tenir"),
        ("CONSEILS", "conseils"),
        ("ALERTE", "consignes_reconsultation")
    ]

    cr_final = ""
    for titre, col in sections:
        blocs = [item[col] for item in selection if item.get(col)]
        if blocs:
            cr_final += f"--- {titre} ---\n" + "\n".join(blocs) + "\n\n"

    # 5. On réaffiche la page avec le texte fusionné
    all_motifs = supabase.table("comptes_rendus").select("*").execute()
    return render_template('index.html', motifs=all_motifs.data, resultat=cr_final)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
