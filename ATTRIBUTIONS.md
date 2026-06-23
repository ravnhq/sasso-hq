# Attributions

Several skills in this repo are vendored from
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT) and adapted for
org use. The MIT license requires that the copyright notice below be preserved.

**Vendored skills:**

- `plugins/hq-core/skills/`: `grill-me`, `grill-with-docs`, `to-prd`, `to-issues`, `handoff`
- `plugins/codebase-toolkit/skills/`: `improve-codebase-architecture`, `write-a-skill`, `triage`, `zoom-out`, `prototype`
- `plugins/fun/skills/`: `caveman`

## External tools driven (not vendored)

Some skills shell out to external tools that we install and drive but do **not**
vendor or redistribute — none of their source ships in this repo, so their
license text isn't reproduced here:

- **[graphify](https://github.com/safishamsi/graphify)** (MIT, © Safi Shamsi) —
  the `map-the-codebase` skill installs the `graphifyy` CLI via
  `uv tool install graphifyy` and drives the binary to build an offline code
  graph. We call it; we don't bundle it.

---

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
