import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import datetime




def save_record():
    name = name_entry.get()
    account = account_var.get()
    activity = activity_var.get()
    start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check if all input fields are filled
    if name == "" or account == "" or activity == "":
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    connection = None
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host='database-solanoteam.crztpf1c2nue.us-east-1.rds.amazonaws.com',
            port=3409,
            database='training',
            user='admin',
            password='394462ydmu1dC4nVNg1L'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Check if the 'diff' column exists in the 'data_entry' table
            cursor.execute("SHOW COLUMNS FROM data_entry LIKE 'diff'")
            if cursor.fetchone() is None:
                # 'diff' column does not exist, add it to the table
                cursor.execute("ALTER TABLE data_entry ADD COLUMN diff INT DEFAULT 0")
                connection.commit()

            # Get the ID and start time of the last record with the same name and same day
            query = "SELECT id, start FROM data_entry WHERE servant_number = %s AND DATE(start) = DATE(%s) ORDER BY id DESC LIMIT 1"
            cursor.execute(query, (name, start))
            result = cursor.fetchone()
            if result:
                last_id, last_start = result

                # Calculate the difference in seconds between the current start and last start
                diff = int((datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S') - last_start).total_seconds())

                # Update the end datetime and diff columns of the last record
                update_query = "UPDATE data_entry SET `end` = %s, diff = %s WHERE id = %s"
                cursor.execute(update_query, (start, diff, last_id))
                connection.commit()

            # Create a new record in the table
            insert_query = "INSERT INTO data_entry (servant_number, account, start, `end`, activity, diff) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (name, account, start, '0', activity, 0)
            cursor.execute(insert_query, values)
            connection.commit()

            messagebox.showinfo("Success", "Record saved successfully!")

            # Reset the input fields
            name_entry.delete(0, tk.END)
            account_var.set(accounts[0])
            activity_var.set(activities[0])

    except Error as e:
        messagebox.showerror("Error", f"Error while connecting to MySQL: {e}")

    finally:
        # Close the database connection
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()



def download_same_day_csv():
    current_date = datetime.date.today()
    records = retrieve_records(current_date, current_date)
    if records:
        save_records_to_csv(records, "current_day_records.csv")
    else:
        messagebox.showinfo("No Records", "No records found for the current day.")

def download_same_week_csv():
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=today.weekday())
    end_date = start_date + datetime.timedelta(days=6)
    records = retrieve_records(start_date, end_date)
    if records:
        save_records_to_csv(records, "same_week_records.csv")
    else:
        messagebox.showinfo("No Records", "No records found for the same week.")

def download_range_of_dates_csv():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        messagebox.showerror("Invalid Date", "Please enter valid start and end dates (YYYY-MM-DD).")
        return
    records = retrieve_records(start_date, end_date)
    if records:
        save_records_to_csv(records, "range_of_dates_records.csv")
    else:
        messagebox.showinfo("No Records", "No records found for the specified range of dates.")

def retrieve_records(start_date, end_date):
    connection = None
    records = []
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host='database-solanoteam.crztpf1c2nue.us-east-1.rds.amazonaws.com',
            port=3409,
            database='training',
            user='admin',
            password='394462ydmu1dC4nVNg1L'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            query = "SELECT * FROM data_entry WHERE DATE(start) BETWEEN %s AND %s"
            cursor.execute(query, (start_date, end_date))
            records = cursor.fetchall()

    except Error as e:
        messagebox.showerror("Error", f"Error while connecting to MySQL: {e}")

    finally:
        # Close the database connection
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

    return records

def save_records_to_csv(records, filename):
    import csv
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Name", "Account", "Start","Activity", "End","Diff(s)"])
        writer.writerows(records)
    messagebox.showinfo("CSV Saved", f"The CSV file '{filename}' has been saved successfully.")

# Create the GUI window
window = tk.Tk()
window.title("Data Entry Form")

# Styling options
window.geometry("450x500")
window.configure(bg="#f0f0f0")

# Create labels and entry fields
name_label = tk.Label(window, text="Número de Servidor:", bg="#f0f0f0")
name_label.pack()
name_entry = ttk.Entry(window, width=30)
name_entry.pack(pady=5)

# Activities dropdown
activities = ["Receiving",
              "QC",
              "Re-etiquetado",
              "Check In",
              "Put Away",
              "Replenishment",
              "Picking",
              "Prepacking",
              "Packing",
              "Postpacking",
              "Shipping",
              "Inventarios",
              "Consolidación",
              "Re-trabajo",
              "Vuelta en U",
              "5's",
              "Insumar",
              "Etiquetado insumos",
              "Conteo Insumos",
              "Destrucción cajas",
              "Tirar basura / carton",
              "Mantenimiento RK's",
              "Actividad FT",
              "Training",
              "SHE",
              "Labor Share",
              "Baño",
              "Break",
              "Comida",
              "Tool Crib",
              "Salida",
              "Actividad otra cuenta",
              "Personalización de material",
              "Revisión de material personalizado",
              "Asignación de proveedores para personalizado",
              "Actividades data clerk",
              "Enfermeria",
              "Entrenamiento"]  # Replace with your actual activities

activity_var = tk.StringVar(window)
activity_var.set(activities[0])  # Set the default selected activity
activity_label = tk.Label(window, text="Nombre de Actividad:", bg="#f0f0f0")
activity_label.pack()
activity_dropdown = tk.OptionMenu(window, activity_var, *activities)
activity_dropdown.pack(pady=5)

accounts = [
    "N/A",
    "ACRONYM LLC",
    "AMANI ENTERPRISES LLC",
    "ATR BRANDS LIMITED",
    "AXION LLC",
    "BEXCO ENTERPRISES INC",
    "BUTTERCUP BODYWEAR INC",
    "CHARLY USA LLC",
    "DECKED LLC",
    "EJAM INC",
    "ERUSI APLICACIONES SA DE CV",
    "FAMOSA NORTH AMERICA INC",
    "GOLDEN DRAGON ASSOCIATION INCDBA GOLDEN LIGHTING",
    "HAMMITT INC",
    "JEG HOLDCO LLC",
    "JUST ACCESS INC",
    "LOLA GETS INC",
    "NAKED WOLFE LIMITED",
    "OTG SURPLUS LLC",
    "PARAVEL INC",
    "PHONESOAP LLC",
    "PINNACLE BRAND GROUP INC",
    "TRU GRIT FITNESS LLC",
    "UNCHARTED SUPPLY COMPANY",
    "XCEL BRANDS INC",
    "ZOIC",
    "THIRTY THREE THREADS INC",
    "ARRIS GROUP DE MEXICO SA DE CV",
    "EWS S DE RL DE CV",
    "MEDTRONIC",
    "SPRINGS WINDOW FASHIONS",
    "WALKING COMPANY",
    "MEDLINE",
    "LEGRAND",
    "PORTLAND PRODUCT WERKS LLC",
    "PHOENIX FOOTWEAR GROUP INC",
    "RECIBOS"
]













account_var = tk.StringVar(window)
account_var.set(accounts[0])  # Set the default selected account
account_label = tk.Label(window, text="Cuenta:", bg="#f0f0f0")
account_label.pack()
account_dropdown = tk.OptionMenu(window, account_var, *accounts)
account_dropdown.pack(pady=5)

# Create save button
save_button = tk.Button(window, text="Save", command=save_record, bg="#4caf50", fg="white", width=10)
save_button.pack(pady=10)

# Create tabs
tab_control = tk.Tk()

tab_control = ttk.Notebook(window)

same_day_tab = tk.Frame(tab_control)
tab_control.add(same_day_tab, text="Reporte de día actual")

same_week_tab = tk.Frame(tab_control)
tab_control.add(same_week_tab, text="Reporte de la semana actual")

range_of_dates_tab = tk.Frame(tab_control)
tab_control.add(range_of_dates_tab, text="Reporte por rango de fechas")

# Same Day Tab
same_day_label = tk.Label(same_day_tab, text="Descargar CSV", bg="#f0f0f0")
same_day_label.pack(pady=5)

same_day_button = tk.Button(same_day_tab, text="Descargar CSV", command=download_same_day_csv)
same_day_button.pack(pady=5)

# Same Week Tab
same_week_label = tk.Label(same_week_tab, text="Descargar CSV", bg="#f0f0f0")
same_week_label.pack(pady=5)

same_week_button = tk.Button(same_week_tab, text="Descargar CSV", command=download_same_week_csv)
same_week_button.pack(pady=5)

# Range of Dates Tab
range_of_dates_label = tk.Label(range_of_dates_tab, text="Descargar CSV", bg="#f0f0f0")
range_of_dates_label.pack(pady=5)

start_date_label = tk.Label(range_of_dates_tab, text="Fecha Inicial (YYYY-MM-DD):", bg="#f0f0f0")
start_date_label.pack()
start_date_entry = tk.Entry(range_of_dates_tab, width=30)
start_date_entry.pack(pady=5)

end_date_label = tk.Label(range_of_dates_tab, text="Fecha Final (YYYY-MM-DD):", bg="#f0f0f0")
end_date_label.pack()
end_date_entry = tk.Entry(range_of_dates_tab, width=30)
end_date_entry.pack(pady=5)

range_of_dates_button = tk.Button(range_of_dates_tab, text="Descargar CSV", command=download_range_of_dates_csv)
range_of_dates_button.pack(pady=5)

# Add tabs to the window
tab_control.pack(expand=1, fill="both")





# Start the main GUI loop
window.mainloop()


