---
name: Technology Stack
description: Build system, tech stack, libraries, frameworks, and common commands
inclusion: auto
---

# Technology Stack

## Build System & Tools

- **Build Tool**: tsup (TypeScript bundler)
- **Package Manager**: bun only (`bun.lock` is the source of truth)
- **TypeScript**: v5.9.3 with strict mode enabled
- **Test Framework**: Vitest v3.2.4
- **Node Version**: >=18 required

## Core Dependencies

- **CLI**: commander, chalk, cli-progress
- **Data Processing**: dayjs, python-struct, lzma-purejs-requirejs
- **Validation**: fastest-validator
- **HTTP**: node-fetch v2.7.0
- **File System**: fs-extra
- **Debugging**: debug

## Code Quality Tools

- **Linter**: ESLint with TypeScript plugin
- **Formatter**: Prettier
- **Prettier Config**:
  - Print width: 100
  - Single quotes
  - 2 space indentation
  - No trailing commas
  - Arrow parens: avoid

## Common Commands

```bash
# Build the project
bun run build

# Run tests
bun run test

# Run tests with coverage
bun run coverage

# Format code
bun run format

# Lint code
bun run lint

# Type check
bun run type-check

# CLI usage (for consumers of the published package)
npx dukascopy-node -i btcusd -from 2019-01-13 -to 2019-01-14 -t tick -f csv
```

## Output Formats

- **ESM**: dist/esm/index.js
- **CJS**: dist/index.js
- **Types**: dist/index.d.ts
- **CLI Binaries**: dukascopy-cli, dukascopy-node

## Testing

- Unit tests located alongside source files (*.test.ts)
- Test data in dedicated test folders
- Mock service worker (msw) for HTTP mocking
