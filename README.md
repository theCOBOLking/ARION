# ARION – Alpinum Readable Indented Object Notation

ARION is a whitespace-indented, line-based data format designed as a
low-token, human-friendly alternative to JSON, optimized for use with
LLMs and configuration files.

> **ARION** = **A**lpinum **R**eadable **I**ndented **O**bject **N**otation

Key properties:

- Fully reversible to/from JSON
- No braces, brackets, commas, or colons
- Uses indentation for structure
- Designed to be easy for humans *and* language models
- Stable, deterministic grammar

This repository contains:

- The ARION 1.0 specification
- Reference implementation in Python (`python/arion.py`)
- Reference implementation in JavaScript (`js/src/arion.js`)
- Examples

## Quick Example

JSON:

```json
{
  "name": "Joachim",
  "age": 29,
  "active": true,
  "skills": ["Python", "Audio", "AI"],
  "profile": {
    "role": "Developer",
    "location": "Austria"
  }
}
```

ARION:

```arion
!ARION 1.0

.name Joachim
.age 29
.active true
.skills
  - Python
  - Audio
  - AI
.profile
  .role Developer
  .location Austria
```

## Spec

See [`spec/ARION-1.0-spec.md`](spec/ARION-1.0-spec.md).

## Python Usage

```python
from arion import dumps_arion, loads_arion

data = {"name": "Joachim", "skills": ["Python", "Audio", "AI"]}

text = dumps_arion(data)
print(text)

decoded = loads_arion(text)
assert decoded == data
```

## JavaScript Usage

```js
import { dumpsArion, loadsArion } from "./js/src/arion.js";

const data = { name: "Joachim", active: true };
const text = dumpsArion(data);
console.log(text);

const decoded = loadsArion(text);
console.log(decoded);
```

## License

MIT – see [`LICENSE`](LICENSE).
