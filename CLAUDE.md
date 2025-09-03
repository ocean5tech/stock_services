# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a stock services backend API project intended for deployment on server IP `35.77.54.203`. The repository is designed for backend API development using Python (Flask/FastAPI/Django) or Node.js (Express/NestJS) frameworks with PostgreSQL database integration.

## Server Configuration

- **Server IP**: 35.77.54.203 (NEVER use localhost or 127.0.0.1 in any configuration or documentation)
- **Available Ports**: 3003, 3004, 3005
- **Database**: PostgreSQL (pre-installed on server)
- **GitHub Repository**: https://github.com/ocean5tech/stock_services

## Development Standards

### Code Quality
- Write clean, maintainable code with Chinese comments for explanations
- Use English for variable and function names following standard conventions
- Implement comprehensive error handling and input validation throughout

### Database Operations
- Always use PostgreSQL with connection pooling
- Use parameterized queries to prevent SQL injection
- Implement proper transaction management
- Query database directly to verify INSERT, UPDATE, and DELETE operations

### Security Requirements
- Implement authentication and authorization
- Use input validation for all endpoints
- Configure HTTPS in production
- Implement rate limiting
- Never expose sensitive credentials

### Performance Optimization
- Optimize database queries with proper indexing
- Implement caching strategies where appropriate
- Use connection pooling for database connections

## Testing Protocol

**CRITICAL**: Never rely solely on HTTP status codes for validation.

- **INSERT operations**: Query PostgreSQL database to verify data actually exists
- **UPDATE operations**: Confirm actual data changes in database  
- **DELETE operations**: Verify data removal from database
- Test all endpoints with real database state verification
- Include security, performance, and edge case testing

## Deployment Requirements

### Port Management
- Kill existing processes on target ports before deployment
- Use assigned ports (3003, 3004, 3005) - do not change port numbers

### Database Setup
- Check PostgreSQL service status before startup
- Run database migrations automatically during deployment
- Verify database connection before starting API services

### Documentation
- Create deployment scripts for easy setup
- Implement one-click recovery procedures
- Generate comprehensive API documentation in Markdown

## API Design Standards

- Follow RESTful principles
- Always use server IP (35.77.54.203) in all URLs and documentation examples
- Include request/response schemas and examples
- Document error handling and security considerations
- Provide performance optimization guidance

## Code Management

- Upload to GitHub after completing major version testing
- Use meaningful commit messages with proper versioning
- Update documentation and changelog with each release
- Tag releases appropriately

## Workflow Approach

1. Analyze requirements and design API architecture
2. Implement code with proper PostgreSQL integration
3. Create comprehensive tests that verify actual database operations
4. Deploy with automatic conflict resolution and service verification
5. Generate documentation and upload to GitHub
6. Provide monitoring and maintenance guidance

## Agent Configuration

This repository includes a specialized `backend-api-developer` agent for handling complex API development tasks. Use this agent for:
- Designing and implementing new API endpoints
- Database integration and optimization
- Server infrastructure setup
- Performance debugging and optimization
- Production deployment procedures