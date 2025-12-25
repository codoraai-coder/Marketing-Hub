import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, JoinColumn, OneToMany } from 'typeorm';
import { User } from './user.entity';
import { Content } from './content.entity';
import { Workflow } from './workflow.entity';
import { SocialAccount } from './social-account.entity';

@Entity('workspaces')
export class Workspace {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ name: 'owner_user_id' })
  ownerUserId: string;

  @Column()
  name: string;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @ManyToOne(() => User, user => user.workspaces)
  @JoinColumn({ name: 'owner_user_id' })
  owner: User;

  @OneToMany(() => Content, content => content.workspace)
  contents: Content[];

  @OneToMany(() => Workflow, workflow => workflow.workspace)
  workflows: Workflow[];

  @OneToMany(() => SocialAccount, socialAccount => socialAccount.workspace)
  socialAccounts: SocialAccount[];
}
