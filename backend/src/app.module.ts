import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { AppController } from './app.controller';
import { AppService } from './app.service';

// Entities
import { User } from './entities/user.entity';
import { Workspace } from './entities/workspace.entity';
import { Content } from './entities/content.entity';
import { Workflow } from './entities/workflow.entity';
import { Job } from './entities/job.entity';
import { SocialAccount } from './entities/social-account.entity';
import { Analytics } from './entities/analytics.entity';

// Modules
import { WorkspaceModule } from './modules/workspace/workspace.module';
import { ContentModule } from './modules/content/content.module';
import { WorkflowModule } from './modules/workflow/workflow.module';
import { JobModule } from './modules/job/job.module';
import { McpModule } from './mcp/mcp.module';

@Module({
  imports: [
    // Configuration
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: '.env',
    }),

    // Database
    TypeOrmModule.forRootAsync({
      imports: [ConfigModule],
      useFactory: (configService: ConfigService) => ({
        type: 'postgres',
        host: configService.get('DATABASE_HOST'),
        port: configService.get('DATABASE_PORT'),
        username: configService.get('DATABASE_USERNAME'),
        password: configService.get('DATABASE_PASSWORD'),
        database: configService.get('DATABASE_NAME'),
        entities: [User, Workspace, Content, Workflow, Job, SocialAccount, Analytics],
        synchronize: true, // Set to false in production, use migrations
        logging: false,
        ssl: configService.get('DATABASE_SSL') === 'true' ? { rejectUnauthorized: false } : false,
        extra: {
          // Force IPv4
          family: 4,
        },
      }),
      inject: [ConfigService],
    }),

    // MCP Core (Master Control Program)
    McpModule,

    // Feature Modules
    WorkspaceModule,
    ContentModule,
    WorkflowModule,
    JobModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
