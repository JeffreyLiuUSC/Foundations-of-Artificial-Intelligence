import numpy as np

import math


class Car:

    def set_start_location(self, location_tuple):
        self.start_location = location_tuple

    def set_end_location(self, location_tuple):
        self.end_location = location_tuple


def average_money_earned():
    input_file = open("input1.txt")

    content = input_file.readlines()

    content = [line.strip() for line in content]

    grid_size = int(content[0])

    num_cars = int(content[1])

    num_obstacles = int(content[2])

    obstacles = set()

    for offset in range(0, num_obstacles):
        obstacle_string = content[3 + offset]

        obstacle_list = obstacle_string.split(",")

        obstacles.add((int(obstacle_list[0]), int(obstacle_list[1])))

    current_index = 3 + num_obstacles

    cars_dict = {}

    for offset in range(0, num_cars):
        car = Car()

        start_string = content[current_index + offset]

        start_list = start_string.split(",")

        car.set_start_location((int(start_list[0]), int(start_list[1])))

        cars_dict[offset] = car

    current_index += num_cars

    for offset in range(0, num_cars):
        car = cars_dict[offset]

        end_string = content[current_index + offset]

        end_list = end_string.split(",")

        car.set_end_location((int(end_list[0]), int(end_list[1])))

    get_average_money_earned_per_car(cars_dict, num_cars, grid_size, obstacles)


def get_average_money_earned_per_car(cars_dict, num_cars, grid_size, obstacles):

    for index in range(0, num_cars):
        car = cars_dict[index]

        average_money = get_average_money(car, grid_size, obstacles)

        output_file = open("output.txt", "a")

        output_file.write(str(average_money) + "\n")

        output_file.close()


def get_average_money(car, grid_size, obstacles):

    total = 0.0

    expected_utility_grid = get_expected_utility_grid(car, grid_size, obstacles)

    policy_grid = create_policy_grid(expected_utility_grid, grid_size)

    for seed in range(1, 11):
        total += money_earned(car, grid_size, obstacles, policy_grid, seed)

    return int(math.floor(total / 10.0))


def money_earned(car, grid_size, obstacles, policy_grid, seed):

    current_location = car.start_location

    if current_location == car.end_location:
        return 99.0

    money = 0.0

    np.random.seed(seed)

    swerve = np.random.random_sample(1000000)

    k = 0

    while current_location != car.end_location:

        desired_move = policy_grid[current_location[0]][current_location[1]]

        actual_move = randomized_move(desired_move, swerve, k)

        current_location = next_location(grid_size, current_location, actual_move)

        money -= 1.0

        if current_location in obstacles:
            money -= 100.0

        k += 1

    money += 100.0

    return money


def turn_left(move):
    if move == "N":

        return "W"

    elif move == "S":

        return "E"

    elif move == "E":

        return "N"

    elif move == "W":

        return "S"


def turn_right(move):
    if move == "N":

        return "E"

    elif move == "S":

        return "W"

    elif move == "E":

        return "S"

    elif move == "W":

        return "N"


def randomized_move(desired_move, swerve, k):

    swerve_round = swerve[k]

    if swerve_round > 0.7:

        if swerve_round > 0.8:

            if swerve_round > 0.9:

                val = turn_left(turn_left(desired_move))

                return val

            else:

                val = turn_left(desired_move)

                return val

        else:

            return turn_right(desired_move)

    return desired_move


def next_location(grid_size, current_location, actual_move):
    move_delta = move_delta_from_move(actual_move)

    next_location = (current_location[0] + move_delta[0], current_location[1] + move_delta[1])

    if valid_location(next_location, grid_size):

        return next_location

    else:

        return current_location


def valid_location(location, grid_size):
    if location[0] < 0 or location[0] >= grid_size:
        return False

    if location[1] < 0 or location[1] >= grid_size:
        return False

    return True


def move_delta_from_move(actual_move):

    if actual_move == "N":

        return (0, 1)

    elif actual_move == "S":

        return (0, -1)

    elif actual_move == "W":

        return (-1, 0)

    else:

        return (1, 0)


def create_policy_grid(expected_utility_grid, grid_size):
    policy_grid = []

    for i in range(0, grid_size):
        column = [0] * grid_size

        policy_grid.append(column)

    for col in range(0, grid_size):

        for row in range(0, grid_size):
            policy_grid[col][row] = best_move(col, row, expected_utility_grid, grid_size)

    return policy_grid


def best_move(col, row, utility_grid, grid_size):

    preference = ["W", "E", "S", "N"]

    best_move = ""

    max_expected_utility = None

    north_utility = get_north_utility(col, row, utility_grid, grid_size)

    west_utility = get_west_utility(col, row, utility_grid, grid_size)

    south_utility = get_south_utility(col, row, utility_grid, grid_size)

    east_utility = get_east_utility(col, row, utility_grid, grid_size)

    for direction in preference:

        utility = None

        if direction == "N":

            utility = 0.7 * north_utility + 0.1 * (west_utility + east_utility + south_utility)

        elif direction == "S":

            utility = 0.7 * south_utility + 0.1 * (west_utility + east_utility + north_utility)

        elif direction == "W":

            utility = 0.7 * west_utility + 0.1 * (south_utility + east_utility + north_utility)

        else:

            utility = 0.7 * east_utility + 0.1 * (south_utility + west_utility + north_utility)

        if max_expected_utility == None or utility > max_expected_utility:

            max_expected_utility = utility

            best_move = direction

        elif max_expected_utility == utility:

            best_move = direction

    return best_move


def get_expected_utility_grid(car, grid_size, obstacles):
    utility_grid = []

    for i in range(0, grid_size):
        column = [-1.0] * grid_size;

        utility_grid.append(column)

    for location in obstacles:
        utility_grid[location[0]][location[1]] -= 100.0

    end_col = car.end_location[0]

    end_row = car.end_location[1]

    utility_grid[end_col][end_row] += 100.0

    return value_iterate(car, utility_grid, obstacles)


def value_iterate(car, utility_grid, obstacles):
    grid_size = len(utility_grid[0])

    while True:

        temp_grid = []

        for i in range(0, grid_size):
            column = [0.0] * grid_size;

            temp_grid.append(column)

        max_diff = 0.0

        for col in range(0, grid_size):

            for row in range(0, grid_size):

                if (col, row) == car.end_location:
                    temp_grid[col][row] = 99.0

                    continue

                max_expected_utility = get_max_expected_utility(col, row, utility_grid)

                reward = get_reward((col, row), car, obstacles)

                updated_utility = reward + 0.90 * max_expected_utility

                temp_grid[col][row] = updated_utility

                current_diff = abs(updated_utility - utility_grid[col][row])

                if current_diff > max_diff:
                    max_diff = current_diff

        if max_diff < 0.01:
            break

        utility_grid = temp_grid

    return utility_grid


def get_max_expected_utility(col, row, utility_grid):
    grid_size = len(utility_grid[0])

    north_utility = get_north_utility(col, row, utility_grid, grid_size)

    west_utility = get_west_utility(col, row, utility_grid, grid_size)

    south_utility = get_south_utility(col, row, utility_grid, grid_size)

    east_utility = get_east_utility(col, row, utility_grid, grid_size)

    expected_north = (0.7 * north_utility) + (0.1 * west_utility) + (0.1 * east_utility) + (0.1 * south_utility)

    expected_south = (0.7 * south_utility) + (0.1 * west_utility) + (0.1 * east_utility) + (0.1 * north_utility)

    expected_west = (0.7 * west_utility) + (0.1 * south_utility) + (0.1 * east_utility) + (0.1 * north_utility)

    expected_east = (0.7 * east_utility) + (0.1 * south_utility) + (0.1 * west_utility) + (0.1 * north_utility)

    return max([expected_north, expected_south, expected_west, expected_east])


def get_reward(location, car, obstacles):
    if location in obstacles:

        return -101.0

    elif location == car.end_location:

        return 99.0

    else:

        return -1.0


def get_north_utility(col, row, utility_grid, grid_size):
    if valid_location((col, row + 1), grid_size):

        return utility_grid[col][row + 1]

    else:

        return utility_grid[col][row]


def get_south_utility(col, row, utility_grid, grid_size):
    if valid_location((col, row - 1), grid_size):

        return utility_grid[col][row - 1]

    else:

        return utility_grid[col][row]


def get_east_utility(col, row, utility_grid, grid_size):
    if valid_location((col + 1, row), grid_size):

        return utility_grid[col + 1][row]

    else:

        return utility_grid[col][row]


def get_west_utility(col, row, utility_grid, grid_size):
    if valid_location((col - 1, row), grid_size):

        return utility_grid[col - 1][row]

    else:

        return utility_grid[col][row]


if __name__ == "__main__":
    average_money_earned()

