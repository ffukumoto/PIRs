package com.HDU;



import jdk.nashorn.internal.runtime.regexp.joni.exception.ValueException;

import java.util.*;

public abstract class Corpus {
    String originalFile = null;
    public Corpus(String originalFile){
        this.originalFile = originalFile;
    }
    HashMap<Integer, String> sentences = new HashMap<>();
    HashMap<Integer, HashMap<String,Object>> parsedSentences = new HashMap<>();

    public abstract ArrayList<HashMap<String,Object>> loadOriginalFile() throws Exception;
    public abstract HashMap<Object, HashMap<String,Object>> parseSentences();
    public abstract void saveParseResult();

    public void parseCorpus() throws Exception {
        int a = 0;
        this.loadOriginalFile();
        System.out.println("completed load");
        this.parseSentences();
        System.out.println("completed parse");
        this.saveParseResult();
        System.out.println("completed save");
        a = a+1;
    }
}

class QQP extends Corpus{

    public QQP(String originalFile) {
        super(originalFile);
    }

    @Override
    public ArrayList<HashMap<String, Object>> loadOriginalFile() {
        ArrayList<String> rows = (ArrayList<String>) Loader.readFileIntoStringArrList(this.originalFile);
        ArrayList<HashMap<String, Object>> result= new ArrayList<>();
        rows.remove(0);
        ArrayList<String> errorRows = new ArrayList<>();
        for (String row: rows) {
            String[] items = row.trim().split("\t");
            HashMap<String, Object> example = new HashMap<>();
            if (items.length!=6) {
                errorRows.add(row);
                continue;
            }
//                throw new ValueException("file content error");
            example.put("id", Integer.valueOf(items[0]));
            example.put("qid1", Integer.valueOf(items[1]));
            example.put("qid2", Integer.valueOf(items[2]));
            example.put("q1", items[3].trim());
            example.put("q2", items[4].trim());
            example.put("label", Integer.valueOf(items[5]));
            result.add(example);
            this.sentences.put((Integer)(example.get("qid1")), (String)(example.get("q1")));
            this.sentences.put((Integer)(example.get("qid2")), (String)(example.get("q2")));
        }
        if (errorRows.size()!=0)
            throw new ValueException("file content error");
        return result;
    }

    @Override
    public HashMap<Object, HashMap<String,Object>> parseSentences() {
        HashMap<Object, HashMap<String,Object>> result = new HashMap<>();
        MyParser parser = new MyParser();
        for (Integer key : this.sentences.keySet()) {
//            System.out.println("Key = " + key);
            HashMap<String, Object> parserOutput = parser.parserSentence(this.sentences.get(key));
            result.put(key, parserOutput);
            this.parsedSentences.put(key, parserOutput);
        }
        return result;
    }

    @Override
    public void saveParseResult() {
        ArrayList<String> saveList = new ArrayList<>();
        for (Integer key : this.parsedSentences.keySet()) {
//            System.out.println("Key = " + key);
            String line = "";
            HashMap<String,Object> parseInfo = this.parsedSentences.get(key);
            ArrayList<String> dependencies = (ArrayList<String>)(parseInfo.get("dependencies"));
            ArrayList<String> tokens = (ArrayList<String>)(parseInfo.get("tokens"));
            String tokensStr = tokens.get(0);
            String dependenciesStr = dependencies.get(0);
            for (int i = 1; i < dependencies.size(); i++) {
                dependenciesStr += "[De]"+dependencies.get(i);
            }
            for (int i = 1; i < tokens.size(); i++) {
                tokensStr += " " + tokens.get(i);
            }

            line = line+key+" [Sq] "+this.sentences.get(key) + " [Sq] " + tokensStr + " [Sq] " + dependenciesStr;
            saveList.add(line);
        }
        Saver.saveStrList("src/com/HDU/result/parsedCorpus.txt", saveList);
    }

    @Override
    public void parseCorpus() {
        int a = 0;
        this.loadOriginalFile();
        System.out.println("completed load");
        this.parseSentences();
        System.out.println("completed parse");
        this.saveParseResult();
        System.out.println("completed save");
        a = a+1;
    }

    public static void main(String[] args) throws Exception {
//        QQP qqp = new QQP("src/com/HDU/data/QQP/program_test.tsv");
        QQP qqp = new QQP("src/com/HDU/data/QQP/program_test.tsv");
        qqp.parseCorpus();
    }
}

class MRPC extends Corpus{

    public MRPC(String originalFile) {
        super(originalFile);
    }

    @Override
    public ArrayList<HashMap<String, Object>> loadOriginalFile() throws Exception {
        ArrayList<String> rows = (ArrayList<String>) Loader.readFileIntoStringArrList(this.originalFile);
        ArrayList<HashMap<String, Object>> result= new ArrayList<>();
        rows.remove(0);
        ArrayList<String> errorRows = new ArrayList<>();
        for (String row: rows) {
            String[] items = row.trim().split("\t");
            HashMap<String, Object> example = new HashMap<>();
            if (items.length!=7) {
                errorRows.add(row);
                continue;
            }
//                throw new ValueException("file content error");
            example.put("id", Integer.valueOf(items[0]));
            example.put("sentence", items[1].trim());
            result.add(example);
            this.sentences.put((Integer)(example.get("id")), (String)(example.get("sentence")));
        }
        if (errorRows.size()!=0)
            throw new ValueException("file content error");
        return result;
    }

    @Override
    public HashMap<Object, HashMap<String,Object>> parseSentences() {
        HashMap<Object, HashMap<String,Object>> result = new HashMap<>();
        MyParser parser = new MyParser();
        for (Integer key : this.sentences.keySet()) {
//            System.out.println("Key = " + key);
            HashMap<String, Object> parserOutput = parser.parserSentence(this.sentences.get(key));
            result.put(key, parserOutput);
            this.parsedSentences.put(key, parserOutput);
        }
        return result;
    }

    @Override
    public void saveParseResult() {
        ArrayList<String> saveList = new ArrayList<>();
        for (Integer key : this.parsedSentences.keySet()) {
//            System.out.println("Key = " + key);
            String line = "";
            HashMap<String,Object> parseInfo = this.parsedSentences.get(key);
            ArrayList<String> dependencies = (ArrayList<String>)(parseInfo.get("dependencies"));
            ArrayList<String> tokens = (ArrayList<String>)(parseInfo.get("tokens"));
            String tokensStr = tokens.get(0);
            String dependenciesStr = dependencies.get(0);
            for (int i = 1; i < dependencies.size(); i++) {
                dependenciesStr += "[De]"+dependencies.get(i);
            }
            for (int i = 1; i < tokens.size(); i++) {
                tokensStr += " " + tokens.get(i);
            }

            line = line+key+" [Sq] "+this.sentences.get(key) + " [Sq] " + tokensStr + " [Sq] " + dependenciesStr;
            saveList.add(line);
        }
        Saver.saveStrList("src/com/HDU/data/MRPC/parsed_sentences_test.txt", saveList);
    }


    public static void main(String[] args) throws Exception {
//        QQP qqp = new QQP("src/com/HDU/data/QQP/program_test.tsv");
//        QQP qqp = new QQP("src/com/HDU/data/MRPC/sentence_data_test.txt");
//        qqp.parseCorpus();
        MRPC mrpc = new MRPC("src/com/HDU/data/MRPC/sentence_data_test.txt");
        mrpc.parseCorpus();
    }
}

class MRPCSentTokensVersion extends MRPC{
    HashMap<Integer, String[]> sentence_words = new HashMap<>();
    public MRPCSentTokensVersion(String originalFile) {
        super(originalFile);
    }

    public ArrayList<HashMap<String, Object>> loadWordsFile(String filename) throws Exception {
        ArrayList<String> rows = (ArrayList<String>) Loader.readFileIntoStringArrList(filename);
        ArrayList<HashMap<String, Object>> result= new ArrayList<>();
        ArrayList<String> errorRows = new ArrayList<>();
        for (String row: rows) {
            String[] items = row.trim().split("\t");
            HashMap<String, Object> example = new HashMap<>();
            if (items.length!=2) {
                errorRows.add(row);
                continue;
            }
//                throw new ValueException("file content error");
            example.put("id", Integer.valueOf(items[0]));
            String[] words = items[1].trim().split(" ");
            for (String word: words) {
                if (word.equals("")){
                    throw new ValueException("file content error");
                }
            }
            example.put("sentence", words);
            result.add(example);
            this.sentence_words.put((Integer)(example.get("id")), (String[])(example.get("sentence")));
        }
        if (errorRows.size()!=0)
            throw new ValueException("file content error");
        return result;
    }

    @Override
    public HashMap<Object, HashMap<String,Object>> parseSentences() {
        HashMap<Object, HashMap<String,Object>> result = new HashMap<>();
        MyParser parser = new MyParser();
        for (Integer key : this.sentence_words.keySet()) {
//            System.out.println("Key = " + key);
            String[] words = this.sentence_words.get(key);
            HashMap<String, Object> parserOutput = parser.parserSentence(words);
            result.put(key, parserOutput);
            List<String> parsedTokens = (List<String>) parserOutput.get("tokens");


            if (parsedTokens.size() != words.length +1 ){
                throw new ValueException("tokens content error");
            }
            for (int i = 0; i < words.length; i++) {
                if(! words[i].equals(parsedTokens.get(i+1)))
                    throw new ValueException("tokens content error");
            }
            this.parsedSentences.put(key, parserOutput);
        }
        return result;
    }

    public static void main(String[] args) throws Exception {
//        QQP qqp = new QQP("src/com/HDU/data/QQP/program_test.tsv");
//        QQP qqp = new QQP("src/com/HDU/data/MRPC/sentence_data_test.txt");
//        qqp.parseCorpus();
        MRPCSentTokensVersion mrpc = new MRPCSentTokensVersion("src/com/HDU/data/MRPC/sentence_data.txt");
        mrpc.loadWordsFile("src/com/HDU/data/MRPC/sentence_words_test.txt");
        mrpc.parseCorpus();
    }
}


class QQPSentTokensVersion extends QQP{
    HashMap<Integer, String[]> sentence_words = new HashMap<>();
    public QQPSentTokensVersion(String originalFile) {
        super(originalFile);
    }

    public ArrayList<HashMap<String, Object>> loadWordsFile(String filename) throws Exception {
        ArrayList<String> rows = (ArrayList<String>) Loader.readFileIntoStringArrList(filename);
        ArrayList<HashMap<String, Object>> result= new ArrayList<>();
        ArrayList<String> errorRows = new ArrayList<>();
        for (String row: rows) {
            String[] items = row.trim().split("\t");
            HashMap<String, Object> example = new HashMap<>();
            if (items.length!=2) {
                errorRows.add(row);
                continue;
            }
//                throw new ValueException("file content error");
            example.put("id", Integer.valueOf(items[0]));
            String[] words = items[1].trim().split(" ");
            for (String word: words) {
                if (word.equals("")){
                    throw new ValueException("file content error");
                }
            }
            example.put("sentence", words);
            result.add(example);
            this.sentence_words.put((Integer)(example.get("id")), (String[])(example.get("sentence")));
        }
        if (errorRows.size()!=0)
            throw new ValueException("file content error");
        return result;
    }

    @Override
    public HashMap<Object, HashMap<String,Object>> parseSentences() {
        HashMap<Object, HashMap<String,Object>> result = new HashMap<>();
        MyParser parser = new MyParser();
        for (Integer key : this.sentence_words.keySet()) {
//            System.out.println("Key = " + key);
            String[] words = this.sentence_words.get(key);
            HashMap<String, Object> parserOutput = parser.parserSentence(words);
            result.put(key, parserOutput);
            List<String> parsedTokens = (List<String>) parserOutput.get("tokens");


            if (parsedTokens.size() != words.length +1 ){
                throw new ValueException("tokens content error");
            }
            for (int i = 0; i < words.length; i++) {
                if(! words[i].equals(parsedTokens.get(i+1)))
                    throw new ValueException("tokens content error");
            }
            this.parsedSentences.put(key, parserOutput);
        }
        return result;
    }

    @Override
    public void parseCorpus() {
        int a = 0;
        this.loadOriginalFile();
        System.out.println("completed load");
        this.parseSentences();
        System.out.println("completed parse");
        this.saveParseResult();
        System.out.println("completed save");
        a = a+1;
    }

    public static void main(String[] args) throws Exception {
//        QQP qqp = new QQP("src/com/HDU/data/QQP/program_test.tsv");
        QQPSentTokensVersion qqp = new QQPSentTokensVersion("src/com/HDU/data/QQP/quora_duplicate_questions.tsv");
        qqp.loadWordsFile("src/com/HDU/data/QQP/sentence_words.txt");
        qqp.parseCorpus();
    }
}


class STSBSentTokensVersion extends Corpus{
    HashMap<Integer, String[]> sentence_words = new HashMap<>();
    public STSBSentTokensVersion(String originalFile) {
        super(originalFile);
    }

    @Override
    public ArrayList<HashMap<String, Object>> loadOriginalFile() {
        ArrayList<String> rows = (ArrayList<String>) Loader.readFileIntoStringArrList(this.originalFile);
        ArrayList<HashMap<String, Object>> result= new ArrayList<>();
        rows.remove(0);
        ArrayList<String> errorRows = new ArrayList<>();
        for (String row: rows) {
            String[] items = row.trim().split("\t");
            HashMap<String, Object> sentence = new HashMap<>();
            if (items.length!=2) {
                errorRows.add(row);
                continue;
            }
//                throw new ValueException("file content error");
            sentence.put("id", Integer.valueOf(items[0]));
            sentence.put("original", items[1].trim());

            result.add(sentence);
            this.sentences.put((Integer)(sentence.get("id")), (String)(sentence.get("original")));

        }
        if (errorRows.size()!=0)
            throw new ValueException("file content error");
        return result;
    }

    public ArrayList<HashMap<String, Object>> loadWordsFile(String filename) throws Exception {
        ArrayList<String> rows = (ArrayList<String>) Loader.readFileIntoStringArrList(filename);
        ArrayList<HashMap<String, Object>> result= new ArrayList<>();
        ArrayList<String> errorRows = new ArrayList<>();
        for (String row: rows) {
            String[] items = row.trim().split("\t");
            HashMap<String, Object> example = new HashMap<>();
            if (items.length!=2) {
                errorRows.add(row);
                continue;
            }
//                throw new ValueException("file content error");
            example.put("id", Integer.valueOf(items[0]));
            String[] words = items[1].trim().split(" ");
            for (String word: words) {
                if (word.equals("")){
                    throw new ValueException("file content error");
                }
            }
            example.put("sentence", words);
            result.add(example);
            this.sentence_words.put((Integer)(example.get("id")), (String[])(example.get("sentence")));
        }
        if (errorRows.size()!=0)
            throw new ValueException("file content error");
        return result;
    }

    @Override
    public HashMap<Object, HashMap<String,Object>> parseSentences() {
        HashMap<Object, HashMap<String,Object>> result = new HashMap<>();
        MyParser parser = new MyParser();
        for (Integer key : this.sentence_words.keySet()) {
//            System.out.println("Key = " + key);
            String[] words = this.sentence_words.get(key);
            HashMap<String, Object> parserOutput = parser.parserSentence(words);
            result.put(key, parserOutput);
            List<String> parsedTokens = (List<String>) parserOutput.get("tokens");


            if (parsedTokens.size() != words.length +1 ){
                throw new ValueException("tokens content error");
            }
            for (int i = 0; i < words.length; i++) {
                if(! words[i].equals(parsedTokens.get(i+1)))
                    throw new ValueException("tokens content error");
            }
            this.parsedSentences.put(key, parserOutput);
        }
        return result;
    }

    @Override
    public void saveParseResult() {
        ArrayList<String> saveList = new ArrayList<>();
        for (Integer key : this.parsedSentences.keySet()) {
//            System.out.println("Key = " + key);
            String line = "";
            HashMap<String,Object> parseInfo = this.parsedSentences.get(key);
            ArrayList<String> dependencies = (ArrayList<String>)(parseInfo.get("dependencies"));
            ArrayList<String> tokens = (ArrayList<String>)(parseInfo.get("tokens"));
            String tokensStr = tokens.get(0);
            String dependenciesStr = dependencies.get(0);
            for (int i = 1; i < dependencies.size(); i++) {
                dependenciesStr += "[De]"+dependencies.get(i);
            }
            for (int i = 1; i < tokens.size(); i++) {
                tokensStr += " " + tokens.get(i);
            }

            line = line+key+" [Sq] "+this.sentences.get(key) + " [Sq] " + tokensStr + " [Sq] " + dependenciesStr;
            saveList.add(line);
        }
        Saver.saveStrList("src/com/HDU/result/parsedCorpus.txt", saveList);
    }

    @Override
    public void parseCorpus() {
        int a = 0;
        this.loadOriginalFile();
        System.out.println("completed load");
        this.parseSentences();
        System.out.println("completed parse");
        this.saveParseResult();
        System.out.println("completed save");
        a = a+1;
    }

    public static void main(String[] args) throws Exception {
        STSBSentTokensVersion stsb = new STSBSentTokensVersion("src/com/HDU/data/STS-B/original_sentence.txt");
        stsb.loadWordsFile("src/com/HDU/data/STS-B/sentence_words.txt");
        stsb.parseCorpus();
    }
}



class Generation extends Corpus{
    HashMap<String, String> sentences = new HashMap<>();
    HashMap<String, HashMap<String,Object>> parsedSentences = new HashMap<>();

    public Generation(String originalFile) {
        super(originalFile);
    }

    @Override
    public ArrayList<HashMap<String, Object>> loadOriginalFile() throws Exception {
        ArrayList<String> rows = (ArrayList<String>) Loader.readFileIntoStringArrList(this.originalFile);
        ArrayList<HashMap<String, Object>> result= new ArrayList<>();
        ArrayList<String> errorRows = new ArrayList<>();
        for (String row: rows) {
            String[] items = row.trim().split("\t");
            HashMap<String, Object> example = new HashMap<>();
            if (items.length!=2) {
                errorRows.add(row);
                continue;
            }
//                throw new ValueException("file content error");
            example.put("id", items[0].trim());
            example.put("sentence", items[1].trim());
            result.add(example);
            this.sentences.put((String)(example.get("id")), (String)(example.get("sentence")));
        }
        if (errorRows.size()!=0)
            throw new ValueException("file content error");
        return result;
    }

    @Override
    public HashMap<Object, HashMap<String,Object>> parseSentences() {
        HashMap<Object, HashMap<String,Object>> result = new HashMap<>();
        MyParser parser = new MyParser();
        for (String key : this.sentences.keySet()) {
//            System.out.println("Key = " + key);
            HashMap<String, Object> parserOutput = parser.parserSentence(this.sentences.get(key));
            result.put(key, parserOutput);
            this.parsedSentences.put(key, parserOutput);
        }
        return result;
    }

    @Override
    public void saveParseResult() {
        ArrayList<String> saveList = new ArrayList<>();
        for (String key : this.parsedSentences.keySet()) {
//            System.out.println("Key = " + key);
            String line = "";
            HashMap<String,Object> parseInfo = this.parsedSentences.get(key);
            ArrayList<String> dependencies = (ArrayList<String>)(parseInfo.get("dependencies"));
            ArrayList<String> tokens = (ArrayList<String>)(parseInfo.get("tokens"));
            String tokensStr = tokens.get(0);
            String dependenciesStr = dependencies.get(0);
            for (int i = 1; i < dependencies.size(); i++) {
                dependenciesStr += "[De]"+dependencies.get(i);
            }
            for (int i = 1; i < tokens.size(); i++) {
                tokensStr += " " + tokens.get(i);
            }

            line = line+key+" [Sq] "+this.sentences.get(key) + " [Sq] " + tokensStr + " [Sq] " + dependenciesStr;
            saveList.add(line);
        }
        Saver.saveStrList("src/com/HDU/data/generation/mrpc/parsed_sentences.txt", saveList);
    }


    public static void main(String[] args) throws Exception {
        MRPC mrpc = new MRPC("src/com/HDU/data/generation/mrpc/sentence_data_test.txt");
        mrpc.parseCorpus();
    }
}
class GenerationSentTokensVersion extends Generation{
    HashMap<String, String[]> sentence_words = new HashMap<>();
    public GenerationSentTokensVersion(String originalFile) {
        super(originalFile);
    }

    public ArrayList<HashMap<String, Object>> loadWordsFile(String filename) throws Exception {
        ArrayList<String> rows = (ArrayList<String>) Loader.readFileIntoStringArrList(filename);
        ArrayList<HashMap<String, Object>> result= new ArrayList<>();
        ArrayList<String> errorRows = new ArrayList<>();
        for (String row: rows) {
            String[] items = row.trim().split("\t");
            HashMap<String, Object> example = new HashMap<>();
            if (items.length!=2) {
                errorRows.add(row);
                continue;
            }
//                throw new ValueException("file content error");
            example.put("id", items[0].trim());
            String[] words = items[1].trim().split(" ");
            for (String word: words) {
                if (word.equals("")){
                    throw new ValueException("file content error");
                }
            }
            example.put("sentence", words);
            result.add(example);
            this.sentence_words.put((String)(example.get("id")), (String[])(example.get("sentence")));
        }
        if (errorRows.size()!=0)
            throw new ValueException("file content error");
        return result;
    }

    @Override
    public HashMap<Object, HashMap<String,Object>> parseSentences() {
        HashMap<Object, HashMap<String,Object>> result = new HashMap<>();
        MyParser parser = new MyParser();
        for (String key : this.sentence_words.keySet()) {
//            System.out.println("Key = " + key);
            String[] words = this.sentence_words.get(key);
            HashMap<String, Object> parserOutput = parser.parserSentence(words);
            result.put(key, parserOutput);
            List<String> parsedTokens = (List<String>) parserOutput.get("tokens");


            if (parsedTokens.size() != words.length +1 ){
                throw new ValueException("tokens content error");
            }
            for (int i = 0; i < words.length; i++) {
                if(! words[i].equals(parsedTokens.get(i+1)))
                    throw new ValueException("tokens content error");
            }
            this.parsedSentences.put(key, parserOutput);
        }
        return result;
    }

    public static void main(String[] args) throws Exception {
//        QQP qqp = new QQP("src/com/HDU/data/QQP/program_test.tsv");
//        QQP qqp = new QQP("src/com/HDU/data/MRPC/sentence_data_test.txt");
//        qqp.parseCorpus();
        GenerationSentTokensVersion corpus = new GenerationSentTokensVersion("src/com/HDU/data/generation/mrpc/original_sentence.txt");
        corpus.loadWordsFile("src/com/HDU/data/generation/mrpc/sentence_words.txt");
        corpus.parseCorpus();
    }
}