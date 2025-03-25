import base64
import requests
import os
import json
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import tkinter.messagebox as messagebox
import time
import random
import tkinter as tk

# Path to store the credentials
CREDENTIALS_FILE = "credentials.json"

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            return json.load(file)
    return None

# Function to save credentials to file
def save_credentials(username, password, api_key, sleep_time):
    credentials = {
        'username': username,
        'password': password,
        'api_key': api_key,
        'sleep_time': sleep_time
    }
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file)

# Function to show the interface for inputting or changing credentials
def show_credentials_input():
    def submit_credentials():
        global username_value, password_value, api_key_value, sleep_time
        username_value = username_entry.get()
        password_value = password_entry.get()
        api_key_value = api_key_entry.get()
        sleep_time = int(sleep_time_entry.get()) if sleep_time_entry.get().isdigit() else 10  # Default to 10 seconds if invalid
        save_credentials(username_value, password_value, api_key_value, sleep_time)  # Save new credentials
        root.destroy()

    root = tk.Tk()
    root.title("iClicker Credentials Input")

    tk.Label(root, text="iClicker Username/Email").grid(row=0)
    tk.Label(root, text="iClicker Password").grid(row=1)
    tk.Label(root, text="OpenAI API Key").grid(row=2)
    tk.Label(root, text="Time between every check for active classes (seconds)").grid(row=3)

    username_entry = tk.Entry(root)
    password_entry = tk.Entry(root, show="*")
    api_key_entry = tk.Entry(root)
    sleep_time_entry = tk.Entry(root)

    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)
    api_key_entry.grid(row=2, column=1)
    sleep_time_entry.grid(row=3, column=1)

    tk.Button(root, text="Submit", command=submit_credentials).grid(row=4, column=1)

    root.mainloop()

# Function to display "Start" or "Change Credentials" option
def show_startup_options():
    def start_program():
        global username_value, password_value, api_key_value, sleep_time
        username_value = credentials['username']
        password_value = credentials['password']
        api_key_value = credentials['api_key']
        sleep_time = credentials['sleep_time']
        root.destroy()

    def change_credentials():
        root.destroy()
        show_credentials_input()

    root = tk.Tk()
    root.title("iClicker Bot")

    tk.Label(root, text="Would you like to start or change credentials?").pack()
    tk.Button(root, text="Start", command=start_program).pack()
    tk.Button(root, text="Change Credentials", command=change_credentials).pack()

    root.mainloop()

# Check if credentials exist
credentials = load_credentials()

if credentials:
    show_startup_options()  # Show option to start or change credentials
else:
    show_credentials_input()  # No credentials stored, show input interface

# Get the current directory of the executable or script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Paths for driver and chrome
chrome_binary_path = os.path.join(current_dir, "bin", "chrome-win64", "chrome.exe")
chromedriver_path = os.path.join(current_dir, "bin", "chromedriver-win64", "chromedriver.exe")

# Set chrome options
chrome_options = Options()
chrome_options.binary_location = chrome_binary_path

# Initialize ChromeDriver service
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the iClicker login page
driver.get("https://student.iclicker.com/#/login")

# Log in
driver.find_element(By.ID, "input-email").send_keys(username_value)
driver.find_element(By.ID, "input-password").send_keys(password_value)
driver.find_element(By.ID, "sign-in-button").click()

# Wait for the courses page to load
time.sleep(5)

# OpenAI API Key
api_key = api_key_value

# Function to encode the image in base64 and delete the image file after encoding
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Attempt to delete the file after encoding
    try:
        os.remove(image_path)
        print(f"Screenshot {image_path} deleted.")
    except Exception as e:
        print(f"Failed to delete {image_path}: {e}")
    
    return encoded_image


# Function to send the image to GPT-4 Vision and get the answer
def get_poll_answer(question_type):
    try:
        poll_image_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='question-image-container']//img"))
        )

        # Check if the image has a valid height
        image_height = poll_image_element.size['height']
        if image_height == 0:
            print("Error: Poll image height is 0. Skipping this poll.")
            return None

        poll_image_element.screenshot('poll_question.png')
        print("Poll screenshot captured.")

        # Encode the image to base64
        base64_image = encode_image('poll_question.png')

        # Set headers and payload for the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # Get the appropriate prompt for the question type
        prompt = get_prompt(question_type)
        if prompt is None:
            print("Unable to generate prompt.")
            return None

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        # Send the request to the OpenAI API
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Get the extracted answer from the GPT-4 Vision response
        extracted_answer = response.json()['choices'][0]['message']['content'].strip()
        print(f"Extracted Answer from GPT-4 Vision: {extracted_answer}")
        return extracted_answer

    except TimeoutException:
        print("Poll image not found.")
        return None

        # Send the request to the OpenAI API
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Get the extracted answer from the GPT-4 Vision response
        extracted_answer = response.json()['choices'][0]['message']['content'].strip()
        print(f"Extracted Answer from GPT-4 Vision: {extracted_answer}")
        return extracted_answer

    except TimeoutException:
        print("Poll image not found.")
        return None

# Function to submit the answer based on question type
def submit_answer(answer, question_type):
    try:
        if question_type == QuestionType.MULTIPLE_CHOICE:
            options = ['a', 'b', 'c', 'd', 'e']
            for option in options:
                if option.lower() in answer.lower():
                    answer_button_id = f"multiple-choice-{option}"
                    answer_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, answer_button_id))
                    )
                    answer_button.click()
                    print(f"Answered with option {option.upper()}")
                    return True

            # If no valid answer, select randomly
            random_option = random.choice(options)
            answer_button_id = f"multiple-choice-{random_option}"
            answer_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, answer_button_id))
            )
            answer_button.click()
            print(f"Answered randomly with option {random_option.upper()}")
            return True

        elif question_type == QuestionType.SHORT_ANSWER:
            short_answer_box = driver.find_element(By.ID, "shortAnswerInput")
            short_answer_box.send_keys(answer)
            send_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send Answer') and @class='button primary rounded-button']")))
            send_button.click()
            print(f"Submitted short answer: {answer}")
            return True

    except TimeoutException:
        print("Could not find the answer input field.")
        return False
    
# Function to get the letter limit for short answer
def get_short_answer_limit():
    try:
        limit_element = driver.find_element(By.XPATH, "//div[@class='character-limit']//span")
        limit_text = limit_element.text.strip()
        character_limit = int(limit_text) if limit_text.isdigit() else 140  # Default to 140 if no limit found
        return character_limit
    except NoSuchElementException:
        print("Character limit element not found, using default of 140.")
        return 140  # Default character limit

# Polling loop to check for polls and process questions

answered = False

def poll_loop():
    global answered
    while True:
        try:
            print("Checking for active poll...")

            if check_class_end():
                answered = False  # Reset flag for the next course
                break  # Exit the poll loop and return to course checking

            if is_answer_received() or is_answer_already_displayed():
                print("Skipping question as it has already been answered or the poll is closed.")
                answered = False  # Reset flag for the next question
                time.sleep(2)
            else:
                # Determine the type of question
                question_type = determine_question_type(driver)

                if question_type:
                    # Get the poll answer based on the question type
                    answer = get_poll_answer(question_type)
                    
                    if answer:
                        # Submit the answer based on the question type
                        submit_answer(answer, question_type)
                        answered = True  # Mark as answered to prevent multiple clicks
                        time.sleep(2)
                    else:
                        answered = False

            time.sleep(2)  # Poll every 2 seconds
        except Exception as e:
            print(f"Error encountered during checking: {e}")
            time.sleep(2)

# Function to refresh course list after returning to the "Courses" page
def refresh_course_list():
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//li//label[contains(@class, 'course-title')]"))
        )
        return driver.find_elements(By.XPATH, "//li//label[contains(@class, 'course-title')]")
    except TimeoutException:
        print("Error: Unable to refresh course list.")
        return []
    
def check_class_end():
    try:
        # Check for the presence of "Score" or "Attendance" headers on the page
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//h2[text()='Score']"))
        )
        print("Class has ended. Returning to course checking.")
        return True
    except TimeoutException:
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, "//h2[text()='Attendance']"))
            )
            print("Class has ended. Returning to course checking.")
            return True
        except TimeoutException:
            return False


# Function to return to the course list using "Return to all courses" button
def return_to_course_list():
    try:
        return_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//label[contains(text(), 'Return to all courses')]"))
        )
        return_button.click()
        time.sleep(3)  # Wait for the page to return to course list
    except TimeoutException:
        print("Error: Unable to find the 'Return to all courses' button.")
        return False
    return True

# Function to check for the "Join Class" button on each course page
def check_for_join_button():
    while True:
        courses = refresh_course_list()  # Refresh the course list after every return to the main page

        if not courses:
            print("No active courses found.")
            return False

        for i in range(len(courses)):
            # Refresh the courses list again after returning to ensure it’s not stale
            courses = refresh_course_list()
            course = courses[i]

            course_name = course.text  # Fetch the course name before clicking to avoid stale element
            print(f"Checking course: {course_name}")
            try:
                course.click()  # Click on the course to navigate to its page
                time.sleep(7)  # Wait 7 seconds to give time for the course page and the "Join Class" button to load

                # Check for the presence of the "Join Class" button and if it is visible and clickable
                join_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "btnJoin"))
                )
                if join_button and join_button.is_displayed() and join_button.is_enabled():
                    print(f"Join button found for {course_name}, joining class.")
                    join_button.click()
                    time.sleep(6.5)
                    poll_loop()  # Begin polling after joining class
                else:
                    print(f"Join button is present but not visible or clickable for {course_name}.")
                    
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                print(f"No 'Join Class' button found for {course_name}. Returning to courses.")

            # Return to course list if no join button is found
            if not return_to_course_list():
                print("Failed to return to course list.")
                return False

        print("No active courses found with a 'Join Class' button.")
        return False
    

# Function to check if the answer has already been received
def is_answer_received():
    try:
        status_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "status-text-container-id"))
        )
        if "received".lower() in status_element.text.lower():
            print("Answer has already been submitted for this question.")
            return True
        else:
            return False
    except TimeoutException:
        return False

# Function to check if the "Your Answer" text is displayed after poll closure
def is_answer_already_displayed():
    try:
        your_answer_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your Answer')]"))
        )
        if "Your Answer" in your_answer_element.text:
            print("The poll is closed, and your answer has already been displayed.")
            return True
        else:
            return False
    except TimeoutException:
        return False

#helper function for deciding what type of question  

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"


from selenium.common.exceptions import NoSuchElementException, TimeoutException

def determine_question_type(driver):
    # Define element IDs for different question types
    multiple_choice_indicators = {"multiple-choice-a", "multiple-choice-b", "multiple-choice-c", "multiple-choice-d", "multiple-choice-e"}
    short_answer_indicators = {"shortAnswerInput"}  # Correct ID for short answer

    try:
        # Check for multiple choice question
        for option_id in multiple_choice_indicators:
            try:
                element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, option_id)))
                if element.is_displayed():
                    print("Question is multiple choice")
                    return QuestionType.MULTIPLE_CHOICE
            except TimeoutException:
                continue  # Continue if multiple choice elements are not found

        # Check for short answer question
        for option_id in short_answer_indicators:
            try:
                element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, option_id)))
                if element.is_displayed():
                    print("Question is short answer")
                    return QuestionType.SHORT_ANSWER
            except TimeoutException:
                continue  # Continue if short answer elements are not found

        # No question type found
        print("No recognizable question type found.")
        return None

    except NoSuchElementException as e:
        print(f"Error encountered while determining question type: {e}")
        return None

    
# Modifying the prompt to suit the question type
def get_prompt(question_type):
    if question_type == QuestionType.MULTIPLE_CHOICE:
        return "You are an AI that answers multiple-choice questions, giving only the corresponding letter as the answer."
    elif question_type == QuestionType.SHORT_ANSWER:
        char_limit = get_short_answer_limit()
        return "You will be given questions. Provide a brief response based on the question. For questions that seem to be asking for a perspective, please assume the personality of the average person and answer from a personal perspective. Eg. please refer to yourslef as I. Lastly and importantly, keep your response within {char_limit} characters."
    else:
        return None

# Looping the function 
while True:
    print("Checking for available classes...")
    if not check_for_join_button():  # This will check for available classes
        print("No classes found, retrying in" + " " + str(sleep_time) + " " + "seconds...")
        time.sleep(sleep_time)  # Wait 10 seconds before checking again
    else:
        print("Class joined or process interrupted. Will check again after class ends.")

# Close the browser after the loop completes (if needed)
driver.quit() 