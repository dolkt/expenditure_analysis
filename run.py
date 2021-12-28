import files
import database
import utils
import Reports
import os
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


user_action = input("""Select your action:
[1] Upload new data
[2] Produce Expenditure Report
Select: """)

if user_action == str(1):
    df = files.chosen_file()
    utils.categorization(df)

    database.upload_data(df)

    print("Upload Success! - Data Uploaded to Database")

elif user_action == str(2):

    report_type = input("""Which Expenditure Report Should Be Produced?
    [1] One-Month Report
    [2] Quarterly Report
    Select: """)
    
    if report_type == "1":
        chosen_month = input("Select which month to analyze, as YYYY-MM: ")

        df = database.pull_data(chosen_month, chosen_month)
        
        os.chdir(Reports.get_report_path())

        monthly_report = PdfPages(f"One Month Report for Period {chosen_month}.pdf")
        monthly_report.savefig(utils.month_hbarplot(df))
        monthly_report.close()

    
    elif report_type == "2":
        
        start_date = input("Select which period as start, as YYYY-MM: ")
        end_date = input("Select which period to end the quarterly report, as YYYY-MM: ")
    
        df = database.pull_data(start_date, end_date)


        os.chdir(Reports.get_report_path())

        quarterly_report = PdfPages(f"Quarterly Report {start_date} to {end_date}.pdf")
        quarterly_report.savefig(utils.line_plot(df))
        for figure in utils.bar_plot(df):
            quarterly_report.savefig(figure)

        quarterly_report.close()
    

#Add a license