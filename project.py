#libraries
import json
import sys
from datetime import date, timedelta

class Habit:
    #storing data for each habit
    def __init__(self, name, history=None):
        self.name = name
        self.history = history if history else []
    def to_data(self):
        return {
            "name": self.name,
            "history": self.history
        }   
    def get_stats(self):
        longest_streak = 0
        current_streak = 0
        history_dates = [date.fromisoformat(d) for d in self.history]
        sorted_history = sorted(history_dates)
        for i in range(len(sorted_history)):
            if i == 0 or (sorted_history[i] - sorted_history[i - 1]).days == 1:
                current_streak += 1
            else:
                current_streak = 1
            longest_streak = max(longest_streak, current_streak)

        # Check if today or yesterday is in the history to determine the current streak
        today = date.today()
        yesterday = today - timedelta(days=1)
        if today in sorted_history:
            check_date = today
        elif yesterday in sorted_history:
            check_date = yesterday
        else:
            check_date = 0

        # Calculate the current streak based on the last checked date
        current_streak = 0
        if check_date:
            for d in reversed(sorted_history):
                if d == check_date:
                    current_streak += 1
                    check_date -= timedelta(days=1)
                elif d < check_date:
                    break

        # Calculate completion rate
        if self.history:
            first_date = sorted_history[0]
            today = date.today()
            total_days_since_start = (today - first_date).days + 1
            completion_rate = (len(self.history) / total_days_since_start) * 100
        else:
            completion_rate = 0
        return {
            "current_streak": current_streak, #returning current streak
            "longest_streak": longest_streak, #returning longest streak
            "completion_rate": completion_rate #returning completion rate
        }
class HabitTracker:
    def __init__(self):
        self.habits = []
        self.pet = Pet("Nebula")

    def check_penalies(self):
        today_str = date.today().isoformat()

        if self.pet.last_penalty_date == today_str:
            return  # Already checked penalties today

        today = date.today()
        penalty_applied = False

        for habit in self.habits:
            if habit.history:
                last_checkin_date = date.fromisoformat(habit.history[-1])
                if (today - last_checkin_date).days > 1:
                    self.pet.lose_hp(20)  # Apply penalty for missed habit
                    penalty_applied = True
                    print(f"Penalty applied for habit '{habit.name}' due to missed check-ins.")
            else:
                print(f"You haven't checked in for habit '{habit.name}' yet. Your pet will lose HP.")
                self.pet.lose_hp(20)  # Lose 20 HP if the habit has never been checked in
                penalty_applied = True
        if penalty_applied:
            self.pet.last_penalty_date = today_str  # Update the last penalty date
            print(f"You got a penalty. {self.pet.name}'s current HP: {self.pet.hp}.")

    # Add a habit to the tracker
    def add_habit(self, habit):
        self.habits.append(habit)

    # Remove a habit from the tracker by name
    def remove_habit(self, habit_name):
        self.habits = [habit for habit in self.habits if habit.name != habit_name]

    # Get the list of habits
    def get_habits(self):
        return self.habits

    # Save the habits and pet data to a JSON file
    def save_to_file(self, filename):
        data = {"habits": [habit.to_data() for habit in self.habits], "pet": self.pet.to_data()}
        with open(filename, 'w') as file:
            json.dump(data, file)

    # Load the habits and pet data from a JSON file
    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                self.habits = [Habit(habit_data["name"], habit_data["history"]) for habit_data in data["habits"]]
                if "pet" in data:
                    pet_data = data["pet"]
                    self.pet = Pet(pet_data["name"])
                    self.pet.stage = pet_data["stage"]
                    self.pet.hp = pet_data["hp"]
                    self.pet.xp = pet_data["xp"]
                    self.pet.is_alive = pet_data["is_alive"]
                    self.pet.happiness = pet_data["happiness"]
                    self.pet.last_penalty_date = pet_data["last_penalty_date"]
                else:
                    self.pet = Pet("Nebula")
        except FileNotFoundError:
            print(f"No existing habit data found in {filename}. Starting fresh.")
            self.pet = Pet("Nebula")
class Pet:
    #storing data for the pet
    def __init__(self, name):
        self.name = name
        self.stage = "egg"
        self.happiness = 50
        self.hp = 100
        self.xp = 0
        self.is_alive = True
        self.last_penalty_date = ""

    def add_hp(self, amount):
        self.hp = min(100, self.hp + amount)
        print(f"{self.name} gained {amount} HP. Current HP: {self.hp}.")

    def get_status(self):
        print("\n--- Pet Status ---")
        print(f"Name: {self.name}")
        print(f"Stage: {self.stage}")
        print(f"Happiness: {self.happiness}")
        print(f"HP: {self.hp}")
        print(f"XP: {self.xp}")
        print(f"Is Alive: {self.is_alive}")

        hp_bar = "[" + "🟩" * (self.hp // 10) + " " * (10 - self.hp // 10) + "]"
        print(f"HP Bar: {hp_bar}")

        if not self.is_alive:
            print("Status: DEAD 💀")
        elif self.hp < 30:
            print("Status: CRITICAL 🤒. LOCK IN.")
        else:
            print("Status: ALIVE and HAPPY 😀. Good job!")
    def lose_hp(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            print(f"{self.name} has died.")
            print("Game Over. All habits will be reset. Your actions have consequences.")
        else:
            print(f"{self.name} lost {amount} HP. Current HP: {self.hp}. What are you doing? Lock in.")

    def to_data(self):
        return {
            "name": self.name,
            "stage": self.stage,
            "hp": self.hp,
            "xp": self.xp,
            "is_alive": self.is_alive,
            "happiness": self.happiness,
            "last_penalty_date": self.last_penalty_date
        }

    # Feed the pet to increase happiness
    def feed(self):
        self.happiness = min(100, self.happiness + 10)
        print(f"{self.name} has been fed. Happiness is now {self.happiness}.")

    # Play with the pet to increase happiness
    def play(self):
        self.happiness = min(100, self.happiness + 15)
        print(f"You played with {self.name}. Happiness is now {self.happiness}.")

    # Check the pet's happiness level
    def check_happiness(self):
        print(f"{self.name}'s happiness level is {self.happiness}.")

    # Add experience points to the pet and check for level up
    def add_xp(self, amount):
        self.xp += amount
        print(f"{self.name} gained {amount} XP. Total XP is now {self.xp}.")
        self.check_level_up()

    # Check if the pet has enough XP to level up and evolve
    def check_level_up(self):
        if self.xp >= 100:
            self.xp -= 100
            self.stage = "baby"
            print(f"Congrats, {self.name} has evolved into a baby!")

def main():
    tracker = HabitTracker()
    tracker.load_from_file('habits.json')
    tracker.check_penalies()  # Check for missed habits and apply penalties

    while True:
        print("\nHabit Tracker Menu:")
        print("1. Add Habit")
        print("2. Remove Habit")
        print("3. View Habits")
        print("4. View Habit Stats")
        print("5. Save and Exit")
        print("6. Check-in Habit")
        print("7. View Pet Status")
        print("99. [Debug] Fast_forward by 100 xp")
        print("98. Losing Hp")
        choice = input("Enter your choice: ")

        # Add Habit
        if choice == '1':
            habit_name = input("Enter the name of the habit: ")
            habit = Habit(habit_name)
            tracker.add_habit(habit)
            print(f"Habit '{habit_name}' added.")

        # Remove Habit
        elif choice == '2':
            habit_name = input("Enter the name of the habit to remove: ")
            tracker.remove_habit(habit_name)
            print(f"Habit '{habit_name}' removed.")

        # View Habits
        elif choice == '3':
            habits = tracker.get_habits()
            if habits:
                print("Current Habits:")
                for habit in habits:
                    print(f"- {habit.name}")
            else:
                print("No habits found.")

        # View Habit Stats
        elif choice == '4':
            habits = tracker.get_habits()
            if habits:
                print("Habit Stats:")
                for habit in habits:
                    stats = habit.get_stats()
                    print(f"- {habit.name}:")
                    print(f"  Current Streak: {stats['current_streak']}")
                    print(f"  Longest Streak: {stats['longest_streak']}")
                    print(f"  Completion Rate: {stats['completion_rate']:.2f}%")
            else:
                print("No habits found.")

        # Save and Exit
        elif choice == '5':
            tracker.save_to_file('habits.json')
            print("Habits saved. Exiting.")
            break

        # Check-in Habit
        elif choice == '6':
            habit_name = input("Enter the name of the habit to check-in: ")
            habit = next((h for h in tracker.get_habits() if h.name == habit_name), None)
            if habit:
                today_str = date.today().isoformat()
                if today_str not in habit.history:
                    habit.history.append(today_str)
                    print(f"Checked in for habit '{habit_name}' on {today_str}.")
                    tracker.pet.add_xp(20) # Add XP to your pet for each action
                else:
                    print(f"You have already checked in for habit '{habit_name}' today.")
            else:
                print(f"Habit '{habit_name}' not found.")

        elif choice == '99':
            tracker.pet.add_xp(100)
            print(f"Debug: Added 100 XP to {tracker.pet.name}. Total XP is now {tracker.pet.xp}.")

        elif choice == '98':
            tracker.pet.lose_hp(30)
            print(f"Debug: {tracker.pet.name} lost 30 HP. Current HP is now {tracker.pet.hp}.")

        elif choice == '7':
            tracker.pet.get_status()

if __name__ == "__main__":
    main()