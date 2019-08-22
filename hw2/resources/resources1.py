# variables are the applicants
# domain is { spla, lahsa, denied }
# algorithm
# 1. loop through applicants and set the possible values based on constraints.
# 2. keep track of list of candidates that will maximize the efficiency for spla
# 3. loop through list and V

import math

# classes


class SPLA:
    def __init__(self, num_spaces):
        self.space = {
            "monday": 0,
            "tuesday": 0,
            "wednesday": 0,
            "thursday": 0,
            "friday": 0,
            "saturday": 0,
            "sunday": 0}
        self.num_spaces = num_spaces
        self.efficiency = 0
        self.possible_applicants = set()

    def num_spaces(self):
        return self.num_spaces

    def fit(self, applicant):
        for day_needed in applicant.days_needed:
            if self.space[day_needed] >= self.num_spaces:
                return False
        return True

    def add_applicant(self, applicant):
        for day_needed in applicant.days_needed:
            self.space[day_needed] += 1
            self.efficiency += 1

    def remove_applicant(self, applicant):
        for day_needed in applicant.days_needed:
            self.space[day_needed] -= 1
            self.efficiency -= 1


class LAHSA:
    def __init__(self, num_beds):
        self.taken_beds = {
            "monday": 0,
            "tuesday": 0,
            "wednesday": 0,
            "thursday": 0,
            "friday": 0,
            "saturday": 0,
            "sunday": 0}
        self.num_beds = num_beds
        self.efficiency = 0
        self.possible_applicants = set()

    def num_beds(self):
        return self.num_beds

    def fit(self, applicant):
        for day_needed in applicant.days_needed:
            if self.taken_beds[day_needed] >= self.num_beds:
                return False
        return True

    def add_applicant(self, applicant):
        for day_needed in applicant.days_needed:
            self.taken_beds[day_needed] += 1
            self.efficiency += 1

    def remove_applicant(self, applicant):
        for day_needed in applicant.days_needed:
            self.taken_beds[day_needed] -= 1
            self.efficiency -= 1


class Homeless:
    def __init__(self,
                 ID,
                 gender,
                 age,
                 pet,
                 medical_condition,
                 car,
                 driver_lisence,
                 shelter_needing_day):
        self.ID = ID
        self.gender = gender
        self.pet = pet
        self.age = age
        self.medical_condition = medical_condition
        self.car = car
        self.driver_lisence = driver_lisence
        self.days_needed = []
        self.set_shelter_needing_day(shelter_needing_day)
        self.possible_programs = []
        self.set_possible_programs()

    def __repr__(self):
        return self.ID

    def set_possible_programs(self):
        self.possible_programs.append("None")
        if self.car == "Y" and self.driver_lisence == "Y" and self.medical_condition == "N":
            self.possible_programs.append("spla")
        if self.gender == "F" and self.age > 17 and self.pet == "N":
            self.possible_programs.append("lahsa")

    def set_shelter_needing_day(self, days_string):
        if int(days_string[0]) == 1:
            self.days_needed.append("monday")
        if int(days_string[1]) == 1:
            self.days_needed.append("tuesday")
        if int(days_string[2]) == 1:
            self.days_needed.append("wednesday")
        if int(days_string[3]) == 1:
            self.days_needed.append("thursday")
        if int(days_string[4]) == 1:
            self.days_needed.append("friday")
        if int(days_string[5]) == 1:
            self.days_needed.append("saturday")
        if int(days_string[6]) == 1:
            self.days_needed.append("sunday")


# methods

def next_spla_applicant():
    input_file = open("input2.txt")
    data = input_file.readlines()
    data = [line.strip() for line in data]
    # get num beds, num spaces
    num_beds = int(data[0])
    num_spaces = int(data[1])

    # create programs
    spla = SPLA(num_spaces)
    lahsa = LAHSA(num_beds)

    # get already chosen ID's
    num_lahsa_chosen = int(data[2])
    lahsa_chosen = set()

    current_index = 3
    for iteration in range(0, num_lahsa_chosen):
        lahsa_chosen.add(data[current_index])
        current_index += 1

    num_spla_chosen = int(data[current_index])
    spla_chosen = set()
    current_index += 1

    for iteration in range(0, num_spla_chosen):
        spla_chosen.add(data[current_index])
        current_index += 1

    # create applicants
    applicants = []
    num_total_applicants = int(data[current_index])
    current_index += 1
    for iteration in range(0, num_total_applicants):
        applicants.append(create_applicant(spla,  spla_chosen, lahsa, lahsa_chosen,  data[current_index]))
        current_index += 1

    # do minimax algorithm
    accepted_ID = next_accepted(spla, spla_chosen, lahsa, lahsa_chosen)
    output_file = open("output.txt", "w")
    output_file.write(accepted_ID + "\n")
    output_file.close()


def next_accepted(spla, spla_chosen, lahsa, lahsa_chosen):
    # If there is more spla chosen then we need to have lahsa choose to catch up.
    while len(spla_chosen) < len(lahsa_chosen) and len(lahsa.possible_applicants) > 0:
        applicant = next_lahsa_accepted(spla, lahsa)
        lahsa_chosen.add(applicant.ID)
        lahsa.add_applicant(applicant)
        lahsa.possible_applicants.remove(applicant)
        spla.possible_applicants.remove(applicant)
    return next_spla_accepted(spla, lahsa)


def next_lahsa_accepted(spla, lahsa):
    max_efficiency = -1
    best_applicant = None
    for applicant in lahsa.possible_applicants.copy():
        # remove this applicant from lahsa and maybe from spla
        lahsa.possible_applicants.remove(applicant)
        removed_from_spla = False
        added_to_lahsa = False
        if lahsa.fit(applicant):
            lahsa.add_applicant(applicant)
            added_to_lahsa = True
            if applicant in spla.possible_applicants:
                spla.possible_applicants.remove(applicant)
                removed_from_spla = True
        spla_efficiency, lahsa_efficiency = spla_turn_max(spla, lahsa)
        if (lahsa_efficiency > max_efficiency or
                (lahsa_efficiency == max_efficiency and applicant.ID < best_applicant.ID)):
            max_efficiency = lahsa_efficiency
            best_applicant = applicant
        lahsa.possible_applicants.add(applicant)
        if added_to_lahsa:
            lahsa.remove_applicant(applicant)
        if removed_from_spla:
            spla.possible_applicants.add(applicant)
    return best_applicant


def next_spla_accepted(spla, lahsa):
    max_efficiency = -1
    best_applicant = None
    for applicant in spla.possible_applicants.copy():
        # remove this applicant from SPLA and maybe from LAHSA
        spla.possible_applicants.remove(applicant)
        removed_from_lahsa = False
        added_to_spla = False
        if spla.fit(applicant):
            spla.add_applicant(applicant)
            added_to_spla = True
            if applicant in lahsa.possible_applicants:
                lahsa.possible_applicants.remove(applicant)
                removed_from_lahsa = True
        spla_efficiency, lahsa_efficiency = lahsa_turn_max(spla, lahsa)
        if (spla_efficiency > max_efficiency or
                (spla_efficiency == max_efficiency and applicant.ID < best_applicant.ID)):
            max_efficiency = spla_efficiency
            best_applicant = applicant
        spla.possible_applicants.add(applicant)
        if added_to_spla:
            spla.remove_applicant(applicant)
        if removed_from_lahsa:
            lahsa.possible_applicants.add(applicant)
    return best_applicant.ID


def lahsa_turn_max(spla, lahsa):
    if len(lahsa.possible_applicants) == 0 and len(spla.possible_applicants) == 0:
        return spla.efficiency, lahsa.efficiency
    elif len(lahsa.possible_applicants) == 0:
        return spla_turn_max(spla, lahsa)

    best_lahsa_efficiency = -1
    associated_spla_efficiency = -1
    for applicant in lahsa.possible_applicants.copy():
        lahsa.possible_applicants.remove(applicant)
        removed_from_spla = False
        added_to_lahsa = False
        if lahsa.fit(applicant):
            lahsa.add_applicant(applicant)
            added_to_lahsa = True
            if applicant in spla.possible_applicants:
                spla.possible_applicants.remove(applicant)
                removed_from_spla = True
        spla_efficiency, lahsa_efficiency = spla_turn_max(spla, lahsa)
        if best_lahsa_efficiency < lahsa_efficiency:
            best_lahsa_efficiency = lahsa_efficiency
            associated_spla_efficiency = spla_efficiency
        lahsa.possible_applicants.add(applicant)
        if added_to_lahsa:
            lahsa.remove_applicant(applicant)
        if removed_from_spla:
            spla.possible_applicants.add(applicant)
    return associated_spla_efficiency, best_lahsa_efficiency


def spla_turn_max(spla, lahsa):
    if len(spla.possible_applicants) == 0 and len(lahsa.possible_applicants) == 0:
        return spla.efficiency, lahsa.efficiency
    elif len(spla.possible_applicants) == 0:
        return lahsa_turn_max(spla, lahsa)

    best_spla_efficiency = -1
    associated_lahsa_efficiency = -1
    for applicant in spla.possible_applicants.copy():
        spla.possible_applicants.remove(applicant)
        removed_from_lahsa = False
        added_to_spla = False
        if spla.fit(applicant):
            spla.add_applicant(applicant)
            added_to_spla = True
            if applicant in lahsa.possible_applicants:
                lahsa.possible_applicants.remove(applicant)
                removed_from_lahsa = True
        spla_efficiency, lahsa_efficiency = lahsa_turn_max(spla, lahsa)
        if best_spla_efficiency < spla_efficiency:
            best_spla_efficiency = spla_efficiency
            associated_lahsa_efficiency = lahsa_efficiency
        spla.possible_applicants.add(applicant)
        if added_to_spla:
            spla.remove_applicant(applicant)
        if removed_from_lahsa:
            lahsa.possible_applicants.add(applicant)
    return best_spla_efficiency, associated_lahsa_efficiency


def create_applicant(spla, spla_chosen, lahsa, lahsa_chosen, applicant_string):
    ID = applicant_string[0:5]
    gender = applicant_string[5]
    age = int(applicant_string[6:9])
    pet = applicant_string[9]
    medical_condition = applicant_string[10]
    car = applicant_string[11]
    driver_lisence = applicant_string[12]
    shelter_needing_day = applicant_string[13:]

    applicant = Homeless(
            ID,
            gender,
            age,
            pet,
            medical_condition,
            car,
            driver_lisence,
            shelter_needing_day)
    # if the applicant has been chosen, add them to the correct program.
    if applicant.ID in spla_chosen:
        spla.add_applicant(applicant)
        return applicant
    elif applicant.ID in lahsa_chosen:
        lahsa.add_applicant(applicant)
        return applicant

    if "spla" in applicant.possible_programs:
        spla.possible_applicants.add(applicant)
    if "lahsa" in applicant.possible_programs:
        lahsa.possible_applicants.add(applicant)
    return applicant


if __name__ == "__main__":
    next_spla_applicant()