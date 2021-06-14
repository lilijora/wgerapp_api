from wger import Api
import pytest
import string
import random


@pytest.fixture()
def user():
    """
    :return: the object login of the Api Class that is used for tests.
    """
    login = Api("Token ffb50c5ea4d743aefa7540aa176590d7de57c907", "lilijora", "belive2021")
    return login


@pytest.fixture(scope="function")
def delete_entities(user, request):
    """
    Clean up fixture.
    """
    def delete_all_workouts():
        return [user.delete_workout(i["name"])for i in user.get_info("workout/")[1].get("results") if i in user.workouts]
    request.addfinalizer(delete_all_workouts)


def get_existing_entities(user, url_path):
    """
    :return: a list containing the ids of the existing entities for a specific api endpoint.
    """
    req = user.get_info(url_path)[1].get("results")
    ids = [i["id"] for i in req]
    return ids


def random_text_generator(name_len):
    """
    :return: a random string containing all types of characters.
    """
    s = ""
    chr_list = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(string.digits) + list('@_!#$%^&*()<>?}{~:')
    for i in range(name_len):
        s = s+random.choice(chr_list)
    return s


def random_number_generator(no_len):
    """
    :return: a random number that has the length equal to a given value
    """
    no = ""
    no_digits = list(string.digits)
    for i in range(no_len):
        no = no+random.choice(no_digits)
    return int(no)


@pytest.mark.usefixtures('delete_entities')
class TestWorkout:

    #POSITIVE TESTS

    def test_add_one_workout(self, user):
        """
        The role of this test is to check if you can create an workout without providing not even a name.
        Expected result: Workout created successfully with a default name.
        """
        assert user.create_workout()[0] == True


    def test_add_one_workout_with_name_and_description(self, user):
        """
        This test checks if you can create a workout with name and description.
        Expected result: Workout created successfully.
        """
        assert user.create_workout(workout_name=random_text_generator(10), description=random_text_generator(20))[0] == True


    # @pytest.mark.skip
    def test_add_a_large_number_of_workouts(self, user):
        """
        This test checks if you can create workouts for all the weeks in a year.
        Expected result: Workouts created successfully.
        """
        assert all([user.create_workout(workout_name=f"Workout {i}")[0] for i in range(1, 52)]) == True


    def test_add_trainingday(self, user):
        """
        This test function checks if you can create a training day.
        Steps:
            creates a workout
            checks if the workout was created successfully
            creates a training day using the workout id
            checks if the training day was created successfully.
        """
        req = user.create_workout("Test_Workout")
        assert req[0] == True
        workout_id = req[1].get("id")
        assert user.create_trainingday(workout_id, description="First Day", day_no=1)[0] == True


    @pytest.mark.parametrize("ex_id,sets,reps,repetition_unit,weight_unit,result", [(325, 4, 12, 1, 1, True), (325, 4, 12, 1, 1, True)])
    def test_add_exercises(self, user, ex_id, sets, reps, repetition_unit, weight_unit, result):
        """
        This test function checks if you can add an exercise to a specific training day
        Steps:
            creates a workout
            checks if the workout was created successfully
            creates a training day using the workout id
            checks if the training day was created successfully
            adds an exercise to the training day providing all the parameters needed:
                    training day id,
                    exercise id,
                    number of sets,
                    number of repetitons,
                    repetition unit id,
                    weight unit id.
            checks if the exercise was added successfully.
        The test function also check if you can add the same exercise more than once in the same training day.
        """
        req_workout = user.create_workout(workout_name="Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, description="Test_Day", day_no=1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        req_exercise_one = user.add_exercise(day_id, ex_id, sets, reps, repetition_unit, weight_unit)
        assert req_exercise_one[0] == result


    #NEGATIVE TESTS

    @pytest.mark.parametrize("name_len, description_len, result", [(100, 1000, True), (101, 1000, False), (100, 1001, False)])
    def test_add_one_workout_with_special_name_and_long_description(self, user, name_len, description_len, result):
        """
        This test verifies if a workout can only be created if the name length is less or equal to 100 and the description
        length is less or equal to 1000.
        """
        assert user.create_workout(random_text_generator(name_len), random_text_generator(description_len))[0] == result


    @pytest.mark.parametrize("ex_id,sets,reps,repetition_unit,weight_unit,result", [(24, 10, 12, 1, 1, True), (24, 11, 12, 1, 1, False)])
    def test_add_more_than_ten_sets(self, user, ex_id, sets, reps, repetition_unit, weight_unit, result):
        """
        This test function checks the maximum number of sets.
        Steps:
            creates a workout
            checks if the workout was created successfully
            creates a training day using the workout id
            checks if the training day was created successfully
            adds an exercise to the training day providing all the parameters needed:
                    training day id,
                    exercise id,
                    number of sets,
                    number of repetitons,
                    repetition unit id,
                    weight unit id.
            checks if the request has the expected value.
        Expected result:
            The function should return False if the number of sets is greater than the maximum value - 10.
        """
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        assert user.add_exercise(day_id, ex_id, sets, reps, repetition_unit, weight_unit)[0] == result


    def test_add_trainingday_to_an_inexistent_workout(self, user):
        """
        This test function checks the case of adding a training day to an inexistent workout.
        Steps:
            generates a random workout id until this is unique
            creates the training day using the generated workout id
            checks that the request was unsuccessful
        """
        workout_id = random_number_generator(6)
        while workout_id in get_existing_entities(user, 'workout/'):
            workout_id = random_number_generator(6)
        assert user.create_trainingday(workout_id, description="Test_Day", day_no=1)[0] == False


    def test_add_more_than_seven_days_to_one_workout(self, user):
        """
        This test function checks the maximum number of days.
        Steps:
            creates a workout
            checks if the workout was created successfully
            creates training days until the maximum value is exceeded
            checks that the request was unsuccessful.
        Expected result:
            The function should return False because the number of days is greater than the maximum value - 7.
        """
        req=""
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        for i in range(1, 9):
            req=user.create_trainingday(workout_id, f"Day {i}", i)
        assert req[0]==False


    @pytest.mark.skip(reason="Bug")
    def test_add_same_weekday_more_than_once(self, user):
        """
        This test function verify if there is a possibility to add the same weekday more than once in the same week.
        Steps:
            creates a workout
            checks if the workout was created successfully
            creates training days with the same day number id
            checks that the request was unsuccessful.
         Expected result:
            The function should return False because there is no possibility to have the same weekday more than once
            in a week.
        """
        req = ""
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        for i in range(1, 8):
            req=user.create_trainingday(workout_id, description=f"Day {i}", day_no=1)
        assert req[0]==False


    @pytest.mark.parametrize("description_len,day_no,result", [(100, 1, True), (101, 1, False)])
    def test_add_trainingday_with_long_description(self, user, description_len, day_no, result):
        """
        This test verifies if a training day can only be created if the description length is less or equal to 100.
        Steps:
            creates a workout
            checks if the workout was created successfully
            creates training day using the workout id
            checks if the request has the expected value
        Expected result: Training day created successfully if the length of the description is less or equal to 100.
        """
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        assert user.create_trainingday(workout_id, random_text_generator(description_len), day_no)[0] == result


    def test_add_exercise_to_an_inexisting_trainingday(self, user):
        """
        This test function checks the case of adding an exercise to an inexistent training day.
        Steps:
            generates a random training day id until this is unique
            adds the exercise to a training day using the generated training day id
            checks that the request was unsuccessful
        """
        day_id = random_number_generator(6)
        while day_id in get_existing_entities(user, 'day/'):
            day_id = random_number_generator(6)
        assert user.add_exercise(day_id, ex_id=325, sets=4, reps=12, repetition_unit=1, weight_unit=1)[0] == False


    def test_add_inexisting_exercise(self, user):
        """
        This test function checks the case of adding an inexistent exercise to a training day.
        Steps:
        creates a workout
            checks if the workout was created successfully
            creates a training day using the workout id
            checks if the training day was created successfully
            generates a random exercise id until this is an inexistent one
            adds the exercise to a training day using the generated training day id
            checks that the request was unsuccessful.
        """
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        exercise_id = random_number_generator(4)
        while exercise_id in get_existing_entities(user, 'exercise/'):
            exercise_id = random_number_generator(4)
        assert user.add_exercise(day_id, exercise_id, sets=4, reps=12, repetition_unit=1, weight_unit=1)[0] == False


    def test_add_trainingday_with_invalid_parameters(self, user):
        """
        This test verify the create training day function using invalid values for the parameters.
        Steps:
            creates a workout
            checks if the workout was created successfully
            creates training day using the workout id and invalid values for the description and day number.
            checks that the request was unsuccessful.
        Expected result:
            Training day not created because the description should be a string not an integer and day number id should
            be an integer and not a string.
        """
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        assert user.create_trainingday(workout_id, description=random_text_generator(100), day_no=random_text_generator(2))[0] == False


    def test_add_exercise_without_all_parameters(self, user):
        """
        This test function checks if you can add an exercise without providing same parameters.
        Steps:
            creates a workout
            checks if the workout was created successfully
            creates a training day using the workout id
            checks if the training day was created successfully
            adds an exercise without providing values for : number of sets,
                                                            number of repetitons,
                                                            repetition unit id,
                                                            weight unit id.
            checks that the request was unsuccessful
        """
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_id = req_workout[1].get("id")
        req_day = user.create_trainingday(workout_id, "Test_Day", 1)
        assert req_day[0] == True
        day_id = req_day[1].get("id")
        exercise_id = random.choice([i["id"] for i in user.get_info('exercise/')[1].get("results")])
        assert user.add_exercise(day_id, exercise_id, sets="", reps="", repetition_unit="", weight_unit="")[0] == False


    def test_delete_an_inexisting_workout(self, user):
        """
        This test function checks the case of trying to delete an inexistent workout.
        Steps:
            generates a random workout id until this is unique
            deletes the workout using the workout name corresponding to the generated workout id
            checks that the request was unsuccessful
        """
        workout_name = random_text_generator(10)
        while workout_name in [i['name'] for i in user.get_info('workout/')[1].get("results")]:
            workout_name = random_text_generator(10)
        assert user.delete_workout(workout_name)[0] == False


    def test_delete_an_inexiting_trainingday(self, user):
        """
        This test function checks the case of trying to delete an inexistent training day.
        Steps:
            creates a workout
            checks if the workout was created successfully
            generates a random training day id
            deletes the training day using the workout name and the generated training day id
            checks that the request was unsuccessful
        """
        req_workout = user.create_workout("Test_Workout")
        assert req_workout[0] == True
        workout_name = req_workout[1].get("name")
        day_id = random_text_generator(10)
        assert user.delete_trainingday(workout_name, day=day_id)[0] == False
