import requests
from datetime import datetime
import json 

def get_seconds(string_date_finish, string_date_start):
    # Format the dates
    date_format1 = string_date_finish[:10] + ' ' + string_date_finish[12:19]
    date_format2 = string_date_start[:10] + ' ' + string_date_start[12:19]
    # Convert String to data Time
    date1 = datetime.strptime(date_format1, '%Y-%m-%d %H:%M:%S')
    date2 = datetime.strptime(date_format2, '%Y-%m-%d %H:%M:%S')
    diff = (date1-date2)
    #Return the seconds
    return diff.total_seconds()


def build_user_sessions(activities_json):
    # I get the array from the dictionary
    activities_array = activities_json['activities']
    users_sessions = {}
    # First and only loop in the function. The complexity is O(n).
    for activities in activities_array:
        #If the key exists in the dictionary I compare to the last activity submitted
        if (activities["user_id"] in users_sessions):
            # I get the array associated to the key so I can use it
            aux = users_sessions[activities['user_id']]
            # I use my function get_seconds to check if the time between both activities is greater than five minutes
            if ( get_seconds(activities["answered_at"] , aux[-1]["ended_at"]) < 300 ) :
                aux[-1]["ended_at"] = activities['answered_at']
                aux[-1]["activity_ids"].append(activities["id"])
                # I compute the durations in seconds
                aux[-1]["duration_seconds"] = get_seconds(activities["answered_at"], aux[-1]["started_at"])
            else:
                # more than 5 minutes have elapsed between the two dates, we add it as a new session
                aux.append({ "ended_at" : activities["answered_at"], "started_at" : activities["first_seen_at"], "activity_ids" : [activities["id"]], "duration_seconds": get_seconds(activities["answered_at"] , activities["first_seen_at"]) })
            # I assign the array again to its key in the dictionary
            users_sessions[activities['user_id']] = aux
        else:
            #It´s a new session from a new user
            users_sessions[activities['user_id']] = [ {"ended_at" : activities["answered_at"], "started_at" : activities["first_seen_at"], "activity_ids" : [activities["id"]], "duration_seconds": get_seconds(activities["answered_at"] , activities["first_seen_at"])  } ]
      
    return users_sessions

def main():

    user_sessions = {}
    activities_response = requests.get("https://api.slangapp.com/challenges/v1/activities",headers={"Authorization": "Basic MTQ0Om5aRUlBYkgvaFFFR2RNRnVDYnpOZlU2cmt2eUEyclVWWmpNeTZaRVFMQTQ9"}) # ← replace with your key
    
    if activities_response.status_code == requests.codes.ok:
        # Succes (Code 200)
        user_sessions = {"user_sessions": build_user_sessions(activities_response.json())}
    else:
        #Fail
        return False
    
    print(json.dumps(user_sessions, indent=3))

    send = requests.post("https://api.slangapp.com/challenges/v1/activities/sessions",
    headers={"Authorization": "Basic MTQ0Om5aRUlBYkgvaFFFR2RNRnVDYnpOZlU2cmt2eUEyclVWWmpNeTZaRVFMQTQ9"}, 
    json=user_sessions) # Keep in mind this should be a dictionary {“user_sessions”: {...}}

    if send.status_code == 204:
        # Succes (Code 204)
        return True
    else:
        #Fail
        return False

if __name__ == "__main__":
    main()