import Phaser from 'phaser';
import { PartieService } from '../../services/partie.service';
import { SallePublique } from '../../services/models';
export class PreloadScene extends Phaser.Scene {
  constructor() { super('Preload'); }
  preload() {
    // this.load.image('tiles', 'assets/tilemaps/tiles.png');
    // this.load.spritesheet('player', 'assets/sprites/player.png', { frameWidth: 32, frameHeight: 32 });
  }
  async create() {
  const partie = this.registry.get('partie') as PartieService;
  if (partie.partie()?.statut !== 'en_cours') await partie.nouvelle();   // provisoire
  const salles = this.registry.get('salles') as SallePublique[];
  this.scene.start('Room', { roomId: salles[0].id });
}
}