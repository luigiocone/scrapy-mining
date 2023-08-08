import os
import sys
import json
import numpy as np
from datetime import timedelta
from issue_filtering import is_issue_completed, get_interarrivals, is_issue_of_interest


def get_thresholds(data: []):
    q1 = np.quantile(data, q=0.25)
    q3 = np.quantile(data, q=0.75)
    extreme_outlier = q3 + 3 * (q3 - q1)

    min_interarrival = timedelta(hours=extreme_outlier)
    max_burst = timedelta(hours=q3)

    print(q3)
    print(np.quantile(data, q=0.5))
    print(q1)
    exit(0)

    return min_interarrival, max_burst


if __name__ == "__main__":
    # Check the cmd arguments
    if len(sys.argv) < 3:
        print(f"USAGE: python {sys.argv[0]} <dataset> <output_dir>")
        exit(1)

    # Create output dir if it doesn't exist
    output_dir = sys.argv[2]
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Load in memory a json array of issues (from cmd or default)
    dataset = sys.argv[1]
    with open(dataset, mode='r', encoding='utf-8') as file:
        issues = json.load(file)

    # Filter completed issues
    completed = [i for i in issues if is_issue_completed(i)]
    print(f'Selected {len(completed)} issues out of {len(issues)}')

    # Get comments' interarrivals for each completed issue
    all_interarrivals = []
    for issue in completed:
        temp = get_interarrivals(issue)          # interarrivals from this issue's comments
        all_interarrivals += temp                # append these interarrivals in a list
        issue['data']['interarrivals'] = temp    # add a field 'interarrivals' to the json of the issue

    # Initialize the two thresholds and get the issues of interest
    t1, t2 = get_thresholds(all_interarrivals)
    filtered = [i for i in completed if is_issue_of_interest(i, t1, t2)]
    print(f'Interarrival threshold used: {t1}')
    print(f'Burst threshold used: {t2})')
    print()
    print('Using those thresholds to select issues of interest')
    print(f'Selected {len(filtered)} issues out of {len(completed)}')

    # Store interarrivals
    path = os.path.join(output_dir, 'interarrivals.txt')
    with open(path, mode='w', encoding="utf-8") as file:
        for i in all_interarrivals:
            file.write(str(i) + '\n')

    # Store all data about selected issues
    path = os.path.join(output_dir, 'issues.json')
    with open(path, mode='w', encoding="utf-8") as file:
        json.dump(filtered, file)

    # Store html url of all selected issues
    path = os.path.join(output_dir, 'html_urls.txt')
    with open(path, mode='w', encoding="utf-8") as file:
        for f in filtered:
            file.write(f['data']['html_url'] + '\n')
