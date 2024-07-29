# SPPU Result Extractor
This simple python script uses the provided csv file containting the Seat No, Student Name and Mother Name to download the results on a mass scale. You can download SPPU results of hundreads or thousands of students. This script is currently working on only single thread and could be adjusted to work on multiple thread to save time and make requests in parallel. 

I use SPPU [official website](http://unipune.ac.in/)'s backend api to download these results. This is not an intended functionality of this api.

This could be illegal due to excesive stress on unipune server and this script is only for demonstration puposes.

Use it at your own risk.

Anyways, heres how to use it

# Usage

- Go to unipune [result page](https://onlineresults.unipune.ac.in/Result/Dashboard/Default)
- Open your dev tools and navigate to the networks tab
- Click on "Go for Results" on the course you want to extract results from
- A "ViewResultpop" request would be sent, click on that request in network tab
- Navigate to "Payload"
- Copy the PatternName and PatternID values and paste them into the script at respective positions
- Start the script, This will start downloading results in current folder.
- I recommend you not do this, this is probably illegal.

# Todo list
- [ ] Implement course selection from user at start
- [ ] Get the pattern id and pattern name automatically
- [ ] Make script run in parallel
- [ ] Download the results in specified folder or create a folder to store results
