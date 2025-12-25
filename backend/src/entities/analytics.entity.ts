import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, ManyToOne, JoinColumn } from 'typeorm';
import { Content } from './content.entity';

@Entity('analytics')
export class Analytics {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ name: 'content_id' })
  contentId: string;

  @Column()
  platform: string;

  @Column({ default: 0 })
  likes: number;

  @Column({ default: 0 })
  comments: number;

  @Column({ default: 0 })
  shares: number;

  @Column({ default: 0 })
  impressions: number;

  @CreateDateColumn({ name: 'collected_at' })
  collectedAt: Date;

  @ManyToOne(() => Content, content => content.analytics)
  @JoinColumn({ name: 'content_id' })
  content: Content;
}
