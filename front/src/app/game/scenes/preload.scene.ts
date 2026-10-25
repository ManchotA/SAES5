import Phaser from 'phaser';
export class PreloadScene extends Phaser.Scene {
  constructor() { super('Preload'); }
  preload() {
    // this.load.image('tiles', 'assets/tilemaps/tiles.png');
    // this.load.spritesheet('player', 'assets/sprites/player.png', { frameWidth: 32, frameHeight: 32 });
  }
  create() { this.scene.start('Level'); }
}