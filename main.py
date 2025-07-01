#### Version --1
### Fastly responds
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pathlib
import csv
import os
import warnings
from time import sleep
import logging
import pyautogui
from selenium.webdriver.common.action_chains import ActionChains

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.openai import Gpt


def setup_logging():
    """Setup logging with proper UTF-8 encoding for Windows"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler with UTF-8 encoding
    # file_handler = logging.FileHandler('internshala_bot.log', encoding='utf-8')
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    
    # Console handler with UTF-8 encoding (fallback to ASCII if needed)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Try to set UTF-8 encoding for console on Windows
    try:
        import sys
        if sys.platform.startswith('win'):
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        # If UTF-8 setup fails, continue with default encoding
        pass
    
    logger.addHandler(console_handler)
    return logger


logger = setup_logging()


sys_prompt = """
You are a Job Application Question Responder Bot.

Your role is to automatically generate short, relevant answers to job application form questions using predefined rules and applicant information.

Rules & Response Patterns:
- Do **not** disclose that you're an AI or assistant.
- Do **not** include any information not belonging to the applicant.
- Always keep answers clear, concise, and professional.

Auto-detect question intent using keywords and respond as follows:

1. **Notice Period**  
   Keywords: "notice period", "available to join", "joining time"  
   → Respond with: **"0"**

2. **Expected Salary**  
   Keywords: "expected salary", "salary expectation"  
   → Respond with: **"Negotiable"**

3. **Last Drawn CTC / Current CTC**  
   Keywords: "last drawn CTC", "current salary", "past salary", "monthly salary"  
   → Respond with: **"2.5"**

4. **Years of Experience (Content Writing or Others)**  
   Keywords: "years of experience", "experience in", "how many years"  
   → Respond with: **numeric digits only** (e.g., "3", not "three")

5. **Portfolio / Links / Profiles**  
   Keywords: "LinkedIn", "GitHub", "portfolio", "online profile"  
   → Respond using the applicant's relevant URLs.

6. **Contact Information**  
   Keywords: "email", "mobile", "phone number", "contact"  
   → Use the applicant's provided contact details.

7. **General Open-Ended Questions** (e.g., "Tell us about yourself", "Why should we hire you?")  
   → Respond with a short and meaningful paragraph tailored to the applicant's profile (wait for user or system to provide content context).

Applicant Details:
    Name: J Chandu  
    Mobile: +91 7032654675  
    Email: chanduj8351@gmail.com  
    LinkedIn: https://www.linkedin.com/in/chandu-j-24558236b/  
    GitHub: https://github.com/chanduj8351

"""

warnings.simplefilter('ignore')

# Setup driver
ScriptDir = pathlib.Path().absolute()
options = uc.ChromeOptions()
options.add_argument('--profile-directory=Default')
options.add_argument(f'--user-data-dir={ScriptDir}\\assets\\chromedata')
driver = uc.Chrome(options=options, driver_executable_path=os.path.join(ScriptDir, 'assets', 'chromedriver.exe'))
driver.maximize_window()

# XPaths dictionary
xpaths = {
    "intershala": (By.XPATH, '//*[@id="content"]/div/div[1]/div/h1'),
    "jobs_btn": (By.XPATH, '//*[@id="jobs_new_superscript"]'),
    "container": (By.XPATH, '//*[@id="internships_list_container"]'),
    "job_details": (By.XPATH, '//*[@id="details_container"]/div[2]'),
    "top_apply_btn": (By.XPATH, '//*[@id="top_easy_apply_button"]'),
    "bottom_apply_btn": (By.XPATH, '//*[@id="easy_apply_button"]'),
    "apply_details": (By.XPATH, '//*[@id="application-form-container"]'),
    "submit_btn": (By.XPATH, '//*[@id="submit"]')
}

# Navigate to Internshala dashboard
def login():
    url = "https://internshala.com/student/dashboard"
    driver.get(url)

# Wait for element
def wait_for_element(locator, timeout=15):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return element
    except TimeoutException:
        print(f"Element {locator} not found within {timeout} seconds.")
        return None
    
def cover_letter_prompt():
    # Generate cover letter based on job details
    base_prompt = """
    You are a highly skilled and professional Cover Letter Generator.

    Your task is to write a compelling, tailored cover letter for a job application, focusing on why the applicant is a strong fit for the role.

    You will be provided with specific job details, including the job title, responsibilities, and requirements.

    Using this information, craft a well-structured cover letter that:
    - Highlights the applicant's relevant skills, qualifications, and experience
    - Aligns the applicant’s background with the job description
    - Demonstrates enthusiasm and professionalism
    - Concludes with a strong call to action

    Applicant Details:
        Name: J Chandu
        Email: chanduj8351@gmail.com
        Linkdin: https://www.linkedin.com/in/chandu-j-24558236b/


    Wait for the job description before generating the cover letter.
    """
    return base_prompt

def parse_jobs_to_csv(html, filename=os.getcwd() + '/data/internshala/jobs.csv'):  
    soup = BeautifulSoup(html, 'html.parser')
    internships = soup.find_all('div', class_='individual_internship')

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Company', 'Stipend', 'Experience', 'Posted Time', 'Job Link'])

        for internship in internships:
            # Initialize all fields with defaults
            title = company = stipend = 'N/A'
            experience = posted_time = job_link = 'N/A'

            # Extract title and company
            title_tag = internship.find('h3', class_='job-internship-name')
            if title_tag:
                title = title_tag.text.strip()

            company_tag = internship.find('p', class_='company-name')
            if company_tag:
                company = company_tag.text.strip()

            stipend_tag = internship.find('span', class_='desktop')
            if stipend_tag:
                stipend = stipend_tag.text.strip()

       
            experience = 'N/A'
            for div in internship.find_all('div', class_='row-1-item'):
                if div.find('i', class_='ic-16-briefcase'):
                    span = div.find('span')
                    if span:
                        experience = span.text.strip()
                    break


            # Posted Time
            posted_div = internship.find('div', class_='status-success')
            if posted_div and posted_div.find('i', class_='ic-16-reschedule'):
                span = posted_div.find('span')
                if span:
                    posted_time = span.text.strip()

            # Job Link
            job_anchor = internship.find('a', class_='job-title-href')
            if job_anchor and job_anchor.has_attr('href'):
                job_link = 'https://internshala.com' + job_anchor['href']

            writer.writerow([
                title,
                company,
                stipend,
                experience,
                posted_time,
                job_link
            ])

    print(f"✅ Saved {len(internships)} jobs to {filename}")


def fill_cover_letter(job_details: str) -> bool:
    """Fill cover letter in application form"""
    try:
        logger.info("[WRITE] Filling cover letter...")
        
        # Wait for cover letter editor
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#cover_letter_holder .ql-editor[contenteditable='true']"))
        )
        
        ql_editor = driver.find_element(By.CSS_SELECTOR, "#cover_letter_holder .ql-editor[contenteditable='true']")
        
        # Clear and fill content
        driver.execute_script("""
            arguments[0].innerHTML = '';
            arguments[0].focus();
        """, ql_editor)

        cv_text = Gpt(prompt= f"Job Details: \n {job_details}", system_prompt=cover_letter_prompt())
        
        # Type the cover letter
        ActionChains(driver).move_to_element(ql_editor).click().send_keys(cv_text).perform()
        
        logger.info("[OK] Cover letter filled successfully")
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to fill cover letter: {e}")
        return False


def submit(job_link):
    try:
        submit_btn = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        sleep(1)
        submit_btn.click()
        print("🚀 Application submitted successfully.")
        with open('data/internshala/applied_jobs.txt', 'a') as f:
            f.write(f"{job_link}\n")

    except Exception as e:
        print(f"❌ Submit failed: {e}")


def fill_additional_questions():
    try:
        question_blocks = driver.find_elements(By.CLASS_NAME, "form-group")
        for block in question_blocks:
            try:
                # Get the question label
                label_elem = block.find_element(By.CLASS_NAME, "assessment_question").find_element(By.TAG_NAME, "label")
                question_text = label_elem.text.strip()
                print(f"🔍 Question: {question_text}")

                try:
                    radio_yes = block.find_element(By.XPATH, './/input[@type="radio" and contains(@id, "Yes")]')
                    driver.execute_script("arguments[0].click();", radio_yes)
                    print("✅ Selected YES for radio-type question.\n")
                    continue  

                except:
                    pass

                textarea = block.find_element(By.TAG_NAME, "textarea")
                answer = Gpt(
                    prompt=question_text,
                    system_prompt=sys_prompt
                )
                textarea.clear()
                textarea.send_keys(answer)        
                print(f"✅ Filled answer: {answer}\n")

            except Exception as e:
                # print(f"❌ Error processing question block")
                pass

    except Exception as e:
        print(f"❌ Error locating additional questions: {e}")


# Main workflow
def internshala():
    driver.quit()
    login()
    print('Login Successful.')
    wait_for_element(xpaths["intershala"])

    print('Searching WFH Jobs')
    jobs_btn = wait_for_element(xpaths["jobs_btn"])
    if jobs_btn:
        jobs_btn.click()
    else:
        print("❌ Failed to click Jobs button.")
        return

    #print('[3] Waiting for jobs container...')
    container = wait_for_element(xpaths["container"])
    if not container:
        print("❌ Job container not found.")
        return
    
    container_html = container.get_attribute('outerHTML')
    parse_jobs_to_csv(container_html)

    with open('data/internshala/applied_jobs.txt', 'r', encoding='utf-8') as f:
        jobs = f.readlines()
        applied_jobs = [job.strip() for job in jobs]

    with open('data/internshala/jobs.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header


        for row in reader:
            try:
                title, company, stipend, duration, posted, job_link = row

                if title == 'N/A':
                    continue

                if duration == '0 year(s)':
                    print(f"\n🟢 Applying for: {title} at {company}")
                    print(f"🔗 {job_link}")

                    if job_link in applied_jobs:
                        print("✅ Already applied for this job.")
                        continue

                    driver.get(job_link)
                    sleep(2)

                    job_details = wait_for_element(xpaths['job_details']).text
                    with open('data/internshala/job_details.txt', 'w', encoding='utf-8') as f:
                        f.write(job_details)

                    try:
                        wait_for_element(xpaths['top_apply_btn']).click()
                        sleep(2)
                    except:
                        wait_for_element(xpaths['bottom_apply_btn']).click()
                        sleep(2)

                    apply_details = wait_for_element(xpaths['apply_details'])                    
                    if apply_details.text:
                        pyautogui.scroll(4)
                        try:  
                            if 'Additional question(s)' in apply_details.text: 
                                print("🔎 Filling additional questions...")
                                fill_additional_questions()
                                submit(job_link)

                            elif 'Cover letter' in apply_details.text:
                                print("📝 Filling cover letter...")
                                fill_cover_letter(job_details)
                                submit(job_link)

                            elif 'Additional question(s)'in apply_details.text and 'Cover letter' in apply_details.text:
                                print("🔎 Filling additional questions...")
                                fill_additional_questions()
                                submit(job_link)
                                print("📝 Filling cover letter...")
                                fill_cover_letter(job_details)
                                submit(job_link)

                            else:
                                print("🔎 No additional questions")
                                submit(job_link=job_link)
                        except :
                            print('Error in applying')
                            
                    else:
                        print("No details Found")
                        pass
        

            except (TimeoutException, NoSuchElementException) as e:
                print(f"❌ Failed to apply for {title}: {e}")
                continue
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                continue
            finally:
                driver.quit()
                
    print("\n🎯 Finished applying to all eligible jobs.")

if __name__ == "__main__":
    internshala() 


























########## Version --2
#### Slow and Accurate

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pathlib
import csv
import os
import warnings
from time import sleep
import logging
import pyautogui
from selenium.webdriver.common.action_chains import ActionChains
import random
import urllib3.exceptions

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.openai import Gpt


def setup_logging():
    """Setup logging with proper UTF-8 encoding for Windows"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Console handler with UTF-8 encoding (fallback to ASCII if needed)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Try to set UTF-8 encoding for console on Windows
    try:
        import sys
        if sys.platform.startswith('win'):
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        # If UTF-8 setup fails, continue with default encoding
        pass
    
    logger.addHandler(console_handler)
    return logger


logger = setup_logging()


sys_prompt = """
You are a Job Application Question Responder Bot.

Your role is to automatically generate short, relevant answers to job application form questions using predefined rules and applicant information.

Rules & Response Patterns:
- Do **not** disclose that you're an AI or assistant.
- Do **not** include any information not belonging to the applicant.
- Always keep answers clear, concise, and professional.

Auto-detect question intent using keywords and respond as follows:

1. **Notice Period**  
   Keywords: "notice period", "available to join", "joining time"  
   → Respond with: **"0"**

2. **Expected Salary**  
   Keywords: "expected salary", "salary expectation"  
   → Respond with: **"Negotiable"**

3. **Last Drawn CTC / Current CTC**  
   Keywords: "last drawn CTC", "current salary", "past salary", "monthly salary"  
   → Respond with: **"2.5"**

4. **Years of Experience (Content Writing or Others)**  
   Keywords: "years of experience", "experience in", "how many years"  
   → Respond with: **numeric digits only** (e.g., "3", not "three")

5. **Portfolio / Links / Profiles**  
   Keywords: "LinkedIn", "GitHub", "portfolio", "online profile"  
   → Respond using the applicant's relevant URLs.

6. **Contact Information**  
   Keywords: "email", "mobile", "phone number", "contact"  
   → Use the applicant's provided contact details.

7. **General Open-Ended Questions** (e.g., "Tell us about yourself", "Why should we hire you?")  
   → Respond with a short and meaningful paragraph tailored to the applicant's profile (wait for user or system to provide content context).

Applicant Details:
    Name: J Chandu  
    Mobile: +91 7032654675  
    Email: chanduj8351@gmail.com
    Institute: Lakireddy Bali Reddy College of Engineering 
    LinkedIn: https://www.linkedin.com/in/chandu-j-24558236b/  
    GitHub: https://github.com/chanduj8351

"""

warnings.simplefilter('ignore')

# Global driver variable
driver = None

def setup_driver():
    """Setup Chrome driver with improved options for stability"""
    global driver
    
    ScriptDir = pathlib.Path().absolute()
    options = uc.ChromeOptions()
    
    # Basic options
    options.add_argument('--profile-directory=Default')
    options.add_argument(f'--user-data-dir={ScriptDir}\\assets\\chromedata')
    
    # Stability and performance options
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--aggressive-cache-discard')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-backgrounding-occluded-windows')
    
    # Network options
    options.add_argument('--timeout=30000')
    options.add_argument('--page-load-strategy=eager')
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = uc.Chrome(
            options=options, 
            driver_executable_path=os.path.join(ScriptDir, 'assets', 'chromedriver.exe')
        )
        driver.maximize_window()
        
        # Set timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        logger.info("✅ Driver setup successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Driver setup failed: {e}")
        return False

def safe_get(url, max_retries=3):
    """Safely navigate to URL with retry logic"""
    global driver
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Navigating to: {url} (Attempt {attempt + 1})")
            driver.get(url)
            sleep(random.uniform(2, 4))  # Random delay
            return True
            
        except (WebDriverException, urllib3.exceptions.ProtocolError, ConnectionResetError) as e:
            logger.warning(f"Navigation attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                delay = random.uniform(3, 7)
                logger.info(f"Retrying in {delay:.1f} seconds...")
                sleep(delay)
                
                # Recreate driver if connection issues persist
                if attempt == max_retries - 2:
                    logger.info("Recreating driver for final attempt...")
                    driver.quit()
                    if not setup_driver():
                        return False
            else:
                logger.error(f"Failed to navigate to {url} after {max_retries} attempts")
                return False
                
    return False

# XPaths dictionary
xpaths = {
    "intershala": (By.XPATH, '//*[@id="content"]/div/div[1]/div/h1'),
    "jobs_btn": (By.XPATH, '//*[@id="jobs_new_superscript"]'),
    "container": (By.XPATH, '//*[@id="internships_list_container"]'),
    "job_details": (By.XPATH, '//*[@id="details_container"]/div[2]'),
    "top_apply_btn": (By.XPATH, '//*[@id="top_easy_apply_button"]'),
    "bottom_apply_btn": (By.XPATH, '//*[@id="easy_apply_button"]'),
    "apply_details": (By.XPATH, '//*[@id="application-form-container"]'),
    "submit_btn": (By.XPATH, '//*[@id="submit"]')
}

def login():
    """Navigate to Internshala dashboard with error handling"""
    url = "https://internshala.com/student/dashboard"
    if safe_get(url):
        # Wait for page to fully load and check for login requirements
        sleep(3)
        
        # Check if we're redirected to login page
        current_url = driver.current_url
        if "login" in current_url.lower():
            logger.warning("⚠️ Redirected to login page - manual login may be required")
            input("Please complete login manually and press Enter to continue...")
            
        # Try to find any dashboard element to confirm we're logged in
        dashboard_indicators = [
            (By.XPATH, '//*[@id="content"]'),
            (By.XPATH, '//h1[contains(text(), "Dashboard")]'),
            (By.XPATH, '//h1[contains(text(), "Internshala")]'),
            (By.CLASS_NAME, "dashboard"),
            (By.ID, "jobs_new_superscript"),
            (By.XPATH, '//a[contains(@href, "jobs")]')
        ]
        
        for locator in dashboard_indicators:
            element = wait_for_element(locator, timeout=5)
            if element:
                logger.info(f"✅ Found dashboard element: {locator}")
                return True
                
        logger.warning("⚠️ Dashboard elements not found, but continuing...")
        return True
    return False

def debug_page_elements():
    """Debug function to find available elements on the page"""
    try:
        logger.info("🔍 Debugging page elements...")
        
        # Common element types to check
        common_selectors = [
            "h1", "h2", "h3", "a", "button", 
            "div[id]", "div[class]", "nav", "header"
        ]
        
        for selector in common_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                logger.info(f"Found {len(elements)} elements with selector '{selector}'")
                for i, elem in enumerate(elements[:3]):  # Show first 3
                    try:
                        text = elem.text.strip()[:50] if elem.text else "No text"
                        logger.info(f"  [{i}] Text: {text}")
                    except:
                        pass
    except Exception as e:
        logger.error(f"Debug failed: {e}")

def wait_for_element(locator, timeout=15):
    """Wait for element with better error handling"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return element
    except TimeoutException:
        logger.warning(f"Element {locator} not found within {timeout} seconds.")
        return None
    except Exception as e:
        logger.error(f"Error waiting for element {locator}: {e}")
        return None
    
def cover_letter_prompt():
    """Generate cover letter based on job details"""
    base_prompt = """
    You are a highly skilled and professional Cover Letter Generator.

    Your task is to write a compelling, tailored cover letter for a job application, focusing on why the applicant is a strong fit for the role.

    You will be provided with specific job details, including the job title, responsibilities, and requirements.

    Using this information, craft a well-structured cover letter that:
    - Highlights the applicant's relevant skills, qualifications, and experience
    - Aligns the applicant's background with the job description
    - Demonstrates enthusiasm and professionalism
    - Concludes with a strong call to action

    Note:
    - The cover letter should be written as me to the company. Not as an AI generated cover letter
    - The cover letter should be written in a professional and formal tone
    - Don't exceed 2048 characters

    Applicant Details:
        Name: J Chandu
        Email: chanduj8351@gmail.com
        Institute/College: Lakireddy Bali Reddy College of Engineering 
        LinkedIn: https://www.linkedin.com/in/chandu-j-24558236b/ 
        GitHub: https://github.com/chanduj8351

    Wait for the job description before generating the cover letter.
    """
    return base_prompt

def ensure_directory_exists(filepath):
    """Ensure directory exists for file operations"""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def parse_jobs_to_csv(html, filename='data/internshala/jobs.csv'):  
    """Parse jobs from HTML and save to CSV with error handling"""
    try:
        ensure_directory_exists(filename)
        
        soup = BeautifulSoup(html, 'html.parser')
        internships = soup.find_all('div', class_='individual_internship')

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Title', 'Company', 'Stipend', 'Experience', 'Posted Time', 'Job Link'])

            for internship in internships:
                # Initialize all fields with defaults
                title = company = stipend = 'N/A'
                experience = posted_time = job_link = 'N/A'

                # Extract title and company
                title_tag = internship.find('h3', class_='job-internship-name')
                if title_tag:
                    title = title_tag.text.strip()

                company_tag = internship.find('p', class_='company-name')
                if company_tag:
                    company = company_tag.text.strip()

                stipend_tag = internship.find('span', class_='desktop')
                if stipend_tag:
                    stipend = stipend_tag.text.strip()

                # Experience
                experience = 'N/A'
                for div in internship.find_all('div', class_='row-1-item'):
                    if div.find('i', class_='ic-16-briefcase'):
                        span = div.find('span')
                        if span:
                            experience = span.text.strip()
                        break

                # Posted Time
                posted_div = internship.find('div', class_='status-success')
                if posted_div and posted_div.find('i', class_='ic-16-reschedule'):
                    span = posted_div.find('span')
                    if span:
                        posted_time = span.text.strip()

                # Job Link
                job_anchor = internship.find('a', class_='job-title-href')
                if job_anchor and job_anchor.has_attr('href'):
                    job_link = 'https://internshala.com' + job_anchor['href']

                writer.writerow([
                    title,
                    company,
                    stipend,
                    experience,
                    posted_time,
                    job_link
                ])

        logger.info(f"✅ Saved {len(internships)} jobs to {filename}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error parsing jobs to CSV: {e}")
        return False

def fill_cover_letter(job_details: str) -> bool:
    """Fill cover letter in application form"""
    try:
        logger.info("[WRITE] Filling cover letter...")
        
        # Wait for cover letter editor
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#cover_letter_holder .ql-editor[contenteditable='true']"))
        )
        
        ql_editor = driver.find_element(By.CSS_SELECTOR, "#cover_letter_holder .ql-editor[contenteditable='true']")
        
        # Clear and fill content
        driver.execute_script("""
            arguments[0].innerHTML = '';
            arguments[0].focus();
        """, ql_editor)

        cv_text = Gpt(prompt=f"Job Details: \n {job_details}", system_prompt=cover_letter_prompt())
        
        # Type the cover letter
        ActionChains(driver).move_to_element(ql_editor).click().send_keys(cv_text).perform()
        
        logger.info("[OK] Cover letter filled successfully")
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to fill cover letter: {e}")
        return False

def submit(job_link):
    """Submit application with error handling"""
    try:
        submit_btn = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
        sleep(1)
        submit_btn.click()
        logger.info("🚀 Application submitted successfully.")
        
        # Save applied job
        ensure_directory_exists('data/internshala/applied_jobs.txt')
        with open('data/internshala/applied_jobs.txt', 'a', encoding='utf-8') as f:
            f.write(f"{job_link}\n")
        return True

    except Exception as e:
        logger.error(f"❌ Submit failed: {e}")
        return False

def fill_additional_questions():
    """Fill additional questions with improved error handling"""
    try:
        question_blocks = driver.find_elements(By.CLASS_NAME, "form-group")
        for block in question_blocks:
            try:
                # Get the question label
                label_elem = block.find_element(By.CLASS_NAME, "assessment_question").find_element(By.TAG_NAME, "label")
                question_text = label_elem.text.strip()
                logger.info(f"🔍 Question: {question_text}")

                # Try radio button first
                try:
                    radio_yes = block.find_element(By.XPATH, './/input[@type="radio" and contains(@id, "Yes")]')
                    driver.execute_script("arguments[0].click();", radio_yes)
                    logger.info("✅ Selected YES for radio-type question.\n")
                    continue  
                except:
                    pass

                # Try textarea
                try:
                    textarea = block.find_element(By.TAG_NAME, "textarea")
                    answer = Gpt(
                        prompt=question_text,
                        system_prompt=sys_prompt
                    )
                    textarea.clear()
                    textarea.send_keys(answer)        
                    logger.info(f"✅ Filled answer: {answer}\n")
                except:
                    pass

            except Exception as e:
                logger.debug(f"Error processing question block: {e}")
                continue

    except Exception as e:
        logger.error(f"❌ Error locating additional questions: {e}")

def get_applied_jobs():
    """Get list of already applied jobs"""
    try:
        ensure_directory_exists('data/internshala/applied_jobs.txt')
        if os.path.exists('data/internshala/applied_jobs.txt'):
            with open('data/internshala/applied_jobs.txt', 'r', encoding='utf-8') as f:
                jobs = f.readlines()
                return [job.strip() for job in jobs]
        return []
    except Exception as e:
        logger.error(f"Error reading applied jobs: {e}")
        return []

def internshala(your_experience: str):
    """Main workflow with comprehensive error handling"""
    global driver
    
    try:
        # Setup driver
        if not setup_driver():
            logger.error("❌ Failed to setup driver")
            return
        
        # Login with improved detection
        logger.info('Attempting login...')
        if not login():
            logger.error("❌ Login failed")
            return
        
        logger.info('✅ Login successful.')
        
        # Try multiple selectors to find the main page content
        main_page_selectors = [
            (By.XPATH, '//*[@id="content"]/div/div[1]/div/h1'),
            (By.XPATH, '//*[@id="content"]'),
            (By.XPATH, '//h1[contains(text(), "Dashboard")]'),
            (By.XPATH, '//h1[contains(text(), "Internshala")]'),
            (By.ID, "jobs_new_superscript"),
            (By.CLASS_NAME, "main-content"),
            (By.XPATH, '//div[contains(@class, "dashboard")]')
        ]
        
        main_page_found = False
        for selector in main_page_selectors:
            element = wait_for_element(selector, timeout=10)
            if element:
                logger.info(f"✅ Main page loaded - found element: {selector}")
                main_page_found = True
                break
        
        if not main_page_found:
            logger.warning("⚠️ Main page elements not found, but continuing...")
            # Print current page info for debugging
            current_url = driver.current_url
            page_title = driver.title
            logger.info(f"Current URL: {current_url}")
            logger.info(f"Page Title: {page_title}")
            
            # Debug page elements
            debug_page_elements()
            
            # Save page source for debugging
            try:
                with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                logger.info("📄 Page source saved to debug_page_source.html")
            except Exception as e:
                logger.error(f"Could not save page source: {e}")

        # Navigate to jobs with multiple selector attempts
        logger.info('🔍 Searching WFH Jobs...')
        
        jobs_button_selectors = [
            (By.XPATH, '//*[@id="jobs_new_superscript"]'), 
            (By.XPATH, '//a[contains(@href, "jobs")]'),
            (By.XPATH, '//a[contains(text(), "Jobs")]'),
            (By.LINK_TEXT, "Jobs"),
            (By.PARTIAL_LINK_TEXT, "Jobs"),
            (By.CSS_SELECTOR, 'a[href*="jobs"]')
        ]
        
        jobs_btn_clicked = False
        for selector in jobs_button_selectors:
            jobs_btn = wait_for_element(selector, timeout=5)
            if jobs_btn:
                try:
                    # Scroll to element and click
                    driver.execute_script("arguments[0].scrollIntoView(true);", jobs_btn)
                    sleep(1)
                    jobs_btn.click()
                    sleep(3)
                    jobs_btn_clicked = True
                    logger.info(f"✅ Clicked jobs button using selector: {selector}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to click jobs button with selector {selector}: {e}")
                    continue
        
        if not jobs_btn_clicked:
            logger.error("❌ Failed to click Jobs button with all selectors.")
            # Try direct navigation as fallback
            logger.info("🔄 Trying direct navigation to jobs page...")
            if not safe_get("https://internshala.com/jobs"):
                return

        # Wait for jobs container
        container = wait_for_element(xpaths["container"])
        if not container:
            logger.error("❌ Job container not found.")
            return
        
        # Parse jobs
        container_html = container.get_attribute('outerHTML')
        if not parse_jobs_to_csv(container_html):
            logger.error("❌ Failed to parse jobs")
            return

        # Get applied jobs
        applied_jobs = get_applied_jobs()

        # Process jobs
        if not os.path.exists('data/internshala/jobs.csv'):
            logger.error("❌ Jobs CSV file not found")
            return
            
        with open('data/internshala/jobs.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header

            for row in reader:
                try:
                    title, company, stipend, duration, posted, job_link = row

                    if title == 'N/A' or not job_link:
                        continue

                    if duration == your_experience + " year(s)":
                        logger.info(f"\n🟢 Processing: {title} at {company}")
                        logger.info(f"🔗 {job_link}")

                        if job_link in applied_jobs:
                            logger.info("✅ Already applied for this job.")
                            continue

                        # Navigate to job page
                        if not safe_get(job_link):
                            logger.error(f"❌ Failed to load job page: {job_link}")
                            continue

                        # Get job details
                        job_details_elem = wait_for_element(xpaths['job_details'])
                        if not job_details_elem:
                            logger.error("❌ Job details not found")
                            continue
                            
                        job_details = job_details_elem.text
                        ensure_directory_exists('data/internshala/job_details.txt')
                        with open('data/internshala/job_details.txt', 'w', encoding='utf-8') as f:
                            f.write(job_details)

                        # Click apply button
                        apply_clicked = False
                        try:
                            top_apply = wait_for_element(xpaths['top_apply_btn'], timeout=5)
                            if top_apply:
                                top_apply.click()
                                apply_clicked = True
                        except:
                            try:
                                bottom_apply = wait_for_element(xpaths['bottom_apply_btn'], timeout=5)
                                if bottom_apply:
                                    bottom_apply.click()
                                    apply_clicked = True
                            except:
                                pass
                        
                        if not apply_clicked:
                            logger.error("❌ Could not find apply button")
                            continue

                        sleep(2)

                        # Handle application form
                        apply_details = wait_for_element(xpaths['apply_details'])                    
                        if apply_details and apply_details.text:
                            pyautogui.scroll(4)
                            
                            form_text = apply_details.text
                            has_questions = 'Additional question(s)' in form_text
                            has_cover_letter = 'Cover letter' in form_text
                            
                            if has_questions:
                                logger.info("🔎 Filling additional questions...")
                                fill_additional_questions()
                            
                            if has_cover_letter:
                                logger.info("📝 Filling cover letter...")
                                fill_cover_letter(job_details)
                            
                            # Submit application
                            submit(job_link)
                        else:
                            logger.info("🔎 No additional form fields")
                            submit(job_link)

                except Exception as e:
                    logger.error(f"❌ Error processing job {title}: {e}")
                    continue

        logger.info("\n🎯 Finished applying to all eligible jobs.")

    except Exception as e:
        logger.error(f"❌ Unexpected error in main workflow: {e}")
    finally:
        if driver:
            driver.quit()
            logger.info("🔄 Driver closed.")

if __name__ == "__main__":
    internshala()
