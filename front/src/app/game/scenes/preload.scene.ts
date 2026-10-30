import Phaser from 'phaser';
import { PartieService } from '../../services/partie.service';
import { SallePublique } from '../../services/models';

export class PreloadScene extends Phaser.Scene {
  constructor() { super('Preload'); }

  preload() {
    // this.load.image(...)
  }

  create() {
    const partie = this.registry.get('partie') as PartieService;
    const salles = this.registry.get('salles') as SallePublique[];

    if (salles.length === 0) {
      this.add.text(480, 270, 'Aucune salle reçue du back', { color: '#f66' }).setOrigin(0.5);
      return;
    }
    const depart = salles.find(s => s.id === partie.salleCourante())?.id ?? salles[0].id;
    this.scene.start('Room', { roomId: depart });
  }
}