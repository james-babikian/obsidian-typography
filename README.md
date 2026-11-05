# Typography for Minimal

This is the CSS snippet I use to make my Obsidian notes look more like a printed book. It's made for the [Minimal](https://github.com/kepano/obsidian-minimal) theme, and each part can be switched on or off with the [Style Settings](https://github.com/mgmeyers/obsidian-style-settings) plugin.

## What it does

Running text gets old-style figures. Tables, code and numbered lists keep lining figures, so columns line up. Footnote references use the font's superior figures, without Obsidian's brackets, which keeps the lines evenly spaced. Tables get a firm rule above and below, a thin rule under the header and nothing between rows.

Smaller things:

- no lone word on the last line of a paragraph
- balanced headings
- highlights that look like a marker stroke
- finer link underlines
- slashed zero in code
- section breaks as three asterisks
- Live Preview spaced like Reading view (headings, quotes, callouts)
- small caps for the first line after each H2, if you want it

Some fonts are embedded in the snippet so they reach the phone through Obsidian Sync. You can pick different fonts for the computer and the phone, or keep Obsidian's own.

Text size, line width and line height are left to Minimal Theme Settings, and headings aren't restyled. PDF export gets the same typography.

## Installing

1. Download `typography.css` and `OFL.txt`.
2. In Obsidian, open Settings → Appearance → CSS snippets and click the folder icon. Put both files in the folder that opens.
3. Back in Obsidian, reload the snippet list and turn on **typography**.
4. Install the Style Settings plugin, then go to Settings → Style Settings → **Typography**. Fonts are under **Fonts**; the other groups hold the switches. Choose fonts here, not in Appearance → Font, because the phone can't see fonts inside a snippet.

## My settings

`style-settings.json` holds my own Style Settings, for Minimal and for this snippet. The snippet works without it. I tuned the typography with these settings on, though, so this is the look I actually see. It sets warm paper-coloured backgrounds, a deep crimson accent, my heading sizes and weights, and my spacing.

To import it, go to Settings → Style Settings → **Import** and paste the file's contents. It overwrites your current values for those settings, so export yours first.

## Rebuilding

`typography.css` is built from `snippets/` and `fonts/` by `python tools/build_fonts.py`, which needs [fontTools](https://github.com/fonttools/fonttools) with brotli. The script trims the fonts to Latin-script languages, keeps their OpenType features and writes the snippet to `private/snippets/`. 

## Licences

My CSS, the build script and the settings file are MIT (see `LICENSE`). The fonts are under the SIL Open Font License, so `OFL.txt` has to go with the snippet. Thanks to their designers:

- Alegreya and Alegreya Sans by Juan Pablo del Peral, Huerta Tipográfica
- JetBrains Mono by JetBrains
- Courier Prime by Alan Dague-Greene for Quote-Unquote Apps
- iA Writer Mono S by Information Architects, based on IBM Plex Mono. The licence reserves the names "iA Writer" and "Plex" for unmodified copies, so the snippet calls it Quill Mono.
