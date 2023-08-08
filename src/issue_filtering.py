from datetime import datetime, timedelta


def is_issue_completed(perceval_json: dict) -> bool:
    """ Return 'True' if the json issue correspond to a merged pull request or a fixed bug issue """
    data = perceval_json['data']

    # Issues and pull_request should be 'closed'
    if data['state'] != 'closed':
        return False

    # Pull requests should be merged ('merged_at' != None)
    if 'pull_request' in data and data['pull_request']['merged_at']:
        return True

    # Issues should be labelled as 'bug' and fixed
    for label in data['labels']:
        if label['name'] == 'bug':
            return data['state_reason'] == 'completed'

    return False


def get_interarrivals(perceval_json: dict) -> list:
    """ Compute the comments interrarrivals from the json object """
    data = perceval_json['data']
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    interarrivals = []

    # Interarrivals computation
    prev = datetime.strptime(data['created_at'], fmt)                # Issue creation datetime
    closure = datetime.strptime(data['closed_at'], fmt)              # Issue closure/merging datetime
    for elem in data['comments_data']:                               # For each comment of this issue
        curr = datetime.strptime(elem['created_at'], fmt)            # Comment creation datetime
        if curr > closure: break                                     # Ignore comments after the closure of the issue
        hours = round((curr-prev).total_seconds()/3600, ndigits=3)   # Interarrival converted in hours
        interarrivals.append(hours)
        prev = curr
    hours = round((closure-prev).total_seconds()/3600, ndigits=3)    # Last interarrival with the closure datetime
    interarrivals.append(hours)

    return interarrivals


def is_issue_of_interest(issue: dict, min_interarrival: timedelta, max_burst: timedelta) -> bool:
    """
    Return True if both of the following conditions are satisfied:
      1) issue has a closure time or a comment with a large interarrival (beyond min_interarrival)
      2) after the comment with large interarrival, the issue should be closed rapidly (within max_burst)

    :param issue: A json element of an issue having an additional field: ['data']['interarrivals']
    :param min_interarrival: Lower threshold for interarrivals
    :param max_burst: Upper threshold for burst
    """

    data = issue['data']
    fmt = "%Y-%m-%dT%H:%M:%SZ"

    # Get the indices of the interarrivals beyond the threshold
    threshold = min_interarrival.total_seconds()/3600  # in hours
    interarrivals_beyond = [data['interarrivals'].index(elem) for elem in data['interarrivals'] if elem > threshold]

    # Return False if all interarrivals are lower than the treshold
    if len(interarrivals_beyond) == 0:
        return False

    # Return True if the last interarrival (i.e. diff between closure/merging timestamp and comment) is beyond the
    # threshold. No needs to check for the burst time.
    if len(data['interarrivals'])-1 in interarrivals_beyond:
        return True

    # Get the last comment related to a large interarrival
    last_late_comment = data['comments_data'][interarrivals_beyond[-1]]

    # Check if the last late comment is followed by a burst (rapid closure)
    iss_closure = datetime.strptime(data['closed_at'], fmt)
    cmt_creation = datetime.strptime(last_late_comment['created_at'], fmt)
    diff = iss_closure - cmt_creation
    return diff <= max_burst
