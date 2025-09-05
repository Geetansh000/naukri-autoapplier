import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver

from app.infer import infer_answer


def apply_web(driver, url):
    wait = WebDriverWait(driver, 5)
    print(f"🔗 Navigating to job URL: {url}")
    driver.get(url)
    time.sleep(2)

    try:
        try:
            apply_buttons = driver.find_elements(
                By.CSS_SELECTOR, ".styles_jhc__apply-button-container__5Bqnb button")
            apply_button = apply_buttons[1] if apply_buttons else None
            if not apply_button:
                if (apply_buttons[0].text.lower().strip() == "applied"):
                    print("❌ Already applied. Skipping.")
                    return True
                apply_button = driver.find_element(
                    By.XPATH, "//button[contains(text(), 'Apply')]")
            text = apply_button.text.lower().strip()
            if text not in ["apply"]:
                match text:
                    case "already applied":
                        print("❌ Already applied. Skipping.")
                        return True
                    case "apply on company site":
                        print("❌ External application. Skipping.")
                        return
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

        apply_button.click()
        print("✅ Clicked 'Apply'.")
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
        try:
            # Check green success header
            wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                "//span[contains(text(), 'successfully applied') or contains(text(), 'You have successfully applied')]"))
            )
            print("🎉 Successfully applied (no questions).")
            return True
        except TimeoutException:
            pass  # Proceed to chatbot
        try:
            chatbot = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "chatbot_Drawer"))
            )
            status = True
            while status:
                if driver.find_elements(By.CSS_SELECTOR, ".applied-job-content"):
                    print("🎉 Successfully applied (post-answer).")
                    # applied_count += 1
                    # applied = True
                    status = False
                    break
                # if driver.find_elements(By.XPATH,
                #                         "//span[contains(text(), 'successfully applied') or contains(text(), 'You have successfully applied')]"):
                #     print("🎉 Successfully applied (post-answer).")
                #     # applied_count += 1
                #     # applied = True
                #     status = False
                #     break

                # Check green success header
                # if driver.find_elements(By.XPATH,
                #                         "//div[contains(@class, 'apply-status-header') and contains(@class, 'green')]"):
                #     print("🎉 Applied successfully (green header).")
                #     # applied_count += 1
                #     # applied = True
                #     status = False
                #     break

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
                        print(question_text)
                    except:
                        question_text = "Choose an option:"

                    print(f"❓ Radio Question: {question_text}")
                    options_list = []
                    value_map = {}  # index -> container

                    for idx, container in enumerate(radio_containers):
                        try:
                            label = container.find_element(
                                By.TAG_NAME, "label").text
                            value = container.find_element(
                                By.TAG_NAME, "input").get_attribute("value")
                            options_list.append(label)
                            value_map[idx + 1] = container
                            print(f"   {idx + 1}. {label}")
                        except:
                            continue

                    if not options_list:
                        print("No valid options found.")
                        continue

                    # Get AI response
                    print(f"🤖 AI Question: {question_text}")
                    print(f"   Options: {options_list}")
                    try:
                        # ai_response = bard_flash_response(
                        #     "\n".join([question_text] + options_list))
                        ai_response = infer_answer(question_text, options_list)
                        print(f"💬 AI Answer: {ai_response}")
                        for idx, option in enumerate(options_list):
                            if ai_response.lower() in option.lower():
                                selected_index = idx + 1
                                break
                    except Exception as e:
                        print(
                            f"🤖 AI parsing failed: {e}. Defaulting to 1.")
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
                        print(checkbox_containers)
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
                            # ai_response = bard_flash_response(
                            #     "\n".join([question_text] + options_list))
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
                            # For text questions
                            # last_question_elem = driver.find_element(
                            #     By.XPATH, "//li[contains(@class, 'botItem')]/div/div/span")

                            question_text = last_ques.text
                            if question_text == "Hi Geetansh Sharma, thank you for showing interest. Kindly answer all the recruiter's questions to successfully apply for the job.":
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
                            # retries += 1
                            continue

                        # AI response
                        try:
                            # ai_response = bard_flash_response(
                            #     question_text)
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
                    print("💾 Saved answer.")
                except Exception as e:
                    print(f"❌ Save button click failed: {e}")
                    continue

                # Re-check success after save
                if driver.find_elements(By.XPATH,
                                        "//div[contains(text(), 'Applied to')]"):
                    print("🎉 Successfully applied after save.")
                    # applied_count += 1
                    # applied = True
                    # status = False

                time.sleep(10)

        # if not applied:
        #     print("❌ Failed to apply after retries.")
        #     failed_count += 1

        # # --- Small delay between jobs ---
        # time.sleep(2)
        # ques = []
        # ques = driver.find_element(By.CLASS_NAME, "botMsg")

        except Exception as e:
            print(f"⚠️ Chatbot drawer not found, proceeding without it: {e}")
            # add a popup and pause for manual apply
            driver.execute_script(
                "alert('Please complete the application manually.');")

            # Inject a custom popup with 3 buttons: Continue, Manual, Quit
            popup_script = """
            // Remove existing popup if any
            if (document.getElementById('customPopup')) {
                document.getElementById('customPopup').remove();
            }

            // Create popup container
            var popup = document.createElement('div');
            popup.id = 'customPopup';
            popup.style.position = 'fixed';
            popup.style.top = '0';
            popup.style.left = '0';
            popup.style.width = '100%';
            popup.style.height = '100%';
            popup.style.backgroundColor = 'rgba(0,0,0,0.6)';
            popup.style.display = 'flex';
            popup.style.alignItems = 'center';
            popup.style.justifyContent = 'center';
            popup.style.zIndex = '999999';

            // Create inner box
            var box = document.createElement('div');
            box.style.backgroundColor = '#fff';
            box.style.padding = '20px';
            box.style.borderRadius = '10px';
            box.style.textAlign = 'center';
            box.style.fontFamily = 'Arial';
            box.style.boxShadow = '0 4px 8px rgba(0,0,0,0.3)';
            box.innerHTML = '<h2>Please choose an action</h2>';

            // Create buttons
            var continueBtn = document.createElement('button');
            continueBtn.innerText = 'Continue';
            continueBtn.style.margin = '10px';
            continueBtn.style.padding = '8px 15px';
            continueBtn.style.backgroundColor = '#4CAF50';
            continueBtn.style.color = '#fff';
            continueBtn.style.border = 'none';
            continueBtn.style.borderRadius = '5px';
            continueBtn.style.cursor = 'pointer';
            continueBtn.onclick = function() {
                window._popupChoice = 'continue';
                popup.remove();
            };

            var manualBtn = document.createElement('button');
            manualBtn.innerText = 'Manual';
            manualBtn.style.margin = '10px';
            manualBtn.style.padding = '8px 15px';
            manualBtn.style.backgroundColor = '#2196F3';
            manualBtn.style.color = '#fff';
            manualBtn.style.border = 'none';
            manualBtn.style.borderRadius = '5px';
            manualBtn.style.cursor = 'pointer';
            manualBtn.onclick = function() {
                window._popupChoice = 'manual';
                alert('You selected Manual mode. Please complete the application manually and close this alert when done.');
            };

            var quitBtn = document.createElement('button');
            quitBtn.innerText = 'Quit';
            quitBtn.style.margin = '10px';
            quitBtn.style.padding = '8px 15px';
            quitBtn.style.backgroundColor = '#f44336';
            quitBtn.style.color = '#fff';
            quitBtn.style.border = 'none';
            quitBtn.style.borderRadius = '5px';
            quitBtn.style.cursor = 'pointer';
            quitBtn.onclick = function() {
                window._popupChoice = 'quit';
                popup.remove();
            };

            // Append buttons to the box
            box.appendChild(continueBtn);
            box.appendChild(manualBtn);
            box.appendChild(quitBtn);

            // Append box to popup
            popup.appendChild(box);

            // Append popup to body
            document.body.appendChild(popup);
            """

            # Inject the popup into the browser
            driver.execute_script(popup_script)

            # Wait until user clicks a button
            while True:
                choice = driver.execute_script(
                    "return window._popupChoice || null;")
                if choice:
                    break
                time.sleep(1)

            # Handle actions based on user choice
            if choice == "continue":
                print("▶️ Continuing automation...")
            elif choice == "manual":
                print("✋ Waiting for manual completion...")
                input(
                    "Press Enter here in the terminal after completing the application manually...")
            elif choice == "quit":
                print("🛑 Quitting automation.")
                driver.quit()
                exit()
        # Handle potential pop-ups or new windows
        # main_window = driver.current_window_handle
        # all_windows = driver.window_handles

        # for handle in all_windows:
        #     if handle != main_window:
        #         driver.switch_to.window(handle)
        #         print("🔄 Switched to new window for application.")
        #         break

        # Here you can add more steps to fill out forms if necessary
        print("✅ Application process initiated. Please complete any additional steps manually if required.")

        # After completing, switch back to the main window
        # driver.switch_to.window(main_window)
        print("🔄 Switched back to main window.")
        return

    except Exception as e:
        print(f"❌ Error during application process: {e}")
