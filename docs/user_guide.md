# Internet Memory Layer (IML): User Documentation & Guide

Welcome to the **Internet Memory Layer (IML)**: your private, local-first internet brain. This guide covers features, setup walkthroughs, and UI navigation tips.

---

## 1. Navigating the IML Dashboard

Once the Tauri desktop app loads, you'll see a unified three-pane interface:

### 1.1 Pane Breakdown
- **Left Sidebar**: Ingestion activity streams, timeline calendar, project spaces, and quick search.
- **Center Canvas**: The Interactive 3D Knowledge Graph, Mind Map cluster views, or the active research document editor.
- **Right Context Inspector**: Inspects the selected graph node, highlights matching vectors, edits notes, and interacts with the AI Research Assistant.

---

## 2. Platform Core Features

### 2.1 Timeline & Internet Time Machine
The Timeline allows you to replay your browsing sessions sequentially:
1. Navigate to the **Timeline** tab.
2. Select a target date using the **Memory Calendar**.
3. Use the playback slider to see what pages you viewed, how long you read them, and how your knowledge graph expanded that hour.

### 2.2 Learning Mode
Helps reinforce concepts you read across the web:
- **Interactive Flashcards**: Generates active recall questions from your captured web chunks using local LLMs.
- **Progress Tracking**: Shows your "Knowledge Score" for different topic clusters (e.g. Kubernetes, Economics).
- **Spaced Repetition**: Re-surfaces old or complex topics automatically in the "Daily Review Queue" based on your retention rate.

### 2.3 Research Mode
Accelerates academic and technical research tasks:
- **Literature Reviews**: Highlight a node and select "Generate Literature Review". The engine merges content from all associated PDFs, research papers, and blogs.
- **Citation Graphing**: Shows the connections between articles, research papers, and repositories.
- **Hypothesis Generation**: AI reviews distant nodes in the graph and flags potentially novel correlations.

---

## 3. Configuration & Exclusions

You can configure what and when IML captures page content:
- **Blocklists**: Add specific domains (e.g., `*.bank.com`, `*.localhost`, banking sites, local files) in the settings panel to stop them from being tracked.
- **Active Hours**: Restrict passive tracking to work or study hours.
- **Data Export (Universal Memory Protocol)**: Export your entire graph structure, logs, and notes to local JSON/markdown folders compatible with Obsidian.

---

## 4. License (MIT)

This project is licensed under the MIT License:

```
MIT License

Copyright (c) 2026 Vijay Mahes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
