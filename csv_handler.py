import csv                                                # standard csv library
import os                                                 # for checking file existence
from datetime import datetime                             # for getting current time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))     # get script directory
CSV_FILE = os.path.join(BASE_DIR, "attendance.csv")       # attendance storage file path


def create_csv_file():
    if not os.path.exists(CSV_FILE):                      # check if file doesn't exist
        f = open(CSV_FILE, "w", newline="", encoding="utf-8") # create new file
        writer = csv.writer(f)                            # initialize csv writer
        writer.writerow(["class_name", "subject", "date", "lecture_time", "roll_number", "time"]) # headers
        f.close()                                         # close file


def read_present_students(class_name, subject, date_str, lecture_time=None):
    create_csv_file()                                     # ensure file exists first
    present = []                                          # list to store roll numbers

    f = open(CSV_FILE, "r", newline="", encoding="utf-8") # open file in read mode
    reader = csv.DictReader(f)                            # read rows as dictionaries
    for row in reader:                                    # loop through each row
        # Match class, subject, date, and optionally lecture_time
        match_class = (row.get("class_name") == class_name)
        match_subject = (row.get("subject") == subject)
        match_date = (row.get("date") == date_str)
        match_time = (lecture_time is None or row.get("lecture_time") == lecture_time)

        if match_class and match_subject and match_date and match_time:
            roll = row.get("roll_number")                 # extract roll number
            if roll and roll not in present:              # avoid duplicate in list
                present.append(roll)                      # add to present list
    f.close()                                             # close file
    return present                                        # return list of roll numbers


def append_attendance_to_csv(class_name, subject, date_str, lecture_time, roll_number):
    time_now = datetime.now().strftime("%H:%M:%S")        # current time in HH:MM:SS
    f = open(CSV_FILE, "a", newline="", encoding="utf-8") # open file in append mode
    writer = csv.writer(f)                                # csv writer
    writer.writerow([class_name, subject, date_str, lecture_time, roll_number, time_now]) # append row
    f.close()                                             # close file


def get_subject_sessions(subject):
    create_csv_file()                                     # ensure file exists
    sessions = {}                                         # store unique sessions

    f = open(CSV_FILE, "r", newline="", encoding="utf-8") # open file in read mode
    reader = csv.DictReader(f)                            # read rows
    for row in reader:                                    # loop through records
        if row.get("subject") == subject:                 # filter by teacher's subject
            c = row.get("class_name", "")                 # class name
            d = row.get("date", "")                       # date string
            t = row.get("lecture_time", "")               # time slot
            key = (c, d, t)                               # session identifier
            if key not in sessions:
                sessions[key] = []                        # list of rolls for this session
            roll = row.get("roll_number")                 # roll number
            if roll and roll not in sessions[key]:
                sessions[key].append(roll)                # record roll
    f.close()                                             # close file
    return sessions                                       # return sessions dict
