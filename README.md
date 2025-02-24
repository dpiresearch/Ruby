# Initial work to identify and collect personas

ExperimentUsers.py - notebook where initial investigation started.
  - isolated user actions
  - Gather statistics on users, actions, and possible personas
  - Also has code to split up the filtered.csv into individual files <user_id>.txt

call_vertext_2.py - For each <user_id>.txt file, call Gemini to characterize the user and suggest personas
  - write results into <user_id>_response.txt files

At this point all files were uploaded into S3

create_personas.py - like call_vertext_2.py, but operating on s3 instead of local disk.  Skip _response files if already processed

create_persona_files.py - create persona.csv and user_persona.csv files.  These two files shoud hold users and their memberships to personas.

call_buyer_propensity.py - initial attempt at estimating buyer's propensity.
