const fs = require("node:fs");
const readline = require("readline");
// const jsonFile = require("../update.json");

const askQuestion = (rl, query) => {
  return new Promise((resolve) => {
    const rly = rl;
    rly.question(query, resolve);
    console.log("Hit");
  });
};

const updateJson = async () => {
  //   Names of all relevant files
  const nameJson = "update.json";
  const nameProp = "module.prop";
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  //   Step 1: Modify the update.json file
  updateJsonFile = JSON.parse(fs.readFileSync(`../${nameJson}`));

  //   List of options to pick to update version number
  const versionNumberList = updateJsonFile.version.replace("v", "").split(".");
  const versionNumberPick = [
    `v${parseInt(versionNumberList[0]) + 1}.0.0`,
    `v${versionNumberList[0]}.${parseInt(versionNumberList[1]) + 1}.0`,
    `v${versionNumberList[0]}.0.${parseInt(versionNumberList[2]) + 1}`,
  ];

  //   Now inquire about it
  console.log("FOSS App Stores Magisk Module");
  console.log(`\nCurrent Version: ${updateJsonFile.version}`);
  console.log("\nHow should we update this package?");
  console.log("\t Option 1 — " + versionNumberPick[0] + " — a MAJOR update");
  console.log("\t Option 2 — " + versionNumberPick[1] + " — a MINOR update");
  console.log(
    "\t Option 3 — " + versionNumberPick[2] + " — a SUB-MINOR update"
  );
  //   console.log("\nPlease enter your answer [1, 2, 3]: ");

  let answer = await askQuestion(rl, "\nPlease enter your answer [1, 2, 3]: ");

  while (
    isNaN(answer) ||
    !(
      parseInt(answer) - 1 >= 0 &&
      parseInt(answer) - 1 <= versionNumberPick.length
    )
  ) {
    answerRaw = await askQuestion(rl, "\nPlease enter your answer [1, 2, 3]: ");
  }

  console.log(answer);
};

updateJson();
