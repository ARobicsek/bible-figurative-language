# Contributing to Tzafun

Thank you for your interest in contributing! This project benefits from community involvement in validation, feature development, bug reporting, and documentation.

---

## Table of Contents

1. [Ways to Contribute](#ways-to-contribute)
2. [Reporting Issues](#reporting-issues)
3. [Reporting Classification Errors](#reporting-classification-errors)
4. [Suggesting Features](#suggesting-features)
5. [Contributing Code](#contributing-code)
6. [Contributing Documentation](#contributing-documentation)
7. [Development Guidelines](#development-guidelines)
8. [Code of Conduct](#code-of-conduct)
9. [Recognition](#recognition)

---

## Ways to Contribute

We welcome contributions in many forms:

### 🔍 Validation & Quality Assurance
- Report incorrect figurative language classifications
- Identify missing figurative language instances
- Verify AI reasoning and explanations
- Test the interface across different browsers/devices

### 🐛 Bug Reports
- Report interface issues
- Identify performance problems
- Document unexpected behavior
- Test and report edge cases

### ✨ Feature Suggestions
- Propose new search capabilities
- Suggest interface improvements
- Request additional data visualizations
- Recommend new export formats

### 📖 Documentation
- Improve setup instructions
- Add examples and use cases
- Translate documentation
- Create tutorials or video guides

### 💻 Code Contributions
- Fix bugs
- Implement new features
- Optimize performance
- Improve accessibility

---

## Reporting Issues

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Check the FAQ** at [docs/FAQ.md](docs/FAQ.md)
3. **Try the latest version** to ensure the issue still exists
4. **Gather details** about your environment (browser, OS, etc.)

### Creating an Issue

Use our issue templates when possible:

- **Bug Report**: [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- **Classification Feedback**: [.github/ISSUE_TEMPLATE/classification_feedback.md](.github/ISSUE_TEMPLATE/classification_feedback.md)
- **Feature Request**: [.github/ISSUE_TEMPLATE/feature_request.md](.github/ISSUE_TEMPLATE/feature_request.md)

Include:
- **Clear title** describing the issue
- **Detailed description** of the problem
- **Steps to reproduce** (for bugs)
- **Expected vs actual behavior**
- **Screenshots** if applicable
- **Environment details** (browser, OS, screen size)

---

## Reporting Classification Errors

The AI analysis may contain errors. Your feedback helps improve data quality!

### Types of Classification Issues

1. **False Positive**: Text marked as figurative but is literal
2. **False Negative**: Figurative language not detected
3. **Wrong Type**: Classified as wrong figurative type (e.g., marked as metaphor but is actually a simile)
4. **Incorrect Metadata**: Wrong Target/Vehicle/Ground/Posture classification

### What to Include

When reporting classification issues, please provide:

```markdown
**Verse Reference**: Genesis 1:2

**Current Classification**: Metaphor

**Issue Type**: False Positive / False Negative / Wrong Type / Incorrect Metadata

**Explanation**:
[Explain why you believe the current classification is incorrect]

**Suggested Classification**:
[What should it be instead?]

**Supporting Evidence**:
- Biblical commentaries
- Hebrew grammar references
- Scholarly sources
- Linguistic analysis

**Hebrew Text**: [if relevant to your argument]

**English Translation**: [if relevant]
```

### Scholarly Standards

We appreciate contributions that reference:
- Traditional biblical commentaries (Rashi, Ibn Ezra, Ramban, etc.)
- Modern scholarly works
- Hebrew grammar references
- Linguistic analysis

**Note**: We value diverse scholarly perspectives. You don't need to be an expert—thoughtful observations are welcome!

---

## Suggesting Features

We're always looking to improve the tool. Great feature suggestions include:

### What Makes a Good Feature Request?

- **Clear use case**: Explain who benefits and how
- **Specific functionality**: Describe what the feature should do
- **Examples**: Show how it would work in practice
- **Priority**: Indicate how important this is to you

### Feature Ideas We're Considering

See our [roadmap in README.md](README.md#-roadmap) for planned features.

Areas we're particularly interested in:
- Export formats (CSV, JSON, BibTeX)
- Advanced visualizations (Sankey diagrams, network graphs)
- Enhanced search capabilities
- Mobile experience improvements
- Accessibility enhancements
- Integration with other tools

---

## Contributing Code

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/bible-figurative-language-concordance.git
   cd bible-figurative-language-concordance
   ```

3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. **Make your changes** following our coding standards

5. **Test thoroughly** across browsers and devices

6. **Commit your changes** with clear messages:
   ```bash
   git commit -m "feat: Add CSV export functionality"
   # or
   git commit -m "fix: Resolve Hebrew text display issue on Safari"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** from your fork to our main repository

### Commit Message Convention

We use conventional commits for clarity:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```bash
feat: Add metadata export to CSV
fix: Resolve Hebrew keyboard input on mobile
docs: Improve setup instructions for Windows
perf: Optimize database query for large result sets
```

### Pull Request Guidelines

**Before submitting:**
- [ ] Test your changes locally
- [ ] Update documentation if needed
- [ ] Add comments to complex code
- [ ] Follow the existing code style
- [ ] Ensure all features work on Chrome, Firefox, and Safari

**In your PR description, include:**
- What changes you made
- Why you made them
- How to test them
- Screenshots (for UI changes)
- Related issue numbers (e.g., "Fixes #123")

---

## Contributing Documentation

Documentation improvements are highly valued!

### Types of Documentation

1. **Setup Guides**: Help users install and deploy
2. **Feature Documentation**: Explain how to use features
3. **Examples**: Provide real-world use cases
4. **Tutorials**: Step-by-step guides for common tasks
5. **API Documentation**: Document query patterns and data structures

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots where helpful
- Test all instructions yourself
- Link to related documentation
- Use proper Markdown formatting

### Where to Contribute

- `README.md` - Project overview and quick start
- `SETUP.md` - Installation and deployment
- `docs/FEATURES.md` - Interface features
- `docs/FAQ.md` - Common questions
- `docs/DATABASE_SCHEMA.md` - Database structure
- `docs/METHODOLOGY.md` - Research methodology

---

## Development Guidelines

### Code Style

**HTML/JavaScript:**
- 4-space indentation
- Clear variable names
- Comments for complex logic
- Consistent naming conventions

**SQL:**
- Uppercase keywords
- Clear table/column aliases
- Proper indentation for readability

### Testing Checklist

Before submitting code, test:

**Browsers:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

**Devices:**
- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

**Core Functionality:**
- [ ] Verse loading
- [ ] Search (Hebrew and English)
- [ ] Filtering by type
- [ ] Metadata search
- [ ] Sacred/non-sacred toggle
- [ ] Click interactions
- [ ] Pagination

### Performance Considerations

- Keep queries optimized
- Minimize API calls
- Implement pagination for large datasets
- Use efficient DOM manipulation
- Optimize images and assets

### Accessibility

- Maintain keyboard navigation
- Ensure proper color contrast (WCAG AA)
- Add ARIA labels where appropriate
- Test with screen readers when possible
- Provide text alternatives for visual content

---

## Code of Conduct

### Our Standards

We are committed to providing a welcoming and respectful environment:

**Expected Behavior:**
- ✅ Be respectful and professional
- ✅ Welcome diverse perspectives
- ✅ Accept constructive criticism gracefully
- ✅ Focus on what's best for the community
- ✅ Show empathy and kindness

**Unacceptable Behavior:**
- ❌ Harassment or discrimination
- ❌ Trolling or inflammatory comments
- ❌ Personal attacks
- ❌ Publishing others' private information
- ❌ Unprofessional conduct

### Enforcement

Violations may result in:
1. **Warning** - First minor offense
2. **Temporary Ban** - Repeated or serious violations
3. **Permanent Ban** - Severe or persistent violations

### Reporting Issues

To report Code of Conduct violations:
- Open a confidential issue
- Email the maintainer (if available)
- Contact via GitHub's reporting mechanisms

All reports will be handled with discretion and confidentiality.

---

## Recognition

We value all contributions and recognize contributors in multiple ways:

### Automatic Recognition

- All PR authors are automatically added to our contributors list
- Your GitHub profile appears in the repository contributors

### Acknowledgments

We maintain a `CONTRIBUTORS.md` file listing:
- Code contributors
- Documentation contributors
- Quality assurance contributors
- Community support contributors

### Special Recognition

Outstanding contributions may be recognized:
- In release notes
- In project documentation
- On social media announcements
- In academic citations (for substantial scholarly contributions)

### Academic Credit

For substantial research contributions that improve the data quality or methodology:
- Co-authorship consideration for academic papers
- Acknowledgment in scholarly publications
- Citation in the project's methodology documentation

---

## Questions?

**Have questions about contributing?**

- 💬 Open a [GitHub Discussion](https://github.com/[username]/bible-figurative-language-concordance/discussions)
- 🐛 Create an issue with the "question" label
- 📧 Check our [FAQ](docs/FAQ.md)

**Need help getting started?**

Look for issues labeled:
- `good first issue` - Perfect for newcomers
- `help wanted` - We need assistance with these
- `documentation` - Great for non-coders

---

## License

By contributing, you agree that your contributions will be licensed under:

- **Code contributions**: MIT License ([LICENSE-CODE.md](LICENSE-CODE.md))
- **Data/documentation contributions**: CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md))

This ensures your work remains open and accessible to the community.

---

## Thank You!

Your contributions make this project better for researchers, students, and enthusiasts worldwide. Whether you're fixing a typo, reporting a bug, or implementing a major feature, your effort is appreciated and valued.

**Together, we're building a valuable resource for biblical scholarship and digital humanities!** 🎉

---

**Questions or need clarification?** Open an issue with the "question" label, and we'll help you get started!
