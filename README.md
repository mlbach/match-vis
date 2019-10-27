# MatchVis
Use Python to create simple animated visualizations of football matches from positional data.

## How to use
Clone the repository, install all libraries from requirements.txt and run

`python visualize.py --match-logs "data/Match_426_1.log"`

*Table 1: Listing of all command line arguments that visualize.py accepts*

Argument | Type | Meaning
---------|------|--------
`--match-logs` | string | Pass path and filename of the match logs you want to visualize
`--file-sequence` | boolean (optional) | Set to true if you want to pass visualize multiple game logs from one recording session. The script will check the directory given in `--match-logs` for other files of the same type and name prefix, i.e. all files named "Match_426_**{suffix}**.log"
`--save-video` | boolean (optional) | Set to true if you want to save the visualizations to a video file instead of displaying it from command line
`--player-focus` | string (optional) | Speficy a valid external ID (i.e. `A_0144`)of a player contained in the match logs to visualize all of his movements
