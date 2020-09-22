import json
from json import JSONEncoder

class Student:
    def __init__(self, rollNumber, name):
        self.rollNumber, self.name = rollNumber, name

    def print_roll(self):
        print(self.rollNumber)

class StudentEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

def customStudentDecoder(studentDict):
    return Student(**studentDict)

student = Student(1, "Emma")

# dumps() produces JSON in native str format. if you want to writ it in file use dump()
studentJson = json.dumps(student, indent=4, cls=StudentEncoder)
print("Student JSON")
print(studentJson)

# Parse JSON into an object with attributes corresponding to dict keys.
studObj = json.loads(studentJson, object_hook=customStudentDecoder)

print("After Converting JSON Data into Custom Python Object")
print(studObj.rollNumber, studObj.name)

studObj.print_roll()