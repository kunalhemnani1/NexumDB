# Changelog

All notable changes to NexumDB will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-02-03

### Added
- Projection-aware SELECT with alias support
- SHOW TABLES, DESCRIBE, and DROP TABLE (IF EXISTS)
- Best-effort coercion for INSERT/UPDATE with schema validation
- Full cache invalidation on data writes
- Catalog persistence test coverage

### Changed
- StorageEngine clone now shares underlying sled database
- Semantic cache keys now include projection, WHERE, ORDER BY, LIMIT

### Tests
- Added projection, coercion, and table management coverage
- Extended integration tests for table lifecycle

## [0.3.0] - 2025-11-26

### Added
- Advanced SQL operators
  - LIKE operator for pattern matching (supports % and _ wildcards)
  - IN operator for list membership testing
  - BETWEEN operator for inclusive range queries
- Query modifiers
  - ORDER BY clause with multi-column sorting (ASC/DESC)
  - LIMIT clause for result truncation
- Persistent RL agent
  - save_state() and load_state() methods using joblib
  - Auto-load Q-table on agent initialization
  - Learning persists across database restarts
- Model management system
  - ModelManager class for automatic LLM downloads
  - HuggingFace Hub integration
  - Automatic download of phi-2.Q4_K_M.gguf model
  - Graceful fallback to rule-based translation
- 6 new unit tests for advanced operators
- 3 new integration tests for combined features

### Changed
- Updated Statement::Select to include order_by and limit fields
- Extended ExpressionEvaluator with LIKE, IN, BETWEEN support
- Modified NLTranslator to use ModelManager
- Enhanced parser to handle ORDER BY and LIMIT clauses
- Executor now performs sorting and limiting operations

### Dependencies
- Added: regex = "1.10" (Rust)
- Added: huggingface-hub>=0.20.0 (Python)

### Performance
- LIKE: ~100µs overhead per query
- IN (5 items): ~50µs overhead
- BETWEEN: ~40µs overhead
- ORDER BY (1000 rows): ~2ms
- LIMIT: ~1µs overhead
- RL save/load: ~5ms/~3ms

### Tests
- 21 tests passing (was 18)
- Zero regressions
- All existing functionality preserved

## [0.2.0] - 2025-11-25

### Added
- WHERE clause filtering with full expression evaluation
  - Comparison operators: =, >, <, >=, <=, !=
  - Logical operators: AND, OR
  - Support for Integer, Float, Text, Boolean types
- Natural Language Query interface (ASK command)
  - NLTranslator class with llama-cpp-python support
  - Fallback rule-based translator
  - Schema-aware translation
- Reinforcement Learning query optimizer
  - Q-Learning agent with state/action/reward
  - Epsilon-greedy exploration
  - Automatic learning from query performance
- ExpressionEvaluator for WHERE clause evaluation
- NLTranslator PyO3 bridge integration
- Schema introspection for NL context
- 3 new integration tests for WHERE filtering
- CLI ASK command mode

### Changed
- Updated CLI to v0.2.0 with enhanced command modes
- Extended Python AI engine with translator and RL agent
- Improved PyO3 bridge with NLTranslator export
- Enhanced README with v0.2.0 features

### Fixed
- Parser now correctly handles WHERE clause expressions
- Fixed unused variable warnings in executor

### Dependencies
- Added: llama-cpp-python>=0.2.0
- Added: diskcache (via llama-cpp-python)

### Tests
- 15 unit tests passing (was 11)
- 3 integration tests passing (new)
- Total: 18/18 tests passing

## [0.1.0] - 2025-11-25

### Added
- Initial release with core SQL database functionality
- Storage engine using sled
- SQL parser for CREATE TABLE, INSERT, SELECT
- Query executor with end-to-end workflow
- Catalog for table metadata management
- Semantic caching using sentence-transformers
- PyO3 Rust-Python integration
- CLI REPL interface
- 11 comprehensive unit tests

### Features
- Persistent KV storage
- SQL query execution
- AI-powered semantic caching
- 60x query speedup on cache hits
- Local-only execution (no cloud dependencies)

[0.4.0]: https://github.com/aviralgarg05/NexumDB/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/aviralgarg05/NexumDB/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/aviralgarg05/NexumDB/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/aviralgarg05/NexumDB/releases/tag/v0.1.0
