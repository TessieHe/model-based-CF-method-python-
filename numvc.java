import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.DecimalFormat;
import java.util.Map.Entry;
import java.util.*;


public class numvc {
	Graph graph;
	private HashSet<Integer> cover; //vertex cover 
	private HashSet<Integer> optCover; 
	private HashMap<Integer, HashSet<Integer>> uncoverEdges;
	private HashSet<Integer> uncoverNodes;
	private long startTime;
	private long duration = 0;
	private Random generator;
	private PrintWriter outSol;
	private PrintWriter outTrace;;
	private double maxTime; //seconds
	public static void main(String args[]) throws IOException{
//		filename.graph cutoff  [BnB|Approx|LS1|LS2]  −seed 
		numvc sa  = new numvc();
		if(args.length< 4 || (!args[2].equals("LS2") && !args[2].equals("LS2_greedy")))
		{
			System.err.println("Unexpected command line arguments\n");
			System.out.println("java *.graph LS2/LS2_greedy cutoff seed");
			System.exit(1);
		}
		
		sa.generator = new Random(Integer.parseInt(args[3]));
		sa.readGraph(args[0]); 
//		sa.readGraph("./DATA/" + args[0]);
		sa.maxTime = Double.parseDouble(args[1]);
		File file = new File("./output" );
		
		//if output directory didn't exist, create directory first
		if (!file.exists()){
			file.mkdirs();
		}
		String[] temp = args[0].split("/");
		String filename = temp[temp.length-1];

		sa.outSol = new PrintWriter(new File("./output/" + filename.split(".graph")[0] + "_" + args[2] + '_' + args[1] + "_" + args[3]+".sol"));
		sa.outTrace = new PrintWriter(new File("./output/" + filename.split(".graph")[0] + "_" +  args[2] + '_' + args[1] + "_" + args[3]+".trace"));
		if(args[2] == "LS2_greedy"){
//			greedy "edge deleting" initialize
			EdgeDeletionInitialize ed = new EdgeDeletionInitialize(sa.maxTime);
			sa.cover = ed.initialize(new Graph(sa.graph)); 
			sa.duration = ed.duration;
		}
		else
//			basic initialize as the entire node
			sa.cover = new HashSet<Integer>(sa.graph.edgemap.keySet());
		sa.uncoverNodes = new HashSet<Integer>(sa.graph.edgemap.keySet());
		sa.uncoverNodes.removeAll(sa.cover);
		sa.uncoverEdges = new HashMap<Integer,HashSet<Integer>>();

		sa.localSearch();

		sa.outSol.println(sa.optCover.size());

		sa.outSol.println(sa.optCover.toString().replaceAll("[\\[\\]]",""));
		sa.outSol.close();
		sa.outTrace.close();
	}
	public void localSearch() {
		Integer lastInsert = 0;
		DecimalFormat df = new DecimalFormat("#.##");  
//		this duration includes the time for greedy initialize
		if(duration == 0) 
			startTime = System.nanoTime();
		else
			startTime = System.nanoTime() - duration;
		
		duration =  System.nanoTime() - startTime;
		int iter = 0;
		double decreaseRate = 0.3;
		double weightThreshold = ((double)graph.getVtn())/2.0;//the threshold to decide whether to decrease weight
		optCover = new HashSet<Integer>();
		while((double)duration / 1000000000.0 < maxTime){
			iter++;
			if(checkCover()) {
				outTrace.println(Double.valueOf(df.format((double)duration/1000000000.0)) + ", " + cover.size());
				optCover = new HashSet<Integer>(cover);
				
//				choose an exit node form current cover which has the highest dscore
				int node = getNodeFromHighestDscore();
				cover.remove(node);
				uncoverNodes.add(node);
				graph.setAge(node, iter);
				for(Integer neighbor: graph.edgemap.get(node).keySet()){
//					if current cover doesn't have neighbor which means this edge won't be covered
					if(!cover.contains(neighbor)){
						uncoverEdges.put(node,new HashSet<Integer>(Arrays.asList(neighbor)));
						uncoverEdges.put(neighbor, new HashSet<Integer>(Arrays.asList(node)));
					}
				}

				duration = System.nanoTime() - startTime;
				if((double)duration/1000000000.0 >= maxTime)
					break;
				continue;
			}

//			keep track of last inserted node in order to avoid delete immediately
			if(lastInsert != 0)
				cover.remove(lastInsert);
			int toExit = chooseExitNode();
			
			cover.remove(toExit);	
//			after select exit node ,recover lastInsert node
			if(lastInsert != 0)
				cover.add(lastInsert); 
			graph.setConf(toExit, 0);
			graph.setAge(toExit, iter);
//			when remove a node from current cover, update uncoverEdge HashMap
			for(Integer neighbor: graph.edgemap.get(toExit).keySet()){
				if(!cover.contains(neighbor)){
//	after checkCover and remove a node from current cover, at this time "cover" set may not cover all edges, need to check before update
					if(uncoverEdges.containsKey(toExit))
						uncoverEdges.get(toExit).add(neighbor);
					else
						uncoverEdges.put(toExit,new HashSet<Integer>(Arrays.asList(neighbor)));
	
					if(uncoverEdges.containsKey(neighbor))
						uncoverEdges.get(neighbor).add(toExit);
					else
						uncoverEdges.put(neighbor, new HashSet<Integer>(Arrays.asList(toExit)));
				}			
			}	
			uncoverNodes.add(toExit);
			updateNeighborConf(toExit);
			int toEnter = chooseToEnter();

			cover.add(toEnter);

			lastInsert = toEnter;
			graph.setAge(toEnter,iter);	
		    uncoverNodes.remove(toEnter);
//			when add a node to cover, update uncoverEdges hashmap
			if(uncoverEdges.containsKey(toEnter)){
				for(Integer neighbor: uncoverEdges.get(toEnter)){
					if(uncoverEdges.containsKey(neighbor)){
						uncoverEdges.get(neighbor).remove(toEnter);
						if(uncoverEdges.get(neighbor).size() == 0)
							uncoverEdges.remove(neighbor);
					}
				}
				uncoverEdges.remove(toEnter);
			}
			
			
			updateNeighborConf(toEnter);
			IncreaseWeight();
			weightForget(decreaseRate,weightThreshold);
			duration =  System.nanoTime() - startTime;
		}
		
	}
	
	private void weightForget(double decreaseRate,double weightThreshold) {
		double averageWeight = 0;
		int sum = 0;
		for(Entry<Integer, HashMap<Integer,Integer>> entry: graph.edgemap.entrySet()){
			HashMap<Integer,Integer> weight = entry.getValue();
			for(Entry<Integer,Integer> entryweight: weight.entrySet())
				sum += entryweight.getValue();
		}
		
		averageWeight = ((double)sum)/(graph.getEgn()*2);
		if(averageWeight >= weightThreshold){
			for(Entry<Integer, HashMap<Integer,Integer>> entry: graph.edgemap.entrySet()){
				HashMap<Integer,Integer> weight = entry.getValue();
				for(Entry<Integer,Integer> entryweight: weight.entrySet())
					entryweight.setValue((new Double(entryweight.getValue() * decreaseRate)).intValue());	
			}
		}
	}
	private void IncreaseWeight() {
		for(Entry<Integer,HashSet<Integer>> entry: uncoverEdges.entrySet()){
			Integer node1 = entry.getKey();
			for(Integer node2: entry.getValue()){
				graph.edgemap.get(node1).put(node2, graph.edgemap.get(node1).get(node2) + 1);
			}
		}	
	}
	private int chooseToEnter() {
		ArrayList<Integer> uncoverList = new ArrayList<Integer>(uncoverEdges.keySet());
		int node1Index = generator.nextInt(uncoverList.size());
		
		int node1 = uncoverList.get(node1Index);


		ArrayList<Integer> neighborList = new ArrayList<Integer>(uncoverEdges.get(node1));
		
		int node2Index = generator.nextInt(neighborList.size());
		int node2 = neighborList.get(node2Index);
	
//		configuration check scheme
		int node1conf = graph.getConf(node1);
		int node2conf = graph.getConf(node2);
		if(node1conf == 1 && node2conf == 0 )
			return node1;
		if(node2conf == 1 && node1conf == 0)
			return node2;
		if(node2conf == 1 && node1conf == 1){
			int dscoreNode1 = cost(node1);
			int dscoreNode2 = cost(node2);
			if(dscoreNode1 > dscoreNode2)
				return node1;
			else if(dscoreNode1 < dscoreNode2)
				return node2;
			else{
//				break ties in favor of old age
				if(graph.getAge(node1) < graph.getAge(node2))
					return node1;
				else
					return node2;
			}
		}
		return 0;
	}
	private void updateNeighborConf(int toExit) {
		for(Integer neighbor: graph.edgemap.get(toExit).keySet()){
			graph.setConf(neighbor,1);
		}
		
	}
	private int chooseExitNode() {
		SortedSet<Entry<Integer, Integer>> sortedset = new TreeSet<Map.Entry<Integer, Integer>>(
	            new Comparator<Map.Entry<Integer, Integer>>() {
	                @Override
	                public int compare(Map.Entry<Integer, Integer> dscore1,
	                        Map.Entry<Integer, Integer> dscore2) {
	                    return dscore2.getValue().compareTo(dscore1.getValue());
	                }
	            });
		SortedMap<Integer, Integer> sortedMap = new TreeMap<Integer, Integer>();
		computeDscore(sortedMap);
		
		if(sortedMap.size() == 0){
			debug("no sortedmap");
			System.exit(0);
		}
		
		sortedset.addAll(sortedMap.entrySet());
		
		
		Integer toExitNode = sortedset.first().getKey();
		Iterator<Entry<Integer, Integer>> it =  sortedset.iterator();
		
		while(it.hasNext()){
			Entry<Integer, Integer> entry = it.next();
			Integer otherNode = entry.getKey();
			if(entry.getValue() == sortedMap.get(toExitNode)){
				if(graph.getAge(otherNode) < graph.getAge(toExitNode)){
					toExitNode = otherNode;
				}
			}	
//			the first key is the largest dscore, it there is no equal relation, that means all others smaller than it
			else
				break;
		}
		return toExitNode;
	}
	
	private int getNodeFromHighestDscore() {
		SortedSet<Entry<Integer, Integer>> sortedset = new TreeSet<Map.Entry<Integer, Integer>>(
	            new Comparator<Map.Entry<Integer, Integer>>() {
	                @Override
	                public int compare(Map.Entry<Integer, Integer> dscore1,
	                        Map.Entry<Integer, Integer> dscore2) {
	                    return dscore1.getValue().compareTo(dscore2.getValue());
	                }
	            });
		SortedMap<Integer, Integer> sortedMap = new TreeMap<Integer, Integer>();
		computeDscore(sortedMap);
		sortedset.addAll(sortedMap.entrySet());
		return sortedset.last().getKey();
	}
	private void computeDscore(SortedMap<Integer, Integer> myMap) {
		for(Integer node:cover){
			myMap.put(node, cost(node));
		}
	}
	private int cost(Integer node) {
		int cost = 0;
//		if this node has been removed from cover, its incident edges will be potential uncovered, check whether they are in cover
		for(Integer neighbor:graph.edgemap.get(node).keySet()){
			if(!cover.contains(neighbor)){
				cost -= graph.edgemap.get(node).get(neighbor);
			}
		}
		return cost;
	}
	private boolean checkCover() {
		HashSet<Integer> uncover = new HashSet<Integer>(graph.edgemap.keySet());
		uncover.removeAll(cover);
		for(Integer node: uncover){
			Set<Integer> neighbor = graph.edgemap.get(node).keySet();
			for(Integer n: neighbor)
				if(!cover.contains(n)){
					return false;
				}			
		}
		return true;
	}
	public void readGraph(String filename) throws IOException{
		BufferedReader bufread = new BufferedReader(new FileReader(filename));
		String line = bufread.readLine();
		String[] neighbor = line.split(" ");
		int vtn = Integer.parseInt(neighbor[0]);
		int edn = Integer.parseInt(neighbor[1]);
		
		this.graph=new Graph(vtn,edn);
		int i=0;
		while(i<vtn){
			line = bufread.readLine();
			i++;
			neighbor = line.split(" ");
			graph.addedge(neighbor,i);
		}
		bufread.close();
	}
//	a helper function to debug via printing
	public static void debug(Object o){
		System.out.println(o);
	}
}
