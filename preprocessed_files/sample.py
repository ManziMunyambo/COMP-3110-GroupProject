#get the user's name and age and see if they are old or not

print("Yo\n")
name = input("What is your name? -> ")
age = int(input       ("How old are you? -> "))

if age < 67:
    years_left = 67 -   age
    print(f"Hey {name}, you got {years_left} years until you turn 67!")
else:
    print(f"Hey {name}, you are 67 years old or older.")