from dataset import Dataset
from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick

style.use("ggplot")


def main():
    dataset = Dataset.load()

    # for (_, dish) in dataset.dishes.items():
    #     print(dish.title)

    days = dataset.past_days()

    # labels = list(map(lambda day: [day.cornflakes], days))

    def get_mean_co2e(day):
        dishes = list(map(lambda dish: dataset.dishes.get(dish), day.dishes))

        return sum(map(lambda dish: dish.co2e, dishes)) / len(dishes)

    x = np.array(list(map(get_mean_co2e, days)))
    cornflakes = np.array(list(map(lambda day: day.cornflakes, days)))
    lingon = np.array(list(map(lambda day: day.lingon, days)))

    fig, ax = plt.subplots()  # Create a figure containing a single axes.

    ax.set_xlabel("kg CO2e per portion")
    ax.set_ylabel("Chans")

    def scatter_with_linear_regression(y, label, marker, color):
        ax.scatter(x, y, label=label, marker=marker, c=color)
        m, b = np.polyfit(x, y, 1)
        plt.plot(x, m * x + b, c=color, linestyle=":", linewidth=1, alpha=0.5)

    scatter_with_linear_regression(cornflakes, "Cornflakes", "s", "b")
    scatter_with_linear_regression(lingon, "Lingon", "x", "r")

    ax.yaxis.set_major_formatter(
        mtick.FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

    plt.legend()

    plt.savefig("plot.png")


if __name__ == "__main__":
    main()
