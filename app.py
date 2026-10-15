from csv_handler import create_csv_file                   # initialize attendance storage
from ui import render_app                                 # load streamlit frontend interface


def main():
    create_csv_file()                                     # create attendance.csv if not exists
    render_app()                                          # run main application


if __name__ == "__main__":
    main()                                                # script entry point
