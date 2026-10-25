export interface DocumentSalle { id: string; titre: string; texte: string; }

export interface SallePublique {
  id: string;
  etage: number;
  nom: string;
  documents: DocumentSalle[];
}

export type Statut = 'aucune' | 'en_cours' | 'gagnee' | 'perdue';

export interface Partie {
  statut: Statut;
  fin_a: string | null;
  etages_ouverts: number[];
  salles_resolues: string[];
  enigme_en_cours: string | null;
}

export type TypeEvenement =
  | 'enigme_resolue'
  | 'partie_terminee'
  | 'boitier_deconnecte'
  | 'boitier_reconnecte';

export interface EvenementWs {
  type: TypeEvenement;
  salle?: string;
  partie: Partie;
}