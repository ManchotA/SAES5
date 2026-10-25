import Phaser from 'phaser';
import { Subscription } from 'rxjs';
import { PartieService } from '../../services/partie.service';
import { SallePublique } from '../../services/models';

export class RoomScene extends Phaser.Scene {
  private roomId = '';
  private partie!: PartieService;
  private player!: Phaser.GameObjects.Rectangle;
  private panneau!: Phaser.GameObjects.Rectangle;
  private porte!: Phaser.GameObjects.Rectangle;
  private chrono!: Phaser.GameObjects.Text;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private touchE!: Phaser.Input.Keyboard.Key;
  private abonnement?: Subscription;

  constructor() { super('Room'); }
  init(data: { roomId: string }) { this.roomId = data.roomId; }

  create() {
    this.partie = this.registry.get('partie');
    const salle = (this.registry.get('salles') as SallePublique[]).find(s => s.id === this.roomId)!;

    this.add.text(480, 30, `${salle.nom} (étage ${salle.etage})`, { fontSize: '24px', color: '#fff' }).setOrigin(0.5);
    this.chrono = this.add.text(940, 20, '', { fontSize: '24px', color: '#ff0' }).setOrigin(1, 0);

    const sol = this.add.rectangle(480, 520, 960, 40, 0x555555);
    this.physics.add.existing(sol, true);
    this.player = this.add.rectangle(100, 440, 24, 40, 0x44aaff);
    this.physics.add.existing(this.player);
    (this.player.body as Phaser.Physics.Arcade.Body).setCollideWorldBounds(true);
    this.physics.add.collider(this.player, sol);

    this.panneau = this.add.rectangle(480, 480, 40, 70, 0x3388ff);
    this.porte = this.add.rectangle(880, 470, 50, 100, 0x884422);

    this.cursors = this.input.keyboard!.createCursorKeys();
    this.touchE = this.input.keyboard!.addKey('E');

    this.majPorte();
    this.abonnement = this.partie.evenements$.subscribe(ev => {
      if (ev.type === 'enigme_resolue' && ev.salle === this.roomId) this.majPorte();
    });
    this.events.once('shutdown', () => this.abonnement?.unsubscribe());
  }

  override update() {
    const body = this.player.body as Phaser.Physics.Arcade.Body;
    body.setVelocityX(this.cursors.left.isDown ? -180 : this.cursors.right.isDown ? 180 : 0);
    if (this.cursors.up.isDown && body.blocked.down) body.setVelocityY(-450);

    if (Phaser.Input.Keyboard.JustDown(this.touchE) &&
        Math.abs(this.player.x - this.panneau.x) < 50) {
      this.partie.lancerEnigme(this.roomId).catch(e => console.warn(e.error?.erreur ?? e));
    }

    // Chrono : recalculé à chaque image depuis fin_a, comme le prévoit le contrat
    const fin = this.partie.partie()?.fin_a;
    if (fin) {
      const reste = Math.max(0, Math.floor((new Date(fin).getTime() - Date.now()) / 1000));
      this.chrono.setText(`${Math.floor(reste / 60)}:${String(reste % 60).padStart(2, '0')}`);
    }
  }

  private majPorte() {
    const resolue = this.partie.partie()?.salles_resolues.includes(this.roomId);
    this.porte.setFillStyle(resolue ? 0x44aa44 : 0x884422);   // vert = ouverte
  }
}