import { Component, ElementRef, NgZone, OnDestroy, AfterViewInit, ViewChild } from '@angular/core';
import Phaser from 'phaser';
import { gameConfig } from './game.config';

@Component({
  selector: 'app-game',
  standalone: true,
  template: `<div #host class="game-host"></div>`,
  styles: [`.game-host { width: 100%; height: 100vh; display: flex; justify-content: center; }`],
})
export class GameComponent implements AfterViewInit, OnDestroy {
  @ViewChild('host', { static: true }) host!: ElementRef<HTMLDivElement>;
  private game?: Phaser.Game;

  constructor(private zone: NgZone) {}

  ngAfterViewInit() {
    // Phaser tourne hors zone Angular pour éviter des détections de changements à chaque frame
    this.zone.runOutsideAngular(() => {
      this.game = new Phaser.Game({ ...gameConfig, parent: this.host.nativeElement });
    });
  }

  ngOnDestroy() {
    this.game?.destroy(true);
  }
}