# 🧠 Brain Squeeze

<!-- badges: start -->

![Pylint](https://github.com/CodeStarter25/brain_squeeze_flask/actions/workflows/pylint.yml/badge.svg)
![CodeQL](https://github.com/CodeStarter25/brain_squeeze_flask/actions/workflows/codeql.yml/badge.svg)
[![Codecov test coverage](https://codecov.io/gh/CodeStarter25/co2emissionsanalyzer/graph/badge.svg)](https://app.codecov.io/gh/CodeStarter25/co2emissionsanalyzer) 
<img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />

<!-- badges: end -->

### 🎥 [Video Demo](https://youtu.be/-s2VwBVfW2w)

## 📌 Description

**Brain Squeeze** is a two-player web-based game built in Flask for my CS50x final project. It combines Python, HTML, CSS, JavaScript, and Jinja templating to create a full-stack game experience.

Players are given a random letter and must come up with five words — each fitting into a fixed category — all starting with that letter. Once submitted (or when time runs out), the backend checks the answers and calculates a score based on uniqueness and validity, displaying a results page with the winner and submitted words.

This project includes:
- 🔐 User registration and login
- 💾 Gameplay history saved in a database
- 🖥️ Frontend built with Bootstrap, HTML, and JavaScript
- ⚙️ Backend built in Python (Flask), with secure routing and input validation

---

## 🧪 Features

- User authentication (register, sign in, login before each game)
- Session tracking with history and scoring
- Input validation against category-specific word lists
- Score calculations with uniqueness checks
- Frontend logic handled via JavaScript (timers, UI reveals, etc.)
- Responsive design using Bootstrap
- Separate gameplay modes: Quick, Extra, Long

---

## 🧱 File Structure

### `app.py`
The main Flask app that routes pages, handles backend logic, and interacts with helper functions for modularity and better structure.

### `helper.py`
Contains core logic functions:
- Account creation and updates
- Input validation and word list checking
- Scoring system logic
- Database operations with automatic handling

---

## 🌐 Webpages

| Page             | Description |
|------------------|-------------|
| `index.html`     | Landing page |
| `layout.html`    | Shared base layout |
| `register.html`  | Create account |
| `signin.html`    | Sign in to view profile |
| `profile.html`   | View/edit account, gameplay history |
| `quick.html`     | Game mode |
| `extra.html`     | Game mode |
| `long.html`      | Game mode |
| `results.html`   | Game results and winner |

---

## 📦 Requirements

```text
blinker==1.9.0
cachelib==0.13.0
click==8.1.8
colorama==0.4.6
Flask==3.1.0
Flask-Session==0.8.0
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
msgspec==0.19.0
pytz==2025.2
Werkzeug==3.1.3
```

## 📚 Data Resources

Category word lists were sourced from various open web resources:

- **Animals**: [animals.net](https://animals.net/)
- **Objects**: [Common nouns](https://grammarvocab.com/things-name-list-a-to-z)
- **Countries & Names**: GitHub datasets
- **Movies**: CS50X content
- **Picture**: [Winner badge PNG](https://www.pikpng.com/pngvi/iToxTbJ_winner-free-png-image-winner-badge-roblox-clipart/)
- **Picture (favicon)**: [Brain Image for tabs](https://icons8.com/icon/2070/brain)


Additional resources for coding and debugging:
- [Stack Overflow](https://stackoverflow.com)
- [W3Schools](https://www.w3schools.com)
- [GeeksForGeeks](https://www.geeksforgeeks.org)

---

## 🛠️ Development Journey

This project took about a month to complete. As a beginner (CS50X being my first exposure to programming), I went through countless iterations, testing different solutions, refactoring code, and learning how to split logic between `app.py` and `helper.py`.

I struggled with local environment setup (first with WSL, then switching to GitHub Codespaces, then to VSCode locally). It was frustrating at times, but I learned how to:

- Refactor messy code into reusable functions
- Use Flask’s routing and session management
- Implement front-end logic with JavaScript
- Design responsive layouts with Bootstrap
- Write SQL queries and manage user data securely

It wasn’t easy — but it was worth it.

---

## 🗓️ Project Info

- **Start Date:** April 17, 2025  
- **Completion Date:** May 7, 2025  
- **Total Commits:** 98  

---

## 🙏 Thanks

Thanks to the [CS50x](https://cs50.harvard.edu/x/) team for the course and everyone on Stack Overflow, GeeksForGeeks, and W3Schools for guidance.

---

## 💭 Final Thoughts

This project taught me the value of debugging, iteration, and attention to detail. The first solution is rarely the best one — and sometimes rewriting everything is part of the process.

---
