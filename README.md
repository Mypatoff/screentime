# screentime

Small Linux (X11) screen-time tracker with a local web dashboard.

- `tracker.py` checks the active window every 5 seconds and adds the time to a SQLite database
  (`~/.local/share/screentime/data.db`). It skips time when you have been idle for 2 minutes.
- `dashboard.py` is a Flask page that shows the totals per app for today and for the last 7 days.
- `systemd/` has user services that start both at login.

## Open the dashboard
Go to **http://127.0.0.1:5000** in a browser (`/week` for the last 7 days). It only listens on your own
computer.

## Install
```
sudo pacman -S xdotool xprintidle python-flask      # or: pip install -r requirements.txt
git clone https://github.com/Mypatoff/screentime.git ~/screentime
mkdir -p ~/.config/systemd/user
cp ~/screentime/systemd/*.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now screentime-tracker screentime-dashboard
```

## Manage
```
systemctl --user status screentime-tracker screentime-dashboard
systemctl --user restart screentime-tracker
journalctl --user -u screentime-tracker -n 20
```
