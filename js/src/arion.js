// ARION 1.0 reference implementation (JavaScript/ES module)
//
// Exports:
//   loadsArion(text: string) -> any
//   dumpsArion(value: any, header: boolean = true) -> string

function isNumberLike(s) {
  try {
    const v = JSON.parse(s);
    return typeof v === "number";
  } catch {
    return false;
  }
}

function parseScalar(raw) {
  const s = raw.trim();
  if (s === "") return "";
  if (s.startsWith("'")) return s.slice(1);
  if (s === "true") return true;
  if (s === "false") return false;
  if (s === "null") return null;
  if (isNumberLike(s)) return JSON.parse(s);
  return s;
}

function tokenizeLines(text) {
  const result = [];
  const lines = text.split(/\r?\n/);
  for (let line of lines) {
    if (!line.trim()) continue;
    const stripped = line.replace(/^ +/, "");
    const indent = line.length - stripped.length;
    if (stripped.startsWith("!ARION")) continue;
    if (stripped.startsWith("#")) continue;
    result.push([indent, stripped]);
  }
  return result;
}

function loadsArion(text) {
  const lines = tokenizeLines(text);

  function parseBlock(index, currentIndent) {
    const obj = {};
    let arr = null;

    while (index < lines.length) {
      const [indent, stripped] = lines[index];
      if (indent < currentIndent) break;

      if (stripped.startsWith(".")) {
        const content = stripped.slice(1);
        const spaceIdx = content.indexOf(" ");
        if (spaceIdx !== -1) {
          const key = content.slice(0, spaceIdx);
          const valueStr = content.slice(spaceIdx + 1);
          obj[key] = parseScalar(valueStr);
          index++;
        } else {
          const key = content;
          if (index + 1 >= lines.length) {
            obj[key] = {};
            index++;
            continue;
          }
          const [nextIndent, nextStripped] = lines[index + 1];
          if (nextIndent <= indent) {
            obj[key] = {};
            index++;
            continue;
          }
          if (!(nextStripped.startsWith(".") || nextStripped.startsWith("-"))) {
            // multiline string
            const multiline = [];
            let j = index + 1;
            const childIndent = nextIndent;
            while (j < lines.length) {
              const [ci, cs] = lines[j];
              if (ci < childIndent) break;
              if (ci === childIndent && !(cs.startsWith(".") || cs.startsWith("-"))) {
                multiline.push(cs);
                j++;
              } else {
                break;
              }
            }
            obj[key] = multiline.join("\n");
            index = j;
          } else {
            // nested structure
            const result = parseBlock(index + 1, indent + 1);
            obj[key] = result.value;
            index = result.index;
          }
        }
      } else if (stripped.startsWith("-")) {
        if (arr === null) arr = [];
        const tail = stripped.slice(1).trim();
        if (tail) {
          arr.push(parseScalar(tail));
          index++;
        } else {
          if (index + 1 >= lines.length) {
            arr.push({});
            index++;
            continue;
          }
          const [nextIndent, nextStripped] = lines[index + 1];
          if (nextIndent <= indent) {
            arr.push({});
            index++;
            continue;
          }
          const result = parseBlock(index + 1, indent + 1);
          arr.push(result.value);
          index = result.index;
        }
      } else {
        throw new Error(`Invalid ARION line at indent ${indent}: ${stripped}`);
      }
    }

    if (arr !== null && Object.keys(obj).length === 0) {
      return { index, value: arr };
    }
    if (arr !== null && Object.keys(obj).length > 0) {
      throw new Error("Mixed object and array at the same level is not allowed");
    }
    return { index, value: obj };
  }

  if (lines.length === 0) return null;

  const [firstIndent, firstStripped] = lines[0];
  const result = parseBlock(0, firstIndent);
  return result.value;
}

function dumpsArion(value, header = true) {
  function encodeScalar(v) {
    if (typeof v === "boolean") return v ? "true" : "false";
    if (v === null) return "null";
    if (typeof v === "number") return JSON.stringify(v);
    const s = String(v);
    if (s === "true" || s === "false" || s === "null" || isNumberLike(s)) {
      return "'" + s;
    }
    return s;
  }

  function encodeBlock(v, indent, asArray) {
    const lines = [];
    const sp = " ".repeat(indent);
    if (Array.isArray(v)) {
      for (const item of v) {
        if (Array.isArray(item) || (item && typeof item === "object")) {
          lines.push(sp + "-");
          lines.push(...encodeBlock(item, indent + 2, Array.isArray(item)));
        } else if (typeof item === "string" && item.includes("\n")) {
          lines.push(sp + "-");
          for (const line of item.split("\n")) {
            lines.push(" ".repeat(indent + 2) + line);
          }
        } else {
          lines.push(sp + "- " + encodeScalar(item));
        }
      }
    } else if (v && typeof v === "object") {
      for (const [k, val] of Object.entries(v)) {
        if (Array.isArray(val) || (val && typeof val === "object")) {
          lines.push(sp + "." + k);
          lines.push(...encodeBlock(val, indent + 2, Array.isArray(val)));
        } else if (typeof val === "string" && val.includes("\n")) {
          lines.push(sp + "." + k);
          for (const line of val.split("\n")) {
            lines.push(" ".repeat(indent + 2) + line);
          }
        } else {
          lines.push(sp + "." + k + " " + encodeScalar(val));
        }
      }
    } else {
      lines.push(sp + "- " + encodeScalar(v));
    }
    return lines;
  }

  const lines = [];
  if (header) {
    lines.push("!ARION 1.0");
    lines.push("");
  }
  lines.push(...encodeBlock(value, 0, Array.isArray(value)));
  return lines.join("\n") + "\n";
}

export { loadsArion, dumpsArion };
