import groovy.json.JsonBuilder
import java.nio.charset.Charset
import java.nio.charset.CharsetDecoder
import java.nio.charset.CharsetEncoder
import java.nio.ByteBuffer
import java.nio.CharBuffer

def download(address)
{
    def file = new FileOutputStream(address.tokenize("/")[-1])
    def out = new BufferedOutputStream(file)
    out << new URL(address).openStream()
    out.close()
}

def toJson(bookName, bibleMap)
{
    download(toUrl(bookName))

    def fileHtml = new File("${bookName}.htm")

    String genesis = fileHtml.getText("windows-1252");

    def results = genesis.split(/\r?\n/)

    def book = [:]

    results.each {

        try
        {
            if (it.startsWith("{"))
            {
                def endMeta = it.indexOf("}")
                def meta = it.substring(0, endMeta+1)

                def strtIdx = endMeta + 2;

                it = it.replaceAll("<BR>", "")
                def content = it.substring(strtIdx)

                // Create the encoder and decoder for UTF-8
                Charset charset = Charset.forName("UTF-8");
                CharsetDecoder decoder = charset.newDecoder();
                CharsetEncoder encoder = charset.newEncoder();

                def chapter = meta.substring(1, meta.indexOf(":"))
                def verse = meta.substring(meta.indexOf(":")+1, meta.indexOf("}"))

                // Convert a string to UTF-8 bytes in a ByteBuffer
                // The new ByteBuffer is ready to be read.
                ByteBuffer bbuf = encoder.encode(CharBuffer.wrap(content));

                // Convert UTF-8 bytes in a ByteBuffer to a character ByteBuffer and then to a string.
                // The new ByteBuffer is ready to be read.
                CharBuffer cbuf = decoder.decode(bbuf);

                if (!book[chapter])
                {
                    book[chapter] = [:]
                }

                def chapterMap = book[chapter]
                chapterMap[verse] = cbuf.toString()

            }
        }
        catch(Exception e)
        {
            e.printStackTrace()
        }
    }

    if (bibleMap != null)
    {
        bibleMap["${bookName.substring(bookName.indexOf("_")+1)}"] = book.clone()
    }

    book["charset"]= "UTF-8"

    def jsonBuilder = new JsonBuilder(book)

    File fileJson = new File("CPDV-JSON/${bookName}.json")
    fileJson.setText(jsonBuilder.toPrettyString(), "UTF-8")

    fileHtml.delete()
}

def toUrl(bookName)
{
    def host = "https://www.sacredbible.org/catholic/"

    return "${host}${bookName}.htm"
}

println "Encoding Bible-CPDV to JSON"

def bibleMap = [:]
bibleMap["charset"] = "UTF-8"

new File("CPDV-JSON").mkdir();

long startTime = System.currentTimeMillis()

toJson("OT-01_Genesis", bibleMap)
toJson("OT-02_Exodus", bibleMap)
toJson("OT-03_Leviticus", bibleMap)
toJson("OT-04_Numbers", bibleMap)
toJson("OT-05_Deuteronomy", bibleMap)
toJson("OT-06_Joshua", bibleMap)
toJson("OT-07_Judges", bibleMap)
toJson("OT-08_Ruth", bibleMap)
toJson("OT-09_1-Samuel", bibleMap)
toJson("OT-10_2-Samuel", bibleMap)
toJson("OT-11_1-Kings", bibleMap)
toJson("OT-12_2-Kings", bibleMap)
toJson("OT-13_1-Chronicles", bibleMap)
toJson("OT-14_2-Chronicles", bibleMap)
toJson("OT-15_Ezra", bibleMap)
toJson("OT-16_Nehemiah", bibleMap)
toJson("OT-17_Tobit", bibleMap)
toJson("OT-18_Judith", bibleMap)
toJson("OT-19_Esther", bibleMap)
toJson("OT-20_Job", bibleMap)
toJson("OT-21_Psalms", bibleMap)
toJson("OT-22_Proverbs", bibleMap)
toJson("OT-23_Ecclesiastes", bibleMap)
toJson("OT-24_Song2", bibleMap)
toJson("OT-25_Wisdom", bibleMap)
toJson("OT-26_Sirach", bibleMap)
toJson("OT-27_Isaiah", bibleMap)
toJson("OT-28_Jeremiah", bibleMap)
toJson("OT-29_Lamentations", bibleMap)
toJson("OT-30_Baruch", bibleMap)
toJson("OT-31_Ezekiel", bibleMap)
toJson("OT-32_Daniel", bibleMap)
toJson("OT-33_Hosea", bibleMap)
toJson("OT-34_Joel", bibleMap)
toJson("OT-35_Amos", bibleMap)
toJson("OT-36_Obadiah", bibleMap)
toJson("OT-37_Jonah", bibleMap)
toJson("OT-38_Micah", bibleMap)
toJson("OT-39_Nahum", bibleMap)
toJson("OT-40_Habakkuk", bibleMap)
toJson("OT-41_Zephaniah", bibleMap)
toJson("OT-42_Haggai", bibleMap)
toJson("OT-43_Zechariah", bibleMap)
toJson("OT-44_Malachi", bibleMap)
toJson("OT-45_1-Maccabees", bibleMap)
toJson("OT-46_2-Maccabees", bibleMap)

toJson("NT-01_Matthew", bibleMap)
toJson("NT-02_Mark", bibleMap)
toJson("NT-03_Luke", bibleMap)
toJson("NT-04_John", bibleMap)
toJson("NT-05_Acts", bibleMap)
toJson("NT-06_Romans", bibleMap)
toJson("NT-07_1-Corinthians", bibleMap)
toJson("NT-08_2-Corinthians", bibleMap)
toJson("NT-09_Galatians", bibleMap)
toJson("NT-10_Ephesians", bibleMap)
toJson("NT-11_Philippians", bibleMap)
toJson("NT-12_Colossians", bibleMap)
toJson("NT-13_1-Thessalonians", bibleMap)
toJson("NT-14_2-Thessalonians", bibleMap)
toJson("NT-15_1-Timothy", bibleMap)
toJson("NT-16_2-Timothy", bibleMap)
toJson("NT-17_Titus", bibleMap)
toJson("NT-18_Philemon", bibleMap)
toJson("NT-19_Hebrews", bibleMap)
toJson("NT-20_James", bibleMap)
toJson("NT-21_1-Peter", bibleMap)
toJson("NT-22_2-Peter", bibleMap)
toJson("NT-23_1-John", bibleMap)
toJson("NT-24_2-John", bibleMap)
toJson("NT-25_3-John", bibleMap)
toJson("NT-26_Jude", bibleMap)
toJson("NT-27_Revelation", bibleMap)

long endTime = System.currentTimeMillis()

long totalTime = endTime-startTime

println "Finished encoding CPDV Bible to JSON - ${totalTime}ms"

def jsonBuilder = new JsonBuilder(bibleMap)
File fileJson = new File("CPDV-JSON/EntireBible-CPDV.json")
fileJson.setText(jsonBuilder.toPrettyString(), "UTF-8")
