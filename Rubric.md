# Rubric

Total base score: 100 points  
Optional bonus: up to 10 extra points

## 1. Server Foundation - 20 points

- 5 pts: FastMCP server starts successfully
- 5 pts: project structure is clean and understandable
- 5 pts: SQLite database is initialized with reproducible schema/data
- 5 pts: code is organized into server logic and database logic

## 2. Required Tools - 30 points

- 10 pts: `search` works with filters, ordering, and pagination
- 10 pts: `insert` works and returns the inserted payload
- 10 pts: `aggregate` supports useful metrics such as `count`, `avg`, `sum`, `min`, `max`

## 3. MCP Resources - 15 points

- 8 pts: full database schema resource is exposed
- 7 pts: per-table schema resource template is exposed and readable

## 4. Safety and Error Handling - 15 points

- 5 pts: invalid table and column names are rejected
- 5 pts: unsupported operators or bad aggregate requests are rejected
- 5 pts: SQL execution uses safe parameterized patterns where appropriate

## 5. Verification - 10 points

- 4 pts: tool discovery is verified
- 3 pts: successful tool calls are demonstrated
- 3 pts: failing tool calls are demonstrated with clear errors

## 6. Client Integration and Demo - 10 points

- 4 pts: at least one MCP client is configured correctly
- 3 pts: README includes setup and test steps
- 3 pts: short demo or screenshots show the server in use

## Bonus - up to 10 points

- 5 pts: SSE or HTTP auth implemented and demonstrated
- 3 pts: support for both SQLite and PostgreSQL behind a shared interface
- 2 pts: extra polish such as pagination guidance, output limits, or structured testing

## Scoring Guide

- 90-100: production-quality student submission; complete, verified, and well documented
- 75-89: correct core implementation with small gaps or weak polish
- 60-74: partial implementation; tools mostly work but testing, resources, or validation are thin
- 40-59: significant missing functionality
- 0-39: does not meet core lab requirements

## Quick Grading Questions

1. Can I start the server and discover the tools?
2. Do `search`, `insert`, and `aggregate` all work?
3. Can I read the schema resource and the per-table schema template?
4. Does the project reject bad input safely?
5. Is there a repeatable verification story?
6. Can at least one client actually use the server?
