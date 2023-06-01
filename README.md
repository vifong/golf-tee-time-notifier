## ⛳ GolfNow Tee Time Notifier ⏰

This workflow scrapes the [GolfNow website](https://www.golfnow.com/), extracts the open tee times given various parameters (golf courses, # of players, time cutoff, days of the week, etc.), and sends an SMS text message when a new tee time of interest is available.

### 🛠️ How does it work
The workflow uses the following tools:
* __Selenium__ web driver to spin up a browser and scrape the webpage.
* __GitHub Actions__ to upload/download data snapshots and send __[Twilio SMS notifications](https://github.com/marketplace/actions/twilio-sms)__.
* __Cloudflare__ worker to dispatch the workflow on cron schedule.
  * _Note: [GitHub Actions scheduling isn't very reliable](https://upptime.js.org/blog/2021/01/22/github-actions-schedule-not-working/). See inspiration for the solution [here](https://github.com/upptime/upptime/issues/42#issuecomment-840264035)._

#### 🚧 Constaints
Currently it's built for our specific use case, but in the future I can abstract the parameter to make the workflow more generalizable:
* Hardcoded 5 golf courses of interest.
* Only scrapes weekends within the next 7 days.
* Filters for tee times between 7:45am and 3pm.
* Filters for at least 2 golfer spots available.
* Only sends a text message if there are new tee times added when comparing to the previous notification.
* Workflow runs every 2 minutes, scheduled via Cloudflare worker.


#### 📁 Files
```
golfteetimenotifier/
  - main.py              # main script: computes the target dates, runs the scraper (one thread per golf course), and aggregates the results
  - scraper.py           # launches Selenium, navigates and scrapes the webpage, and cleans the data and collates into a pandas DataFrame 
  - snapshot_handler.py  # downloads the previous snapshot and compares with the current data to determine diffs
  - message_writer.py    # crafts the notification message text

.github/
  - scrape.yml           # workflow definition: download/cache dependencies, download/upload snapshots, run script, and send SMS
 
requirements.txt         # list of python dependencies
message.txt              # message text to send; if does not exist, do not send a text
snapshot.pickle          # serialized DataFrame of the snapshot
snapshot.csv             # human-readable version of the snapshot (for debugging)
```

#### 📲 Example text message
```
*** Tee Times Alert! ***

BALBOA
Sat, Jun 03 [2:00PM(4), 2:40PM(2)]

ENCINO
Sun, Jun 04 [2:25PM(4)]

RANCHO PARK
Sat, Jun 03 [7:50AM(3), 11:30AM(2), 3:00PM(4)]
Sun, Jun 04 [1:40PM(2)]
```
