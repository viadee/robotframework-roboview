# RoboView - Keyword Management in Robot Framework
![banner](./static/github_banner.png)
[![PyPI version](https://img.shields.io/pypi/v/robotframework-roboview.svg)](https://pypi.org/project/robotframework-roboview/)
![license](https://img.shields.io/badge/license-Apache--2.0-green)
![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)


RoboView is a Visual Studio Code extension designed to help you manage keywords within your Robot Framework projects and improve overall test quality through built-in Robocop integration. Its primary goal is to provide a comprehensive overview of all keywords and their relationships, making it easier to understand and maintain your test automation codebase.

---

## ✨ Key Features

- 🗂️ **Workspace:** Automatically selects your current workspace project and generates comprehensive overviews.
- 📈 **Dashboard:** Get key performance indicators and a general overview of your robot framework project.
- 📝 **Keyword Overview & Filtering:** Instantly view all keywords of a selected file, filter by type (initialized, called).
- ❓ **Global Filter:** Searches your files for any keywords lacking documentation, unused keywords or faulty keywords with cycle calling.
- 📖 **Detailed Keyword Insights:** Select any keyword to see where it is defined, how often it is used (both in its own file and across the project), and view its documentation.
- 🧩 **Similarity Detection:** Get information about similar or potentially duplicate keywords through similarity analysis of keyword source code.
- 🧭 **Code Navigation:** Jump straight to a keyword’s definition with a simple Ctrl+Click.
- 🛡️ **Robocop Integration:** Runs Robocop directly from within RoboView, inspect lint results in context, and use your custom configuration file (e.g. robocop.toml) out of the box.
- 🔍 **Search & Sorting:** Quickly find keywords using the search bar and sort them by name or usage statistics.

---

## ⚙️ Installation Guide

RoboView consists of two parts: a **backend** (Python package) and a **frontend** (Visual Studio Code extension).

### ✅ Backend

Install the backend via **pip**:

```bash
pip install robotframework-roboview
```

### ✅ Frontend

The Frontend is available as a Visual Studio Code extension on the Marketplace – install it in seconds from the VS Code Extensions view.
1. Open **Visual Studio Code**.
2. Go to the **Extensions** view (`Ctrl+Shift+X` / `Cmd+Shift+X`).
3. Search for **"RoboView"**.
4. Install the RoboView extension by *viadee Unternehmensberatung AG*.

---

## 🛠️ GitHub

You can find the RoboView source code and issue tracker on GitHub:

👉 **https://github.com/viadee/robotframework-roboview**

---

## 📝 Notes and Recommendations

- For Robocop to automatically detect your configuration, name the file **`robocop.toml`**, **`robot.toml`** or integrate in **`pyproject.toml`**.  
  If you cannot change the filename in your project, you can instead set the environment variable **`ROBOCOP_CONFIG_PATH`** to the full path of your config file.
- If the Robocop configuration file is outdated or cannot be parsed, RoboView falls back to **Robocop’s default settings**. The same applies if no configuration file is found.
- RoboView follows your IDE’s color theme. We recommend using a **dark theme**, as text in light themes can be harder to read - but feel free to experiment and choose what works best for you.

---

## 🔍 How to navigate RoboView

In the following three sections, we will dive deeper into how to navigate RoboView: where to find the features and understand the terminology we use. We start with the dashboard, then look at the keyword usage overview, and finally the Robocop integration.
You can switch between these views using the buttons in the top-right corner of RoboView: <code>Dashboard</code>, <code>Keyword Usage</code>, and <code>Robocop</code>.

## 📋 1) Dashboard

The **Dashboard** gives you a high‑level overview of the selected Robot Framework project and its overall health.


<p align="center">
  <img src="./static/dashboard_1.png" alt="keyword_list" width="900"/>
</p>
<p align="center">
  <img src="./static/dashboard_2.png" alt="keyword_list" width="900"/>
</p>

<br>

At the top of the dashboard you’ll see the **Selected Project**. RoboView automatically detects your current workspace and shows:
- The **project name**
- The **absolute path** to the project root

This ensures all metrics are calculated against the correct `.robot` and `.resource` files.

### KPIs

The **KPIs** section summarizes the most important metrics of your test suite:
- **User Defined Keywords**: Total number of custom keywords found in your project.
- **Keyword Reuse Rate**: Percentage of keywords that are used more than once. A higher value indicates better reuse and less duplication/redundancy.
- **Unused Keywords**: Number of keywords that are never called anywhere in the project. Use this to identify dead code and candidates for cleanup.
- **Robocop Issues**: Total number of Robocop violations detected across the project. This helps you quickly assess structural and style problems in your tests.
- **Documentation Coverage**: Percentage of keywords that contain a `[Documentation]` section. A higher value means your test suite is better documented and easier to maintain.
- **Robot Framework Files**: Total number of `.robot` and `.resource` files that were analyzed. Use the dashboard to quickly spot problematic areas (e.g. many unused keywords, low documentation coverage, or a high number of Robocop issues) and decide where to focus your refactoring or cleanup efforts first.


## 🌳 2) Keyword Overview

<p align="center" style="margin-bottom: 0.5em;">
  <strong>Keyword Overview Layout</strong>
</p>
<p align="center" style="font-family: monospace; line-height: 1.4; white-space: pre;">
[ Left: File Navigation &amp; Keyword Filters ]   [ Middle: Keyword List ]   [ Right: Keyword Details ]
</p>

<p align="center">
  <img src="./static/keyword_usage.png" alt="graph_view" width="900"/>
</p>

<br>

### ⬅️ Left Side – Navigation &amp; Filters

- <strong>File Selection:</strong> At the top, a dropdown lets you select a file. The current VS Code workspace is used as root, and all
  <code>.robot</code> and <code>.resource</code> files are available.
- <strong>Type Filter:</strong> Choose which group of keywords to display for the selected file:
    - <strong>All Keywords:</strong> Shows every keyword that is either defined in or used by the selected file.
    - <strong>Initialized Keywords:</strong> Only keywords that are defined/implemented in the selected file.
    - <strong>Called Keywords:</strong> Only keywords that are used in the selected file but defined elsewhere.
- <strong>Global Filter:</strong> Jump directly to common problem areas across the entire project:
    - <strong>Keywords without Documentation:</strong> Keywords that are missing documentation.
    - <strong>Unused Keywords:</strong> Keywords that are never called in any analyzed file.
    - <strong>Keywords with Calling Cycles:</strong> Keywords that participate in cyclic calls (A calls B, B calls A, etc.), which can indicate design or maintainability issues.

<br>

### 📊 Middle – Keyword List

The middle section lists all keywords found in the selected file and shows key information about each of them:

- <strong>Origin indicator:</strong> A color-coded label to the left of the keyword name shows where the keyword comes from:
    - <strong>U</strong>: User-defined keyword.
    - <strong>E</strong>: External keyword (e.g. from <code>BuiltIn</code> or libraries like <code>Browser</code>).
- <strong>Definition location:</strong> The file in which the keyword is defined.
- <strong>File-local usage count:</strong> How often the keyword is used (called) in the selected file.
- <strong>Project-wide usage count:</strong> How often the keyword is used across all <code>.robot</code> and <code>.resource</code> files in the current project.

<br>

### ➡️ Right Side – Keyword Details

When you select a keyword (by clicking a row in the middle table), the right panel shows detailed information:

- <strong>Documentation:</strong> The keyword’s documentation as defined in the source code.
- <strong>Usage across files:</strong> In which <code>.robot</code> and <code>.resource</code> files the keyword is used, and how often in each file.
- <strong>Similarity analysis:</strong> A list of up to five keywords that are most similar to the selected one, based on its name and source code using term-frequency-based similarity.

<br>

---

<h3 style="border-bottom: none; margin-bottom: 1em;">🛡️ 3) Robocop</h3>

The **Robocop** view integrates the `https://robocop.readthedocs.io/` linter directly into RoboView, so you can spot and fix structural and style issues in your Robot Framework tests without leaving VS Code.

<p align="center" style="margin-bottom: 0.5em;">
  <strong>Robocop Issues Layout</strong>
</p>
<p align="center" style="font-family: monospace; line-height: 1.4; white-space: pre;">
[ Left: Error Overview ]   [ Middle: Error List ]   [ Right: Error Details ]


<p align="center">
  <img src="./static/robocop.png" alt="robocop_issues" width="900"/>
</p>


<br>

### How it works

- **Left: Error Overview**  
  The left panel shows a compact **overview of all detected issues**, for example:
    - Total number of Robocop findings
    - Issues grouped by **rule** or **category**
    - A quick way to see which types of problems are most common
      This helps you understand the overall state of your project at a glance.
- **Middle: Error List**  
  The middle panel contains the **list of individual Robocop issues**.  
  Each entry typically shows:
    - The **file** where the issue was found
    - The **rule id** and short **message**
    - The **line** number in the file

  You can scroll through this list and select a specific issue to inspect it in detail.

- **Right: Error Details**
  The right panel displays **details for the currently selected issue**, including:
    - The full Robocop message
    - The rule id and its description
    - The file and line information
    - Additional context that helps you understand why this issue was reported

<br>

---

## 🔮 Outlook

RoboView is an actively evolving project. ✨  
We’re continuously adding new features, polishing existing workflows, and exploring fresh ideas to make working with Robot Framework even more enjoyable. 💡

We’re happy to have you along for the journey – stay tuned for new releases and improvements! 🚀