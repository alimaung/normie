const path = require("path");
const fs = require("fs");
const lunr = require("lunr");
const cheerio = require("cheerio");

// Valid search fields: "title", "description", "keywords", "body"
const SEARCH_FIELDS = ["title", "description", "keywords", "body"];
const EXCLUDE_FILES = ["search.html"];
const OUTPUT_INDEX = "lunr_index.js"; // Index file
const OUTPUT_STOP_WORDS = "lunr_stop_words.js"; // File containing configured stop words

// This list is identical to the stop words that Lunr uses by default
// Having the list here allows us to customize it in the future and display it to the user
const STOP_WORDS = [
  'a',
  'able',
  'about',
  'across',
  'after',
  'all',
  'almost',
  'also',
  'am',
  'among',
  'an',
  'and',
  'any',
  'are',
  'as',
  'at',
  'be',
  'because',
  'been',
  'but',
  'by',
  'can',
  'cannot',
  'could',
  'dear',
  'did',
  'do',
  'does',
  'either',
  'else',
  'ever',
  'every',
  'for',
  'from',
  'get',
  'got',
  'had',
  'has',
  'have',
  'he',
  'her',
  'hers',
  'him',
  'his',
  'how',
  'however',
  'i',
  'if',
  'in',
  'into',
  'is',
  'it',
  'its',
  'just',
  'least',
  'let',
  'like',
  'likely',
  'may',
  'me',
  'might',
  'most',
  'must',
  'my',
  'neither',
  'no',
  'nor',
  'not',
  'of',
  'off',
  'often',
  'on',
  'only',
  'or',
  'other',
  'our',
  'own',
  'rather',
  'said',
  'say',
  'says',
  'she',
  'should',
  'since',
  'so',
  'some',
  'than',
  'that',
  'the',
  'their',
  'them',
  'then',
  'there',
  'these',
  'they',
  'this',
  'tis',
  'to',
  'too',
  'twas',
  'us',
  'wants',
  'was',
  'we',
  'were',
  'what',
  'when',
  'where',
  'which',
  'while',
  'who',
  'whom',
  'why',
  'will',
  'with',
  'would',
  'yet',
  'you',
  'your'
];

function isHtml(filename) {
  let lower = filename.toLowerCase();
  return lower.endsWith(".htm") || lower.endsWith(".html");
}

function findHtml(folder) {
  if (!fs.existsSync(folder)) {
    console.log("Could not find folder: ", folder);
    return;
  }

  var files = fs.readdirSync(folder);
  var htmls = [];
  for (var i = 0; i < files.length; i++) {
    var filename = path.join(folder, files[i]);
    var stat = fs.lstatSync(filename);
    if (stat.isDirectory()) {
      var recursed = findHtml(filename);
      for (var j = 0; j < recursed.length; j++) {
        recursed[j] = path.join(files[i], recursed[j]).replace(/\\/g, "/");
      }
      htmls.push.apply(htmls, recursed);
    } else if (isHtml(filename) && !EXCLUDE_FILES.includes(files[i])) {
      htmls.push(files[i]);
    }
  }
  return htmls;
}

function readHtml(archiveDir, htmlDir, file, fileId) {
  var absoluteFilePath = path.join(archiveDir, htmlDir, file);
  var relativeFilePath = path.join(htmlDir, file);

  var txt = fs.readFileSync(absoluteFilePath).toString();
  var $ = cheerio.load(txt);

  var title = $("title").text();
  if (typeof title == "undefined" || title.length == 0) {
    title = file;
  }

  var body = $("body").text();
  if (typeof body == "undefined") {
    body = "";
  }

  return {
    id: fileId,
    link: relativeFilePath,
    t: title,
    b: body,
  };
}

function buildIndex(docs) {
  let customStopWordFilter = lunr.generateStopWordFilter(STOP_WORDS);
  lunr.Pipeline.registerFunction(customStopWordFilter, 'customStopWordFilter');

  var idx = lunr(function () {
    this.tokenizer.separator = /\s+/;

    this.pipeline.remove(lunr.stemmer);
    this.searchPipeline.remove(lunr.stemmer);
    this.pipeline.before(lunr.stopWordFilter, customStopWordFilter);
    this.pipeline.remove(lunr.stopWordFilter);
    this.ref("id");
    for (var i = 0; i < SEARCH_FIELDS.length; i++) {
      this.field(SEARCH_FIELDS[i].slice(0, 1));
    }
    docs.forEach(function (doc) {
      this.add(doc);
    }, this);
  });
  return idx;
}

function buildPreviews(docs) {
  var result = {};
  for (var i = 0; i < docs.length; i++) {
    var doc = docs[i];
    result[doc["id"]] = {
      t: doc["t"],
      l: doc["link"],
    };
  }
  return result;
}

function buildStopWordObject() {
  // Convert stop word array into a javascript object
  return STOP_WORDS.reduce(function (words, stopWord) {
    words[stopWord] = stopWord
    return words
  }, {});
}

function runProcess() {
  const archiveFolder = process.argv[2];
  const htmlFolder = process.argv[3];

  console.time("findHtml");
  const files = findHtml(path.join(archiveFolder, htmlFolder));
  console.timeEnd("findHtml");

  console.time("readHtml");
  var docs = [];
  for (var i = 0; i < files.length; i++) {
    docs.push(readHtml(archiveFolder, htmlFolder, files[i], i));
  }
  console.timeEnd("readHtml");

  console.time("buildIndex");
  var idx = buildIndex(docs);
  console.timeEnd("buildIndex");

  console.time("buildPreviews");
  var previews = buildPreviews(docs);
  console.timeEnd("buildPreviews");

  var js =
    "const LUNR_DATA = " +
    JSON.stringify(idx) +
    ";\n" +
    "const PREVIEW_LOOKUP = " +
    JSON.stringify(previews) +
    ";"
  writeFile(js, path.join(archiveFolder, OUTPUT_INDEX));

  var stopWords =
    "const STOP_WORDS = " +
    JSON.stringify(buildStopWordObject()) +
    ";";
  writeFile(stopWords, path.join(archiveFolder, OUTPUT_STOP_WORDS));
}

function writeFile(contents, filePath) {
  fs.writeFile(filePath, contents,
    function (err) {
      if (err) {
        return console.log(err);
      }
      console.log("File saved as " + filePath);
    }
  );
}

function main() {
  if (process.argv.length < 4) {
    console.error("Expected arguments: <absolute path to archive directory> <name of folder containing HTML>");
    process.exitCode = 1;
  } else {
    runProcess();
  }
}

main();
