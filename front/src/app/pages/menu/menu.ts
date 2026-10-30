import { Component, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { PartieService } from '../../services/partie.service';
import { ParametresService } from '../../services/parametres.service';

@Component({
  selector: 'app-menu',
  standalone: true,
  template: `
    <main class="menu">
      <h1>Titre du jeu</h1>

      @if (erreur()) { <p class="erreur">{{ erreur() }}</p> }

      @if (!parametresOuverts()) {
        <button (click)="nouvellePartie()" [disabled]="!!erreur()">Nouvelle partie</button>
        @if (enCours()) {
          <button (click)="continuer()">Continuer</button>
        }
        <button (click)="parametresOuverts.set(true)">Paramètres</button>
      } @else {
        <section class="parametres">
          <label>
            Volume : {{ params.valeurs().volume }}
            <input type="range" min="0" max="100"
                   [value]="params.valeurs().volume" (input)="changerVolume($event)" />
          </label>
          <label>
            <input type="checkbox"
                   [checked]="params.valeurs().afficherChrono" (change)="changerChrono($event)" />
            Afficher le chrono
          </label>
          <button (click)="pleinEcran()">Plein écran</button>
          <button (click)="parametresOuverts.set(false)">Retour</button>
        </section>
      }
    </main>
  `,
  styles: [`
    .menu { min-height: 100vh; display: flex; flex-direction: column; align-items: center;
            justify-content: center; gap: 1rem; color: #fff; font-family: sans-serif; }
    h1 { font-size: 3rem; margin: 0 0 1.5rem; }
    button { min-width: 240px; padding: .8rem 1.2rem; font-size: 1.1rem; cursor: pointer;
             border: 0; border-radius: 6px; background: #3388ff; color: #fff; }
    button:disabled { background: #555; cursor: not-allowed; }
    .parametres { display: flex; flex-direction: column; gap: 1rem; align-items: center; }
    .erreur { color: #f66; }
  `],
})
export class MenuComponent {
  private router = inject(Router);
  private partie = inject(PartieService);
  protected params = inject(ParametresService);

  protected erreur = signal('');
  protected parametresOuverts = signal(false);
  protected enCours = computed(() => this.partie.partie()?.statut === 'en_cours');

  constructor() {
    this.partie.init().catch(() =>
      this.erreur.set('Impossible de joindre le back. Est-il lancé ?'));
  }

  async nouvellePartie() {
    if (this.enCours() && !confirm('Une partie est en cours. La recommencer depuis le début ?')) return;
    try {
      await this.partie.nouvelle();
      this.router.navigate(['/jeu']);
    } catch {
      this.erreur.set('Impossible de lancer la partie.');
    }
  }

  continuer() { this.router.navigate(['/jeu']); }

  changerVolume(e: Event) {
    this.params.maj({ volume: +(e.target as HTMLInputElement).value });
  }
  changerChrono(e: Event) {
    this.params.maj({ afficherChrono: (e.target as HTMLInputElement).checked });
  }
  pleinEcran() { document.documentElement.requestFullscreen?.(); }
}