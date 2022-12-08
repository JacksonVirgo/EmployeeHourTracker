import tkinter as tk
from tkinter import ttk
from functools import partial
import calendar
import pickle
from datetime import datetime


## TWO DATA STUCTS USED.
## 1. Used as a base Storage (individual_employee_data)
## 2. Used when requesting a report.

##

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Work From Home Tracker')
        self.geometry('500x500')
        self.file_handle = 'employee_data.dat'

        self.individual_employee_data = {}
        self.all_employee_hours = {}

        ## Create an empty file if it does not exist.
        ## Load from it, if it does.
        try:
            self.individual_employee_data = pickle.load(open(self.file_handle, 'rb'))
        except:
            self.save_data({})

    ## FILE SYSTEM
    def save_data(self, data = None):
        data_to_save = data
        if data_to_save == None:
            data_to_save = self.individual_employee_data
        pickle.dump(self.individual_employee_data, open(self.file_handle, "wb"))
        return self.individual_employee_data
    def load_data(self):
        try:
            loaded_file = pickle.load(open(self.file_handle, 'rb'))
            return loaded_file
        except:
            return None

    # Add a new employee to the data structure
    def add_employee(self, id, name):
        new_employee = {
            "id": id,
            "name": name,
            "hours": {}
        }
        if (self.individual_employee_data.get(id) != None):
            return False
        else:
            self.individual_employee_data[id] = new_employee
            return True

    # Remove an employee from the data structure
    def remove_employee(self, id):
        if (self.individual_employee_data.get(id) != None):
            self.individual_employee_data.pop(id)
            return True
        else:
            return False
            
    # Add hours to an employee
    def add_employee_hours(self, id, hours):
        employee = self.individual_employee_data.get(id)
        date = datetime.utcnow()
        unixtime = calendar.timegm(date.utctimetuple())
        print(unixtime)
        if employee == None:
            return False
        employee.get("hours")[str(unixtime)] = hours
        return True

    # Get the latest X submitted hours.
    def get_latest_hours(self, last = 1):
        timestamps = []
        total_hours = {}
        for employee_id in self.individual_employee_data:
            employee = self.individual_employee_data[employee_id]
            list_of_hours = employee.get("hours")
            for timestamp in list_of_hours:
                timestamps.append(timestamp)
                hours = list_of_hours[timestamp]
                hours["id"] = employee_id
                total_hours[timestamp] = hours
        
        timestamps.sort(reverse=True)
        trimmed_timestamps = []
        for timestamp in timestamps:
            if len(trimmed_timestamps) < last:
                trimmed_timestamps.append(timestamp)

        final_object = {}
        for timestamp in trimmed_timestamps:
            final_object[timestamp] = total_hours[timestamp]
        
        return final_object

    ## Window Management
    # Remove all children from the window.
    def detach_children(self):
        for child in self.winfo_children(): 
            child.destroy()

    # Removes all children, ten reapplies them
    def reset_children(self):
        self.detach_children()
        window.attach_children()

    # Applys children to the window.
    def attach_children(self):
        current_row_index = 0
        amount_fetched = tk.Entry(window)
        amount_fetched.grid(row=current_row_index, column=3, columnspan=2)
        show_report = partial(self.show_weekly_report, amount_fetched.get())

        tk.Button(window, text= "View X Employee Reports", command=show_report).grid(row=current_row_index, column=0, columnspan=3)
        current_row_index += 1
        tk.Button(window, text= "Add New Employee", command=self.show_new_employee_form).grid(row=current_row_index, columnspan=5)
        current_row_index += 1
        tk.Label(window, text="Employee ID").grid(row=current_row_index, column=0)
        tk.Label(window, text="Employee Name").grid(row=current_row_index, column=2)
        current_row_index += 1

        for handle in self.individual_employee_data:
            employee = self.individual_employee_data[handle]
            tk.Label(window, text=employee["id"]).grid(row=current_row_index, column=0)
            tk.Label(window, text=employee["name"]).grid(row=current_row_index, column=2)
            update_action = partial(self.show_add_hours_form, employee["id"])
            tk.Button(window, text="Add Hours", command=update_action).grid(row=current_row_index, column=4)
            current_row_index += 1


    ## Popup Windows

    # Shows the report when requested.
    def show_weekly_report(self, fetch_size_raw):
        top= tk.Toplevel(self)
        top.geometry("500x500")
        top.title("Weekly Report")
        top.resizable(0,0)

        fetch_size = 5
        try:
            fetch_size = int(fetch_size_raw)
        except:
            print("Error fetchign size, defaulting to 5")

        latest_hour_data = self.get_latest_hours(fetch_size)
        less_than = []
        more_than = []
        just_right = []

        tk.Label(top, text="Employee Weekly Hours - %s most recent" % fetch_size).grid(row=0, column=0, columnspan=5)
        row_index = 0

        tk.Label(top, text="Employee ID").grid(row=1, column=0)
        tk.Label(top, text="Employee Name").grid(row=1, column=1)
        tk.Label(top, text="Week").grid(row=1, column=2)
        tk.Label(top, text="Total Hours").grid(row=1, column=3)

        row_index = 2
        for timestamp in latest_hour_data:
            hours_data = latest_hour_data.get(timestamp)
            employee_id = hours_data["id"]
            employee = self.individual_employee_data.get(employee_id)
            employee_name = employee.get("name")
            week = hours_data["WEEK"]

            employee_hours = 0
            days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
            for day in days:
                day_hours = hours_data[day]
                try:
                    if (day_hours == None):
                        employee_hours += 0
                    else:
                        employee_hours += float(day_hours)
                except:
                    print("Error Parsing Hours")


            if (employee_hours < 30):
                less_than.append(employee_id)
            elif (employee_hours > 40):
                more_than.append(employee_id)
            elif (employee_hours >= 37 and employee_hours <= 39):
                just_right.append(employee_id)

            tk.Label(top, text=employee_id).grid(row=row_index, column=0)
            tk.Label(top, text=employee_name).grid(row=row_index, column=1)
            tk.Label(top, text=week).grid(row=row_index, column=2)
            tk.Label(top, text=employee_hours).grid(row=row_index, column=3)
            row_index += 1

        tk.Label(top, text="AVERAGES").grid(row=row_index, column=1, columnspan=2)
        tk.Label(top, text="%s people worked less than 30 hours" % len(less_than)).grid(row=row_index+1, column=1, columnspan=2)
        tk.Label(top, text="%s people worked more than 40 hours" % len(more_than)).grid(row=row_index+2, column=1, columnspan=2)
        tk.Label(top, text="%s people worked between than 37 and 39 hours" % len(just_right)).grid(row=row_index+3, column=1, columnspan=2)

        def quit():
            top.destroy()
            top.update()

        tk.Button(top, text='Exit Weekly Report', command=quit).grid(row=row_index, column=0, columnspan=5)

    # Shows form dialogue for adding a new employee
    def show_new_employee_form(self):
        top= tk.Toplevel(self)
        top.geometry("280x300")
        top.title("Add New Employee")
        top.resizable(0,0)

        tk.Label(top, text="Employee ID").grid(row=2, columnspan=5)
        employee_id = tk.Entry(top)
        employee_id.grid(row=3, columnspan=5)

        tk.Label(top, text="Employee Name").grid(row=4, columnspan=5)
        employee_name = tk.Entry(top)
        employee_name.grid(row=5, columnspan=5)

        def quit():
            top.destroy()
            top.update()

        def add_new_employee_event():
            result = self.add_employee(employee_id.get(), employee_name.get())
            if result == False:
                self.show_error_message("Employee already exists under that ID")
            else:
                self.save_data()
                top.destroy()
                top.update()
                self.reset_children()
        tk.Button(top,  text='Save New Employee', command=add_new_employee_event).grid(row=9, column=0, columnspan=5)
        tk.Button(top, text='Exit Without Saving', command=quit).grid(row=10, column=0, columnspan=5)

    # Shows form dialogue for adding hours for an employee
    def show_add_hours_form(self, employee_id):
        top= tk.Toplevel(self)
        top.geometry("280x300")
        top.title("Add Hours Form")
        top.resizable(0,0)

        tk.Label(top, text="Working Week Number").grid(row=0, columnspan=5)
        week_number = tk.Entry(top)
        week_number.grid(row=1, columnspan=5)

        tk.Label(top, text="Employee Hours").grid(row=2, column=0, columnspan=5)
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        day_values = {}
        index = 0
        for x in days:
            tk.Label(top, text=x).grid(row=3, column=index)
            day_values[x] = tk.Entry(top, width=5)
            day_values[x].grid(row=4, column=index)
            index += 1

        def quit():
            top.destroy()
            top.update()

        def add_new_employee_event():
            def parseDay(val):
                hours_raw = day_values[val].get()
                try:
                    number = float(hours_raw)
                    return number
                except:
                    return 0

            hours_data = {
                "WEEK": week_number.get(),
                "MON": parseDay('MON'),
                "TUE": parseDay('TUE'),
                "WED": parseDay('WED'),
                "THU": parseDay('THU'),
                "FRI": parseDay('FRI'),
            }

            add_hours_result = self.add_employee_hours(employee_id, hours_data)

            if add_hours_result == False:
                self.show_error_message("An unexpected error has occurred.")
            else:
                error_messages = []
                hours_in_week = 0
                for day in hours_data:
                    if (day == "WEEK"): continue
                    hours_for_day = hours_data[day]
                    hours_in_week += hours_for_day
                    if (hours_for_day > 10):
                        error_messages.append("Too many hours worked on %s" % day)
                    elif (hours_for_day < 4):
                        error_messages.append("Not enough hours worked on %s" % day)

                if (hours_in_week > 40):
                    error_messages.append("You are working too hard!!")
                elif (hours_in_week < 30):
                    error_messages.append("You didn't do enough work this week")

                self.save_data()
                top.destroy()
                top.update()
                self.reset_children()
                
                if len(error_messages) > 0:
                    singular_message = '\n'.join(error_messages)
                    self.show_error_message(singular_message)
            

        tk.Button(top, text='Exit Employee Tracker', command=quit).grid(row=9, column=0, columnspan=5)
        tk.Button(top,  text='Save Employee Data', command=add_new_employee_event).grid(row=10, column=0, columnspan=5)

    # Shows an error messasge if something went wrong
    def show_error_message(self, error_message):
        error_top = tk.Toplevel(self)
        error_top.geometry("280x150")
        error_top.title("Error")
        error_top.resizable(0,0)
        tk.Label(error_top, text=error_message).pack()
        def quit():
                error_top.destroy()
                error_top.update()
        tk.Button(error_top, text='Exit Message', command=quit).pack()
    

if __name__ == "__main__":
    window = App()
    window.attach_children()
    window.mainloop()