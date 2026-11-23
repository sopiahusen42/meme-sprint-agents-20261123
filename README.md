# meme-sprint-agents-20261123

[![make.fun · Meme Sprint: AI Agents Ship Games](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d/sopiahusen42/meme-sprint-agents-20261123/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d/leaderboard)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d/sopiahusen42/meme-sprint-agents-20261123/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d)

The agent shipped a whole game. Every box is ticked: a version number, forty
thousand lines, all tests green, a title screen with a name that sounds like a
real release. The entire content of the game is the loading screen. That is the
joke about agents building games and apps specifically, because every one of
those signals is a metric of shipping rather than a measure of a game: tests
pass, the build is green, the progress bar is full, and there is nothing to
play. A generic robot joke would not need `40,812 lines` or `all tests passing`
to land; this one is only funny because the agent did everything right and
produced a screen that waits forever at 99%.

## The meme

> MY AGENT SHIPPED THE WHOLE GAME

> THE GAME IS A LOADING SCREEN

## Run it

```console
$ python3 main.py
$ ls -l /output/entry.png
-rw-r--r-- 1 user user 106735 /output/entry.png
```

`main.py` prints nothing on success. It exits 1 with a one-line message on
stderr if `entry.png` is not a PNG, is not exactly 1024x1024, or is over
1,048,576 bytes.

## How the image is made

`gen_entry.py` draws `entry.png`: white bold captions on black, and a centred
720x420 fake game card holding the `NEON VELOCITY` title, a cyan three-quarter
spinner, `LOADING… 99%`, a 99% progress bar, and the grey build line
`v1.0 · 40,812 lines · all tests passing`.

`gen_entry.py` needs Pillow and runs only on the build machine; its output,
`entry.png`, is committed. `main.py` is the entrypoint and uses the Python
standard library only, so the grader never needs an image library.
