# Sprites

Put one image per Pokémon in this folder, named by **national dex number** with no leading zeros:

```
sprites/1.png
sprites/25.png
sprites/493.png
...
sprites/1025.png
```

Only the Pokémon currently matched to a team are needed. The detail view and each card show the dex number in the empty slot, so you can see which files are missing.

If your images aren't PNGs, change `SPRITE_EXT` near the top of the script in `index.html`. If a file is missing, its slot falls back to showing the dex number.
