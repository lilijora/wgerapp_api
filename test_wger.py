from wger.py import Api

user = Api("Token ffb50c5ea4d743aefa7540aa176590d7de57c907", "lilijora", "belive2021")
def test_get():
    assert isinstance(user.get_info('day/'), dict) == True

def test_post():
    assert user.post_info('workout/',{"id": "","creation_date": "","name": "test_workout","description": ""})!=False

def test_create_workouts():
    assert user.create_workout("Test_Workout")!=False
    assert any(i for i in user.get_info("workout/").get("results") if i["name"]=="Test_Workout")==True
