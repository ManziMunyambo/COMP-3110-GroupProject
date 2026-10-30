import java.nio.file.Path;
import java.nio.file.Paths;

public class Driver {
    public static void main(String[] args){
        String testingFile = "RPSJava.java";
        Path sampleFile = Paths.get(testingFile);
        //^ the file should be another Java file in the same directory as Driver and Javapreprocessor, e.x. RPSJava.java
        System.out.println("\nRunning preprocessor on " + testingFile);

        String result = JavaPreprocessor.preprocessAndRun(sampleFile);

        //after the above line is executed, the program freezes. How to fix?
        //OR, the program takes an extremely long time to do preprocessing. Will need to try a different approoach

        if(result != null){
            System.out.println("\n\n--- Processing Complete! ---\nPreprocessed Code:\n");
            System.out.println(result + "\n");
        } else{
            System.out.println("\n\n--- Processing Failed! ---\nNULL was returned\n");
        }

        /**compile Driver and JavaPreprocessor together
         * javac Driver.java JavaPreprocessor.java
         * java Driver 
        */
    }
}
