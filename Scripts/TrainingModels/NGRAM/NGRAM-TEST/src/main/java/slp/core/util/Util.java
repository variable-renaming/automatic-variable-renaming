package slp.core.util;

import com.google.gson.Gson;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import slp.core.lexing.runners.LexerRunner;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class Util {
	public static List<File> getFiles(File root) {
		if (root.isFile()) return Collections.singletonList(root);
		List<File> files = new ArrayList<>();
		for (String child : root.list()) {
			File file = new File(root, child);
			if (file.isFile()) {
				files.add(file);
			}
			else if (file.isDirectory()) files.addAll(getFiles(file));
		}
		return files;
	}

	public static List<String> findFiles(Path path, String fileExtension)
			throws IOException {

		if (!Files.isDirectory(path)) {
			throw new IllegalArgumentException("Path must be a directory!");
		}

		List<String> result;

		try (Stream<Path> walk = Files.walk(path)) {
			result = walk
					.filter(p -> !Files.isDirectory(p))
					// this is a path, not string,
					// this only test if path end with a certain path
					//.filter(p -> p.endsWith(fileExtension))
					// convert path to string first
					.map(p -> p.toString().toLowerCase())
					.filter(f -> f.endsWith(fileExtension))
					.collect(Collectors.toList());
		}

		return result;
	}

	public static void refineJson(LexerRunner lexerRunner, String fileToRefineJson){

		//String fileToRefineJson = "/Users/antonio/SLP-Prove/FlatFileDatabase.json";
		String outputRefinedFile = fileToRefineJson.replace(".json","_refined.json");
		String JP = fileToRefineJson.replace(".json",".JP").replace("All-Test-JSON","JP_FILES");
		List<List<String>> tt = null;
		try{
			tt = lexerRunner.lexFile(new File(JP))
					.map(l -> l.collect(Collectors.toList())).collect(Collectors.toList());
		} catch(Exception e){
			System.out.println("This file cannot be retrieved! "+JP);
			return;
		}

		JSONParser parser = new JSONParser();
		ArrayList<JSONObject> refinedMethods = new ArrayList();
		try {
			Object obj = parser.parse(new FileReader(fileToRefineJson));

			// A JSON object. Key value pairs are unordered. JSONObject supports java.util.Map interface.
			JSONArray jsonArray = (JSONArray) obj;
			JSONObject jsonObject = (JSONObject) jsonArray.get(0);
			String sourcePath = (String) jsonObject.get("extracted_from");
			String classBody = (String) jsonObject.get("classBody");
			String classLines[] = classBody.toString().split("\\r?\\n");

			ArrayList<String> originalLines = new ArrayList<String>();
			BufferedReader reader;
			try {
				reader = new BufferedReader(new FileReader(
						fileToRefineJson));
				String line = reader.readLine();
				while (line != null) {
					originalLines.add(line);
					// read next line
					line = reader.readLine();
				}
				reader.close();
			} catch (IOException e) { }


			int offset = 0;
			for(String line: originalLines){
				if(line.equals(classLines[0])){
					break;
				}
				offset+=1;
			}

			JSONArray items = (JSONArray) jsonObject.get("methodList");
			for (Object methodItem: items){
				Object method = parser.parse(methodItem.toString());
				JSONObject jMethod = (JSONObject) method;
				Long lBound = (Long)jMethod.get("lowerBound");
				String mName = (String)jMethod.get("methodName");
				String methodBody = (String)jMethod.get("methodBody");

				FileWriter file_java = new FileWriter("method.java");
				file_java.write(methodBody);
				file_java.close();

				//System.out.println("name: "+mName + " -------- "+ lBound);
				int token_counter = 0;
				List<List<String>> subList = tt.subList(0, Math.toIntExact(lBound-1));
				for(List l: subList){
					token_counter += l.size();
				}
				jMethod.put("base_token_counter",token_counter+1);
				refinedMethods.add(jMethod);
			}
			jsonObject.remove(items);
			jsonObject.put("methodList",refinedMethods);
			jsonObject.put("offsetClass", offset);
			Gson gson = new Gson();
			String json_result = gson.toJson(jsonObject);
			FileWriter file_res = new FileWriter(outputRefinedFile);
			//System.out.println(json_result);
			file_res.write(json_result);
			file_res.close();

		} catch(Exception e){}
	}
}
