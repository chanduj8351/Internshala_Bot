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
