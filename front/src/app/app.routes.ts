import { Routes } from '@angular/router';
import { MenuComponent } from './pages/menu/menu';
import { GameComponent } from './game/game';

export const routes: Routes = [
  { path: '', component: MenuComponent },
  { path: 'jeu', component: GameComponent },
  { path: '**', redirectTo: '' },
];