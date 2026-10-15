import os                                                 # file path operations
import csv                                                # standard csv reading and writing
from datetime import datetime                             # timestamps for attendance records

BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # current project directory
CSV_FILE = os.path.join(BASE_DIR, "attendance.csv")       # path to csv database


def create_csv_file():
    if not os.path.exists(CSV_FILE):                      # check if csv does not exist
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)                        # initialize csv writer
            writer.writerow(["class_name", "subject", "date", "lecture_time", "roll_number", "time"]) # header


def read_present_students(class_name, subject, date_str, lecture_time=None):
    create_csv_file()                                     # ensure file exists
    present = []                                          # store roll numbers

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)                        # read rows as dictionaries
        for row in reader:
            matches_class = (row.get("class_name") == class_name)       # match class
            matches_sub = (row.get("subject") == subject)               # match subject
            matches_date = (row.get("date") == date_str)                 # match date
            matches_time = (lecture_time is None or row.get("lecture_time") == lecture_time) # match slot

            if matches_class and matches_sub and matches_date and matches_time:
                roll = row.get("roll_number")             # extract roll
                if roll and roll not in present:
                    present.append(roll)                  # avoid duplicates in list

    return present                                        # return list of present rolls


def append_attendance_to_csv(class_name, subject, date_str, lecture_time, roll_number):
    create_csv_file()                                     # ensure file exists
    now_time = datetime.now().strftime("%H:%M:%S")        # current time in HH:MM:SS

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)                            # csv writer
        writer.writerow([class_name, subject, date_str, lecture_time, roll_number, now_time]) # write row


def get_subject_sessions(subject):
    create_csv_file()                                     # ensure file exists
    sessions = {}                                         # store past sessions

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)                        # read records
        for row in reader:
            if row.get("subject") == subject:             # filter by faculty subject
                c = row.get("class_name", "")             # class
                d = row.get("date", "")                   # date
                t = row.get("lecture_time", "")           # time slot
                key = (c, d, t)                           # session composite key

                if key not in sessions:
                    sessions[key] = []                    # initialize session list

                roll = row.get("roll_number")             # roll number
                if roll and roll not in sessions[key]:
                    sessions[key].append(roll)            # add roll to session list

    return sessions                                       # return sessions map
