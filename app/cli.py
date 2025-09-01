import argparse, schedule, time
from . import naukri_driver as nd

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
    main()
