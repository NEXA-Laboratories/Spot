# Contributing to NEXA Spot

Thank you for your interest in contributing to **NEXA Spot**!

NEXA Spot is an open-source project, and contributions from developers, hardware enthusiasts, designers, testers, and documentation writers are welcome.

Our goal is to build a privacy-first smart speaker that anyone can understand, improve, and use.

---

## Before You Start

Please read the README first to understand the project's goals and current architecture.

NEXA Spot is currently in the **Prototype** stage, so the architecture may change as development progresses.

If you're not sure whether your idea fits the project, open an Issue and discuss it with the community first.

---

## Ways to Contribute

You don't have to be an expert programmer to contribute.

### 💻 Code

You can help with:

* Python development
* Local LLM integration
* Speech-to-Text
* Piper TTS
* Wake-word detection
* Amigo
* Smart-home integrations
* Performance improvements
* Testing

### 🧪 Testing

Try the project on your hardware and report:

* Bugs
* Unexpected behavior
* Performance problems
* Compatibility issues

Good bug reports are extremely valuable during the Prototype stage.

### 📚 Documentation

You can improve:

* Installation instructions
* Configuration guides
* API documentation
* Examples
* Troubleshooting guides

### 💡 Ideas

Have an idea for Spot?

Open a **Feature Request** and explain:

1. What the feature does
2. Why it would be useful
3. How you think it could work

---

# Development Workflow

## 1. Fork the Repository

Create your own fork of the NEXA Spot repository.

---

## 2. Clone Your Fork

```bash
git clone https://github.com/NEXA-Laboratories/Spot.git
cd Spot
```

## 3. Create a Branch

Please avoid making changes directly to main.

Create a branch for your work:

```bash
git checkout -b feature/your-feature
```

For a bug fix:

```bash
git checkout -b fix/your-fix
```

Use a clear branch name describing your changes.

## 4. Make Your Changes

Implement your changes while keeping the project architecture and coding style in mind.

Try to keep commits focused.

For example:

```
Add Piper voice configuration
```
is preferable to:

```
update stuff
```
## 5. Test Your Changes

Before opening a Pull Request, make sure your changes work as expected.

If you add a new feature, test both the new functionality and existing functionality that could be affected.

6. Commit Your Changes

Example:

```bash
git add .
git commit -m "Add Piper voice configuration"
```

Keep commit messages short and descriptive.

7. Push Your Branch

```bash
git push origin feature/your-feature
```

## Pull Requests

Once your changes are ready, open a Pull Request against the main branch.

Your Pull Request should explain:

What you changed
Why you changed it
How you tested it
Any limitations or known issues

Example:

```
## What changed

Added Piper TTS voice configuration.

## Why

Allows users to select different Piper voices.

## Testing

Tested locally with two Piper voices.

## Notes

Additional voice configuration may be added later.
```

## Pull Request Guidelines

Please:

- Keep Pull Requests focused
- Explain your changes clearly
- Test your code before submitting
- Update documentation when necessary
- Be respectful during code review

A Pull Request may be requested to be changed before it is merged. This is a normal part of collaborative development.

## Issues

Use GitHub Issues for:

# 🐛 Bug Reports

Something doesn't work as expected.

# 💡 Feature Requests

You have an idea for improving Spot.

# 📚 Documentation

Something is missing, unclear, or incorrect.

Please search existing Issues before creating a duplicate.

## Code of Conduct

Be respectful to other contributors.

NEXA Spot is an open-source project. People with different levels of experience should be able to participate without harassment or hostility.

Technical disagreements are normal.

Personal attacks are not.

## Thank You

Every contribution matters.

Whether you submit a Pull Request, report a bug, improve a sentence in the documentation, or simply test Spot on your hardware — you're helping build the project.

Build openly. Build responsibly.
