# Preprocessing Notes

once you pull these changes onto your local machine, please read this!

## Java

here are the **compilation instructions**
to run the preprocessing properly...
1. compile Driver.java and JavaPreprocessor.java together
2. run Driver.java

in Driver.java, you find this line of code on Line 6...

`String testingFile = "insertJavaFileHere.java";`

the Java file that is inserted here will be preprocessed. Once Driver.java is executed, a temporary file and folder are created on your computer that stores the preprocessed file. In your Windows directory, you can find them at...

*C:\Users\JoeSchmo\AppData\Local\Temp* 
the folder should be called *preprocesser_test(randomNumbers)* 
your temporary file should be contained within.

it might work the same way for Mac users? I dunno. Good luck with that ¯\(ツ)/¯

**Note:** it is important that the **Java file** is in the **same directory** as **Driver.java and JavaPreprocessor.java!** Otherwise, the program may not be able to find the file you are referencing, and it will get very angry at you.

the preprocessor works under the assumption that the inputted Java file is able to be compiled and executed properly. The contents of the Java file are arbitrary. Therefore, the preprocessor only checks if the inputted file can be compiled, but it does not run it! That creates a lot of problems that I am not smart enough to handle. 

## Python

For this preprocessor, you can just run PythonDriver.py. As long as the driver, preprocessor, and sample Python file are in the same directory, it should work!

The algorithm is mostly the same, except indentation. Because Python is sensitive with indents, I altered the algorithm so that it gets rid of excess whitespaces but preserves necessary indents

Reach out to me if you have any questions! ;)

- Manzi