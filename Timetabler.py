from datetime import datetime, timedelta
import json


class Assignment:
    def __init__(self, name, due_date, status="Not Started"):
        self.name = name
        self.due_date = due_date
        self.status = status

    def to_dict(self):
        return {"name": self.name, "due_date": self.due_date, "status": self.status}


class Writeup(Assignment):
    def __init__(self, name, due_date, status="Not Started"):
        super().__init__(f"Writeup {name}", due_date, status)


class Execution(Assignment):
    def __init__(self, name, due_date, status="Not Started"):
        super().__init__(f"Execution {name}", due_date, status)


class Lecture:
    def __init__(self, name, start_time, end_time, location, instructor, lecture_type):
        self.name = name
        self.type = lecture_type
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.instructor = instructor


class Day:
    def __init__(self, name):
        self.name = name
        self.lectures = []

    def add_lecture(self, lecture):
        self.lectures.append(lecture)


class Timetable:
    def __init__(self):
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        self.days = [Day(day_name) for day_name in day_names]

    def add_lecture(
        self, name, day_idx, start_time, duration, location, instructor, lecture_type
    ):
        end_time = (
            datetime.strptime(start_time, "%H:%M") + timedelta(minutes=int(duration))
        ).strftime("%H:%M")
        new_lecture = Lecture(
            name=name,
            start_time=start_time,
            end_time=end_time,
            location=location,
            instructor=instructor,
            lecture_type=lecture_type,
        )
        self.days[day_idx].add_lecture(new_lecture)

    def get_lectures(self, day_idx):
        res = []
        for lecture in self.days[day_idx].lectures:
            res.append(
                f"{lecture.name} ({lecture.type})\n"
                f"Time: {lecture.start_time} - {lecture.end_time}\n"
                f"Location: {lecture.location}\n"
                f"Instructor: {lecture.instructor}\n"
            )
        return "\n".join(res) if res else "No lectures scheduled"


def save_assignments(assignments, filename="assignments.json"):
    with open(filename, "w") as f:
        json.dump([a.to_dict() for a in assignments], f)


def load_assignments(filename="assignments.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            assignments = []
            for item in data:
                if item["name"].startswith("Writeup"):
                    assignments.append(
                        Writeup(
                            item["name"].replace("Writeup ", ""),
                            item["due_date"],
                            item["status"],
                        )
                    )
                elif item["name"].startswith("Execution"):
                    assignments.append(
                        Execution(
                            item["name"].replace("Execution ", ""),
                            item["due_date"],
                            item["status"],
                        )
                    )
                else:
                    assignments.append(
                        Assignment(item["name"], item["due_date"], item["status"])
                    )
            return assignments
    except (FileNotFoundError, json.JSONDecodeError):
        return []


if __name__ == "__main__":
    # Initialize timetable
    timetable = Timetable()

    # Check if we need to load or create timetable data
    try:
        with open("timetable.json", "r") as f:
            content = f.read()
            if content.strip():
                timetable_data = json.loads(content)
                # Load timetable data here if needed
            else:
                raise json.JSONDecodeError("Empty file", "", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Let's set up your weekly timetable!")
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        for day_idx, day_name in enumerate(day_names):
            print(f"\n{day_name}'s Schedule:")
            while True:
                name = input("\nEnter lecture name (or 'done' to finish day): ")
                if name.lower() == "done":
                    break

                start_time = input("Start time (HH:MM): ")
                duration = input("Duration in minutes: ")
                location = input("Location: ")
                instructor = input("Instructor: ")
                lecture_type = input("Type (Theory/Lab/Other): ")

                timetable.add_lecture(
                    name,
                    day_idx,
                    start_time,
                    duration,
                    location,
                    instructor,
                    lecture_type,
                )

                if input("Add another lecture? (y/n): ").lower() != "y":
                    break

        # Save empty timetable structure
        with open("timetable.json", "w") as f:
            json.dump(
                {
                    "monday": [],
                    "tuesday": [],
                    "wednesday": [],
                    "thursday": [],
                    "friday": [],
                },
                f,
            )

    # Assignment management
    assignments = load_assignments()

    # Check for new assignments
    current_day = datetime.now().strftime("%A").lower()
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday"]

    if current_day not in weekdays:
        print("\nIt's the weekend! Showing Friday's schedule:")
        day_idx = 4  # Friday's index
        current_day = "friday"
    else:
        day_idx = weekdays.index(current_day)

    print(f"\n{current_day.capitalize()}'s Lectures:")
    print(timetable.get_lectures(day_idx))

    if day_idx is not None:
        for lecture in timetable.days[day_idx].lectures:
            if (
                input(
                    f"\nWas there an assignment given for {lecture.name}? (y/n): "
                ).lower()
                == "y"
            ):
                if lecture.type.lower() == "lab":
                    assignments.append(
                        Writeup(
                            input("Enter writeup number: "),
                            input("Enter due date (YYYY-MM-DD): "),
                            "Not Started",
                        )
                    )
                    assignments.append(
                        Execution(
                            input("Enter experiment number: "),
                            input("Enter due date (YYYY-MM-DD): "),
                            "Not Started",
                        )
                    )
                else:
                    assignments.append(
                        Assignment(
                            input("Enter assignment name: "),
                            input("Enter due date (YYYY-MM-DD): "),
                            "Not Started",
                        )
                    )

    # Check for completed assignments
    if assignments:
        print("\nCurrent Assignments:")
        for i, assignment in enumerate(assignments, 1):
            print(
                f"{i}. {assignment.name} - Due: {assignment.due_date} - Status: {assignment.status}"
            )

        while True:
            complete = input(
                "\nEnter assignment number to mark as completed (or 'done'): "
            )
            if complete.lower() == "done":
                break
            try:
                idx = int(complete) - 1
                if 0 <= idx < len(assignments):
                    assignments[idx].status = "Completed"
                    print(f"Marked '{assignments[idx].name}' as completed!")
            except ValueError:
                print("Please enter a valid number or 'done'")

    # Save all assignments
    save_assignments(assignments)

    # Show pending assignments
    pending = [a for a in assignments if a.status != "Completed"]
    if pending:
        print("\nPending Assignments:")
        for assignment in pending:
            print(f"- {assignment.name} (Due: {assignment.due_date})")
    else:
        print("\nNo pending assignments!")
