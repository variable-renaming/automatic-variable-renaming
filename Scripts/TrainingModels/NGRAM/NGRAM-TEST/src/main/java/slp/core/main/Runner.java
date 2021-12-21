package slp.core.main;

import java.io.*;
import java.util.*;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;

import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import slp.core.counting.Counter;
import slp.core.counting.io.CounterIO;
import slp.core.lexing.Lexer;
import slp.core.lexing.code.JavaLexer;
import slp.core.lexing.runners.LexerRunner;
import slp.core.modeling.Model;
import slp.core.modeling.dynamic.CacheModel;
import slp.core.modeling.dynamic.NestedModel;
import slp.core.modeling.mix.MixModel;
import slp.core.modeling.ngram.JMModel;
import slp.core.modeling.runners.ModelRunner;
import slp.core.translating.Vocabulary;
import slp.core.translating.VocabularyRunner;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;


//From terminal type" mvn compile exec:java -Dexec.mainClass="slp.core.main.Runner" -Dexec.args="../Data/train.counts ../Data/train.vocab mapped_4.json"

public class Runner {

    public Runner() {
    }

    public static void main(String[] args) throws IOException {

        Lexer lexer = new JavaLexer();
        LexerRunner lexerRunner = new LexerRunner(lexer, false);
        lexerRunner.setSentenceMarkers(false);

        //   c. Only lex (and model) files that end with "java". See also 'setRegex'

        lexerRunner.setExtension("java");


        Vocabulary vocabulary = VocabularyRunner.read(new File(args[1]));


        File counterFile = new File(args[0]);
        long t = System.currentTimeMillis();
        System.out.println("Retrieving counter from file");
        Counter counter = CounterIO.readCounter(counterFile);
        System.out.println("Counter retrieved in " + (System.currentTimeMillis() - t)/1000 + "s");


        String json_file = args[2];

        ObjectMapper mapper = new ObjectMapper();

        try {

            List<Map<String, Object>> jMap =
                    mapper.readValue(new File(json_file) , new TypeReference<List<Map<String, Object>>>(){});


            for(int i = 0; i < jMap.size(); i++){

                String project = (String) jMap.get(i).keySet().toArray()[0];

                System.out.println(project);

                List<String> fileProjectTarget = (List<String>) jMap.get(i).get(project);

                //Renaming all the files we don't want to model. (ie file which already contain the solution)
                for (String fileName: fileProjectTarget){

                    String targetJavaFile = fileName.replace(".JP",".java");
                    File old_file = new File(targetJavaFile);

                    String targetJavaFileRenamed = targetJavaFile.replace(".java","no_model_java.old");
                    File new_file = new File(targetJavaFileRenamed);

                    boolean success = old_file.renameTo(new_file);
                }

                Model model = new JMModel(3, counter);

                model = new NestedModel(model, lexerRunner, vocabulary, new File(project));

                model = MixModel.standard(model, new CacheModel());

                ModelRunner modelRunner = new ModelRunner(model, lexerRunner, vocabulary);

                modelRunner.modelDirectory(new File(project));

                for (String fileName: fileProjectTarget){

                    String newFileName = fileName.replace(".JP","_target.java");
                    Files.copy(new File(fileName).toPath(), new File(newFileName).toPath(), StandardCopyOption.REPLACE_EXISTING);

                    String prediction_filename = fileName.replace(".JP","_pred_tokens_nv.txt").replace("large-scale-dataset/large-scale-repos-mvn-compilable",
                            "Baselines/SLP-Core/Data/large-scale-test-repos");

                    if (!new File(prediction_filename).exists()) {
                        System.out.println("[+] Predicting file: " + fileName);
                        modelRunner.predictFileSingle(new File(newFileName), newFileName);
                    }
                }


            }

        } catch (Exception e) {
            e.printStackTrace();
        }

    }
}
