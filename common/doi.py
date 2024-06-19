import uuid


class DOIManager:
    def __init__(self, db, doi_model):
        self.db = db
        self.DOI = doi_model  # Utilisation directe de l'instance de la classe DOI

    def enregistrer_doi(self, prefixe, titre, auteur, date, type_objet):
        suffixe = str(uuid.uuid4())
        doi = f"{prefixe}/{suffixe}"

        nouvel_objet = self.DOI(
            doi=doi,
            titre=titre,
            auteur=auteur,
            date=date,
            type=type_objet
        )

        self.db.session.add(nouvel_objet)
        self.db.session.commit()

        return doi

    def resoudre_doi(self, doi):
        objet = self.DOI.query.filter_by(doi=doi).first()
        if objet:
            return {
                'doi': objet.doi,
                'titre': objet.titre,
                'auteur': objet.auteur,
                'date': objet.date,
                'type': objet.type
            }
        else:
            return None
