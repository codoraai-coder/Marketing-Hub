import { IsString, IsNotEmpty, IsUUID } from 'class-validator';

export class CreateWorkspaceDto {
  @IsUUID()
  @IsNotEmpty()
  ownerUserId: string;

  @IsString()
  @IsNotEmpty()
  name: string;
}
