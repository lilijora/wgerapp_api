from wger import Api
import pytest
import string
import random


@pytest.fixture()
def user():
    login = Api("Token ffb50c5ea4d743aefa7540aa176590d7de57c907", "lilijora", "belive2021")
    return login


@pytest.fixture(scope="function")
def delete_entities(user, request):
    def delete_all_workouts():
        return [user.delete_workout(i["name"])for i in user.get_info("workout/")[1].get("results") if i in user.workouts]
    request.addfinalizer(delete_all_workouts)


def existing_entities(user, url_path):
    req = user.get_info(url_path)[1].get("results")
    ids = [i["id"] for i in req]
    return ids


def random_text_generator(name_len):
    s = ""
    chr_list = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(string.digits) + list('@_!#$%^&*()<>?}{~:')
    for i in range(name_len):
        s = s+random.choice(chr_list)
    return s


def random_number_generator(no_len):
    no = ""
    no_digits = list(string.digits)
    for i in range(no_len):
        no = no+random.choice(no_digits)
    return int(no)


####POSITIVE TESTS####
@pytest.mark.usefixtures('delete_entities')
class TestWorkout:
    def test_add_one_workout(self,user):
        assert user.create_workout()[0] == True


    def test_add_one_workout_with_name_and_description(self, user):
        assert user.create_workout(workout_name=random_text_generator(10), description=random_text_generator(20))[0] == True


    @pytest.mark.skip
    def test_add_a_large_number_of_workouts(self, user):
        assert all(user.create_workout(workout_name=f"Workout {i}")[0] for i in range(1, 52)) == True



    def test_add_trainingday(self, user):
        req = user.create_workout("Test_Workout")
        assert req[0] == True
        workout_id = req[1].get("id")
        assert user.create_trainingday(workout_id, description="First Day", day_no=1)[0] == True


    @pytest.mark.parametrize("ex_id,sets,reps,repetition_unit,weight_unit,result",[(325, 4, 12, 1, 1, True),(325, 4, 12, 1, 1, True)])
    def test_add_exercises(self, user,ex_id,sets,reps,repetition_unit,weight_unit,result):
        req_workout = user.create_workout(workout_name="Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, description="Test_Day", day_no=1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        req_exercise_one = user.add_exercise(day_id,ex_id,sets,reps,repetition_unit,weight_unit)
        assert req_exercise_one[0] == result


    ####NEGATIVE TESTS####

    @pytest.mark.parametrize("name_len, description_len, result",[(100,1000,True),(101,1000,False),(100,1001,False)])
    def test_add_one_workout_with_special_name_and_long_description(self, user,name_len,description_len,result):
        assert user.create_workout(random_text_generator(name_len), random_text_generator(description_len))[0] == result


    @pytest.mark.parametrize("ex_id,sets,reps,repetition_unit,weight_unit,result",[(24,10,12,1,1,True),(24,11,12,1,1,False)])
    def test_add_more_than_ten_sets(self, user,ex_id,sets,reps,repetition_unit,weight_unit,result):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        assert user.add_exercise(day_id,ex_id,sets,reps,repetition_unit,weight_unit)[0] == result


    def test_add_trainingday_to_an_inexisting_workout(self, user):
        workout_id = random_number_generator(6)
        while workout_id in existing_entities(user, 'workout/'):
            workout_id = random_number_generator(6)
        assert user.create_trainingday(workout_id, description="Test_Day", day_no=1)[0] == False


    def test_add_more_than_seven_days_to_one_workout(self, user):
        req=""
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        for i in range(1, 9):
            req=user.create_trainingday(workout_id, f"Day {i}", i)
        assert req[0]==False



    @pytest.mark.parametrize("description_len,day_no,result",[(100,1,True),(101,1,False)])
    def test_add_trainingday_with_long_description(self, user,description_len,day_no,result):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        assert user.create_trainingday(workout_id, random_text_generator(description_len),day_no)[0] == result



    def test_add_exercise_to_an_inexisting_trainingday(self, user):
        day_id = random_number_generator(6)
        while day_id in existing_entities(user, 'day/'):
            day_id = random_number_generator(6)
        assert user.add_exercise(day_id, ex_id=325, sets=4, reps=12, repetition_unit=1, weight_unit=1)[0] == False


    def test_add_inexisting_exercise(self, user):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        exercise_id = random_number_generator(4)
        while exercise_id in existing_entities(user, 'exercise/'):
            exercise_id = random_number_generator(4)
        assert user.add_exercise(day_id, exercise_id, sets=4, reps=12, repetition_unit=1, weight_unit=1)[0] == False


    def test_add_trainingday_with_invalid_parameters(self, user):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        assert user.create_trainingday(workout_id, description=random_text_generator(100), day_no=random_text_generator(2))[0] == False


    def test_add_exercise_without_all_parameters(self, user):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        exercise_id = random.choice([i["id"] for i in user.get_info('exercise/')[1].get("results")])
        assert user.add_exercise(day_id, exercise_id, sets="", reps="", repetition_unit="", weight_unit="")[0] == False


    def test_delete_an_inexisting_workout(self, user):
        workout_name = random_text_generator(10)
        while workout_name in [i['name'] for i in user.get_info('workout/')[1].get("results")]:
            workout_name = random_text_generator(10)
        assert user.delete_workout(workout_name)[0] == False


    def test_delete_an_inexiting_trainingday(self, user):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_name = req_workout[1].get("name")
        assert user.delete_trainingday(workout_name, day=random_text_generator(10))[0] == False