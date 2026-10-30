import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path; 
import java.util.List;
import java.util.concurrent.TimeUnit;

public class JavaPreprocessor{
    public static String preprocessAndRun(Path sourcePath){
        try{
            //read all the lines from the source file
            System.out.println("\nReading file lines...");
            List<String> lines = Files.readAllLines(sourcePath);
            StringBuilder processedCode = new StringBuilder();

            for(String line : lines){
                //step 4, handling comments by splitting them into separate lines
                int commentIndex = line.indexOf("//");
                if(commentIndex != -1){
                    String comment = line.substring(commentIndex);
                    processedCode.append("\n").append(comment).append("\n");
                    line = line.substring(0, commentIndex);
                }

                //steps 2 and 3, removing indentation and turning multiple spaces into one
                String cleanedLine = line.trim().replace("\\s+", " ");
                if(!cleanedLine.isEmpty()){
                    processedCode.append(cleanedLine).append(" ");
                }
            }

            String finalCode = processedCode.toString().trim();
            System.out.println("Preprocessing complete! Starting sanity check...");
            //step 5, make sure the code can still compile. Sanity check
            if(testCode(finalCode, sourcePath.getFileName().toString())){
                return finalCode; //step 6, return the new file
            } else{
                return null;
            }
        } catch (IOException e){
            System.out.println("\nError reading file: " + e.getMessage());
            return null;
        }
    }

    public static boolean testCode(String processedCode, String originalFileName){
        try{
            //step 1, write processedCode to a temp file
            Path tempDir = Files.createTempDirectory("preprocessor_test");
            Path tempFile = tempDir.resolve(originalFileName);
            Files.writeString(tempFile, processedCode);
            System.out.println("Wrote temporary file to " + tempFile.toAbsolutePath() + "...");

            //step 2, compile with javac
            ProcessBuilder compileProcess = new ProcessBuilder("javac", tempFile.toAbsolutePath().toString());
            compileProcess.redirectErrorStream(true);
            Process compile = compileProcess.start();

            boolean isCompileFinished = compile.waitFor(5, TimeUnit.SECONDS);
            if(!isCompileFinished){
                System.out.println("\nCompilation timed out!");
                compile.destroy();
                return false;
            }

            int compileExitCode = compile.exitValue();
            if(compileExitCode != 0){
                System.out.println("\nSyntax check failed! Preprocessed file cannot compile ;(\nExit code: " + compileExitCode);
                return false;
            }
            else{
                System.out.println("Syntax check passed! Preprocessed code can successfully compile :)");
                return true;
            }
        } catch (IOException | InterruptedException e){
            System.out.println("\nSanity check execution failed!\nError: " + e.getMessage());
            return false;
        }
    }

    public static void main(String[] args){
        System.out.println("\n\nThis java file is meant for Driver.java. Run that instead!\n\n");
    }
}