from csv_handler import create_csv_file                   # import csv initializer
from ui import render_app                                 # import ui renderer


def main():
    create_csv_file()                                     # create attendance.csv if not exists
    render_app()                                          # start the streamlit app


if __name__ == "__main__":
    main()                                                # run main function
