import java.util.*;
public class Graph {
	private int vertexnum;
	private int edgenum;
	HashMap<Integer,HashMap<Integer,Integer>> edgemap;
	private int[] age;
	private int[] config;
	
	Graph(int vtn,int egn){
		this.vertexnum = vtn;
		this.edgenum = egn;
		this.edgemap = new HashMap<>();
		age = new int[vtn];
		config = new int[vtn];
		for(int i=0;i<vertexnum;i++){
			age[i] = 0;
			config[i] = 1;
			edgemap.put(i+1, new HashMap<Integer,Integer>());
		}
	}
//	constructor for copy a given graph
	Graph(Graph g){
		this.vertexnum = g.vertexnum;
		this.edgenum = g.edgenum;
		this.edgemap = new HashMap<Integer,HashMap<Integer,Integer>>();
		this.age = Arrays.copyOf(g.age, g.age.length);
		this.config =  Arrays.copyOf(g.config, g.config.length);
		for(int key:g.edgemap.keySet()){
			this.edgemap.put(key,new HashMap<Integer,Integer>(g.edgemap.get(key)));
		}
	}
	public int getVtn(){
		return this.vertexnum;
	}
	public int getEgn(){
		return this.edgenum;
	}
	public void addedge(String[] neighbor, int row){
		int len =  neighbor.length;
		
		for (int i=0;i<len;i++){
			if(neighbor[i].length() != 0)
				edgemap.get(row).put(Integer.parseInt(neighbor[i]),1);
		}
	}
	public int getAge(int node){
		return this.age[node - 1];
	}
	public int getCurEdgenum() {
		return this.edgemap.size();
	}
	public int getConf(int node){
		return this.config[node - 1];
	}
	public void setAge(int node, int newage){
		this.age[node - 1] = newage;
	}
	public void setConf(int node, int conf){
		this.config[node - 1] = conf;
	}
//	used for edgedeletion
	public void delIncidentEdge(int node) {
		for(Integer key : edgemap.keySet()){
			Set<Integer> neighbor =  edgemap.get(key).keySet();
			if(neighbor.contains(node)){
				neighbor.remove(node);
			}
		}
	}
}
