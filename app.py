import os
from flask import Flask, render_template, request
from supabase import create_client

app = Flask(__name__)

# Récupération des clés configurées dans l'onglet Environment de Render
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    # Récupère tous les motifs dans Supabase pour afficher les cases à cocher
    response = supabase.table("comptes_rendus").select("*").execute()
    return render_template('index.html', motifs=response.data)

@app.route('/fusionner', methods=['POST'])
def fusionner():
    ids = request.form.getlist('motif_ids')
    if not ids:
        return "Aucun motif sélectionné. Veuillez revenir en arrière."

    # Récupère les données des motifs cochés
    response = supabase.table("comptes_rendus").select("*").in_("id", ids).execute()
    selection = response.data

    # Ordre de fusion des sections
    sections = [
        ("DIAGNOSTIC", "diagnostic"),
        ("SIGNES DE GRAVITÉ", "signes_gravite"),
        ("SOINS", "soins_urgences"),
        ("CAT", "conduite_a_tenir"),
        ("CONSEILS", "conseils"),
        ("RECONSULTATION", "consignes_reconsultation")
    ]

    cr_final = ""
    for titre, col in sections:
        blocs = [item[col] for item in selection if item.get(col)]
        if blocs:
            cr_final += f"--- {titre} ---\n" + "\n".join(blocs) + "\n\n"

    # Réaffiche la page avec le résultat
    all_motifs = supabase.table("comptes_rendus").select("*").execute()
    return render_template('index.html', motifs=all_motifs.data, resultat=cr_final)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)