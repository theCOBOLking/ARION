# ARION 1.0 – Alpinum Readable Indented Object Notation

**Status:** Draft  
**Author:** Alpinum Labs  
**File Extension:** `.arion`

ARION is a whitespace-indented, line-based representation of JSON data,
designed to minimize syntactic noise, reduce token usage in LLM prompts,
and remain fully reversible.

ARION keeps the JSON data model:

- Object (unordered mapping of string keys to values)
- Array (ordered list of values)
- String
- Number
- Boolean (`true`, `false`)
- Null (`null`)

---

## 1. Encoding & File Structure

- Text encoding: UTF-8
- Line separator: `\n`
- Indentation: spaces only (MUST NOT use tabs)
- Recommended indentation width: 2 spaces per level

A file MAY start with a header line:

```text
!ARION 1.0
```

Parsers MUST ignore any line that begins with `!ARION`.

---

## 2. Indentation & Nesting

Indentation defines nesting:

- A parent line appears at indentation level *n*
- Its children appear at indentation level *n + 2* (or greater, but consistent)

There are no `{}`, `[]`, `,`, or `:` characters required for structure.

Instead, ARION uses:

- `.key` prefix to denote object keys
- `-` prefix to denote array items

---

## 3. Objects

### 3.1 Key with inline scalar value

Syntax:

```text
.<key> <value>
```

Examples:

```text
.name Joachim
.age 29
.active true
```

Equivalent JSON fragment:

```json
{
  "name": "Joachim",
  "age": 29,
  "active": true
}
```

### 3.2 Nested object

If the line contains only the key (no value), the value is an object (or other compound value) defined by the indented block below it.

```text
.profile
  .role Developer
  .location Austria
```

Equivalent JSON:

```json
"profile": {
  "role": "Developer",
  "location": "Austria"
}
```

---

## 4. Arrays

Arrays are encoded via a key followed by one or more `-` lines.

### 4.1 Array of scalars

```text
.skills
  - Python
  - Audio
  - AI
```

JSON:

```json
"skills": ["Python", "Audio", "AI"]
```

### 4.2 Array of objects

```text
.people
  -
    .name Anna
    .age 25
  -
    .name Max
    .age 31
```

JSON:

```json
"people": [
  { "name": "Anna", "age": 25 },
  { "name": "Max", "age": 31 }
]
```

### 4.3 Top-level array

To encode a top-level array, start directly with `-`:

```text
- 1
- 2
- 3
```

JSON:

```json
[1, 2, 3]
```

If the top-level structure starts with `.key` lines, the top-level value is an object.
If it starts with `-` lines, the top-level value is an array.

---

## 5. Scalar Values & Types

The part after the key or `-` prefix is the scalar representation.

Let `raw` be the trimmed value string.

ARION uses the following rules to recover JSON types:

1. If `raw` starts with a single quote `'`, the value is a **string** with contents `raw[1:]` (the leading `'` is removed).

   Examples:

   ```text
   .flag 'true
   .value '29
   .literal 'null
   ```

   JSON:

   ```json
   { "flag": "true", "value": "29", "literal": "null" }
   ```

2. Otherwise, if `raw` is a valid JSON number literal (integer or floating point), it is parsed as a **number**.

   ```text
   .age 29
   .price -3.14
   ```

3. Otherwise, if `raw` is exactly `true` or `false`, it is parsed as a **boolean**.

4. Otherwise, if `raw` is exactly `null`, it is parsed as **null**.

5. Otherwise, the value is parsed as a **string**.

   ```text
   .title Carry Me Through
   ```

   JSON:

   ```json
   { "title": "Carry Me Through" }
   ```

This scheme ensures that `"true"` vs `true`, `"29"` vs `29`, and `"null"` vs `null` are distinguishable using the leading `'` for forced strings.

---

## 6. Multiline Strings

A key without inline value whose child lines do not start with `.` or `-` encodes a multiline string.

```text
.description
    This is a long text
    that spans multiple lines
    and keeps all line breaks.
```

All child lines at indentation level >= key_indent+2 that do NOT start with `.` or `-` are joined with `\n` to form a single JSON string.

JSON:

```json
"description": "This is a long text\nthat spans multiple lines\nand keeps all line breaks."
```

Parsing stops when indentation decreases or when a child at the same nesting depth begins with `.` or `-`.

---

## 7. Comments

Any line whose first non-space character is `#` is a comment and MUST be ignored by parsers.

```text
# This is a comment
.name Joachim
```

---

## 8. Examples

### 8.1 Simple object

```arion
!ARION 1.0

.name Joachim
.age 29
.active true
```

JSON:

```json
{
  "name": "Joachim",
  "age": 29,
  "active": true
}
```

### 8.2 Nested object with arrays and multiline strings

```arion
!ARION 1.0

.name Joachim
.profile
  .role Developer
  .location Austria
.skills
  - Python
  - Audio
  - AI
.bio
    I am working on several AI-driven platforms.
    Music and education are my core topics.
```

---

## 9. Error Handling

An ARION parser SHOULD:

- Reject tabs in indentation (or optionally expand them as 4 spaces, but this is discouraged).
- Validate indentation consistency (children must have greater indent than parent).
- Provide meaningful error messages including line number and context.

---

## 10. JSON Interoperability

ARION is designed to map 1:1 to JSON:

- Every valid ARION document corresponds to a JSON value.
- Every JSON object/array can be serialized to ARION using the rules in this specification and then losslessly parsed back into the original JSON.

This repository includes reference encoders/decoders in Python and JavaScript.
