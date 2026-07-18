# 🎭 HTML Slides Template

An ultra-premium, dynamic HTML/CSS/JS presentation template system engineered to replace boring PowerPoint slop with stunning, fluidly animated, and brand-aligned motion graphic slides. 

This repository provides an automated, programmatic approach to generating high-converting slide decks using **Claude AI**—perfect for corporate presentations, training events, tech pitches, and sales workflows.

---

## 🚀 The Workflow: How to Create Your Slide Templates

Whether you are using the **Claude Web Interface** or the CLI-based **Claude Code**, you can build stunning, brand-consistent HTML slides in minutes.

### 📁 Directory & Asset Structure
* **`skills/`**: Contains core JSON-based skill files that you import into Claude to teach it how to design slides following universal design principles.
* **`Reference Files (Required)/`**: Reference templates to help define your custom layout, container shapes, and base structures.
* **`HTML Slides (Required Skill Files)/`**: Code snippets and components to deepen Claude's understanding of slide structures, animations, and bento grids.
* **`VMSOIT-Slide-Generator-Prompt.md`**: The master prompt file containing strict instructions, color codes, layouts, and structures to feed into Claude.

---

### 🛠️ Step-by-Step Creation Process

#### Step 1: Establish Your Brand Design System (Quick Method)
To make your slides truly unique, you need a cohesive design template that reflects your brand identity (typography, primary/secondary colors, spacing tokens, and logos). 
* **The Fastest Method:** You can use **Google Pomelli**. It is one of the best tools to spin up a complete brand design template in a fraction of the time. Simply feed your brand's live website URL into Google Pomelli, and it will instantly extract a complete brand design template equipped with every detail you need for your slides.

#### Step 2: Initialize Your Skills in Claude
1. **If using the Claude Web Interface**: 
   * Navigate to the `important skills` folder in this repository.
   * Upload or copy/paste these skill files into Claude's custom instructions or project knowledge base to establish the design constraints.
2. **If using Claude Code (CLI/IDE)**:
   * Run Claude Code directly inside your development workspace (e.g., Cursor, Anti-gravity, or your terminal).
   * Install the standard slide layout skill framework by linking Claude Code directly to these premier community libraries:
     * [ECC Frontend Slides](https://github.com/affaan-m/ECC/tree/main/skills/frontend-slides)
     * [Beautiful HTML Templates](https://github.com/zarazhangrui/beautiful-html-templates)
     * [UI/UX Pro Max Skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
     * [Frontend Slides Framework](https://github.com/zarazhangrui/frontend-slides)

#### Step 3: Configure the Master Prompt Template
* Open the `VMSOIT-Slide-Generator-Prompt.md` file.
* Tweak the core variables (Hex color codes, global fonts, background patterns, and logo files) to match the brand book details you gathered in Step 1.
* *Note: If this template's base styling is already perfect for your needs, you can simply change the font colors and point the image tags to your own logo assets!*

#### Step 4: Generate the Slides

Depending on your daily workflow preferences, choose one of the two generation approaches:

##### Method A: Using Claude Web Interface (1-by-1 Interactive Flow)
1. Provide Claude with the updated text instructions inside `VMSOIT-Slide-Generator-Prompt.md` along with your presentation outline.
2. Direct Claude to generate your slides **one-by-one**. 
   * *Crucial Prompting Tip:* Ask Claude to output **only the component code blocks** for new slides rather than rewriting the full HTML wrapper structure every time.
3. Manually copy and merge the resulting slide sections into the main container class of your primary presentation HTML file.

##### Method B: Using Claude Code (Automated All-at-Once Flow)
1. Initialize Claude Code inside your local repository folder.
2. Direct Claude to pull structural layout principles from the repository assets and programmatically compile the entire slide presentation in a single pass.
3. Spin up a local server to instantly preview the animations, spacing ratios, and responsive layouts on the fly.

---

## 🐍 Automation & Compilation Frameworks

### 1. Dynamic JSON-to-HTML Parsing (Python Option)
If manual copying or constant prompting becomes tedious, you can build a light automation script:
* Design a Python script that takes a structured **`data.json`** file containing slide text, headings, list points, and image links.
* The script reads your brand-aligned master template base and loops through the JSON keys, programmatically stamping the content directly into clean HTML structures.

> **Direct Prompting Alternative:** If you prefer not to manage a local Python setup, simply upload your empty, styled HTML template directly into a Claude thread, provide raw text data (reports, transcripts, drafts), and prompt: *"Convert this data into presentation slides using the layout design principles embedded in this template."* Claude will cleanly generate ready-to-run slide code populated with your content.

### ⚠️ Important Warning Regarding PDF Exports
> [!WARNING]
> If you plan to use a Python script (such as Playwright, Selenium, or WeasyPrint) to programmatically convert your final HTML slides into a downloadable PDF format, keep in mind that **the generated PDF document will not look perfect due to active animations and interactive transitions**. 
> For the best clean static document result, you will need to apply a utility print style sheet (`@media print`) that suppresses CSS transitions, pauses keyframe loops, and displays all content blocks flat on the page layout before running the export script.

---

## 🎨 Design Inspiration & Tutorials

Learn how to leverage design systems, extract brand books, and build spectacular animated bento components using these video tutorials:
* 🎥 [Claude HTML Slides = The NEW Powerpoint Killer (Full Tutorial)](https://www.youtube.com/watch?v=t2ELuj2prA0) — Perfect for learning how to embed custom SVG animations, motion loops, and charts.
* 🎥 [I Replaced PowerPoint With Claude Code](https://www.youtube.com/watch?v=nAfbaZysFuk) — Explains the 20 universal design principles of layout design (whitespace ratios, 5% edge boundaries, data-ink ratio) to make slides look premium and professional.

---

## 🤝 Let's Collaborate: Discuss Workflows, Problems & Solutions

Are you trying to automate your company's presentation creation workflow? Or perhaps you're running into performance, responsiveness, or slide-rendering issues with complex animations? **I can help you build custom solutions.**

### 💡 What We Can Discuss:
* **Workflow Automation:** Creating custom Python/Node scripts to convert JSON datasets, markdown documents, or databases into live branded presentation templates automatically.
* **Custom AI Agent Tooling:** Engineering specialized system prompts to help your marketing/sales teams write perfectly formatted decks.
* **Interactive Components:** Building custom interactive widgets, charts, and real-time data visualizers inside your presentations.
* **Cross-Browser Styling & Printing:** Resolving CSS Page Break issues for clean exports to PDF.

### 📬 Connect With Me

Let's turn your ideas into functional, beautiful web-based presentations!

* **GitHub Issues:** Open an issue right here in this repository to suggest improvements or report bugs.
* **Contact:** [https://docs.google.com/forms/d/e/1FAIpQLSfFlNRMuvdiwHLbjGfhOyMmkXyC5t6ri34_jxiHhGWixAJyFQ/viewform?usp=publish-editor]

---
*If you find this repository helpful, please give it a ⭐ to support the project!*
