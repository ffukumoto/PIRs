package com.HDU;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.SentenceUtils;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.process.CoreLabelTokenFactory;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.process.Tokenizer;
import edu.stanford.nlp.process.TokenizerFactory;
import edu.stanford.nlp.trees.*;

import java.io.StringReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class MyParser {
    LexicalizedParser lp = null;

    public MyParser(String parserModel){

        LexicalizedParser lp = LexicalizedParser.loadModel(parserModel);
        this.lp = lp;
    }

    public MyParser(){
        this("edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz");
    }

    public HashMap<String, Object> parserSentence(String sentence){
        return parserSentence(this.lp, sentence);
    }

    public HashMap<String, Object> parserSentence(String[] words){
        return parserSentence(this.lp, words);
    }

    public HashMap<String, Object> parserSentence(LexicalizedParser lp, String sentence) {
        HashMap<String, Object> result = new HashMap<>();
        TokenizerFactory<CoreLabel> tokenizerFactory =
                PTBTokenizer.factory(new CoreLabelTokenFactory(), "");
        Tokenizer<CoreLabel> tok =
                tokenizerFactory.getTokenizer(new StringReader(sentence));
        List<CoreLabel> rawWords = tok.tokenize();
        Tree parse = lp.apply(rawWords);

        TreebankLanguagePack tlp = lp.treebankLanguagePack(); // PennTreebankLanguagePack for English
        GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
        GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);
        List<TypedDependency> tdl = gs.typedDependenciesCCprocessed();

        List<String> rawWordsStr = new ArrayList<>(rawWords.size());

        for (CoreLabel rawWord : rawWords) rawWordsStr.add(rawWord.toString(CoreLabel.OutputFormat.VALUE));
        rawWordsStr.add(0, "ROOT");

        ArrayList<String> dependencies = new ArrayList<>();
        for (TypedDependency td : tdl){
            dependencies.add(td.reln() + "[|]" + td.gov().toString(CoreLabel.OutputFormat.VALUE_INDEX) + "[|]"
                             + td.dep().toString(CoreLabel.OutputFormat.VALUE_INDEX));
        }

        result.put("tokens", rawWordsStr);
        result.put("dependencies", dependencies);

//        System.out.println(rawWords);
//        System.out.println(rawWordsStr);
//        System.out.println(sentence);
//        System.out.println(tdl);
//        System.out.println(tdl.get(0).reln()+ tdl.get(0).gov().toString(CoreLabel.OutputFormat.VALUE_TAG_INDEX)  + ", " + tdl.get(0).dep() );
//        System.out.println();

        // You can also use a TreePrint object to print trees and dependencies
//        TreePrint tp = new TreePrint("penn,typedDependenciesCollapsed");
//        tp.printTree(parse);
        return result;


    }

    public HashMap<String, Object> parserSentence(LexicalizedParser lp, String[] words) {
        HashMap<String, Object> result = new HashMap<>();

        List<CoreLabel> rawWords = SentenceUtils.toCoreLabelList(words);
        Tree parse = lp.apply(rawWords);

        TreebankLanguagePack tlp = lp.treebankLanguagePack(); // PennTreebankLanguagePack for English
        GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
        GrammaticalStructure gs = gsf.newGrammaticalStructure(parse);
        List<TypedDependency> tdl = gs.typedDependenciesCCprocessed();

        List<String> rawWordsStr = new ArrayList<>(rawWords.size());

        for (CoreLabel rawWord : rawWords) rawWordsStr.add(rawWord.toString(CoreLabel.OutputFormat.VALUE));
        rawWordsStr.add(0, "ROOT");

        ArrayList<String> dependencies = new ArrayList<>();
        for (TypedDependency td : tdl){
            dependencies.add(td.reln() + "[|]" + td.gov().toString(CoreLabel.OutputFormat.VALUE_INDEX) + "[|]"
                    + td.dep().toString(CoreLabel.OutputFormat.VALUE_INDEX));
        }

        result.put("tokens", rawWordsStr);
        result.put("dependencies", dependencies);

        return result;
    }
}
