from typing import List, Dict
import datetime
import requests
import json
import csv
from dateutil.tz import tzutc, tzlocal


class Dish:
    title: str
    co2e: float
    id: str

    def __init__(self, title: str, co2e: float, id: str):
        self.title = title
        self.co2e = co2e
        self.id = id

    @staticmethod
    def from_api(data):
        r = requests.get(data["co2e_url"])

        print("Fetching CO2e emissions for `{}`".format(data["title"]))

        co2e = r.json()["kgCo2E"]

        return Dish(data["title"], co2e, data["id"])

    @staticmethod
    def fetch_all():
        r = requests.get("https://potato.södermalmsskolan.com/dishes")

        print("Found {} dishes!".format(len(r.json())))

        return list(map(Dish.from_api, r.json()))

    @staticmethod
    def parse(data):
        return Dish(data["title"], data["co2e"], data["id"])


class Day:
    dishes: List[str] = []
    datetime: datetime.datetime
    cornflakes: float
    lingon: float

    def __init__(self, dishes: List[str], date: datetime.datetime, cornflakes: float = 0.0, lingon: float = 0.0):
        self.dishes = dishes
        self.date = date
        self.cornflakes = cornflakes
        self.lingon = lingon

    @property
    def weekday(self):
        return self.date.weekday()

    def serialize(self):
        return {
            "dishes": self.dishes,
            "date": self.date.strftime("%Y-%m-%d"),
            "cornflakes": self.cornflakes,
            "lingon": self.lingon
        }

    @staticmethod
    def parse(data):
        return Day(data["dishes"], datetime.datetime.strptime(
            data["date"], "%Y-%m-%d"), data["cornflakes"], data["lingon"])

    @staticmethod
    def from_api(data):
        dish_ids = list(map(lambda dish: dish["id"], data["dishes"]))

        date = datetime.datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S%z").astimezone(tzlocal())

        return Day(dish_ids, date)

    @staticmethod
    def fetch_all():
        r = requests.get("https://potato.södermalmsskolan.com/menu")

        print("Found {} days!".format(len(r.json())))

        return list(map(Day.from_api, r.json()))


class Dataset:
    days: List[Day]
    dishes: Dict[str, Dish]

    def __init__(self, days: List[Day], dishes: List[Dish]):
        self.days = days
        self.dishes = dict(zip(map(lambda dish: dish.id, dishes), dishes))

    @staticmethod
    def download():
        days = Day.fetch_all()
        dishes = Dish.fetch_all()

        return Dataset(days, dishes)

    def save_dishes(self):
        file = "dishes.json"

        with open(file, "w") as f:
            data = dict((k, v.__dict__) for (k, v) in self.dishes.items())

            json.dump(data, f, indent=4)

            print("Saved dishes to {}".format(file))

    def save_days(self):
        file = "days.json"

        with open(file, "w") as f:
            data = [day.serialize() for day in self.days]

            json.dump(data, f, indent=4)

            print("Saved days to {}".format(file))

    def save(self):
        self.save_dishes()
        self.save_days()

    @staticmethod
    def load_dishes():
        with open("dishes.json") as f:
            data = json.load(f)

            return list(Dish.parse(dish) for (_, dish) in data.items())

    @staticmethod
    def load_days():
        with open("days.json") as f:
            data = json.load(f)

            return list(Day.parse(day) for day in data)

    @staticmethod
    def load():
        dishes = Dataset.load_dishes()
        days = Dataset.load_days()

        return Dataset(days, dishes)

    def past_days(self):
        now = datetime.datetime.now()

        return list(filter(lambda day: now > day.date, self.days))


def main():
    dataset = Dataset.download()

    dataset.save()


if __name__ == "__main__":
    main()
