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
        return user.delete_workout(user.get_info("workout/")[1].get("results")[-1].get('name'))
    request.addfinalizer(delete_all_workouts)


def existing_entities(user, url_path):
    req = user.get_info(url_path)[1].get("results")
    ids = [i["id"] for i in req]
    return ids


def random_text_generator(name_len):
    s = ""
    chr_list = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(string.digits) + list('@_!#$%^&*()<>?}{~:')
    for i in range(name_len+1):
        s = s+random.choice(chr_list)
    return s


def random_number_generator(no_len):
    no = ""
    no_digits = list(string.digits)
    for i in range(no_len+1):
        no = no+random.choice(no_digits)
    return int(no)


####POSITIVE TESTS####
# @pytest.mark.usefixtures(user)
class TestWorkout:
    def test_add_one_workout(self,user,delete_entities):
        assert user.create_workout()[0] == True


    def test_add_one_workout_with_name_and_description(self, user, delete_entities):
        assert user.create_workout(random_text_generator(10), random_text_generator(20))[0] == True


    @pytest.mark.skip
    def test_add_a_large_number_of_workouts(self, user, delete_entities):
        assert all(user.create_workout(f"Workout {i}")[0] for i in range(1, 52)) == True
        for i in range(1,51):
            user.delete_workout(user.get_info('workout/')[1].get("results")[-1].get("name"))


    def test_add_trainingday(self, user, delete_entities):
        req = user.create_workout("Test_Workout")
        assert req[0] == True
        workout_id = req[1].get("id")
        assert user.create_trainingday(workout_id, "First Day", 1)[0] == True


    def test_add_exercises(self, user, delete_entities):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        req_exercise_one = user.add_exercise(day_id, 325, 4, 12, 1, 1)
        assert req_exercise_one[0] == True
        req_exercise_two = user.add_exercise(day_id, 325, 4, 12, 1, 1)
        assert req_exercise_two[0] == True


    ####NEGATIVE TESTS####


    def test_add_one_workout_with_special_name_and_long_description(self, user,delete_entities):
        assert user.create_workout(random_text_generator(15), random_text_generator(999))[0] == True
        assert user.create_workout(random_text_generator(100), random_text_generator(999))[0] == False
        assert user.create_workout(random_text_generator(15), random_text_generator(1000))[0] == False


    def test_add_more_than_ten_sets(self, user, delete_entities):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        assert user.add_exercise(day_id, 24, 10, 12, 1, 1)[0] == True
        assert user.add_exercise(day_id, 24, 11, 12, 1, 1)[0] == False


    def test_add_trainingday_to_an_inexisting_workout(self, user):
        workout_id = random_number_generator(6)
        while workout_id in existing_entities(user, 'workout/'):
            workout_id = random_number_generator(6)
        assert user.create_trainingday(workout_id, "Test_Day", 1)[0] == False


    @pytest.mark.skip(reason="Bug")
    def test_add_more_than_seven_days_to_one_workout(self, user, delete_entities):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        for i in range(1, 10):
            user.create_trainingday(workout_id, f"Day {i}", i)
        assert len(user.get_info('day/')[1].get("results")) != 9


    def test_add_trainingday_with_long_description(self, user, delete_entities):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        assert user.create_trainingday(workout_id, random_text_generator(99), 1)[0] == True
        assert user.create_trainingday(workout_id, random_text_generator(100), 1)[0] == False


    def test_add_exercise_to_an_inexisting_trainingday(self, user):
        day_id = random_number_generator(6)
        while day_id in existing_entities(user, 'day/'):
            day_id = random_number_generator(6)
        assert user.add_exercise(day_id, 325, 4, 12, 1, 1)[0] == False


    def test_add_inexisting_exercise(self, user, delete_entities):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        exercise_id = random_number_generator(4)
        while exercise_id in existing_entities(user, 'exercise/'):
            exercise_id = random_number_generator(4)
        assert user.add_exercise(day_id, exercise_id, 4, 12, 1, 1)[0] == False


    def test_add_trainingday_with_invalid_parameters(self, user, delete_entities):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        assert user.create_trainingday(workout_id, random_text_generator(100), random_text_generator(2))[0] == False


    def test_add_exercise_without_all_parameters(self, user, delete_entities):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        exercise_id = random.choice([i["id"] for i in user.get_info('exercise/')[1].get("results")])
        assert user.add_exercise(day_id, exercise_id, "", "", "", "")[0] == False


    def test_delete_an_inexisting_workout(self, user):
        workout_name = random_text_generator(10)
        while workout_name in [i['name'] for i in user.get_info('workout/')[1].get("results")]:
            workout_name = random_text_generator(10)
        assert user.delete_workout(workout_name)[0] == False


    def test_delete_an_inexiting_trainingday(self, user, delete_entities):
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_name = req_workout[1].get("name")
        assert user.delete_trainingday(workout_name, random_text_generator(10))[0] == False