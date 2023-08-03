import pandas as pd
import numpy as np
import networkx as nx
import datetime

t1 = datetime.datetime.now()
all_df = pd.read_csv("data/clickstream-enwiki-2023-06.tsv", sep="\t", nrows=100000, names=["prev", "curr", "type", "occurrences"])

# get proportions of internal vs external referrer per page 
all_df["int_or_ext_referrer"] = np.where(all_df["type"] != "link", "internal_referrer_visits", "external_referrer_visits")
referrer_proportions = all_df.groupby(by=["curr", "int_or_ext_referrer"])["occurrences"].sum().reset_index()
referrer_proportions = referrer_proportions.pivot(index="curr", columns="int_or_ext_referrer", values="occurrences").fillna(1).reset_index()
referrer_proportions["int_visit_pct"] = referrer_proportions["internal_referrer_visits"] / (referrer_proportions["external_referrer_visits"] + referrer_proportions["internal_referrer_visits"])
df = all_df.loc[~all_df["prev"].str.startswith("other-")]

G = nx.from_pandas_edgelist(df=df, source="prev", target="curr", edge_attr="occurrences", create_using=nx.MultiDiGraph)


# centrality --------- DONE
# eigenvector not implemented for multigraphs
t3 = datetime.datetime.now()
print("made graph in time", t3 - t1)
in_centrality = nx.in_degree_centrality(G)
print(datetime.datetime.now())
out_centrality = nx.out_degree_centrality(G)
print(datetime.datetime.now())
closeness_centrality = nx.closeness_centrality(G)
print(datetime.datetime.now())
# betweenness_centrality = nx.betweenness_centrality(G)
print(datetime.datetime.now())
centrality_data = pd.DataFrame({"node": list(in_centrality.keys()), 
                                "in_centrality": list(in_centrality.values()),
                                "out_centrality": list(out_centrality.values()),
                                "closeness_centrality": list(closeness_centrality.values()),
                                # "betweenness_centrality": list(betweenness_centrality.values())
                                })

# dominating set and connectivity ------------- DONE
# # node is in dominating set
# takes a min or so to run for 100000 rows
t4 = datetime.datetime.now()
print("calculated centrality in time", t4-t3)
node_names = []
node_in_dom_set = []
node_connected_comp_size = []
for i, sub in enumerate(nx.weakly_connected_components(G)):
    subG = nx.subgraph(G, sub)
    sub_size = len(sub)
    dom_set = nx.dominating_set(subG)

    for node in subG.nodes():
        node_names.append(node)
        if node in list(dom_set):
            node_in_dom_set.append(1)
        else:
            node_in_dom_set.append(0)
        node_connected_comp_size.append(sub_size)

dom_set_data = pd.DataFrame({"in_dom_set": node_in_dom_set, "connected_comp_size": node_connected_comp_size, "node": node_names})
    

# #  communities ------------- DONE
t5 = datetime.datetime.now() 
print("dom set and conns in time", t5-t4)
node_community_sizes = []
node_names = []
comms = nx.community.greedy_modularity_communities(G)
for comm in comms:
    community_size = len(list(comm))
    for node in comm:
        node_community_sizes.append(community_size)
        node_names.append(node)
comm_sizes_data = pd.DataFrame({"node": node_names, "node_community_size": node_community_sizes})


# cliques ------------
# cliques are not implemented for directed type, can make undirected graph for this
t6 = datetime.datetime.now()
print("comms in time", t6-t5)
undirG = nx.to_undirected(G)
node_clique_sizes = nx.node_clique_number(undirG)
clique_data = pd.DataFrame({"node": list(node_clique_sizes.keys()), "clique_size": list(node_clique_sizes.values())})

# # bridges ------------
# # also not implemented for directed
# print(nx.has_bridges(undirG))
# bridges = nx.bridges(undirG)
# for bridge in bridges:
#     if len(bridge) > 2:
#         print(True)
#         break
# # there are no bridges with length >2 => the only bridges are those between the 2 nodes of a 2 node subgraph


data = centrality_data.merge(dom_set_data, on="node").merge(comm_sizes_data, on="node").merge(clique_data, on="node")
data.to_csv("data/graph_feature_data.csv")

t2 = datetime.datetime.now()
print("cliques in time", t2-t6)
print("total time:", t2 - t1)
print("rows:", len(all_df))