import argparse
import schedule
import time
from . import naukri_driver as nd
import pyautogui
from selenium.common.exceptions import NoSuchWindowException,  WebDriverException


def once(_):
    nd.run()


def daemon(_):
    schedule.every().day.at("09:45").do(nd.run)     # change time
    print("Scheduler started… Ctrl‑C to exit")
    while True:
        schedule.run_pending()
        time.sleep(30)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("run")
    sub.add_parser("daemon")
    args = p.parse_args()
    {"run": once, "daemon": daemon}[args.cmd](args)


if __name__ == "__main__":
    try:
        main()
    except (NoSuchWindowException, WebDriverException) as e:
        print("Browser window closed or session is invalid. Exiting.", e.msg)
    except Exception as e:
        print("In Applier Main", e)
        pyautogui.alert(e, "Exiting..")
    finally:
        from random import choice
        quote = choice([
            "You're one step closer than before.",
            "All the best with your future interviews.",
            "Keep up with the progress. You got this.",
            "If you're tired, learn to take rest but never give up.",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence.",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs",
            "Opportunities don't happen, you create them. - Chris Grosser",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance.",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt"
        ])
        msg = f"\n{quote}\n\n\nBest regards,\nGeetansh Sharma\nhttps://www.linkedin.com/in/geetansh-sharma00/\n\n"
        pyautogui.alert(msg, "Exiting..")
        print(msg, "Closing the browser...")
