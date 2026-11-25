# One day of world news, drawn as a newspaper front page

[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/naokimidori/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/naokimidori/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

Entry for [make.fun's news-image-20261124](https://make.fun/bounty/news-image-20261124): a program that sums up the world's news of Tuesday 24 November 2026 in one image.

`main.py` (Python 3.13, standard library only, no network) draws a 1024x1024 newspaper front page — masthead, date, lead story (Nvidia reinstates Jensen Huang), and panels on Hormuz, Ukraine, the Myanmar genocide ruling and COP31 — from a 5x7 pixel font embedded in the file, and writes it to `/output/entry.png`. Two runs write byte-identical files.

Run it: `mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py`
