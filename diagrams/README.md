# Copilot-Bridge Architecture Diagrams

This directory contains comprehensive Mermaid diagrams explaining the architecture, request flow, task classification, and deployment strategies for copilot-bridge with dual-GPU smart routing.

## 📊 Diagram Overview

### 1. [System Architecture](01_system_architecture.md) 🏗️
**Purpose:** High-level overview of the entire system

**Shows:**
- Client layer (GitHub Copilot, IDEs)
- Proxy layer (routing, metrics, fallback)
- Dual-GPU backend (Ollama, models, GPUs)
- Monitoring and logging infrastructure

**Key Insights:**
- How requests flow through the system
- Model selection based on task complexity
- Integration with Prometheus monitoring
- Automatic fallback mechanisms

**Best For:** Understanding the overall system design

---

### 2. [Request Flow Sequence](02_request_flow_sequence.md) ⚡
**Purpose:** Detailed step-by-step request processing

**Shows:**
- Complete request lifecycle from client to response
- Task classification decision points
- Model selection logic
- Error handling and retry mechanisms
- Metrics collection points

**Key Insights:**
- How a request is classified (SIMPLE/MODERATE/COMPLEX)
- Which model gets selected and why
- What happens during timeouts or errors
- How metrics are collected at each stage

**Best For:** Understanding request processing details

---

### 3. [Task Classification Decision Tree](03_task_classification_tree.md) 🌳
**Purpose:** Detailed classification algorithm and logic

**Shows:**
- Keyword-based classification system
- Decision paths for SIMPLE, MODERATE, and COMPLEX tasks
- Model selection for each complexity level
- Performance characteristics of each path
- Error handling and fallback strategies

**Key Insights:**
- Exact keywords that trigger each classification
- Why 1.5B model is 55.9x faster for SIMPLE tasks
- How the system handles unmatched keywords (default to MODERATE)
- Validation results showing 100% accuracy

**Best For:** Understanding the smart routing algorithm

---

### 4. [Deployment & Integration](04_deployment_integration.md) 🚀
**Purpose:** Production deployment architecture and integration patterns

**Shows:**
- Development environment setup
- Production cluster architecture with load balancing
- Ollama GPU cluster configuration
- Monitoring stack (Prometheus, Grafana, Loki)
- Configuration management
- External service integrations

**Key Insights:**
- How to deploy for development vs production
- Load balancer configuration (nginx)
- Multi-instance cluster setup
- Horizontal and vertical scaling strategies
- High availability patterns

**Best For:** Understanding deployment and operations

---

## 🎯 Quick Reference

### When to Use Each Diagram:

| Use Case | Recommended Diagram |
|----------|---------------------|
| Explaining the system to stakeholders | #1 System Architecture |
| Debugging request issues | #2 Request Flow Sequence |
| Understanding why a model was selected | #3 Task Classification Tree |
| Planning production deployment | #4 Deployment & Integration |
| Onboarding new developers | Start with #1, then #2 |
| Performance optimization | #2 Request Flow + #3 Classification |
| Scaling planning | #4 Deployment & Integration |

---

## 🔍 Key Metrics & Performance

### Performance Improvements:
- **55.9x speedup** for SIMPLE tasks (0.34s vs 19s)
- **87% memory reduction** for SIMPLE tasks (1GB vs 8GB VRAM)
- **100% classification accuracy** (15/15 tests passed)

### Cost Savings:
- **$13,000/year** for 10-developer team
- **62.2 minutes/day** time savings
- **259.4 hours/year** productivity gain

### Task Distribution:
- **SIMPLE:** ~40% of requests (autocomplete, format, lint)
- **MODERATE:** ~35% of requests (refactor, debug, explain)
- **COMPLEX:** ~25% of requests (design, implement, architect)

---

## 📚 Related Documentation

### Setup Guides:
- [Quick Start (5 minutes)](../dual-gpu-implementation/DUAL_GPU_QUICKSTART.md)
- [Complete Setup Guide](../dual-gpu-implementation/DUAL_GPU_SETUP.md)
- [Ollama Workaround](../dual-gpu-implementation/DUAL_GPU_WORKAROUND.md)

### Reference:
- [Command Reference](../DUAL_GPU_COMMANDS.md)
- [Integration Summary](../DUAL_GPU_INTEGRATION_COMPLETE.md)
- [Roadmap](../ROADMAP_DUAL_GPU_UPDATE.md)

### Release:
- [Changelog v1.1.0](../CHANGELOG_v1.1.0.md)
- [Deployment Guide](../DEPLOYMENT_v1.1.0.md)
- [Main Changelog](../CHANGELOG.md)

---

## 🖼️ Viewing the Diagrams

### Online Viewers:
1. **GitHub** - Renders Mermaid natively (just view the .md files)
2. **Mermaid Live Editor** - https://mermaid.live/
3. **VS Code** - Install "Markdown Preview Mermaid Support" extension

### Local Rendering:
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate PNG from diagram
mmdc -i 01_system_architecture.md -o architecture.png

# Generate SVG (better quality)
mmdc -i 01_system_architecture.md -o architecture.svg
```

### VS Code Extension:
```bash
# Install extension
code --install-extension bierner.markdown-mermaid

# Open any diagram file and preview
# Press: Ctrl+Shift+V (Windows/Linux) or Cmd+Shift+V (Mac)
```

---

## 🎨 Diagram Color Coding

### Consistent Color Scheme Across All Diagrams:

| Color | Component Type | Hex Code |
|-------|---------------|----------|
| 🔵 Blue | Client Layer, Default | #e1f5ff |
| 🟠 Orange | Proxy Layer, Moderate | #fff3e0 |
| 🟣 Purple | GPU/Backend, Complex | #f3e5f5 |
| 🟢 Green | Simple Tasks, Monitoring | #e8f5e9 |
| 🔴 Red | Errors, Alerts | #ffebee |
| ⚫ Gray | Processing, Utilities | #f5f5f5 |

---

## 🔧 Customizing Diagrams

### Editing Mermaid Code:
1. Open any `.md` file in this directory
2. Find the code block starting with ` ```mermaid `
3. Edit the Mermaid syntax
4. Preview changes in VS Code or Mermaid Live Editor

### Common Customizations:

**Add a new node:**
```mermaid
NEW_NODE[New Component<br/>Description]
```

**Add a connection:**
```mermaid
NODE1 -->|Label| NODE2
```

**Change styling:**
```mermaid
classDef customStyle fill:#color,stroke:#color,stroke-width:2px
class NODE1,NODE2 customStyle
```

**Add a subgraph:**
```mermaid
subgraph "Group Name"
    NODE1
    NODE2
end
```

---

## 📊 Diagram Statistics

| Diagram | Lines of Code | Nodes | Connections | Subgraphs |
|---------|--------------|-------|-------------|-----------|
| #1 System Architecture | 150 | 28 | 35 | 7 |
| #2 Request Flow Sequence | 180 | 15 | 42 | 1 |
| #3 Task Classification Tree | 220 | 45 | 52 | 0 |
| #4 Deployment & Integration | 200 | 35 | 45 | 8 |
| **Total** | **750** | **123** | **174** | **16** |

---

## 🤝 Contributing

### Adding New Diagrams:

1. **Create new file:** `05_your_diagram_name.md`
2. **Follow template:**
```markdown
# Diagram Title

Brief description of what this diagram shows.

\```mermaid
graph TB
    %% Your diagram code here
\```

## Explanation:
Detailed explanation of the diagram...
```

3. **Update this README** with new diagram reference
4. **Test rendering** in GitHub, VS Code, or Mermaid Live

### Diagram Best Practices:
- ✅ Use consistent color coding
- ✅ Include clear labels and descriptions
- ✅ Add explanatory text after the diagram
- ✅ Keep diagrams focused (one concept per diagram)
- ✅ Use subgraphs to group related components
- ✅ Add styling for visual clarity

---

## 📖 Mermaid Syntax Reference

### Graph Types:
```mermaid
graph TB    # Top to Bottom
graph LR    # Left to Right
graph TD    # Top-Down (alias for TB)
```

### Node Shapes:
```mermaid
NODE1[Rectangle]
NODE2(Rounded)
NODE3([Stadium])
NODE4[[Subroutine]]
NODE5[(Database)]
NODE6((Circle))
NODE7{Diamond}
```

### Connection Types:
```mermaid
A --> B     # Arrow
A --- B     # Line
A -.-> B    # Dotted arrow
A ==> B     # Thick arrow
A -->|text| B  # Labeled arrow
```

### Styling:
```mermaid
classDef className fill:#color,stroke:#color
class NODE1,NODE2 className
```

**Full Documentation:** https://mermaid.js.org/

---

## 🎯 Learning Path

### For New Developers:
1. Start with **System Architecture** (#1) for overview
2. Read **Request Flow Sequence** (#2) for details
3. Study **Task Classification Tree** (#3) for algorithm
4. Review **Deployment & Integration** (#4) before deploying

### For Operations:
1. Focus on **Deployment & Integration** (#4)
2. Review **System Architecture** (#1) for monitoring points
3. Reference **Request Flow Sequence** (#2) for troubleshooting

### For Performance Optimization:
1. Analyze **Task Classification Tree** (#3) for bottlenecks
2. Study **Request Flow Sequence** (#2) for timing
3. Check **System Architecture** (#1) for scaling options

---

## 🔗 External Resources

### Mermaid Documentation:
- Official Docs: https://mermaid.js.org/
- Live Editor: https://mermaid.live/
- Cheat Sheet: https://jojozhuang.github.io/tutorial/mermaid-cheat-sheet/

### Related Projects:
- Ollama: https://github.com/ollama/ollama
- Prometheus: https://prometheus.io/
- GitHub Copilot: https://github.com/features/copilot

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-19 | Initial diagram set created for v1.1.0 release |

---

## 📫 Support

For questions or issues related to these diagrams:
1. Check the main [README.md](../README.md)
2. Review [DUAL_GPU_SETUP.md](../dual-gpu-implementation/DUAL_GPU_SETUP.md)
3. Open an issue on GitHub

---

**Built with ❤️ for the copilot-bridge community**

v1.1.0 - Dual-GPU Smart Routing - October 19, 2025
