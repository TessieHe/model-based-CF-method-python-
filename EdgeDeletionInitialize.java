import java.util.*;



public class EdgeDeletionInitialize {
	private HashSet<Integer> cover;
	private long startTime = System.nanoTime() ;
	private double maxTime;
	long duration;
//	if you want to include the time for initialization, use this constructor
	EdgeDeletionInitialize(double time){
		this.maxTime = time;
	}
	EdgeDeletionInitialize(){
	}
	public HashSet<Integer> initialize(Graph graph) {
		
		//because initialization needs to delete edges in each step, we need a copy of original graph
		Graph graphCopy = new Graph(graph);
		this.cover = new HashSet<Integer>();

//		while(graphCopy.getCurEdgenum() != 0 && (double)(System.nanoTime() - startTime)/1000000000.0 < maxTime){
		while(graphCopy.getCurEdgenum() != 0){
			int node1 = pickNode(graphCopy);

			
			Iterator<Integer> it = graphCopy.edgemap.get(node1).keySet().iterator();
			
//			if this random pickup node has no incident node (due to deletion), remove this node in the map and then pick up another node
			while(!it.hasNext()){
				graphCopy.edgemap.remove(node1);
				node1 = pickNode(graphCopy);
//				if node is the only one remaining node and it is empty ( no edge remaining)
				if(graphCopy.getCurEdgenum() == 0)
					return cover;
				it = graphCopy.edgemap.get(node1).keySet().iterator();
			}

//			select an edge, one of which end point is node1
			int node2 = it.next(); 
			cover.add(node1);
			cover.add(node2);
//remove any nodes which are incident to node1 and node2; remove corresponding key first and then traverse in the edgemap
			graphCopy.edgemap.remove(node1);
			graphCopy.edgemap.remove(node2);
			graphCopy.delIncidentEdge(node1);
			graphCopy.delIncidentEdge(node2);

		}
		
		return cover;
	}
	public static int pickNode(Graph g){
		Iterator<Integer> it = g.edgemap.keySet().iterator();
		
//		pseudo random pickup since a set data structure has been used
		if(it.hasNext()){ 
			return it.next();
		}
		return 0;


	}
}
