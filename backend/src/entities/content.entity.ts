import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, JoinColumn, OneToMany } from 'typeorm';
import { Workspace } from './workspace.entity';
import { Analytics } from './analytics.entity';

export enum ContentType {
  BLOG = 'blog',
  IMAGE = 'image',
  CAPTION = 'caption',
  DOC = 'doc',
}

export enum ContentStatus {
  DRAFT = 'draft',
  APPROVED = 'approved',
  USED = 'used',
  POSTED = 'posted',
}

@Entity('contents')
export class Content {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ name: 'workspace_id' })
  workspaceId: string;

  @Column({
    type: 'enum',
    enum: ContentType,
  })
  type: ContentType;

  @Column({ name: 's3_url', nullable: true })
  s3Url: string | null;

  @Column({ name: 'text_data', type: 'text', nullable: true })
  textData: string | null;

  @Column({
    type: 'enum',
    enum: ContentStatus,
    default: ContentStatus.DRAFT,
  })
  status: ContentStatus;

  @CreateDateColumn({ name: 'created_at' })
  createdAt: Date;

  @ManyToOne(() => Workspace, workspace => workspace.contents)
  @JoinColumn({ name: 'workspace_id' })
  workspace: Workspace;

  @OneToMany(() => Analytics, analytics => analytics.content)
  analytics: Analytics[];
}
