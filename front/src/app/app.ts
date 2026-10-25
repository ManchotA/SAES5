import { Component } from '@angular/core';
import { GameComponent } from './game/game';

@Component({
  selector: 'app-root',
  imports: [GameComponent],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {}