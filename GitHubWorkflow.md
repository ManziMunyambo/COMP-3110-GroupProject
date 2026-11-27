# GitHub Workflow in Preprocessor

I always forget how to do this shit. Ima just write it down

## Step 1 - Commit Locally
git checkout preprocessor (make sure your code is in here!)
git add file1 file2 file3 ...
git commit -m "Look at this cool thing I did!"

## Step 2 - Push to the Remote Branch
git push origin preprocessor

## Step 3 - Merge Updates from main to preprocessor Locally
git checkout main
git pull origin main
git checkout preprocessor 
git merge main