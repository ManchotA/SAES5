import Phaser from 'phaser';

export class LevelScene extends Phaser.Scene {
  private player!: Phaser.GameObjects.Rectangle;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;

  constructor() { super('Level'); }

  create() {
    const ground = this.add.rectangle(480, 520, 960, 40, 0x555555);
    this.physics.add.existing(ground, true); // true = statique

    this.player = this.add.rectangle(100, 300, 24, 40, 0x44aaff);
    this.physics.add.existing(this.player);
    const body = this.player.body as Phaser.Physics.Arcade.Body;
    body.setCollideWorldBounds(true);

    this.physics.add.collider(this.player, ground);
    this.cursors = this.input.keyboard!.createCursorKeys();
  }

  override update() {
    const body = this.player.body as Phaser.Physics.Arcade.Body;
    if (this.cursors.left.isDown) body.setVelocityX(-180);
    else if (this.cursors.right.isDown) body.setVelocityX(180);
    else body.setVelocityX(0);

    if (this.cursors.up.isDown && body.blocked.down) body.setVelocityY(-450);
  }
}