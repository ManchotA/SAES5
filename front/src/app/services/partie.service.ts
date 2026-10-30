import { Injectable, inject, signal } from '@angular/core';
import { Subject } from 'rxjs';
import { ApiService } from './api.service';
import { EvenementWs, Partie } from './models';

const CLE_SALLE = 'sae5.salleCourante';
function lireSalle(): string | null {
  try { return sessionStorage.getItem(CLE_SALLE); } catch { return null; }
}

@Injectable({ providedIn: 'root' })
export class PartieService {
  private api = inject(ApiService);
  private wsOuvert = false;

  readonly partie = signal<Partie | null>(null);
  readonly boitierConnecte = signal(true);
  readonly salleCourante = signal<string | null>(lireSalle());
  readonly evenements$ = new Subject<EvenementWs>();

  async init() {
    await this.rafraichir();
    if (!this.wsOuvert) {
      this.wsOuvert = true;
      this.connecterWs();
    }
  }

  async rafraichir() { this.partie.set(await this.api.getPartie()); }

  async nouvelle() {
    this.partie.set(await this.api.nouvellePartie());
    this.setSalleCourante(null);
  }

  async lancerEnigme(id: string)  { await this.api.lancerEnigme(id);  await this.rafraichir(); }
  async annulerEnigme(id: string) { await this.api.annulerEnigme(id); await this.rafraichir(); }

  setSalleCourante(id: string | null) {
    this.salleCourante.set(id);
    try {
      if (id) sessionStorage.setItem(CLE_SALLE, id);
      else sessionStorage.removeItem(CLE_SALLE);
    } catch { /* stockage indisponible */ }
  }

  private connecterWs() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${location.host}/ws`);

    ws.onmessage = (m) => {
      const ev: EvenementWs = JSON.parse(m.data);
      this.partie.set(ev.partie);
      if (ev.type === 'boitier_deconnecte') this.boitierConnecte.set(false);
      if (ev.type === 'boitier_reconnecte') this.boitierConnecte.set(true);
      this.evenements$.next(ev);
    };

    ws.onclose = () => setTimeout(() => this.connecterWs(), 2000);
  }
}