import { IsEnum, IsNotEmpty } from 'class-validator';
import { ContentStatus } from '../../../entities/content.entity';

export class UpdateContentStatusDto {
  @IsEnum(ContentStatus)
  @IsNotEmpty()
  status: ContentStatus;
}
