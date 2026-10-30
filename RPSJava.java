//a simple rock paper scissors game that's played in console
//meant to test preprocessing Java files

import java.util.Random; 
import java.util.Scanner; 

public class RPSJava{
    public static void main(String[] args){
        //creating objects
        Scanner input = new Scanner(System.in);
        Random rng = new Random();
        System.out.print("--- ROCK PAPER SCISSORS ---");
        String userChoice = "quit";

        //Game loop
        do{
            //asking user for their choice
            System.out.print("\n\n* Rock\n* Paper\n* Scissors\nEnter your choice --> ");
            userChoice = input.nextLine().toLowerCase();

            //validate userChoice 
            while(!userChoice.equals("rock") && !userChoice.equals("paper") && !userChoice.equals("scissors")){
                System.out.print("\nInvalid choice. Please choose rock, paper, or scissors -> ");
                userChoice = input.nextLine().toLowerCase();
            }
            System.out.println("\nUser chose " + userChoice + "!");

            //computer randomly chooses an option
            int rand = rng.nextInt(1,3);
            String compChoice = "empty";

            switch(rand){
                case 1:
                    compChoice = "rock";
                    break;

                case 2:
                    compChoice = "paper";
                    break;

                case 3:
                    compChoice = "scissors";
                    break;

                default:
                    System.out.print("\nProgram chose an invalid value. Starting over...");
                    break;
            }
            System.out.println("Computer chose " + compChoice + "!");

            //if-else tree that decides the winner
            if(userChoice.equals("rock")){
                if(compChoice.equals("rock")){System.out.print("It's a draw!");}
                else if(compChoice.equals("paper")){System.out.print("Computer wins!");}
                else if(compChoice.equals("scissors")){System.out.print("User wins!");}
            } else if(userChoice.equals("paper")){
                if(compChoice.equals("rock")){System.out.print("User wins!");}
                else if(compChoice.equals("paper")){System.out.print("It's a draw!");}
                else if(compChoice.equals("scissors")){System.out.print("Computer wins!");}
            } else if(userChoice.equals("scissors")){
                if(compChoice.equals("rock")){System.out.print("Computer wins!");}
                else if(compChoice.equals("paper")){System.out.print("User wins!");}
                else if(compChoice.equals("scissors")){System.out.print("It's a draw!");}
            }
            
            //ask user if they want to play again
            System.out.print("\n\nPlay again? (Y/N) --> ");
            userChoice = input.nextLine().toLowerCase();
        } while(!userChoice.equals("n"));

        //end the game
        System.out.print("\n--- Thanks for playing! ---\n");
        input.close();
    }
}