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
* **`VMSOIT-Slide-Generator-Prompt.md`**: The master prompt file containing strict instructions, color codes, and structures to feed into Claude.

---

### 🛠️ Step-by-Step Creation Process

#### Step 1: Initialize Your Design System & Skills
1. **Prepare Your Brand Assets**: Identify your primary colors (Hex codes), custom fonts, and logo SVG or PNG assets.
2. **If using Claude Web Interface**: 
   * Navigate to the `important skills` folder in this repo.
   * Upload/import these skill files into Claude's system prompt or custom instructions as a "Skill".
3. **If using Claude Code**:
   * Run Claude Code within your IDE (e.g., Cursor or Anti-gravity).
   * Install the standard skill framework directly by passing the Git URLs of pre-built slide frameworks:
     * [ECC Frontend Slides](https://github.com/affaan-m/ECC/tree/main/skills/frontend-slides)
     * [Beautiful HTML Templates](https://github.com/zarazhangrui/beautiful-html-templates)
     * [UI/UX Pro Max Skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
     * [Frontend Slides Framework](https://github.com/zarazhangrui/frontend-slides)

#### Step 2: Configure the Slide Generator Prompt
* Open `VMSOIT-Slide-Generator-Prompt.md`.
* Tweak the variables (fonts, colors, background styles, and logo placeholders) to match your company's official brand book.
* *Note: If this template is already perfect for your needs, simply update the CSS hex colors and swap the logo paths in the code!*

#### Step 3: Generate the Slides

Depending on your setup, follow one of the two methods:

##### Method A: Using Claude Web Interface (1-by-1 Approach)
1. Provide Claude with the `VMSOIT-Slide-Generator-Prompt.md` instructions and your outline structure.
2. Ask Claude to generate your slides **one-by-one**. 
   * *Tip:* Ask Claude to output **only the core HTML/CSS component code** for new slides, rather than rewriting the entire wrapper file every time.
3. Once all slide blocks are written, manually merge them inside the container class of your main HTML index file.

##### Method B: Using Claude Code (All-at-Once Automation)
1. Run a local development environment.
2. Ask Claude Code to analyze your target website (or brand guidelines) and programmatically compile the entire slide deck layout at once.
3. Use the terminal or local server to instantly preview the slides, adjusting variables on the fly.

---

## 🐍 Pro Tip: Scalable Slide Production with Python 

If manual merging or direct prompting isn't scalable for your workflow, you can automate this using Python! 

1. Write a Python script that takes a structured **`data.json`** file containing slide text, bullet points, and image URLs.
2. Have the script parse the JSON data and programmatically inject the content directly into your brand's HTML slide template wrappers.
3. Output a perfectly formatted, multi-slide single HTML presentation file in seconds.

> **Simplistic Alternative:** If Python isn't your strong suit, you can simply upload this finished HTML template to Claude, provide raw text data (reports, notes, transcripts), and prompt: *"Convert this data into slides using the layout design principles of this template."* It will fill out the content dynamically!

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
* **Email:** [your-email@example.com] *(Replace with your actual email)*
* **LinkedIn:** [Your Name / Profile Link] *(Replace with your LinkedIn)*
* **Schedule a Call:** [Link to Calendly or similar] *(Replace with your booking link)*

---
*If you find this repository helpful, please give it a ⭐ to support the project!*
