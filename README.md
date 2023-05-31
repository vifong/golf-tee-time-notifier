## GolfNow Tee Time Notifier

This workflow scrapes the [GolfNow website](https://www.golfnow.com/), extracts the open tee times given some parameters (golf courses, # of players, time cutoff, days of the week, etc.), and sends an SMS text message when a new tee time of interest is available.

Currently it's built for our specific use case, but I can abstract the parameters in the future to make the workflow more easily customized.

### How does it work
The workflow uses the following tools:
* __Selenium__ web driver to spin up a browser and scrape the webpage.
* __GitHub Actions__ to upload/download data snapshots and send [Twilio SMS notifications](https://github.com/marketplace/actions/twilio-sms)).
* __Cloudflare__ worker to dispatch the workflow on cron schedule, because [GitHub Actions scheduling isn't very reliable](https://upptime.js.org/blog/2021/01/22/github-actions-schedule-not-working/).
  * Inspiration for the solution found [here](https://github.com/upptime/upptime/issues/42#issuecomment-840264035)
