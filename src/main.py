from dataset import Dataset


def main():
    dataset = Dataset.load()

    for (_, dish) in dataset.dishes.items():
        print(dish.title)


if __name__ == "__main__":
    main()
