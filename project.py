import json
from datetime import date, timedelta


class Habit:
    def __init__(self, name, history=None, created_on=None):
        self.name = name.strip()
        self.history = history if history is not None else []
        self.created_on = created_on or date.today().isoformat()

    def to_data(self):
        return {
            "name": self.name,
            "history": self.history,
            "created_on": self.created_on,
        }

    def get_stats(self):
        # Ignore duplicate dates so they don't inflate streaks or completion.
        dates = sorted({
            date.fromisoformat(day)
            for day in self.history
            if date.fromisoformat(day) <= date.today()
        })

        longest_streak = 0
        streak = 0
        previous = None

        for day in dates:
            if previous is not None and (day - previous).days == 1:
                streak += 1
            else:
                streak = 1

            longest_streak = max(longest_streak, streak)
            previous = day

        today = date.today()
        current_streak = 0

        if dates and dates[-1] in (today, today - timedelta(days=1)):
            expected = dates[-1]
            for day in reversed(dates):
                if day == expected:
                    current_streak += 1
                    expected -= timedelta(days=1)
                else:
                    break

        if dates:
            start = date.fromisoformat(self.created_on)
            total_days = max(1, (today - start).days + 1)
            completion_rate = len(dates) / total_days * 100
        else:
            completion_rate = 0

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_rate": min(completion_rate, 100),
        }


class Pet:
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
        self.hp = max(0, self.hp - amount)

        if self.hp == 0:
            self.is_alive = False
            print(f"{self.name} has died.")
            print("Game Over. All habits will be reset. Your actions have consequences.")
        else:
            print(f"{self.name} lost {amount} HP. Current HP: {self.hp}.")

    def to_data(self):
        return {
            "name": self.name,
            "stage": self.stage,
            "hp": self.hp,
            "xp": self.xp,
            "is_alive": self.is_alive,
            "happiness": self.happiness,
            "last_penalty_date": self.last_penalty_date,
        }

    def feed(self):
        self.happiness = min(100, self.happiness + 10)
        print(f"{self.name} has been fed. Happiness is now {self.happiness}.")

    def play(self):
        self.happiness = min(100, self.happiness + 15)
        print(f"You played with {self.name}. Happiness is now {self.happiness}.")

    def check_happiness(self):
        print(f"{self.name}'s happiness level is {self.happiness}.")

    def add_xp(self, amount):
        if not self.is_alive:
            print(f"{self.name} can't gain XP because it has died.")
            return

        self.xp += amount
        print(f"{self.name} gained {amount} XP. Total XP is now {self.xp}.")
        self.check_level_up()

    def check_level_up(self):
        while self.xp >= 100:
            self.xp -= 100

            if self.stage == "egg":
                self.stage = "baby"
                print(f"Congrats, {self.name} has evolved into a baby!")
            else:
                print(f"{self.name} earned 100 XP!")


class HabitTracker:
    def __init__(self):
        self.habits = []
        self.pet = Pet("Nebula")

    def check_penalties(self):
        today = date.today()
        today_str = today.isoformat()

        if self.pet.last_penalty_date == today_str:
            return

        penalty_applied = False

        for habit in self.habits:
            if habit.history:
                last_checkin = max(date.fromisoformat(day) for day in habit.history)
                overdue = (today - last_checkin).days > 1
            else:
                created = date.fromisoformat(habit.created_on)
                overdue = (today - created).days > 1

            if overdue and self.pet.is_alive:
                self.pet.lose_hp(20)
                penalty_applied = True
                print(f"Penalty applied for habit '{habit.name}'.")

        # Record that today's penalty check has happened, even if no penalty applied.
        self.pet.last_penalty_date = today_str

        if penalty_applied:
            print(f"{self.pet.name}'s current HP: {self.pet.hp}.")

    def add_habit(self, habit):
        if not habit.name:
            print("Habit name can't be blank.")
            return False

        if any(existing.name.casefold() == habit.name.casefold()
               for existing in self.habits):
            print("A habit with that name already exists.")
            return False

        self.habits.append(habit)
        return True

    def remove_habit(self, habit_name):
        before = len(self.habits)
        self.habits = [
            habit for habit in self.habits
            if habit.name.casefold() != habit_name.strip().casefold()
        ]
        return len(self.habits) < before

    def get_habits(self):
        return self.habits

    def save_to_file(self, filename):
        data = {
            "habits": [habit.to_data() for habit in self.habits],
            "pet": self.pet.to_data(),
        }

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def load_from_file(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.habits = []
            for habit_data in data.get("habits", []):
                name = habit_data.get("name", "").strip()
                if not name:
                    continue

                history = habit_data.get("history", [])
                # Validate dates and discard duplicates.
                valid_history = sorted({
                    date.fromisoformat(day).isoformat()
                    for day in history
                })

                created_on = habit_data.get("created_on")
                if created_on:
                    created_on = date.fromisoformat(created_on).isoformat()

                self.habits.append(Habit(name, valid_history, created_on))

            pet_data = data.get("pet")
            if pet_data:
                self.pet = Pet(pet_data.get("name", "Nebula"))
                self.pet.stage = pet_data.get("stage", "egg")
                self.pet.hp = max(0, min(100, int(pet_data.get("hp", 100))))
                self.pet.xp = max(0, int(pet_data.get("xp", 0)))
                self.pet.is_alive = bool(pet_data.get("is_alive", True))
                self.pet.happiness = max(
                    0, min(100, int(pet_data.get("happiness", 50)))
                )
                self.pet.last_penalty_date = pet_data.get(
                    "last_penalty_date", ""
                )
            else:
                self.pet = Pet("Nebula")

        except FileNotFoundError:
            print(f"No existing habit data found in {filename}. Starting fresh.")
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            print(f"Could not load {filename}: {error}")
            print("Starting with fresh data.")
            self.habits = []
            self.pet = Pet("Nebula")


def main():
    tracker = HabitTracker()
    tracker.load_from_file("habits.json")
    tracker.check_penalties()

    while True:
        print("\nHabit Tracker Menu:")
        print("1. Add Habit")
        print("2. Remove Habit")
        print("3. View Habits")
        print("4. View Habit Stats")
        print("5. Save and Exit")
        print("6. Check-in Habit")
        print("7. View Pet Status")
        print("8. Feed Pet")
        print("9. Play with Pet")
        print("99. [Debug] Fast-forward by 100 XP")
        print("98. [Debug] Lose HP")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            habit_name = input("Enter the name of the habit: ")
            if tracker.add_habit(Habit(habit_name)):
                print(f"Habit '{habit_name.strip()}' added.")

        elif choice == "2":
            habit_name = input("Enter the name of the habit to remove: ")
            if tracker.remove_habit(habit_name):
                print(f"Habit '{habit_name.strip()}' removed.")
            else:
                print(f"Habit '{habit_name.strip()}' not found.")

        elif choice == "3":
            habits = tracker.get_habits()
            if habits:
                print("Current Habits:")
                for habit in habits:
                    print(f"- {habit.name}")
            else:
                print("No habits found.")

        elif choice == "4":
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

        elif choice == "5":
            tracker.save_to_file("habits.json")
            print("Habits saved. Exiting.")
            break

        elif choice == "6":
            habit_name = input("Enter the name of the habit to check in: ").strip()
            habit = next(
                (h for h in tracker.get_habits()
                 if h.name.casefold() == habit_name.casefold()),
                None,
            )

            if habit is None:
                print(f"Habit '{habit_name}' not found.")
            elif not tracker.pet.is_alive:
                print(f"{tracker.pet.name} has died. Check-ins won't earn XP.")
            else:
                today_str = date.today().isoformat()
                if today_str in habit.history:
                    print(f"You already checked in for '{habit.name}' today.")
                else:
                    habit.history.append(today_str)
                    tracker.pet.add_xp(20)
                    print(f"Checked in for '{habit.name}' on {today_str}.")

        elif choice == "7":
            tracker.pet.get_status()

        elif choice == "8":
            tracker.pet.feed()

        elif choice == "9":
            tracker.pet.play()

        elif choice == "99":
            tracker.pet.add_xp(100)

        elif choice == "98":
            tracker.pet.lose_hp(30)

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()