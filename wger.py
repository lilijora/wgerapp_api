import requests
import random
import os
import toml


class Api:
    base_url = 'https://wger.de/api/v2/'

    def __init__(self, auth_token, username, password):
        self.auth_token = auth_token
        self.username = username
        self.password = password
        self.workouts = []

    def __repr__(self):
        return f"User: {self.username}"

#BASIC FUNCTIONS
    def user_login(self):
        """
        This function do the login procedure for the application
        :return: True,the request body - if the login is successful
                 False,the request body - if the login couldn't be performed
        """

        login_url = 'https://wger.de/en/user/login'

        user = requests.get(login_url)
        xsrftoken = user.cookies.get('csrftoken')
        session_id = user.cookies.get('sessionid')
        cookie_full = f"csrftoken={xsrftoken}; sessionid={session_id}"

        header = {'Authorization': self.auth_token,
                  'X-CSRFToken': xsrftoken,
                  'Cookie': cookie_full,
                  'Referer': login_url
                  }

        login_data = {'username': self.username,
                      'password': self.password,
                      'submit': 'Login'
                      }
        req = requests.post(url=login_url, data=login_data, headers=header)
        if req.status_code in (200, 201):
            return True, req
        return False, req

    def toml_to_dict(self, toml_file):
        """
        The function converts a TOML file to a dictionary
        :param toml_file: The file containing the TOML
        :return: The dictionary containing the data from the TOML file
        """
        with open(toml_file) as f:
            data = f.read()
        data = toml.loads(data)
        return data

    def dict_to_toml(self, dict_data, new_file):
        """
        The function creates a TOML file using the data from a dictionary
        :param dict_data: The dictionary containing the data
        :param new_file: The name of the TOML file that will be created
        :return: True - if the TOML file was created
                 False - if the TOML file was not created
        """
        with open(f"{new_file}.toml", mode="w") as f:
            data = toml.dumps(dict_data)
            f.write(data)
        return bool(f"{new_file}.toml")

    def get_info(self, url_file):
        """
        General function for GET requests
        :return: True, the request body in a JSON format - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        get_url = self.base_url + url_file
        response = requests.get(url=get_url, headers={'Authorization': self.auth_token})
        if response.status_code in (200, 202, 204):
            response = response.json()
            if response.get("next"):
                #set offset equal to the total number of entities 
                offset = response.get("count")
                results = response['results']
                for i in range(20, offset, 20):
                    results.extend(requests.get(url=f"{get_url}?limit=20&offset={i}",
                                                headers={'Authorization': self.auth_token}).json()['results'])
                response['results'] = results
            return True, response
        return False, response

    def post_info(self, url_file, post_data):
        """
        General function for POST requests
        :return: True, the request body in a JSON format - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        post_url = self.base_url+url_file
        response = requests.post(url=post_url, data=post_data, headers={'Authorization': self.auth_token})
        if response.status_code in (201, 202):
            return True, response.json()
        else:
            return False, response

    def delete_info(self, url_file):
        """
        General function for DELETE requests
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        delete_url = self.base_url + url_file
        response = requests.delete(url=delete_url, headers={'Authorization': self.auth_token})
        if response.status_code in (202, 204):
            return True, response
        else:
            return False, response

#!!!!!!!
    def match(self, list_of_dicts, given_value, given_key, key_for_unknow_value):
        """
        The function finds the value for o specific key of a dictionary using another key-value pair
        :param list_of_dicts: The list that contains all the dictionaries
        :param given_value: The value you want to associate
        :param given_key: The key you want to associate
        :param key_for_unknow_value: The key of the value that you want to find
        :return: value of the key_for_unknow_value - if there is an association
                 an empty string - if there is no association
        """
        current_value = ""
        for d in list_of_dicts:
            if d[given_key] == given_value:
                current_value = d.get(key_for_unknow_value)
                break
        return current_value

#WEIGHT RELATED FUNCTION

    def create_weight_goals(self, date, weight):
        """
        The function creates weight goals for a specific date.
        :param date: Date in month/day/year format
        :param weight: Weight in kilograms
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        data = {"id": "",
                "date": date,
                "weight": weight,
                "user": ""
                }
        response = self.post_info('weightentry/', data)
        return response

#NUTRITION RELATED FUNCTIONS

    def create_nutritionplan(self, nutritionplan_name, calories_goal=True):
        """
        The function creates a new nutrition plan
        :param nutritionplan_name: The name of the new nutrition plan
        :param calories_goal: a boolean value that specifies if the nutrition plan has calories goals or not
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        data = {"id": "",
                "creation_date": "",
                "description": nutritionplan_name,
                "has_goal_calories": calories_goal,
                "language": 2
                }
        response = self.post_info('nutritionplan/', data)
        return response

    def create_meal(self, nutritionplan_id, time="08:00:00"):
        """
        The function creates a new meal for a specific plan
        :param nutritionplan_id: The id of the nutrition plan
        :param time: The time of the day when the meal is scheduled
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        data = {"id": "",
                "plan": nutritionplan_id,
                "order": "",
                "time": time
                }
        response = self.post_info('meal/', data)
        return response

    def select_mealitem(self):
        """
        This function selects a random ingredient 
        :return: ingredient id, ingredient energy
        """
        #get all ingredients
        items = self.get_info("ingredient/")
        #select a random ingredient
        new_item = random.choice(items[1].get("results"))
        return new_item.get('id'), new_item.get('energy')

    def add_mealitem(self, meal, item, amount):
        """
        The function adds a new item to a specific meal
        :param meal: The id of the meal
        :param item: The id of the new ingredient
        :param amount: The quantity of the ingredient
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        data_item = {"id": "",
                     "meal": meal,
                     "ingredient": item,
                     "weight_unit": "",
                     "order": 1,
                     "amount": amount
                     }
        request = self.post_info('mealitem/', data_item)
        return request

    def create_nutritionplans(self, kcals):
        """
        The function creates nutrition plans for every single day in a week based on energy targets
        :param kcals: Total number of calories per day
        :return: True - if all days has a nutrition plan
                 False - if there are days that don't have a nutrition plan
        """

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i in days:
            nutrition_plan = self.create_nutritionplan(i, True)
            meal = self.create_meal(nutrition_plan[1].get('id'))
            meal_id = meal[1].get('id')
            total_kcals = 0

            if i in ['Monday', 'Tuesday', 'Wednesday', 'Thursday']:
                while total_kcals <= kcals:
                    new_item = self.select_mealitem()
                    self.add_mealitem(meal_id, new_item[0], 100)
                    total_kcals += new_item[1]

            else:
                while total_kcals < kcals:
                    new_item = self.select_mealitem()
                    total_kcals += new_item[1]
                    if total_kcals < kcals:
                        self.add_mealitem(meal_id, new_item[0], 100)

        return self.get_info('nutritionplan/')[1].get("count") >= len(days)


#WORKOUT RELATED FUNCTION

    def add_exercise(self, day_id, ex_id, sets, reps, repetition_unit, weight_unit):
        """
        The function adds an exercise to a specific training day
        :param day_id: The id of the training day
        :param ex_id: The id of the exercise
        :param sets: Total number of sets
        :param reps: Total number of repetitions per set
        :param repetition_unit: The id of the repetition unit
        :param weight_unit: The id of the weight unit
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        data_set = {"id": "",
                    "exerciseday": day_id,
                    "sets": sets,
                    "order": 1}
        request = self.post_info('set/', data_set)
        if request[0] is True:
            data = {"id": "",
                    "set": request[1].get('id'),
                    "exercise": ex_id,
                    "repetition_unit": repetition_unit,
                    "reps": reps,
                    "weight_unit": weight_unit}
            request = self.post_info('setting/', data)
        return request

    def select_exercises(self, workout_id, day_id, total_exercise_number, muscle_group_exercise_number):
        """
        The function selects a given number of exercises for a given training day based on their ids.
        Also, there needs to be at least 1 exercice for back and one for front per day.
        :param workout_id: The id of the workout
        :param day_id: The id of the training day
        :param total_exercise_number: Total number of exercise per training day
        :param muscle_group_exercise_number: Total number of exercise per group muscle
        :return: True - if the training day has a total number of exercises equal to total_exercise_number parameter
                 False - if the training day has a total number of exercises not equal to total_exercise_number parameter
        """
        selected = []
        if workout_id == "" or day_id == "":
            return False

        categories = dict([(i['name'], 0) for i in self.get_info('exercisecategory/')[1].get('results')])
        exercises = [(i['id'], i['category']['name']) for i in self.get_info("exerciseinfo/")[1].get('results')]

        while len(selected) < total_exercise_number:
            for j in ['Chest', 'Back']:
                if categories[j] < 1:
                    selected.append(random.choice([i for i in exercises if i[1] == j]))
                    categories[j] += 1
            new = random.choice([i for i in exercises])
            if categories[new[1]] < muscle_group_exercise_number:
                selected.append(new)
                categories[new[1]] += 1

        for id_ex in [i[0] for i in selected]:
            self.add_exercise(day_id, id_ex, 4, 12, 1, 1)

        return len([i for i in self.get_info('set/')[1].get('results') if i['exerciseday']==day_id])==total_exercise_number

    def create_trainingday(self, workout_id, description, day_no):
        """
        This function creates a training day for a specific workout
        :param workout_id: The id of the workout
        :param description: The description of the training day
        :param day_no: The id of the weekday (1-7) starting from Monday
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        data_day = {"id": "",
                    "training": workout_id,
                    "description": description,
                    "day": day_no
                    }
        request = self.post_info('day/', data_day)
        return request

    def create_complete_trainingday(self, workout_id, trainingday_name, trainingday_no=0, total_exercise_number=6,
                                    muscle_group_exercise_number=2):
        """
        This function creates a complete training day that has configured all the training day parameters
        :param workout_id: The id of the workout
        :param trainingday_name: The name of the new training day
        :param trainingday_no: The id of the weekday (1-7) starting from Monday
        :param total_exercise_number: Total number of exercise per training day
        :param muscle_group_exercise_number: Total number of exercise per group muscle
        """
        request = self.create_trainingday(workout_id, trainingday_name, trainingday_no)
        self.select_exercises(workout_id, request[1].get('id'), total_exercise_number, muscle_group_exercise_number)

    def create_workout(self, workout_name="", description=""):
        """
        This function creates a new workout
        :param workout_name: The name of the new workout
        :param description: The description of the new workout
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        workout_data = {"id": "",
                        "creation_date": "",
                        "name": workout_name,
                        "description": description
                        }
        request = self.post_info('workout/', workout_data)
        if request[0] is True:
            self.workouts.append(request[1])
        return request

    def create_complete_workout(self, workout_name, no_days, total_exercise_number=6, muscle_group_exercise_number=2):
        """
        The function creates a complete workout.
        :param workout_name: The name of the new workout
        :param no_days: Total number of training days per workout
        :param total_exercise_number: Total number of exercise per day
        :param muscle_group_exercise_number: Total number of exercise per group muscle
        :return: True -  if the workout was created
                 False - if the workout was not created
        """
        counter = 0
        workout_id = ""
        self.create_workout(workout_name)
        for i in self.get_info('workout/')[1].get('results'):
            if i['name'] == workout_name:
                workout_id = i.get('id')
        while counter < no_days:
            self.create_complete_trainingday(workout_id, f"Day {counter + 1}", counter + 1, total_exercise_number,
                                             muscle_group_exercise_number)
            counter += 1
        return any([i['id'] == workout_id for i in self.get_info('workout/')[1].get('results')])

    def create_schedule(self, schedule_name, start_date, is_loop, is_active):
        """
        This function creates a new schedule
        :param schedule_name: The name of the new schedule
        :param start_date: The start_date of the schedule
        :param is_loop: Boolean value that specifies if the schedule is loop or not
        :param is_active: Boolean value that specifies if the schedule is active or not
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """
        data = {"id": "",
                "name": schedule_name,
                "start_date": start_date,
                "is_active": is_active,
                "is_loop": is_loop
                }
        response = self.post_info('schedule/', data)
        return response

    def add_workout_to_schedule(self, schedule_name, workout_name, duration):
        """
        This function adds an existing workout to a schedule
        :param schedule_name: The name of the schedule
        :param workout_name: The name of the workout to be added
        :param duration: The total number of weeks of the schedule
        :return: True, the request body  - if the request was performed successfully
                 False, the request body - if the request couldn't be made
        """

        schedules = self.get_info('schedule/')[1].get('results')
        workouts = self.get_info('workout/')[1].get('results')
        id_schedule = self.match(schedules, schedule_name, 'name', 'id')
        id_workout = self.match(workouts, workout_name, 'name', 'id')
        data = {"id": "",
                "schedule": id_schedule,
                "workout": id_workout,
                "duration": duration}
        response = self.post_info('schedulestep/', data)
        return response

    def delete_exercise(self, workout, day=None, exercise=None):
        """
        The function can deletes an exercise,a day or the enitre workout
        If the exercise is not specified than the day will be deleted
        If the day is not specified than the entire workout will be deleted
        :param workout: The name of the workout
        :param day: The name of the training day
        :param exercise: The name of the exercise to be deleted
        :return:True - if the request was successfully
                False - if the exercise was not deleted
        """

        exercises = self.get_info('exercise/')[1].get('results')
        workouts = self.get_info('workout/')[1].get('results')
        days = self.get_info('day/')[1].get('results')
        sets = self.get_info('set/')[1].get('results')
        settings = self.get_info('setting/')[1].get('results')
        day_ex = []
        id = ""

        id_workout = self.match(workouts, workout, 'name', 'id')
        if id_workout == "":
            return False, "Workout not found"

        if day is None:
            return self.delete_workout(workout)
        id_day = self.match(days, day, 'description', 'id')
        if id_day == "":
            return False, "Day not found"

        if exercise is None:
            return self.delete_trainingday(workout, day)
        id_exercise = self.match(exercises, exercise, 'name', 'id')
        if id_exercise == "":
            return False, "Exercise not found"

        for i in sets:
            if i['exerciseday'] == id_day:
                day_ex.append(i.get('id'))
        for i in settings:
            if i['exercise'] == id_exercise and i['set'] in day_ex:
                id = i.get('set')

        self.delete_info(f'set/{id}')
        return any(i['set'] for i in self.get_info('set/')[1].get('results') if i['sets'] == id) is False

    def delete_trainingday(self, workout, day):
        """
        This function deletes a training day
        :param workout: The name of the workout
        :param day: The name of the training day to be deleted
        :return:True - if the request was successfully
                False - if the training day was not deleted
        """
        id_workout = self.match(self.get_info('workout/')[1].get('results'), workout, 'name', 'id')
        days = [i for i in self.get_info('day/')[1].get('results') if i['training'] == id_workout]
        id_day = self.match(days, day, 'description', 'id')
        if id_day == "":
            return False, "Day not found"
        self.delete_info(f"day/{id_day}")
        return any([i['id'] for i in self.get_info('day/')[1].get('results') if i['id'] == id_day]) is False

    def delete_workout(self, workout_name):
        """
        This function deletes an workout
        :param workout_name: The name of the workout
        :return:True - if the request was successfully
                False - if the workout was not deleted
        """
        workouts = self.get_info('workout/')[1].get('results')
        id = self.match(workouts, workout_name, 'name', 'id')
        if id == "":
            return False, "Workout not found"
        self.delete_info(f'workout/{id}')
        return any([i['name'] for i in self.get_info('workout/')[1].get('results') if i['name'] == workout_name]) == False

    def save_exercises_details(self, dir_name):
        """
        This function saves the details of each exercise in a specified directory
        :param dir_name: The path of the directory
        :return: True - if the directory contain exercise details
                 False - if the directory is empty
        """

        exercises = [i['exercise'] for i in self.get_info('setting/')[1].get('results')]
        ex_images = self.get_info(f'exerciseimage/')[1].get('results')
        ex_comments = self.get_info(f'exercisecomment/')[1].get('results')
        for i in exercises:
            ex_image = "This exercise has no image available."
            ex_comment = "This exercise has no comments available."
            for j in ex_images:
                if j['id'] == i:
                    ex_image = j.get('image')
            for j in ex_comments:
                if j['id'] == i:
                    ex_comment = j.get('comment')
            with open(f'{dir_name}/exercise_{i}.html', mode='w') as f:
                data = f"Exercise ID: {i} \nExercise comments: {ex_comment} \nExercise Image: {ex_image}"
                f.write(data)
        return len(os.listdir(dir_name)) > 0


#TOML FUNCTIONS - NUTRITION RELATED

    def create_nutritionplans_with_tomlfile(self, toml_data):
        """
        The function creates nutriotion plans based on TOML data
        :param toml_data: The TOML data converted into dictionary format
        """

        if 'nutrition_plans' in toml_data:
            for nutritionplan in toml_data.get("nutrition_plans", {}):
                request = self.create_nutritionplan(
                    toml_data.get("nutrition_plans", {}).get(nutritionplan, {}).get("description"), True)
                if request[0] != True:
                    return request
                nutritionplan_name = request[1].get('description')
                if "meals" in toml_data.get("nutrition_plans", {}).get(nutritionplan, {}):
                    self.create_meals_with_tomlfile(
                        toml_data.get("nutrition_plans", {}).get(nutritionplan, {}).get('meals', {}),
                        nutritionplan_name)
                return request

    def create_meals_with_tomlfile(self, toml_data, nutritionplan_name):
        """
        The function creates new meals for a specific nutrition plan
        :param toml_data: The TOML data converted into dictionary format
        :param nutritionplan_name: The name of the nutrition plan
        """
        request = "False"
        nutritionplan_id = self.match(self.get_info('nutritionplan/')[1].get('results'),
                                      nutritionplan_name,
                                      'description',
                                      'id')
        for meal in toml_data:
            request = self.create_meal(nutritionplan_id, toml_data.get(meal, {}).get("time"))
            if request[0] == False:
                return request
            meal_id = request[1].get('id')
            if "items" in toml_data.get(meal, {}):
                self.add_items_from_tomlfile(toml_data.get(meal, {}).get('items', {}), meal_id)
        return request

    def add_items_from_tomlfile(self, toml_data, meal_id):
        """
        The function adds new meal items for a specific meal
        :param toml_data: The TOML data converted into dictionary format
        :param meal_id: The id of the meal
        """
        request = "False"
        for item in toml_data:
            item_id = self.match(self.get_info("ingredient/")[1].get('results'),
                                 toml_data.get(item, {}).get('ingredient'),
                                 'name', 'id')
            if item_id == "":
                return f"Ingredient is not in the list"
            amount = toml_data.get(item, {}).get('amount')
            weight = toml_data.get(item, {}).get('weight')
            total_amount = amount * weight
            request = self.add_mealitem(meal_id, item_id, total_amount)
            if request[0] == False:
                return request
        return request

    # TOML FUNCTIONS - WORKOUT RELATED
    def create_workouts_with_tomlfile(self, toml_data):
        """
        The function creates a workout based on TOML data
        :param toml_data: The TOML data converted into dictionary format
        """
        if 'workouts' in toml_data:
            for workout in toml_data.get("workouts", {}):
                request = self.create_workout(toml_data.get("workouts", {}).get(workout, {}).get('name'))
                if request[0] == False:
                    return request
                workout_name = request[1].get('name')
                if "days" in toml_data.get("workouts", {}).get(workout, {}):
                    self.create_trainingdays_with_tomlfile(toml_data.get("workouts", {}).get(workout, {}), workout_name)
                return request

    def create_trainingdays_with_tomlfile(self, toml_data, workout_name):
        """
        The function creates new training days for a specific workout
        :param toml_data: The TOML data converted into dictionary format
        :param workout_name: The name of the workout
        """
        workout_id = self.match(self.get_info('workout/')[1].get('results'), workout_name, "name", "id")
        for day in toml_data.get("days", {}):
            request = self.create_trainingday(workout_id,
                                              toml_data.get("days").get(day, {}).get("description"),
                                              toml_data.get("days").get(day, {}).get("day", {}))
            if request[0] == False:
                return request
            day_name = request[1].get('description')
            if "exercises" in toml_data.get("days").get(day):
                self.add_exercises_from_tomlfile(toml_data.get("days").get(day, {}), day_name)
            return request

    def add_exercises_from_tomlfile(self, toml_data, day_name):
        """
        The function adds new exercises for a specific training day
        :param toml_data: The TOML data converted into dictionary format
        :param day_name: The name of the training day
        """
        request = "False"
        day_id = self.match(self.get_info('day/')[1].get('results'), day_name, 'description', 'id')
        for exercise in toml_data.get("exercises"):
            exercise_id = self.match(self.get_info('exercise/')[1].get('results'),
                                     toml_data.get("exercises", {}).get(exercise, {}).get("exercise"),
                                     'name',
                                     'id')
            if exercise_id == "":
                return "Exercise not in the list"
            request = self.add_exercise(day_id,
                                        exercise_id,
                                        toml_data.get("exercises", {}).get(exercise, {}).get('sets'),
                                        toml_data.get("exercises").get(exercise, {}).get('reps'),
                                        toml_data.get("exercises").get(exercise, {}).get('repetition_unit'),
                                        toml_data.get("exercises").get(exercise, {}).get('weight_unit')
                                        )
            if request[0] == False:
                return request
        return request

    def create_workouts_and_nutritionplans(self, workouts_file, nutritionplans_file):
        """
        This method creates workouts and nutrition plans
        :param workouts_file: The TOML file containing the data about workouts
        :param nutritionplans_file: The TOML file containing the data about nutrition plans
        """
        workouts_data = self.toml_to_dict(workouts_file)
        nutritionplans_data = self.toml_to_dict(nutritionplans_file)
        self.create_nutritionplans_with_tomlfile(nutritionplans_data)
        self.create_workouts_with_tomlfile(workouts_data)


def api_main():
    user = Api("Token ffb50c5ea4d743aefa7540aa176590d7de57c907", "lilijora", "belive2021")
    # print(user.create_weight_goals('2021-10-18',48))
    # print(user.create_nutritionplans(1750))
    # print(user.create_complete_workout('Workout_Lili',3 ))
    # print(user.save_exercises_details('exercise_details'))
    # print(user.create_schedule("Schedule1","2021-06-18",True,True))
    # print(user.add_workout_to_schedule('Schedule1','Workout_Lili',4))
    # print(user.delete_exercise('Workout_Lili','Day 1','Shoulder Press, on Machine'))
    # print(user.delete_workout('Workout 37'))

    # print(user.create_workouts_and_nutritionplans("workout.toml","nutritionplan.toml"))
    # print(user.create_workouts_with_tomlfile(user.toml_to_dict("workout.toml")))
    # print(user.create_trainingdays_with_tomlfile(user.toml_to_dict("days.toml"),"Test_days"))
    # print(user.add_exercises_from_tomlfile(user.toml_to_dict("exercises.toml"),"First Day"))

api_main()

