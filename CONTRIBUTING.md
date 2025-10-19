# Contributing to Copilot Bridge

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🐛 Reporting Issues

**Bug Reports** should include:
- Python version (`python3 --version`)
- Ollama version (`ollama --version`)
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages / stack traces

**Feature Requests** should include:
- Use case / problem to solve
- Proposed solution
- Alternative approaches considered
- Impact on existing functionality

## 🔧 Development Setup

1. **Fork and clone**:
   ```bash
   git clone https://github.com/yourusername/copilot-bridge.git
   cd copilot-bridge
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama models**:
   ```bash
   ollama pull qwen2.5-coder:7b-instruct-q8_0
   ollama pull llama3.1:8b
   ollama pull gpt-oss:20b  # Optional
   ```

4. **Run tests**:
   ```bash
   python3 examples/demo_showcase.py
   python3 test_instrumentation.py
   cd refactor-quality-tests && python3 test_samples.py
   ```

## 📝 Code Style

### Python Style Guidelines

- **PEP 8** compliant (use `black` for formatting)
- **Type hints** for function signatures:
  ```python
  def route_request(prompt: str, task_type: str = "generation") -> Dict[str, Any]:
      ...
  ```
- **Docstrings** for public functions (Google style):
  ```python
  def generate_draft(self, prompt: str) -> Dict[str, Any]:
      """
      Generate initial draft using large model.
      
      Args:
          prompt: User's request
          
      Returns:
          Draft response with metadata (text, time, tokens)
      """
  ```
- **Descriptive variable names**: `tokens_saved_total` not `tst`
- **Comments** for complex logic, not obvious code

### File Organization

- **Core routing**: `proxy.py`, `proxy_instrumented.py`
- **Meta-reasoning**: `examples/rosencrantz_guildenstern.py`
- **Metrics**: `exporter.py`
- **Demos/examples**: `examples/*.py`
- **Tests**: `test_*.py` or `refactor-quality-tests/`
- **Documentation**: `*.md` files

## 🚀 Pull Request Process

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**:
   - Write clear, focused commits
   - Add tests if adding functionality
   - Update documentation if changing behavior

2. **Test your changes:**
   ```bash
   # Run the demo showcase
   python3 examples/demo_showcase.py
   
   # Run specific test
   python3 test_instrumentation.py
   ```

4. **Commit with descriptive messages**:
   ```bash
   git commit -m "Add feature: Token transparency in R&G audit
   
   - Show token count before generating draft
   - Ask user consent before feeding context
   - Display cost estimate (local vs cloud)
   
   Closes #42"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then open a pull request on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to issue (if applicable)
   - Screenshots (if UI changes)

## 🧪 Testing Expectations

### For Bug Fixes
- Reproduce the bug with a test case
- Fix the bug
- Verify the test now passes
- Ensure no regressions in existing tests

### For New Features
- Add demo or example showing the feature
- Test edge cases (empty input, large input, errors)
- Document usage in README or relevant docs
- Consider performance impact

### Manual Testing Checklist
- [ ] Run `examples/demo_showcase.py` (all 8 demos)
- [ ] Run `examples/rosencrantz_guildenstern.py` (meta-reasoning)
- [ ] Run `test_instrumentation.py` (logging pipeline)
- [ ] Check `refactor-quality-tests/` still work
- [ ] Verify no crashes, reasonable output quality
- [ ] Test with Ollama running and not running (error handling)

## 📚 Documentation

Update documentation when:
- Adding new features
- Changing CLI arguments
- Modifying configuration
- Changing dependencies
- Adding new files/directories

Documentation to update:
- **README.md** - Main overview, quick start
- **QUICKSTART.md** - Setup instructions
- **Architecture docs** - If changing design
- **Inline comments** - For complex code
- **Docstrings** - For public APIs

## 🎯 Focus Areas for Contributions

### High Priority
- **Performance**: Faster routing, reduced latency
- **Quality tests**: More refactoring scenarios
- **Error handling**: Better failure messages
- **Documentation**: Clarify confusing sections

### Medium Priority
- **Model support**: Additional Ollama models
- **Metrics**: New Prometheus metrics
- **Templates**: More proven context templates
- **Examples**: Real-world use cases

### Low Priority (Nice-to-Have)
- **Web UI**: Dashboard for R&G audits
- **PyPI package**: `pip install copilot-bridge`
- **Docker images**: Pre-built containers
- **CI/CD**: Automated testing

## ❓ Questions?

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Report bugs, request features
- **Pull Requests**: Propose changes, improvements

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Celebrate diverse perspectives
- Assume good intentions

## 🙏 Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Credited in release notes
- Mentioned in project README

Thank you for helping make Copilot Bridge better! 🌉
