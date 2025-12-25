import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Content, ContentType, ContentStatus } from '../../entities/content.entity';
import { CreateContentDto } from './dto/create-content.dto';

@Injectable()
export class ContentService {
  constructor(
    @InjectRepository(Content)
    private readonly contentRepository: Repository<Content>,
  ) {}

  async create(createContentDto: CreateContentDto): Promise<Content> {
    const content = this.contentRepository.create(createContentDto);
    return this.contentRepository.save(content);
  }

  async findOne(id: string): Promise<Content> {
    const content = await this.contentRepository.findOne({
      where: { id },
      relations: ['workspace'],
    });

    if (!content) {
      throw new NotFoundException(`Content ${id} not found`);
    }

    return content;
  }

  async findByWorkspace(
    workspaceId: string,
    type?: string,
    status?: string,
  ): Promise<Content[]> {
    const query: any = { workspaceId };

    if (type) {
      query.type = type as ContentType;
    }

    if (status) {
      query.status = status as ContentStatus;
    }

    return this.contentRepository.find({
      where: query,
      order: { createdAt: 'DESC' },
    });
  }

  async updateStatus(id: string, status: ContentStatus): Promise<Content> {
    const content = await this.findOne(id);
    content.status = status;
    return this.contentRepository.save(content);
  }
}
