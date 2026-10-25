import { Injectable, inject, signal } from '@angular/core';
import { Subject } from 'rxjs';
import { ApiService } from './api.service';
import { EvenementWs, Partie } from './models';

@Injectable({ providedIn: 'root' })
export class PartieService {
  private api = inject(ApiService);

  readonly partie = signal<Partie | null>(null);
  readonly boitierConnecte = signal(true);
  readonly evenements$ = new Subject<EvenementWs>();

  async init() {
    await this.rafraichir();
    this.connecterWs();
  }

  async rafraichir()  { this.partie.set(await this.api.getPartie()); }
  async nouvelle()    { this.partie.set(await this.api.nouvellePartie()); }

  async lancerEnigme(id: string)  { await this.api.lancerEnigme(id);  await this.rafraichir(); }
  async annulerEnigme(id: string) { await this.api.annulerEnigme(id); await this.rafraichir(); }

  private connecterWs() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${location.host}/ws`);

    ws.onmessage = (m) => {
      const ev: EvenementWs = JSON.parse(m.data);
      this.partie.set(ev.partie);   // l'état complet est dans chaque message
      if (ev.type === 'boitier_deconnecte') this.boitierConnecte.set(false);
      if (ev.type === 'boitier_reconnecte') this.boitierConnecte.set(true);
      this.evenements$.next(ev);
    };

    ws.onclose = () => setTimeout(() => this.connecterWs(), 2000);   // reconnexion automatique
  }
}