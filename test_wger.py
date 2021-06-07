from wger import Api
import pytest


@pytest.fixture
def user():
    login = Api("Token ffb50c5ea4d743aefa7540aa176590d7de57c907", "lilijora", "belive2021")
    return login


def delete_all_workouts(user):
    return [user.delete_workout(i["name"]) for i in user.get_info("workout/")[1].get("results")]


def create_test_workout(user):
    req = user.create_workout("Test_Workout")
    return req[1].get("id")


def create_test_trainingdays(user):
    req = user.create_trainingday(create_test_workout(user), "Test_Day", 1)
    return req[1].get("id")


####POSITIVE TESTS####
def test_add_one_workout(user):
    delete_all_workouts(user)
    assert user.create_workout()[0] == True


def test_add_one_workout_with_name_and_description(user):
    delete_all_workouts(user)
    assert user.create_workout("Workout_Test1", "First Test")[0] == True


def test_add_one_workout_with_special_name_and_long_description(user):
    delete_all_workouts(user)
    assert user.create_workout("&&&&&******Workout_Test2####!!!!!!]]]]]]",
                               "It is a long established fact that a reader will be distracted"
                               " by the readable content of a page when looking at its layout."
                               " The point of using Lorem Ipsum is that it has a more-or-less normal"
                               " distribution of letters, as opposed to using 'Content here, content here'"
                               ", making it look like readable English. Many desktop publishing packages"
                               " and web page editors now use Lorem Ipsum as their default model text,"
                               " and a search for 'lorem ipsum' will uncover many web sites still in their"
                               " infancy. Various versions have evolved over the years, sometimes by accident"
                               ", sometimes on purpose (injected humour and the like)"
                               )[0] == True


# @pytest.mark.skip
def test_add_a_large_number_of_workouts(user):
    delete_all_workouts(user)
    assert all(user.create_workout(f"Workout {i}")[0] for i in range(1, 53)) == True \
           and user.get_info('workout/')[1].get("count") == 52


def test_add_trainingday(user):
    delete_all_workouts(user)
    workout_id = create_test_workout(user)
    assert user.create_trainingday(workout_id, "First Day", 1)[0] == True


def test_add_exercises(user):
    delete_all_workouts(user)
    day_id = create_test_trainingdays(user)
    request_one = user.add_exercise(day_id, 325, 4, 12, 1, 1)
    assert request_one[0] == True
    request_two = user.add_exercise(day_id, 325, 4, 12, 1, 1)
    assert request_two[0] == True


####NEGATIVE TESTS####
def test_add_more_than_10_sets(user):
    delete_all_workouts(user)
    day_id = create_test_trainingdays(user)
    assert user.add_exercise(day_id, 24, 12, 12, 1, 1)[0] == True


def test_add_trainingday_to_an_inexisting_workout(user):
    delete_all_workouts(user)
    assert user.create_trainingday(100, "Test_Day", 1)[0] == True


def test_add_more_than_7_days_to_one_workout(user):
    delete_all_workouts(user)
    workout_id = create_test_workout(user)
    for i in range(1, 10):
        user.create_trainingday(workout_id, f"Day {i}", i)
    assert len(user.get_info('day/')[1].get("results")) == 9


def test_add_trainingday_with_long_description(user):
    delete_all_workouts(user)
    workout_id = create_test_workout(user)
    assert user.create_trainingday(workout_id,
                                   "It is a long established fact that a reader will be distracted" 
                                   " by the readable content of a page when looking at its layout."
                                   " The point of using Lorem Ipsum is that it has a more-or-less normal"
                                   " distribution of letters, as opposed to using 'Content here, content here'"
                                   ", making it look like readable English. Many desktop publishing packages"
                                   " and web page editors now use Lorem Ipsum as their default model text,"
                                   " and a search for 'lorem ipsum' will uncover many web sites still in their"
                                   " infancy. Various versions have evolved over the years, sometimes by accident"
                                   ", sometimes on purpose (injected humour and the like)",
                                   1,
                                   )[0] == True


def test_add_exercise_to_an_inexisting_trainingday(user):
    delete_all_workouts(user)
    assert user.add_exercise(100, 325, 4, 12, 1, 1)[0] == True


def test_add_inexisting_exercise(user):
    delete_all_workouts(user)
    day_id = create_test_trainingdays(user)
    assert user.add_exercise(day_id, 500000, 4, 12, 1, 1)[0] == True


def test_add_trainingday_with_invalid_parameters(user):
    delete_all_workouts(user)
    workout_id = create_test_workout(user)
    assert user.create_trainingday(workout_id, 100, -10)[0] == True


def test_add_exercise_without_all_parameters(user):
    delete_all_workouts(user)
    day_id = create_test_trainingdays(user)
    assert user.add_exercise(day_id, 25,"","","","")[0] == True


def test_delete_an_inexisting_workout(user):
    delete_all_workouts(user)
    assert user.delete_workout("Invalid_workout")[0] == True


def test_delete_an_inexiting_trainingday(user):
    delete_all_workouts(user)
    create_test_workout(user)
    assert user.delete_trainingday("Test_Workout", "First_Day")[0] == True