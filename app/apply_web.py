import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app.helpers import check_skip_keywords, check_must_have_keywords, find_elements_by_css
from app.infer import infer_answer
import pyautogui
from .config import AUTHOR_NAME
import re

PAUSE_ON_ERROR = True


def apply_web(driver, url):
    wait = WebDriverWait(driver, 3)
    driver.get(url)
    time.sleep(1)

    try:
        try:
            apply_buttons = find_elements_by_css(
                driver, ".styles_jhc__apply-button-container__5Bqnb button")
            apply_button = apply_buttons[1] if apply_buttons else None
            if not apply_button:
                if (apply_buttons[0].text.lower().strip() == "applied"):
                    print("❌ Already applied. Skipping.")
                    return True
                apply_button = find_elements_by_css(
                    driver, "//button[contains(text(), 'Apply')]")
            text = apply_button.text.lower().strip()
            if text not in ["apply"]:
                match text:
                    case "already applied":
                        print("❌ Already applied. Skipping.")
                        return True
                    case "apply on company site":
                        print("❌ External application. Skipping.")
                        return True
                    case "i am interested":
                        print("❌ Walkin application. Skipping.")
                        return True
                    case _:
                        print(
                            f"⚠️ Apply button text is '{text}', expected 'Apply'.")
                        return
            # Expired or alert message
            alert_elements = driver.find_elements(
                By.XPATH, "//*[contains(@class, 'alert-message-text')]")
            if any("expired" in el.text.lower() or "closed" in el.text.lower() for el in alert_elements if el.text):
                print("❌ Job expired. Skipping.")
                return

        except Exception as e:
            return print(f"❌ Could not find Apply button: {e}")
        try:
            title = driver.find_element(By.CSS_SELECTOR, "header")
            title_lower = title.text.lower()
            # ✅ First, check if the title contains any MUST-HAVE keyword
            must_have_keys = check_must_have_keywords(
                title_lower)
            if len(must_have_keys):
                print(
                    f"contains_must_have-- {must_have_keys}")
            else:
                if check_skip_keywords(title):
                    print(f"⛔ Skipping unwanted job: {title.text}")
                    return True

                skills = find_elements_by_css(
                    driver, ".styles_chip__7YCfG")
                skills_array = [skill.text.lower() for skill in skills]
                must_have_keys = check_must_have_keywords(
                    " ".join(skills_array))
                if len(must_have_keys):
                    print(
                        f"✅ Job contains MUST-HAVE keyword: {must_have_keys}")
                elif check_skip_keywords(title):
                    print(f"⛔ Skipping unwanted job: {title.text}")
                    return True
        except Exception:
            pass
        apply_button.click()
        # --- STEP 3: Check immediate success (no questions) ---
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".applied-job-content"))
            )
            print("🎉 Successfully applied (no questions).")
            return True
        except TimeoutException:
            pass

        # --- STEP 4: Check immediate success (post-answer) ---
        try:
            chatbot = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "chatbot_Drawer"))
            )
            status = True
            while status:
                if driver.find_elements(By.CSS_SELECTOR, ".applied-job-content"):
                    print("🎉 Successfully applied (post-answer).")
                    status = False
                    break

                try:
                    wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, ".botItem"))
                    )
                except TimeoutException:
                    print("⏳ Waiting for bot question...")
                    continue
                try:
                    ques = driver.find_elements(By.CLASS_NAME, "botItem")
                    if not ques:
                        print("⏳ No bot questions found yet...")
                        continue
                    last_ques = ques[-1]
                    if not last_ques.is_displayed():
                        driver.execute_script(
                            "arguments[0].scrollIntoView(true);", last_ques)
                        time.sleep(1)
                except Exception as e:
                    print(f"❌ Error scrolling to question: {e}")
                    continue

                # --- RADIO BUTTON QUESTION ---
                radio_containers = []
                try:
                    radio_containers = wait.until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, ".ssrc__radio-btn-container"))
                    )
                except TimeoutException:
                    pass

                if radio_containers:
                    try:
                        question_text = last_ques.text
                    except:
                        question_text = "Choose an option:"

                    print(f"❓ Radio Question: {question_text}")
                    options_list = []
                    value_map = {}  # index -> container

                    for idx, container in enumerate(radio_containers):
                        try:
                            label = container.find_element(
                                By.TAG_NAME, "label").text
                            options_list.append(label)
                            value_map[idx + 1] = container
                            print(f"   {idx + 1}. {label}")
                        except:
                            continue

                    if not options_list:
                        print("No valid options found.")
                        continue

                    # Get AI response
                    print(f"🤖 Question: {question_text}")
                    print(f"   Options: {options_list}")
                    try:
                        ai_response = infer_answer(question_text, options_list)
                        print(f"💬 Answer: {ai_response}")
                        for idx, option in enumerate(options_list):
                            if ai_response.lower() in option.lower():
                                selected_index = idx + 1
                                break
                    except Exception as e:
                        print(
                            f"🤖 Parsing failed: {e}. Defaulting to 1.")
                        selected_index = 1

                    if selected_index not in value_map:
                        selected_index = 1  # fallback

                    try:
                        input_el = value_map[selected_index].find_element(
                            By.TAG_NAME, "input")
                        driver.execute_script(
                            "arguments[0].click();", input_el)
                        print(f"🔘 Selected option {selected_index}.")
                    except Exception as e:
                        print(f"❌ Failed to select radio: {e}")
                        continue

                # --- TEXT INPUT QUESTION ---
                else:
                    checkbox_containers = []
                    try:
                        checkbox_containers = wait.until(
                            EC.presence_of_all_elements_located(
                                (By.CSS_SELECTOR, ".mcc__label"))
                        )
                    except TimeoutException:
                        pass
                    if checkbox_containers:
                        try:
                            question_text = last_ques.text
                        except:
                            question_text = "Select all that apply:"
                        print(f"❓ Checkbox Question: {question_text}")
                        options_list = []
                        value_map = {}  # index -> container
                        try:
                            for idx, container in enumerate(checkbox_containers):
                                text = container.text
                                options_list.append(text)
                                value_map[idx + 1] = container
                            print(f"   {idx + 1}. {text}")
                        except:
                            print("No valid checkbox options found.")
                            continue
                        print(f"🤖 AI Question: {question_text}")
                        print(f"   Options: {options_list}")
                        try:
                            ai_response = infer_answer(
                                question_text, options_list)
                            print(f"💬 AI Answer: {ai_response}")
                            selected_indices = []
                            for idx, option in enumerate(options_list):
                                if ai_response.lower() in option.lower():
                                    selected_indices.append(idx + 1)
                            if not selected_indices:
                                selected_indices = [1]  # fallback
                        except Exception as e:
                            print(
                                f"🤖 AI parsing failed: {e}. Defaulting to 1.")
                            selected_indices = [1]

                        for idx in selected_indices:
                            if idx not in value_map:
                                continue
                            try:
                                input_el = value_map[idx].find_element(
                                    By.TAG_NAME, "label")
                                driver.execute_script(
                                    "arguments[0].click();", input_el)
                                print(f"✅ Checked option {idx}.")
                            except Exception as e:
                                try:
                                    value_map[idx].click()
                                except Exception as e:
                                    print(f"❌ Failed to check checkbox: {e}")
                                    continue
                    else:
                        try:
                            question_text = last_ques.text
                            if question_text == f"Hi {AUTHOR_NAME}, thank you for showing interest. Kindly answer all the recruiter's questions to successfully apply for the job.":
                                last_question_elem = driver.find_element(
                                    By.XPATH, "//li[contains(@class, 'botMsg')]/div/div/span")
                                question_text = last_question_elem.text
                        except Exception as e:
                            # This shows the real error
                            print(
                                f"❌ Error finding text question: {type(e).__name__}: {e}")
                            question_text = "Please provide input."

                        print(f"📝 Text Question: {question_text}")

                        try:
                            input_field = driver.find_element(
                                By.XPATH, "//div[@class='textArea']")
                        except:
                            print("❌ No input field found.")
                            continue

                        # AI response
                        try:
                            ai_response = infer_answer(question_text)
                        except Exception as e:
                            print(f"🤖 AI error: {e}")
                            ai_response = "Not available"

                        # Special handling for DOB
                        if "date of birth" in question_text.lower():
                            driver.execute_script(
                                "arguments[0].value = '01-01-1990'; arguments[0].dispatchEvent(new Event('input'));",
                                input_field
                            )
                        else:
                            input_field.clear()
                            input_field.send_keys(
                                ai_response or "Not available")

                        print(f"💬 Answered: {ai_response}")

                # --- CLICK SAVE ---
                try:
                    save_div = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//div[contains(@class, 'sendMsg') and contains(text(), 'Save') and not(contains(@class, 'disabled'))]"))
                    )
                    driver.execute_script(
                        "arguments[0].click();", save_div)
                except Exception as e:
                    print(f"❌ Save button click failed: {e}")
                    continue

                # Re-check success after save
                if driver.find_elements(By.XPATH,
                                        "//div[contains(text(), 'Applied to')]"):
                    print("🎉 Successfully applied after save.")
                time.sleep(5)

        except Exception as e:
            print(f"⚠️ Chatbot drawer not found, proceeding without it: {e}")
            global PAUSE_ON_ERROR
            if PAUSE_ON_ERROR:
                decision = pyautogui.confirm(
                    text="An error occurred while processing your application. Would you like to continue?",
                    title="Error Confirmation",
                    buttons=["Skip Once", "Skip All", "Manually Completed"]
                )
                match decision:
                    case "Skip Once":
                        print("⏭️ Skipping this job once.")
                        return
                    case "Skip All":
                        print("⏭️ Skipping all future jobs.")
                        PAUSE_ON_ERROR = False
                        return
                    case "Manually Completed":
                        print("🛠️ Please complete the application manually.")
            return True
        # Here you can add more steps to fill out forms if necessary
        print("✅ Application process completed.")

        return

    except Exception as e:
        print(
            f"❌ Error during application process: {e.split('Stacktrace:')[0]}")
