# iClicker Assistant Bot (GPT-4 Vision Enabled)

This project is a Python-based automation assistant for iClicker. It helps students engage with class content by monitoring active courses, detecting polls, and generating responses using GPT-4 Vision. It is particularly useful for accessibility support, study review, and classroom participation assistance.

This tool is not designed or intended for academic dishonesty. It is provided as a framework to support educational engagement, automation learning, and accessibility.

---

## Features

- Secure local credential storage with a simple GUI interface
- Automated detection and handling of iClicker poll types (multiple choice, short answer, multiple answer)
- Poll image capture and analysis using GPT-4 Vision (image-to-text)
- Automatic submission of generated responses
- Compatible with both single-question polls and multi-question quizzes
- Adjustable polling interval between checks for active classes

---

## How It Works

1. On launch, the tool prompts for iClicker login details and OpenAI API key using a local `tkinter` interface.
2. The bot logs in to the iClicker dashboard and polls for active classes.
3. When a class is active, the bot joins the session and checks for open polls.
4. If a poll is detected, it:
   - Captures the poll question as an image
   - Sends it to OpenAI’s GPT-4 Vision API
   - Receives and processes the generated answer
   - Submits the response through the iClicker interface
5. It also supports basic quiz navigation and submission.

---

## Requirements

- Python 3.8 or higher
- Chrome browser (portable or system-installed)
- OpenAI API Key with GPT-4 Vision access
- Python dependencies:
  ```bash
  pip install selenium requests
  ```

---

## File Structure

```
project/
├── main.py                  # Main automation script
├── credentials.json         # Stores login and configuration data
└── bin/
    ├── chrome.exe           # Optional: Portable Chrome browser
    └── chromedriver.exe     # ChromeDriver for automation
```

---

## Usage

1. Clone or download the project.
2. Place `chrome.exe` and `chromedriver.exe` inside the `bin` directory, or modify the script to use your system’s Chrome installation.
3. Run the script:
   ```bash
   python main.py
   ```
4. Enter your iClicker credentials, OpenAI API key, and polling interval when prompted.

The program will automatically monitor your classes and handle polls accordingly.

---

## Important Notice on Responsible Use

This project is provided for:

- Assisting students with accessibility needs
- Supporting real-time participation during live or asynchronous sessions
- Educational demonstration of automation and AI integration in academic tools

By using this software, you agree to comply with your institution’s academic integrity policies. The developer does not condone or support cheating or misuse of the platform. You are solely responsible for how you use this tool.

---

## License

This project is licensed under the MIT License. You may use, modify, and distribute the code for personal or educational purposes. Commercial use is not permitted without express permission.

---

## Contact

For technical inquiries or improvement suggestions, feel free to open an issue or submit a pull request.
