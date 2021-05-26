import requests,random,os,toml

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
        xsrftoken = user.cookies.get('csrftoken')
        session_id = user.cookies.get('sessionid')
        cookie_full=f"csrftoken={xsrftoken}; sessionid={session_id}"

        header={'Authorization': self.auth_token,
                'X-CSRFToken':xsrftoken,
                'Cookie':cookie_full,
                'Referer':login_url}

        login_data= {'username': self.username,
                     'password': self.password,
                     'submit':'Login'}
        req=requests.post(url=login_url, data=login_data, headers=header)
        return req.content


    def get_info(self,url_file,offset=20):
        """General function for GET requests"""
        get_url=self.base_url+url_file
        response=requests.get(url=get_url,headers={'Authorization': self.auth_token}).json()
        if "next" in response and  response["next"]!=None:
            results=response['results']
            for i in range(20,offset,20):
                results.extend(requests.get(url=f"{get_url}?limit=20&offset={i}",headers={'Authorization': self.auth_token}).json()['results'])
            response['results']=results
        return response

    def post_info(self,url_file,post_data):
        """General function for POST requests"""
        post_url=self.base_url+url_file
        response = requests.post(url=post_url,data=post_data,headers={'Authorization': self.auth_token})
        return response.json()

    def delete_info(self,url_file):
        """General function for DELETE requests"""
        delete_url = self.base_url + url_file
        response=requests.delete(url=delete_url,headers={'Authorization': self.auth_token})
        return response

    def match(self,dict1,dict_item,param1,param2):
        current_value=""
        for i in dict1:
            if i[param1] == dict_item:
                current_value = i.get(param2)
        return current_value


    def weight_entry(self,date,weight):
        """The function creates weight goals for a specific date."""

        data={ "id":"",
               "date":date,
               "weight":weight,
               "user":""}
        response=self.post_info('weightentry/',data)
        return response
    
    def make_plan(self,plan_name):
        """The function creates a new nutrition plan and also a meal for the plan"""

        plan_data = {"id": "",
                     "creation_date": "",
                     "description": plan_name,
                     "has_goal_calories": True,
                     "language": 2}
        plan=self.post_info('nutritionplan/',plan_data)
        meal_data={"id":"",
                   "plan": plan.get('id'),
                   "order": "",
                   "time":""}
        meal=self.post_info('meal/',meal_data)
        return meal

    def add_item(self,meal,amount):
        """The function adds a new item to a specific meal"""

        items=self.get_info('/ingredient')
        new_item=random.choice(items['results'])
        ingredient=new_item.get('id')
        data_item={"id":"",
                   "meal": meal,
                   "ingredient": ingredient,
                   "weight_unit":"",
                   "order": 1,
                   "amount":amount}
        self.post_info('mealitem/',data_item)
        return new_item.get('energy')

    def week_program(self,kcals_1,kcals_2):
        """The function creates nutrition plans for every single day in a week based on energy targets"""

        days=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i in days :
            nutrition_plan=self.make_plan(i)
            meal_id=nutrition_plan.get('id')
            total_kcals=0
            total_items=0
            if i in ['Monday', 'Tuesday', 'Wednesday', 'Thursday']:
                while(total_kcals<=kcals_1):
                    new=self.add_item(meal_id,100)
                    total_kcals += new
                    total_items += 1
            else:
                while (total_kcals < kcals_2):
                    new = self.add_item(meal_id,100)
                    total_kcals += new
                    total_items += 1
        return self.get_info('nutritionplan/').get("count")>=len(days)

    def create_exercise(self):
        """This function creates a new exercise."""

        categories = self.get_info('exercisecategory/').get('results')
        equipments = self.get_info('equipment/').get('results')
        muscles = self.get_info('muscle/').get('results')

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
        data={'name':name,
              'description':description,
              'category':category_id,
              'equipment': equipment_id,
              'muscles':muscle_id,
              'license_author': author}
        response=self.post_info('exercise/',data)
        return response

    def select_exercises(self,workout,day,total_ex,ex_musclegroup):
        """
        The function selects 6 exercises for a given training day.
        There needs to be no more than 2 exercises per muscle group per day.
        Also, there needs to be at least 1 exercice for back and one for front per day.
        """
        workouts=self.get_info('workout/').get('results')
        days=self.get_info('day/').get('results')
        selected = []

        id_workout=self.match(workouts, workout, 'name', 'id')
        if id_workout=="":
            return False

        id_day = self.match(days,day, 'description', 'id')
        if id_workout == "":
            return False

        categories =dict( [(i['name'],0) for i in self.get_info('exercisecategory/').get('results')])
        exercises=[(i['id'],i['category']['name']) for i in self.get_info("exerciseinfo/",100).get('results')]
        selected.append(random.choice([i for i in exercises if i[1]==('Chest')]))
        categories['Chest'] += 1
        selected.append(random.choice([i for i in exercises if i[1] == ('Back')]))
        categories['Back'] += 1

        while(len(selected)<total_ex):
            new=random.choice([i for i in exercises])
            if categories[new[1]]<ex_musclegroup:
                selected.append(new)
                categories[new[1]]+=1

        for i in [i[0] for i in selected]:
            id_ex=i
            data_set={"id":""
                ,     "exerciseday":id_day,
                      "sets": 4,
                      "order": 1}
            set_ex=self.post_info('set/',data_set)
            data ={"id":"",
                   "set":set_ex.get('id'),
                   "exercise": id_ex,
                   "repetition_unit": 1,
                   "reps": 12,
                   "weight_unit": 1}
            self.post_info('setting/',data)
        return f"Exercises added successfully to {day}"

    def create_workout(self,workout_name,no_days):
        """
        The function creates a complete workout.
        You can chose the number of training days and also the name of the workout.
        Also, the function selects 6 exercises for each training day.
        """
        counter=0
        id_workout=""
        workout_data={"id":"",
                      "creation_date": "",
                      "name": workout_name,
                      "description": ""}
        self.post_info('workout/',workout_data)
        for i in self.get_info('workout/').get('results'):
            if i['name']==workout_name:
                id_workout=i.get('id')

        while(counter<no_days):
            data_day={"id":"",
                      "training":id_workout ,
                      "description": f"Day {counter+1}",
                      "day": [counter+1]}
            self.post_info('day/',data_day)
            self.select_exercises(workout_name,data_day['description'],6,2)
            counter+=1
        return any([i['id']==id_workout for i in user1.get_info('workout/').get('results')])


    def schedule(self,schedule_name,start_date,is_loop,is_active):
        """This function creates a new schedule.The schedule will be active and will have a given start date"""
        data={"id":"",
              "name": schedule_name,
              "start_date": start_date,
              "is_active": is_active,
              "is_loop": is_loop}
        response=self.post_info('schedule/',data)
        return response

    def workout_in_schedule(self,schedule_name,workout_name,duration):
        """This function adds an existing workout to a schedule"""
        schedules=self.get_info('schedule/')['results']
        workouts=self.get_info('workout/')['results']
        id_schedule=self.match(schedules,schedule_name,'name','id')
        id_workout=self.match(workouts, workout_name, 'name', 'id')
        data={"id":"",
              "schedule": id_schedule,
              "workout":id_workout,
              "duration": duration}
        response=self.post_info('schedulestep/',data)
        return response


    def delete_exercise(self,workout,day=None,exercise=None):
        """The function delete an exercise from a specific training day"""
        exercises=self.get_info('exercise/',420)['results']
        workouts=self.get_info('workout/')['results']
        days=self.get_info('day/')['results']
        sets=self.get_info('set/',41)['results']
        settings=self.get_info('setting/',41)['results']
        day_ex=[]
        id=""

        id_workout=self.match(workouts,workout, 'name', 'id')
        if id_workout=="":
            return (False,"Workout not found")

        if day==None:
            return self.delete_workout(workout)
        id_day=self.match(days, day, 'description', 'id')
        if id_day=="":
            return (False,"Day not found")

        if exercise==None:
            return self.delete_day(workout,day)
        id_exercise=self.match(exercises,exercise, 'name', 'id')
        if id_exercise=="":
            return (False,"Exercise not found")

        for i in sets:
            if i['exerciseday']==id_day:
                day_ex.append(i.get('id'))
        for i in settings:
            if i['exercise']==id_exercise and i['set'] in day_ex:
                id=i.get('set')

        self.delete_info(f'set/{id}')
        return any(i['set'] for i in self.get_info('set/').get('results')if i['sets']==id)==False
    
    def delete_day(self,workout,day):
        """This function delete a training day"""
        id_workout=self.match(self.get_info('workout/').get('results'),workout,'name','id')
        days=[i for i in self.get_info('day/').get('results') if i['training']==id_workout]
        id_day=self.match(days,day,'description','id')
        if id_day=="":
            return (False,"Day not found")
        self.delete_info(f"day/{id_day}")
        return any([i['id'] for i in self.get_info('day/').get('results') if i['id']==id_day])==False

    def delete_workout(self,workout_name):
        """This function delete an workout"""
        workouts=self.get_info('workout/').get('results')
        id=self.match(workouts,workout_name,'name','id')
        if id=="":
            return (False,"Workout not found")
        self.delete_info(f'workout/{id}')
        return any([i['name'] for i in self.get_info('workout/').get('results') if i['name']==workout_name])==False

    def save_ex_details(self,dir_name):
        exercises = [i['exercise'] for i in user1.get_info('setting/').get('results')]
        ex_images=self.get_info(f'exerciseimage/',100).get('results')
        ex_comments=self.get_info(f'exercisecomment/',120).get('results')
        all_exercises=self.get_info(f'exercise/',400).get('results')

        for i in exercises:
            ex_image = "This exercise has no image available."
            ex_comment = "This exercise has no comments available."
            ex_name="Exercise"
            for j in all_exercises:
                if j['id']==i:
                    ex_name=j.get('name')
            for j in ex_images:
                if j['id'] == i:
                    ex_image = j.get('image')
            for j in ex_comments:
                if j['id'] == i:
                    ex_comment = j.get('comment')
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
        return len(os.listdir(dir_name))>0



class TomlClass(Api):

    def toml_to_dict(self, toml_file):
        with open(toml_file) as f:
            data = f.read()
        data = toml.loads(data)
        return data

    def dict_to_toml(self, dict_data, new_file):
        with open(f"{new_file}.toml", mode="w") as f:
            data = toml.dumps(dict_data)
            f.write(data)
        return bool(f"{new_file}.toml")

    def nutrition_plans(self, toml_file):
        toml_data=self.toml_to_dict(toml_file)
        if 'nutrition_plans' in toml_data:
            for i in toml_data.get("nutrition_plans"):
                data = {"id": "",
                        "creation_date": "",
                        "description": i,
                        "has_goal_calories": True,
                        "language": 2}
                request = self.post_info('nutritionplan/', data)
                id = request.get('id')
                if "meals" in toml_data.get("nutrition_plans").get(i):
                    toml_data.get("nutrition_plans", {}).get(i, {}).get("meals")
                    self.meals(toml_data.get("nutrition_plans").get(i).get("meals"), id)
        return request

    def meals(self, toml_data, plan):
        for i in toml_data:
            data = {"id": "",
                    "plan": plan,
                    "order": 1,
                    "time": toml_data.get(i).get("time")}
            self.post_info('meal/', data)
            for j in self.get_info('meal/').get('results'):
                if j['plan'] == plan:
                    id = j.get('id')
            if "items" in toml_data.get(i):
                self.items(toml_data.get(i).get("items"), id)

    def items(self, toml_data, meal):
        for i in toml_data:
            id = ""
            ingredient_name = toml_data.get(i).get("ingredient")
            amount = toml_data.get(i).get("amount")
            weight = toml_data.get(i).get("weight")
            total = amount * weight
            for i in self.get_info("ingredient/").get('results'):
                if i["name"] == ingredient_name:
                    id = i.get("id")
            if id == "":
                return f"Ingredient {ingredient_name} is not in the list"
            data = {"id": "",
                    "meal": meal,
                    "ingredient": id,
                    "weight_unit": "",
                    "order": 1,
                    "amount": total}
            self.post_info("mealitem/", data)

    def workouts(self,toml_file):
        toml_data=self.toml_to_dict(toml_file)
        if 'workouts' in toml_data:
            for i in toml_data.get("workouts"):
                data= {"id": "",
                       "creation_date": "",
                       "name":toml_data.get("workouts").get(i).get('name'),
                       "description": ""}
                request=self.post_info('workout/',data)
                id=request.get('id')
                if "days" in toml_data.get("workouts").get(i):
                    self.days(toml_data.get("workouts").get(i).get("days"),id)
        return request

    def days(self,toml_data,workout):
        for i in toml_data:
            data={"id":"",
                  "training":workout ,
                  "description": toml_data.get(i).get("description"),
                  "day": toml_data.get(i).get("day")}
            request=self.post_info('day/',data)
            id=request.get('id')

            if "exercises" in toml_data.get(i):
                self.exercises(toml_data.get(i).get("exercises"),id)

    def exercises(self,toml_data,day):
        total_ex=self.get_info('exercise/',420).get('results')
        for i in toml_data:
            ex_name = toml_data.get(i).get("exercise")
            ex_id=self.match(total_ex,ex_name,'name','id')

            set_data = {"id": "",
                        "exerciseday": day,
                        "sets":1,
                        "order": 1}
                        # "sets":  toml_data.get(i).get("sets"),
                        # "order": toml_data.get(i).get("order")}
            request=self.post_info('set/', set_data)

            ex_data ={"id":"",
                    "set":request.get('id'),
                    "exercise": ex_id,
                    "repetition_unit": 1 ,
                    "reps": toml_data.get(i).get("reps"),
                    "weight_unit":1,
                    "order" :1}
            self.post_info('setting/',ex_data)


def api_program():
    user = Api("Token ffb50c5ea4d743aefa7540aa176590d7de57c907", "lilijora", "belive2021")
    # print(user.weight_entry('2021-08-18',48))
    # print(user.week_program(1750,1300))
    # print(user.create_workout('Workout1',3 ))
    # print(user.save_ex_details('exercise_details'))
    # print(user.schedule("Schedule3","2021-05-18",True,True))
    # print(user.workout_in_schedule('Schedule2','Workout4',4))
    # print(user.delete_exercise('w1','day1','Back Squat'))
    # print(user.delete_workout('Workout4'))
    pass

def toml_program():
    user = TomlClass("Token ffb50c5ea4d743aefa7540aa176590d7de57c907", "lilijora", "belive2021")
    print(user.nutrition_plans("nutritionplan.toml"))
    print(user.workouts("workout.toml"))

api_program()
toml_program()

