from typing import List, Dict
import datetime
import requests
import json
import csv


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
    def from_api(data):
        dish_ids = list(map(lambda dish: dish["id"], data["dishes"]))
        date = datetime.datetime.strptime(data["date"], "%Y-%m-%dT%H:%M:%S%z")

        return Day(dish_ids, date)

    @staticmethod
    def fetch_all():
        r = requests.get("https://potato.södermalmsskolan.com/menu")

        print("Found {} days!".format(len(r.json())))

        return list(map(Day.from_api, r.json()))


class Dataset:
    days: List[Day] = []
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

def main():
    dataset = Dataset.download()

    dataset.save()


if __name__ == "__main__":
    main()
