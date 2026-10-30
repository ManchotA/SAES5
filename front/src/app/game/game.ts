import { Component, ElementRef, NgZone, OnDestroy, AfterViewInit, ViewChild, inject } from '@angular/core';
import { Router } from '@angular/router';
import Phaser from 'phaser';
import { gameConfig } from './game.config';
import { ApiService } from '../services/api.service';
import { PartieService } from '../services/partie.service';
import { ParametresService } from '../services/parametres.service';

@Component({
  selector: 'app-game',
  standalone: true,
  template: `
    @if (erreur) { <p class="erreur">{{ erreur }}</p> }
    <div #host class="game-host"></div>
  `,
  styles: [`
    .game-host { width: 100%; height: 100vh; display: flex; justify-content: center; }
    .erreur { position: absolute; top: 1rem; left: 1rem; color: #f66; font-family: sans-serif; }
  `],
})
export class GameComponent implements AfterViewInit, OnDestroy {
  @ViewChild('host', { static: true }) host!: ElementRef<HTMLDivElement>;

  private zone = inject(NgZone);
  private router = inject(Router);
  private api = inject(ApiService);
  private partie = inject(PartieService);
  private parametres = inject(ParametresService);
  private game?: Phaser.Game;
  private detruit = false;

  erreur = '';

  async ngAfterViewInit() {
    try {
      const salles = await this.api.getSalles();
      await this.partie.init();

      if (this.detruit) return;
      if (this.partie.partie()?.statut !== 'en_cours') {   // pas de partie : retour au menu
        this.router.navigate(['/']);
        return;
      }

      this.zone.runOutsideAngular(() => {
        this.game = new Phaser.Game({
          ...gameConfig,
          parent: this.host.nativeElement,
          callbacks: {
            preBoot: (game) => {
              game.registry.set('api', this.api);
              game.registry.set('partie', this.partie);
              game.registry.set('parametres', this.parametres);
              game.registry.set('salles', salles);
              game.registry.set('retourMenu', () => this.zone.run(() => this.router.navigate(['/'])));
            },
          },
        });
      });
    } catch (e) {
      console.error(e);
      this.erreur = 'Impossible de joindre le back. Est-il lancé ?';
    }
  }

  ngOnDestroy() {
    this.detruit = true;
    this.game?.destroy(true);
  }
}