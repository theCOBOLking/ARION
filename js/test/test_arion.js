import { loadsArion, dumpsArion } from "../src/arion.js";

function assertEqual(a, b) {
  const ja = JSON.stringify(a);
  const jb = JSON.stringify(b);
  if (ja !== jb) {
    throw new Error("Assertion failed: " + ja + " !== " + jb);
  }
}

function roundtrip(obj) {
  const text = dumpsArion(obj);
  const back = loadsArion(text);
  assertEqual(back, obj);
  return text;
}

function runTests() {
  roundtrip({ name: "Joachim", age: 37, active: true });
  roundtrip({
    name: "Joachim",
    profile: { role: "Developer", location: "Austria" },
    skills: ["Python", "Audio", "AI"],
  });
  roundtrip({
    bio: "Line one\nLine two\nLine three",
  });
  roundtrip({
    flag: "true",
    number_as_string: "37",
    null_as_string: "null",
  });
  console.log("All JS ARION tests passed.");
}

runTests();
