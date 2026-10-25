import Phaser from 'phaser';
import { BootScene } from './scenes/boot.scene';
import { PreloadScene } from './scenes/preload.scene';
import { RoomScene } from './scenes/room.scene';

export const gameConfig: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 960,
  height: 540,
  pixelArt: true,
  physics: {
    default: 'arcade',
    arcade: { gravity: { x: 0, y: 900 }, debug: true },
  },
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [BootScene, PreloadScene, RoomScene],
};