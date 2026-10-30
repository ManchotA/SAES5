import { Injectable, signal } from '@angular/core';

export interface Parametres {
  volume: number;          // 0 à 100
  afficherChrono: boolean;
}

const DEFAUT: Parametres = { volume: 70, afficherChrono: true };
const CLE = 'sae5.parametres';

@Injectable({ providedIn: 'root' })
export class ParametresService {
  readonly valeurs = signal<Parametres>(this.charger());

  maj(modif: Partial<Parametres>) {
    this.valeurs.update(v => ({ ...v, ...modif }));
    this.sauver();
  }

  private charger(): Parametres {
    try { return { ...DEFAUT, ...JSON.parse(localStorage.getItem(CLE) ?? '{}') }; }
    catch { return { ...DEFAUT }; }
  }

  private sauver() {
    try { localStorage.setItem(CLE, JSON.stringify(this.valeurs())); } catch { /* stockage indisponible */ }
  }
}