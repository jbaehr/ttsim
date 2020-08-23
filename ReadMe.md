# TTSim -- a TipToy Simulator

## About

- web front end for [tttool](http://tttool.entropia.de)'s `play` command
- serves SVG files, hit-test on click, extracts the pattern, feeds `tttool`
- requires the Inkscape-based workflow as outlined below

## Workflow

- Use [Inkscape](https://inkscape.org) to create your TipToy Sheets as SVG
  (opposed to the GIMP-based raster image approach).
  - You may load a raster image in a background layer.
  - For the OIDs, draw a path and fill it with a pattern created by `tttool`.
- use `tttool` as usual to work on your GME file.
- export the oid table as SVG (use `--image-format SVG` for the `oid-table` command).
- use the `inject-patterns.py` to inject the patterns from the oid-table SVG into your target SVG.
  (this can be done over and over again, which allows to work on the YAML and SVG in parallel.)
- use `ttsim.py` to fire up a local web server to try out your TipToy Sheet in a browser
  (there you can click onto the image instead of hacking numbers into `tttool play`).
