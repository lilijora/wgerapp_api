import requests,random

class Api():
    base_url='https://wger.de/api/v2/'

    def __init__(self,auth_token,username,password):
        self.auth_token = auth_token
        self.username=username
        self.password=password

    def __repr__(self):
        return f"User: {self.username}"

    def user_login(self):
        """Login Function"""
        login_url='https://wger.de/en/user/login'
        user=requests.get(login_url)

        xsrftoken = user.cookies['csrftoken']
        session_id = user.cookies['sessionid']
        cookie_full=f"csrftoken={xsrftoken}; sessionid={session_id}"

        header={'Authorization': self.auth_token,'X-CSRFToken':xsrftoken,'Cookie':cookie_full,'Referer':login_url}

        login_data= {'username': self.username, 'password': self.password, 'submit':'Login'}
        req=requests.post(url=login_url, data=login_data, headers=header)
        return req.content


    def get_info(self,url_file):
        """General function for GET requests"""
        get_url=self.base_url+url_file
        response = requests.get(url=get_url,headers={'Authorization': self.auth_token})
        return response.json()

    def post_info(self,url_file,post_data):
        """General function for POST requests"""
        post_url=self.base_url+url_file
        response = requests.post(url=post_url,data=post_data,headers={'Authorization': self.auth_token})
        return response.json()

    def delete_info(self,url_file):
        """General function for DELETE requests"""
        delete_url = self.base_url + url_file
        requests.delete(url=delete_url,headers={'Authorization': self.auth_token})
        return "Item Deleted"

    def chose_weight(self,date,weight):
        """The function creates weight goals for a specific date."""

        data={ "id":"","date":date,"weight":weight,"user":""}
        self.post_info('weightentry/',data)
        return "Weight goal added successfully"
    
    def make_plan(self,plan_name):
        """The function creates a new nutrition plan and also a meal for the plan"""

        plan_data = {"id": "", "creation_date": "", "description": plan_name, "has_goal_calories": True,"language": 2}
        plan=self.post_info('nutritionplan/',plan_data)
        meal_data={"id":"","plan": plan['id'],"order": "","time":""}
        meal=self.post_info('meal/',meal_data)
        return meal

    def add_item(self,meal):
        """The function adds a new item to a specific meal"""

        items=self.get_info('/ingredient')
        new_item=random.choice(items['results'])
        ingredient=new_item['id']
        data_item={"id":"","meal": meal,"ingredient": ingredient,"weight_unit":"","order": 1,"amount":"100"}
        self.post_info('mealitem/',data_item)
        return new_item['energy']

    def week_program(self,kcals_1,kcals_2):
        """The function creates nutrition plans for every single day in a week based on energy targets"""

        days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i in days :
            nutrition_plan=self.make_plan(i)
            meal_id=nutrition_plan['id']
            total_kcals=0
            total_items=0
            if i in ['Monday', 'Tuesday', 'Wednesday', 'Thursday']:
                while(total_kcals<=kcals_1):
                    new=self.add_item(meal_id)
                    total_kcals += new
                    total_items += 1
            else:
                while (total_kcals < kcals_2):
                    new = self.add_item(meal_id)
                    total_kcals += new
                    total_items += 1
        return f"Nutrition plans for {tuple(days)} created successfully!"

    def create_exercise(self):
        """This function creates a new exercise."""

        categories = self.get_info('exercisecategory/')['results']
        equipments = self.get_info('equipment/')['results']
        muscles = self.get_info('muscle/')['results']
####### First method - Random exercise details ###################################################################
        category = random.choice([i['name'] for i in categories])
        equipment = random.choice([i['name'] for i in equipments])
        muscle = random.choice([i['name'] for i in muscles])
        name=f"{category} {muscle}"
        author="Lili"
        description = f"Exercise {name}, category {category},equipment {equipment}, muscles {muscle},made by {author}."


####### Second method - Chose details for your exercise ###########################################################
        # name = input("Add a name for the exercise: - ")
        # category = input(f"Chose one category {[i['name'] for i in categories]}: \n- ").capitalize()
        # while(category not in [i['name'] for i in categories] ):
        #     category = input(f"Chose one from the list {[i['name'] for i in categories]}: \n- ").capitalize()
        #
        # equipment = input(f"Any equipment {[i['name'] for i in equipments]} \n- ").capitalize()
        # while(equipment not in [i['name'] for i in equipments] ):
        #     equipment = input(f"Chose one from the list {[i['name'] for i in equipments]} \n- ").capitalize()
        #
        # muscle = input(f"Primary Muscles {[i['name'] for i in muscles]} \n- ").capitalize()
        # while(muscle not in [i['name'] for i in muscles]):
        #     print(muscle)
        #     muscle=input(f"Chose muscles from the list {[i['name'] for i in muscles]} \n- ").capitalize()
        # author = input("Enter your name: - ")
        # description = f"Exercise {name}, category {category},equipment {equipment}, muscles {muscles},made by {author}."

        category_id = str([i['id'] for i in categories if i['name'] == category][0])
        equipment_id = str([i['id'] for i in equipments if i['name'] == equipment][0])
        muscle_id =str([i['id'] for i in muscles if i['name'] == muscle][0])
        data={'name':name, 'description':description, 'category':category_id, 'equipment': equipment_id, 'muscles':muscle_id,
              'license_author': author}
        response=self.post_info('exercise/',data)
        return response

    def select_exercises(self,workout,day):
        """
        The function selects 6 exercises for a given training day.
        There needs to be no more than 2 exercises per muscle group per day.
        Also, there needs to be at least 1 exercice for back and one for front per day.
        """
        id_workout=""
        id_day=""
        selected = []

        for i in self.get_info('workout/')['results']:
            if i['name']==workout:
                id_workout=i['id']
        if id_workout == "":
            return "Workout not found"

        for i in self.get_info('day/')['results']:
            if i['description'] == day:
                id_day = i['id']
        if id_day == "":
            return "Training not found"

        categories =dict( [(i['name'],0) for i in self.get_info('exercisecategory/')['results']])
        exercises=[(i['id'],i['category']['name']) for i in self.get_info("exerciseinfo/?limit=100&offset=100",)['results']]
        selected.append(random.choice([i for i in exercises if i[1]==('Chest')]))
        categories['Chest'] += 1
        selected.append(random.choice([i for i in exercises if i[1] == ('Back')]))
        categories['Back'] += 1

        while(len(selected)<6):
            new=random.choice([i for i in exercises])
            if categories[new[1]]<2:
                selected.append(new)
                categories[new[1]]+=1

        for i in [i[0] for i in selected]:
            id_ex=i
            data_set={"id":"","exerciseday":id_day,"sets": 4,"order": 1}
            set_ex=self.post_info('set/',data_set)
            data ={"id":"","set":set_ex['id'],"exercise": id_ex,"repetition_unit": 1,"reps": 12,"weight_unit": 1}
            self.post_info('setting/',data)
        return f"Exercises added successfully to {day}"

    def create_workout(self,workout_name,nb_days):
        """
        The function creates a complete workout.
        You can chose the number of training days and also the name of the workout.
        Also, the function selects 6 exercises for each training day.
        """
        counter=0
        id_workout=""
        workout_data={"id":"","creation_date": "","name": workout_name,"description": ""}
        self.post_info('workout/',workout_data)
        for i in self.get_info('workout/')['results']:
            if i['name']==workout_name:
                id_workout=i['id']

        while(counter<nb_days):
            data_day={"id":"","training":id_workout ,"description": f"Day {counter+1}","day": [counter+1]}
            self.post_info('day/',data_day)
            self.select_exercises(workout_name,data_day['description'])
            counter+=1
        return f"Workout {workout_name} created successfully!"



    def schedule(self,schedule_name,start_date):
        """This function creates a new schedule.The schedule will be active and will have a given start date"""
        data={"id":"","name": schedule_name,"start_date": start_date,"is_active": True,"is_loop": True}
        response=self.post_info('schedule/',data)
        return response

    def workout_in_schedule(self,schedule_name,workout_name,duration):
        """This function adds an existing workout to a schedule"""
        schedules=self.get_info('schedule/')['results']
        workouts=self.get_info('workout/')['results']
        id_schedule=""
        id_workout=""
        for i in schedules:
            if i['name']==schedule_name:
                id_schedule=i['id']
        if id_schedule=="":
            return "Schedule not found"

        for i in workouts:
            if i['name']==workout_name:
                id_workout=i['id']
        if id_workout=="":
            return "Workout not found"

        data={"id":"","schedule": id_schedule,"workout":id_workout,"duration": duration}
        response=self.post_info('schedulestep/',data)
        return response

    def delete_exercise(self,workout,day,exercise):
        """The function delete an exercise from a specific training day"""
        exercises=[]
        for i in range(20,420,20):
            exercises.extend(self.get_info(f'exercise/?limit=20&offset={i}')['results'])
        workouts=self.get_info('workout/')['results']
        days=self.get_info('day/')['results']
        sets=self.get_info('set/')['results']
        settings=self.get_info('setting/')['results']
        ex_day=[]

        id_exercise = ""
        id_workout=""
        id_day=""
        id=""

        for i in workouts:
            if i['name']==workout:
                id_workout=i['id']
        if id_workout == "":
            return "Workout not found"

        for i in days:
            if i['description'] == day:
                id_day = i['id']
        if id_day == "":
            return "Training not found"

        for i in exercises:
            if i['name']==exercise:
                id_exercise=i['id']
        if id_exercise== "":
            return "Exercise does not exists"

        for i in sets:
            if i['exerciseday']==id_day:
                ex_day.append(i['id'])
        for i in settings:
            if i['set'] in ex_day and i['exercise']==id_exercise:
                id=i['id']

        self.delete_info(f'setting/{id}/')
        return f"Exercise {exercise} was deleted successfully!"

    def delete_workout(self,workout_name):
        """This function delete an workout"""
        workouts=self.get_info('workout/')['results']
        id=""
        for i in workouts:
            if i['name']==workout_name:
                id=i['id']
        if id=="":
            return "Workout not found"
        self.delete_info(f'workout/{id}/')
        return f"Workout {workout_name} was deleted successfully!"

    def save_ex_details(self,dir_name):
        ex_images = []
        ex_comments = []
        all_exercises=[]
        exercises = [i['exercise'] for i in user1.get_info('setting')['results']]
        for i in range(20, 100, 20):
            ex_images.extend(user1.get_info(f'exerciseimage/?limit=20&offset={i}')['results'])
        for i in range(20, 120, 20):
            ex_comments.extend(user1.get_info(f'exercisecomment/?limit=20&offset={i}')['results'])
        for i in range(20, 400, 20):
            all_exercises.extend(user1.get_info(f'exercise/?limit=20&offset={i}')['results'])

        for i in exercises:
            ex_image = "This exercise has no image available."
            ex_comment = "This exercise has no comments available."
            ex_name="Exercise"
            for j in all_exercises:
                if j['id']==i:
                    ex_name=j['name']
            for j in ex_images:
                if j['id'] == i:
                    ex_image = j['image']
            for j in ex_comments:
                if j['id'] == i:
                    ex_comment = j['comment']
            f = open(f'{dir_name}\exercise_{i}.html', 'w')
            message = f"""<html>
            <head></head>
            <body>
            <h1>{ex_name}</h1>
            <h4>{ex_comment}</h4>
            <a href = {ex_image}>Click here for Exercise Image</a>
            </body>
            </html>"""
            f.write(message)
            f.close()
        return f"Exercise details were saved successfully to {dir_name} directly."



user1=Api("Token ffb50c5ea4d743aefa7540aa176590d7de57c907","lilijora","belive2021")
def main_program(user_name):
    # print(user_name.chose_weight('2021-08-18',48))
    # print(user_name.week_program(1750,1300))
    # print(user_name.create_workout('Workout1', 3))
    print(user_name.save_ex_details('exercise_details'))
    # print(user_name.schedule("Schedule1","2021-08-18"))
    # print(user_name.workout_in_schedule('Schedule1','Workout1',4))
    # print(user_name.delete_exercise('Workout1','Day 2','Jumping Jacks'))
    # print(user_name.delete_workout('Workout1'))

main_program(user1)