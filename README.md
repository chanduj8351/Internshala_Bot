# 🚀 Internshala Auto-Apply Bot 🤖

> ✨ Automatically discover, filter, and apply to remote (WFH) jobs on Internshala – with cover letters and application questions answered intelligently using OpenAI.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-Automation-green.svg)
![Web Scraping](https://img.shields.io/badge/Web-Scraping-orange.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-yellow.svg)

---

## 🧠 What is This?

**Internshala Auto-Apply Bot** is a Python-based intelligent automation script designed to:

* Automatically log in to Internshala
* Fetch the latest internships/jobs (WFH only)
* Extract job data and save it to a CSV file
* Auto-fill **Cover Letters** using GPT-generated responses
* Auto-fill **Additional Questions** smartly using AI rules
* Submit the application — like a pro!

It's like having your personal job application assistant 👩‍💻

---

## 🔧 Features

✔️ **Undetectable Chrome Automation** using `undetected_chromedriver`
✔️ **GPT-Driven Answers** for cover letters & questions
✔️ **Avoids Duplicates** by tracking already applied jobs
✔️ **Logs Everything** with clean output and UTF-8 support
✔️ **Resumes Automatically** after exceptions
✔️ **Writes to CSV** for job parsing & record keeping

---

## 📦 Folder Structure

```
project-root/
│
├── assets/
│   ├── chromedriver.exe           # Selenium driver
│   └── chromedata/                # Chrome user data to persist session
│
├── data/
│   ├── internshala/
│   │   ├── jobs.csv               # Scraped job listings
│   │   ├── applied_jobs.txt       # Tracks already applied jobs
│   │   └── job_details.txt        # Stores current job description
│
├── models/
│   └── openai.py                  # GPT wrapper for prompt generation
│
├── main.py                        # Main script (the one you're running)
└── README.md                      # This file
```

---

## 🤖 How It Works

1. Logs in to your Internshala student dashboard
2. Clicks on the "Jobs" section
3. Filters for WFH jobs (`0 year(s)` experience)
4. Scrapes job details
5. For each job:

   * Applies if not already applied
   * Detects if Cover Letter or Additional Questions are required
   * Uses OpenAI to generate responses
   * Submits the application
6. Updates `applied_jobs.txt` to avoid duplicates

---

## ⚙️ Requirements

* Python 3.8+
* Chrome Browser (installed)
* OpenAI API key
* Required libraries (install with pip)

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```txt
undetected-chromedriver
selenium
beautifulsoup4
pyautogui
openai
```

---

## 🧪 GPT Integration

This bot uses a file named `openai.py` inside `models/` with a function `Gpt(prompt, system_prompt)` to generate cover letters and answers. Example logic:

```python
response = Gpt(
    prompt=question_text,
    system_prompt=sys_prompt
)
```

Make sure you handle your OpenAI key and response handling securely in that file.

---

## ✨ Pro Tips

* ✅ Ensure you're already **logged in** to Internshala using Chrome with the same profile (it uses your local Chrome session).
* ⚠️ Keep `chromedriver.exe` version aligned with your Chrome version.
* 🛠 Modify prompts in `sys_prompt` and `cover_letter_prompt()` for different personalities or writing styles.
* 🔁 Re-run the script periodically to keep applying to new listings.

---

## 🧩 Want to Extend?

Here are a few ideas:

* ✅ Add filters (stipend, domain, posted date)
* 📧 Integrate email notifications after each submission
* 💬 Connect with Telegram bot to show job matches
* 💾 Save job descriptions as PDFs
* 🎯 Add analytics (e.g., #jobs applied/day)

---

## 🧍 Applicant Profile

> The bot personalizes every application based on this profile (editable):

```yaml
Name: J Chandu  
Mobile: +91 7032654675  
Email: chanduj8351@gmail.com  
LinkedIn: https://www.linkedin.com/in/chandu-j-24558236b/  
GitHub: https://github.com/chanduj8351
```

---

## 📽️ Demo (Coming Soon)

Want to see this bot in action? Stay tuned for a demo video!

---

## 🛑 Disclaimer

> ⚠️ Use this responsibly. Internshala's terms may not allow automation for submissions. This project is for educational and personal automation purposes only. You're solely responsible for how it's used.

---

## 🙌 Final Words

Whether you're tired of repetitive job applications or want to level up your productivity — **this bot is for you**. Let AI do the grunt work while you focus on interviews!

---

**Made with 💻 + 🤖 by Chandu J**
Drop a ⭐ if this helped you!

---
