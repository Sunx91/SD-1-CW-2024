# Author: Sunath Sandul Jayalath
# Date: 2024/11/10
# Student ID: 20240646 / w2120070

# Task A: Input Validation
def validate_date_input():
    """
    Prompts the user for a date in DD MM YYYY format, validates the input for:
    - Correct data type
    - Correct range for day, month, and year
    """
    while True:
        try:
            day = int(input("Please enter the day of the survey in the format DD: "))
            month = int(input("Please enter the month of the survey in the format MM: "))
            year = int(input("Please enter the year of the survey in the format YYYY: "))

            if not (1 <= day <= 31):
                print("Out of range - day must be between 1 and 31.")
                continue
            if not (1 <= month <= 12):
                print("Out of range - month must be between 1 and 12.")
                continue
            if not (2000 <= year <= 2024):
                print("Out of range - year must be between 2000 and 2024.")
                continue

            date_str = f"{day:02d}{month:02d}{year}"

            # Check if the file exists
            file_name = f"traffic_data{date_str}.csv"
            if file_exists(file_name):
                return file_name
            else:
                print(f"No CSV file found for the date {date_str}. Please try again.")
                continue

        except ValueError:
            print("Invalid input. Please enter integers for day, month, and year.")
            continue


def file_exists(file_name):
    try:
        with open(file_name, 'r'):
            return True
    except FileNotFoundError:
        return False


def validate_continue_input():
    """
    Prompts the user to decide whether to load another dataset:
    - Validates "Y" or "N" input
    """
    while True:
        user_input = input("Do you want to load another dataset? (Y/N): ").strip().upper()
        if user_input == 'Y':
            return True
        elif user_input == 'N':
            return False
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")


# Task B: Processed Outcomes
def process_csv_data(file_path):
    """
    Processes the CSV data for the selected date and extracts:
    - Total vehicles
    - Total trucks
    - Total electric vehicles
    - Two-wheeled vehicles, and other requested metrics
    """
    vehicle_counts = {
        "total": 0,
        "trucks": 0,
        "electric_vehicles": 0,
        "two_wheeled_vehicles": 0,
        "buses_north": 0,
        "no_turns": 0,
        "over_speed_limit": 0,
        "elm_avenue_only": 0,
        "hanley_highway_only": 0,
        "scooters_at_elm": 0,
        "rain_hours": 0,
        "truck_percentage": 0,
        "scooters_at_elm_percentage": 0,
        "highest_vehicles_on_hanley": 0,
        "bikes_per_hour": 0,
        "total_bike_hours": 0
    }

    # Counting bicycles and vehicles on Hanley Highway (hours)
    hanley_highway_counts = {}
    bike_hour_counts = {}

    try:
        with open(file_path, 'r') as file:
            print(f"Processing file: {file_path}")
            lines = file.readlines()

            header = lines[0].strip().split(',')

            for line in lines[1:]:
                row = line.strip().split(',')
                data = {header[i]: row[i] for i in range(len(header))}

                # Count total vehicles
                vehicle_counts["total"] += 1

                # Count trucks
                if data["VehicleType"].lower() == "truck":
                    vehicle_counts["trucks"] += 1

                # Count electric vehicles
                if data["elctricHybrid"].strip().lower() == "true":
                    vehicle_counts["electric_vehicles"] += 1

                # Count two-wheeled vehicles (bike, scooter, motorcycle)
                if data["VehicleType"].lower() in ["bicycle", "scooter", "motorcycle"]:
                    vehicle_counts["two_wheeled_vehicles"] += 1
                    # Track bikes per hour
                    hour = data["timeOfDay"].split(":")[0]
                    if hour in bike_hour_counts:
                        bike_hour_counts[hour] += 1
                    else:
                        bike_hour_counts[hour] = 1

                # Count buses heading north at Elm Avenue/Rabbit road
                junction_name = data["JunctionName"].strip().lower()
                if junction_name == "elm avenue/rabbit road" and data["VehicleType"].lower() == "bus" and data[
                    "travel_Direction_out"].lower() == "n":
                    vehicle_counts["buses_north"] += 1

                # Count vehicles that go straight through the junction (no turn)
                if data["travel_Direction_in"].lower() == data["travel_Direction_out"].lower():
                    vehicle_counts["no_turns"] += 1

                # Count vehicles over the speed limit
                if int(data["VehicleSpeed"]) > int(data["JunctionSpeedLimit"]):
                    vehicle_counts["over_speed_limit"] += 1

                # Count vehicles at Elm Avenue only
                if junction_name == "elm avenue/rabbit road":
                    vehicle_counts["elm_avenue_only"] += 1

                # Count vehicles at Hanley Highway only
                if data["JunctionName"].strip().lower() == "hanley highway/westway":
                    vehicle_counts["hanley_highway_only"] += 1

                # Count scooters at Elm Avenue
                if junction_name == "elm avenue/rabbit road" and data["VehicleType"].lower() == "scooter":
                    vehicle_counts["scooters_at_elm"] += 1

                # Track the hours for Hanley Highway to find peak traffic
                if data["JunctionName"].strip().lower() == "hanley highway/westway":
                    hour = data["timeOfDay"].split(":")[0]
                    if hour in hanley_highway_counts:
                        hanley_highway_counts[hour] += 1
                    else:
                        hanley_highway_counts[hour] = 1

                # Count rain hours
                rain_conditions = ["heavy rain", "light rain"]

                # Count rain hours if the condition matches
                if any(rain_condition in data["Weather_Conditions"].strip().lower() for rain_condition in
                       rain_conditions):
                    vehicle_counts["rain_hours"] += 1

        # Calculate percentages and averages
        if vehicle_counts["total"] > 0:
            vehicle_counts["truck_percentage"] = round((vehicle_counts["trucks"] / vehicle_counts["total"]) * 100)
        if vehicle_counts["elm_avenue_only"] > 0:
            vehicle_counts["scooters_at_elm_percentage"] = round(
                (vehicle_counts["scooters_at_elm"] / vehicle_counts["elm_avenue_only"]) * 100)

        # Calculate peak traffic on Hanley Highway
        max_traffic = max(hanley_highway_counts.values(), default=0)
        peak_hours = [hour for hour, count in hanley_highway_counts.items() if count == max_traffic]
        formatted_peak_hours = [f"{hour}:00 and {int(hour) + 1}:00" for hour in peak_hours]

        # Calculate average bikes per hour
        total_bike_hours = sum(bike_hour_counts.values())
        if total_bike_hours > 0:
            vehicle_counts["bikes_per_hour"] = total_bike_hours / len(bike_hour_counts)

        return vehicle_counts, formatted_peak_hours, max_traffic

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return None, None


def display_outcomes(vehicle_counts, formatted_peak_hours, max_traffic):
    """
    Displays the calculated outcomes in a clear and formatted way.
    """
    print(f"\nThe total number of vehicles recorded for this date is {vehicle_counts['total']}")
    print(f"The total number of trucks recorded for this date is {vehicle_counts['trucks']}")
    print(f"The total number of electric vehicles for this date is {vehicle_counts['electric_vehicles']}")
    print(f"The total number of two-wheeled vehicles for this date is {vehicle_counts['two_wheeled_vehicles']}")
    print(f"The total number of buses leaving Elm Avenue/Rabbit Road heading North is {vehicle_counts['buses_north']}")
    print(
        f"The total number of vehicles through both junctions not turning left or right is {vehicle_counts['no_turns']}")
    print(f"The percentage of vehicles recorded that are trucks for this date is {vehicle_counts['truck_percentage']}%")
    print(f"Average number of bikes per hour this date is {int(vehicle_counts['bikes_per_hour'])}")
    print(
        f"The total number of vehicles recorded as over the speed limit for this date is {vehicle_counts['over_speed_limit']}")
    print(
        f"The total number of vehicles recorded through Elm Avenue/Rabbit Road junction is {vehicle_counts['elm_avenue_only']}")
    print(f"The total number of vehicles recorded through Hanley Highway: {vehicle_counts['hanley_highway_only']}")
    print(
        f"{vehicle_counts['scooters_at_elm_percentage']}% of vehicles recorded through Elm Avenue/Rabbit Road are scooters")
    print(f"The highest number of vehicles in an hour on Hanley Highway/Westway is: {max_traffic}")
    print(f"Total number of rain hours: {vehicle_counts['rain_hours']}")
    print(
        f"The most vehicles through on Hanley Highway/Westway were recorded between {', '.join(formatted_peak_hours)}")


# Task C: Results Saving
def save_results_to_file(vehicle_counts, formatted_peak_hours, file_name, max_traffic):
    """
    Saves the calculated results to a text file.
    """
    output_file = "results.txt"
    try:
        with open(output_file, 'a+') as file:
            file.write(f"\n")
            file.write(f"Data file selected is {file_name} \n")
            file.write(f"The total number of vehicles recorded for this date is {vehicle_counts['total']}\n")
            file.write(f"The total number of trucks recorded for this date is {vehicle_counts['trucks']}\n")
            file.write(
                f"The total number of electric vehicles for this date is {vehicle_counts['electric_vehicles']}\n")
            file.write(
                f"The total number of two-wheeled vehicles for this date is {vehicle_counts['two_wheeled_vehicles']}\n")
            file.write(
                f"The total number of buses leaving Elm Avenue/Rabbit Road heading North is {vehicle_counts['buses_north']}\n")
            file.write(
                f"The total number of vehicles through both junctions not turning left or right is {vehicle_counts['no_turns']}\n")
            file.write(
                f"The percentage of vehicles recorded that are trucks for this date is {vehicle_counts['truck_percentage']}%\n")
            file.write(f"Average number of bikes per hour this date is {int(vehicle_counts['bikes_per_hour'])}\n")
            file.write(
                f"The total number of vehicles recorded as over the speed limit for this date is {vehicle_counts['over_speed_limit']}\n")
            file.write(
                f"The total number of vehicles recorded through Elm Avenue/Rabbit Road junction is {vehicle_counts['elm_avenue_only']}\n")
            file.write(
                f"The total number of vehicles recorded through Hanley Highway: {vehicle_counts['hanley_highway_only']}\n")
            file.write(
                f"{vehicle_counts['scooters_at_elm_percentage']}% of vehicles recorded through Elm Avenue/Rabbit Road are scooters \n")
            file.write(f"The highest number of vehicles in an hour on Hanley Highway/Westway is: {max_traffic}\n")
            file.write(f"Total number of rain hours: {vehicle_counts['rain_hours']}\n")
            file.write(
                f"The most vehicles through on Hanley Highway/Westway were recorded between {', '.join(formatted_peak_hours)}\n \n")
            file.write(f"**********************************************  \n")
            print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while saving the results: {e}")


# Import required modules
import tkinter as tk


# Part D: Visualization with HistogramApp
class HistogramApp:
    """
    This class creates a histogram visualization for vehicle frequency per hour
    based on the provided data. The histogram includes bars for two locations:
    Elm Avenue/Rabbit Road and Hanley Highway/Westway.
    """

    def __init__(self, traffic_data, date):
        """
        Initialize the histogram application.

        Args:
            traffic_data: Dictionary containing hourly vehicle data for two locations.
            date: Date string to be displayed on the histogram title.
        """
        self.traffic_data = traffic_data
        self.date = date
        self.root = tk.Tk()
        self.root.title("Histogram")

        self.setup_window()
        self.draw_histogram()
        self.add_legend()

    def setup_window(self):
        """
        Setup the main window and canvas for the histogram.
        """
        self.canvas_width = 1400
        self.canvas_height = 800
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="#f4f4f4")
        self.canvas.pack()

    def draw_histogram(self):
        """
        Draw the histogram bars and associated labels.
        """
        # Combine the values from both locations into a single list
        all_values = list(self.traffic_data["Elm Avenue/Rabbit Road"].values()) + \
                     list(self.traffic_data["Hanley Highway/Westway"].values())

        # Determine the maximum value to scale bar heights proportionally
        max_value = max(all_values) if all_values else 1  # Use 1 as a fallback if there are no values
        bar_width = 20  # Width of each bar
        group_gap = 10  # Gap between groups of two bars (Elm and Hanley)
        margin = 80  # Margin from the left side of the canvas

        # Loop through 24 hours to draw bars for both locations
        for hour in range(24):
            group_start = margin + hour * (2 * bar_width + group_gap)

            # Draw Elm Avenue bars
            elm_value = self.traffic_data["Elm Avenue/Rabbit Road"][str(hour).zfill(2)]
            x1_elm = group_start
            x2_elm = x1_elm + bar_width
            y1_elm = self.canvas_height - (elm_value / max_value * 600) - 100
            y2_elm = self.canvas_height - 100
            self.canvas.create_rectangle(x1_elm, y1_elm, x2_elm, y2_elm, fill="cyan", outline="black")
            self.canvas.create_text((x1_elm + x2_elm) // 2, y1_elm - 10, text=str(elm_value), fill="black")

            # Draw Hanley Highway bars
            hanley_value = self.traffic_data["Hanley Highway/Westway"][str(hour).zfill(2)]
            x1_hanley = x2_elm
            x2_hanley = x1_hanley + bar_width
            y1_hanley = self.canvas_height - (hanley_value / max_value * 600) - 100
            y2_hanley = self.canvas_height - 100
            self.canvas.create_rectangle(x1_hanley, y1_hanley, x2_hanley, y2_hanley, fill="deep sky blue", outline="black")
            self.canvas.create_text((x1_hanley + x2_hanley) // 2, y1_hanley - 10, text=str(hanley_value), fill="black")

            # Add hour labels at the bottom of the histogram
            time_label = f"{hour:02d}:00"
            self.canvas.create_text((x1_elm + x2_hanley) // 2, self.canvas_height - 80, text=time_label, fill="black", anchor="n")

            self.canvas.create_line(80, 700, 1320, 700, fill="black") # Verticle line at the bottom of the bars

    def add_legend(self):
        """
        Add a legend to the histogram to explain the colors used.
        """
        legend_x_start = 50
        self.canvas.create_rectangle(legend_x_start, 10, legend_x_start + 20, 30, fill="cyan", outline="black")
        self.canvas.create_text(legend_x_start + 30, 20, text="Elm Avenue/Rabbit Road", anchor="w", fill="black")

        self.canvas.create_rectangle(legend_x_start, 40, legend_x_start + 20, 60, fill="deep sky blue", outline="black")
        self.canvas.create_text(legend_x_start + 30, 50, text="Hanley Highway/Westway", anchor="w", fill="black")

        # Add title
        self.canvas.create_text(self.canvas_width // 2, 40,
                                text=f"Histogram of Vehicle Frequency per Hour ({self.date})",
                                font=("Arial", 18, "bold"), fill="black")
        self.canvas.create_text(self.canvas_width // 2, self.canvas_height - 50,
                                text="Hours 00:00 to 24:00", font=("Arial", 12), fill="black")

    def run(self):
        """
        Starts the Tkinter main loop to display the histogram.
        """
        self.root.mainloop()
# Task E: Code Loops to Handle Multiple CSV Files
class MultiCSVProcessor:
    def __init__(self):
        """
        Initializes the application for processing multiple CSV files.
        """
        self.current_data = None

    def load_csv_file(self, file_path):
        """
        Loads a CSV file and processes its data.
        """
        print(f"Loading file: {file_path}")
        vehicle_counts, formatted_peak_hours, max_traffic = process_csv_data(file_path)
        if vehicle_counts and formatted_peak_hours:
            display_outcomes(vehicle_counts, formatted_peak_hours, max_traffic)
            save_results_to_file(vehicle_counts, formatted_peak_hours, file_path, max_traffic)

            hourly_data = {
                "Elm Avenue/Rabbit Road": {str(hour).zfill(2): 0 for hour in range(24)},
                "Hanley Highway/Westway": {str(hour).zfill(2): 0 for hour in range(24)}
            }

            with open(file_path, 'r') as file:
                lines = file.readlines()
                header = lines[0].strip().split(',')
                for line in lines[1:]:
                    row = line.strip().split(',')
                    data = {header[i]: row[i] for i in range(len(header))}
                    junction = data['JunctionName'].strip().lower()
                    hour = data['timeOfDay'][:2]
                    if junction == "elm avenue/rabbit road":
                        hourly_data["Elm Avenue/Rabbit Road"][hour] += 1
                    elif junction == "hanley highway/westway":
                        hourly_data["Hanley Highway/Westway"][hour] += 1

            app = HistogramApp(hourly_data, file_path)
            app.run()

    def clear_previous_data(self):
        """
        Clears data from the previous run to process a new dataset.
        """
        self.current_data = None
        print("Cleared previous data.")

    def handle_user_interaction(self):
        """
        Handles user input for processing multiple files.
        """
        while True:
            file_name = validate_date_input()
            self.clear_previous_data()
            self.load_csv_file(file_name)

            if not validate_continue_input():
                print("Exiting program. Thank you!")
                break

    def process_files(self):
        """
        Main loop for handling multiple CSV files until the user decides to quit.
        """
        print("Welcome to the Traffic Data Analyzer.")
        self.handle_user_interaction()

# Run the processor for Task E
if __name__ == "__main__":
    processor = MultiCSVProcessor()
    processor.process_files()
