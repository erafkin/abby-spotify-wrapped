# Abby's Spotify Wrapped

Abby didn't like her spotify wrapped so this pings the API for a time-frame's (`short_term`, `medium_term`, `long_term`) worth of data and downloads to CSVs. There is a notebook to explore them. Google says that short is around a month, medium is around 6 months, and long is more than a year, maybe multiple years.

## to run
This project has been developed in Python 3.11.6
### set up environmnet
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### set up account
Go to the [Spotify Developer's Dashboard](https://developer.spotify.com/) and register a new application. Select "web api" as the application that will use Spotify api. Put the following values into a `.env` in the root:
```bash
SPOTIPY_CLIENT_ID=<your client id>
SPOTIPY_CLIENT_SECRET=<your secret id>
SPOTIPY_REDIRECT_URI=<callback url>
```
### run
```bash
python get_spotify_info.py <output_folder> [--term ]
```
then explore in `spotify_wrapped.ipynb`