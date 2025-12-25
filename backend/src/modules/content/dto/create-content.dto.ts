import { IsString, IsNotEmpty, IsUUID, IsEnum, IsOptional } from 'class-validator';
import { ContentType, ContentStatus } from '../../../entities/content.entity';

export class CreateContentDto {
  @IsUUID()
  @IsNotEmpty()
  workspaceId: string;

  @IsEnum(ContentType)
  @IsNotEmpty()
  type: ContentType;

  @IsString()
  @IsOptional()
  s3Url?: string;

  @IsString()
  @IsOptional()
  textData?: string;

  @IsEnum(ContentStatus)
  @IsOptional()
  status?: ContentStatus;
}
