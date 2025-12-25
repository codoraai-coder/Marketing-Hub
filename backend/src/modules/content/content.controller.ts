import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { ContentService } from './content.service';
import { CreateContentDto } from './dto/create-content.dto';
import { UpdateContentStatusDto } from './dto/update-content-status.dto';

@Controller('content')
export class ContentController {
  constructor(private readonly contentService: ContentService) {}

  @Post()
  async create(@Body() createContentDto: CreateContentDto) {
    return this.contentService.create(createContentDto);
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.contentService.findOne(id);
  }

  @Get('workspace/:workspaceId')
  async findByWorkspace(
    @Param('workspaceId') workspaceId: string,
    @Query('type') type?: string,
    @Query('status') status?: string,
  ) {
    return this.contentService.findByWorkspace(workspaceId, type, status);
  }

  @Post(':id/status')
  async updateStatus(
    @Param('id') id: string,
    @Body() updateStatusDto: UpdateContentStatusDto,
  ) {
    return this.contentService.updateStatus(id, updateStatusDto.status);
  }
}
