"""Code to simulate the efficacy of different Shut the box strategies.

Shut the box (https://en.wikipedia.org/wiki/Shut_the_box) is a dice game that I've enjoyed
playing, but I've never been able to reason too well about the best strategy. I decided to
write this code to simulate different strategies to see which perform best.

Strategies examined here:
    - Lowest number first
    - Highest number first
    - Remove exact number if possible, then lowest/highest
    - Random (find all possible solutions, pick one randomly)
    - Fewest numbers possible (e.g., choose [2, 4] over [1, 2, 3]), then lowest/highest
    - Most numbers possible (e.g., choose [1, 2, 3] over [2, 4]), then lowest/highest
    - TODO: What about strategies that change when only certain numbers remain?
    - TODO: Strategy where the risk of ruin for a given set of numbers is calculated in advance,
      then choosing which number to remove is a function of the EV of the subsequent positions

TODO: Split this module up
TODO: Write tests for each strategy
TODO: Show histogram of scores for games for each strategy
TODO: Show graph of average turn/score progression within a game for each strategy
TODO: Show stats of each strategy
    - Mean
    - Standard deviation
    - Median
    - Number of exact wins (score = 0)
    - Average number of turns
"""
from random import choice, randint


class Game:
    """
    Represents a single game of shut the box
    """

    def __init__(self, strategy):
        self.numbers = [num for num in range(1, 10)]
        self.strategy = strategy

    def play(self):
        roll = self.roll()
        self.strategy.choose_numbers(self.numbers, roll)
        while self.numbers and self.strategy.answer:
            # Remove numbers as determined by strategy
            for number in strategy.answer:
                self.numbers.remove(number)

            # Reset strategy
            strategy.answer = []

            # Roll again
            roll = self.roll()

            # Choose number(s) to remove
            self.strategy.choose_numbers(self.numbers, roll)

    def roll(self):
        if self.numbers == [1]:  # If only remaining number is 1, roll 1 die
            return randint(1, 6)
        return randint(1, 6) + randint(1, 6)

    def score(self):
        return sum(self.numbers)


class Strategy:
    """
    Represents the number-removing strategy for a game of STB
    """

    def __init__(self):
        self.answer = []

    def choose_numbers(self, numbers, roll):
        raise NotImplementedError


class LowestFirst(Strategy):
    """
    A strategy wherein we remove the lowest possible numbers first
    """

    def __init__(self):
        super().__init__()

    def choose_numbers(self, numbers, roll):
        if roll == 0:
            return True

        for number in numbers:
            if number > roll:
                return False

            self.answer.append(number)

            new_nums = numbers[:]
            new_nums.remove(number)
            if LowestFirst.choose_numbers(self, new_nums, roll - number):
                return True

            self.answer.remove(number)

        return False


class HighestFirst(Strategy):
    """
    A strategy wherein we remove the highest possible numbers first
    """

    def __init__(self):
        super().__init__()

    def choose_numbers(self, numbers, roll):
        if roll == 0:
            return True

        numbers = sorted(numbers, reverse=True)

        for number in numbers:
            if number > roll:
                continue

            self.answer.append(number)

            new_nums = numbers[:]
            new_nums.remove(number)
            if HighestFirst.choose_numbers(self, new_nums, roll - number):
                return True

            self.answer.remove(number)

        return False


class ExactThenLowest(LowestFirst):
    """
    A strategy wherein we remove the exact sum of the dice, if possible, and then lowest first.
    """

    def __init__(self):
        super().__init__()

    def choose_numbers(self, numbers, roll):
        if roll in numbers:
            self.answer.append(roll)
            return

        super().choose_numbers(numbers, roll)


class ExactThenHighest(HighestFirst):
    """
    A strategy wherein we remove the exact sum of the dice, if possible, and then highest first.
    """

    def __init__(self):
        super().__init__()

    def choose_numbers(self, numbers, roll):
        if roll in numbers:
            self.answer.append(roll)
            return

        super().choose_numbers(numbers, roll)


class Random(Strategy):
    """
    A strategy wherein we calculate all possible solutions and then pick one randomly.
    """

    def __init__(self):
        super().__init__()

    def choose_numbers(self, numbers, roll):
        # Calculate all possible solutions
        solutions = find_all_solutions(numbers, roll)

        # Pick one randomly
        if solutions:
            self.answer = choice(solutions)


# TODO: When reorganizing this module into many, put this into a common file
def find_all_solutions(numbers, target):
    solutions = []

    # DFS approach
    def recurse(numbers, target, subsolution):
        if target == 0:
            solutions.append(subsolution)

        if target < 0:
            return

        for index, number in enumerate(numbers):
            recurse(numbers[index + 1 :], target - number, [*subsolution, number])

    recurse(numbers, target, [])

    return solutions


class SolutionLength(Strategy):
    """
    A base class for strategies that aim to use solutions with specific lengths

    Because sorted() yields in increasing order (unless otherwise specified),
    we need to define our secondary_strategy's in a way that gives the best solution
    the lowest value.
      - To get solution with lowest number: min(x)
      - To get solution with highest number: lambda x: -1 * max(x)
    In reality, this level of modularity isn't required for just min and max, because
    any solution that contains the minimum number will also contain the maximum number (proof?).

    However, if we want to, say, use a solution that contains a number which is as close to 7
    as possible, then this is useful.
    """

    def __init__(self, secondary_strategy):
        super().__init__()

        # To break ties, we'll use the secondary_strategy function
        self.secondary_strategy = secondary_strategy

    def choose_numbers(self, numbers, roll):
        raise NotImplementedError


class FewestNumbers(SolutionLength):
    """
    A strategy wherein we choose the solution with the fewest possible numbers
    """

    def __init__(self, secondary_strategy):
        super().__init__(secondary_strategy)

    def choose_numbers(self, numbers, roll):
        solutions = find_all_solutions(numbers, roll)
        if solutions:
            # Only consider solutions of the shortest length
            shortest_solution_length = min(len(solution) for solution in solutions)

            # Find the solution with the lowest/highest number
            self.answer = sorted(
                [solution for solution in solutions if len(solution) == shortest_solution_length],
                key=lambda sol: self.secondary_strategy(sol),
            )[0]


class MostNumbers(SolutionLength):
    """
    A strategy wherein we choose the solution with the most possible numbers
    """

    def __init__(self, secondary_strategy):
        super().__init__(secondary_strategy)

    def choose_numbers(self, numbers, roll):
        solutions = find_all_solutions(numbers, roll)
        if solutions:
            # Only consider solutions of the longest length
            shortest_solution_length = max(len(solution) for solution in solutions)

            # Find the solution with the lowest/highest number
            self.answer = sorted(
                [solution for solution in solutions if len(solution) == shortest_solution_length],
                key=lambda sol: self.secondary_strategy(sol),
            )[0]


if __name__ == "__main__":
    # strategy = LowestFirst()
    # strategy = HighestFirst()
    # strategy = ExactThenLowest()
    # strategy = ExactThenHighest()
    # strategy = Random()
    # strategy = FewestNumbers(secondary_strategy=min)  # If tied, use solution with lowest number
    # strategy = FewestNumbers(
    #     secondary_strategy=lambda x: -1 * max(x)
    # )  # If tied, use solution with highest number
    strategy = MostNumbers(secondary_strategy=min)

    scores = []
    for i in range(1000):
        game = Game(strategy)
        game.play()
        scores.append(game.score())

    print("Scores:", scores)
    print("Average:", sum(scores) / len(scores))
