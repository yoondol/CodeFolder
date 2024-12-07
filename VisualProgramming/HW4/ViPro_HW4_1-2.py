class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def print_dog(self):
        print(f"{self.name}:{self.age}")
    
    def __str__(self):
        return f"{self.name}는 {self.age}살"
    
my_dog = Dog('Mango', 3)
my_dog.print_dog()
print(my_dog)