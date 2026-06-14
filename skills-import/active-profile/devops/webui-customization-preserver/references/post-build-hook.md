# Post-Build Hook Strategy

Add to `package.json` > `scripts`:

```json
{
  "scripts": {
    "build": "vite build && npm run restore-customizations",
    "restore-customizations": "bash scripts/restore-customizations.sh"
  }
}
```

Then create `scripts/restore-customizations.sh`:

```bash
#!/bin/bash
# Runs AFTER vite build, copies custom assets into dist/
cp /mnt/c/Users/thadd/.hermes/images/logo.png dist/client/logo.png
cp /mnt/c/Users/thadd/.hermes/images/startrek\ badge.mp4 dist/client/assets/thinking-light.mp4
cp /mnt/c/Users/thadd/.hermes/images/startrek\ badge.mp4 dist/client/assets/thinking-dark.mp4
```

This makes `npm run build` automatically re-apply customizations after Vite overwrites `dist/`.
