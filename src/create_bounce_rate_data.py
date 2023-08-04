import pandas as pd
import numpy as np
import json
from collections import defaultdict
import networkx as nx

def default_value():
    return []

all_df = pd.read_csv("data/clickstream-enwiki-2023-06.tsv", sep="\t", nrows=10000, names=["prev", "curr", "type", "occurrences"])

# get proportions of internal vs external referrer per page 
all_df["int_or_ext_referrer"] = np.where(all_df["type"] != "link", "internal_referrer_visits", "external_referrer_visits")
print(all_df.head())
ext_referrer_counts = all_df.groupby(by=["curr", "int_or_ext_referrer"])["occurrences"].sum().reset_index()
ext_referrer_counts = ext_referrer_counts.pivot(index="curr", columns="int_or_ext_referrer", values="occurrences").fillna(1).reset_index()
node_attributes = {node: value for node, value in zip(ext_referrer_counts["curr"].to_list(), ext_referrer_counts["external_referrer_visits"].to_list())}
df = all_df.loc[~all_df["prev"].str.startswith("other-")]
# 33 805 178 rows total


G = nx.from_pandas_edgelist(df=df, source="prev", target="curr", edge_attr="occurrences", create_using=nx.MultiDiGraph)
# print(nx.get_node_attributes(G, "aiuf"))
nx.set_node_attributes(G, values=node_attributes, name="ext_referrer_count")
print(G["List_of_number-one_hits_of_1973_(Mexico)"])

i = 0
# print(len(G.nodes))
# bounce_rates = []
# node_names = []
# for node in G.nodes():
#     in_edges = G.in_edges(node)
#     out_edges = G.out_edges(node)
#     n_in_edges = len(in_edges)
#     n_out_edges = len(out_edges)
#     # in_edges = [edge ÷]
#     if (len(in_edges) >= 1) & (len(out_edges) >= 1):
#         external_inbound = node_attributes[node]
#         internal_inbound = sum([G.get_edge_data(edge[0], edge[1])[0]["occurrences"] for edge in in_edges])
#         inbound = sum([external_inbound, internal_inbound])
#         outbound = sum([G.get_edge_data(edge[0], edge[1])[0]["occurrences"] for edge in out_edges])
#         bounce_rate = abs(inbound - outbound) / inbound  
#         bounce_rates.append(round(bounce_rate, 6))
#         node_names.append(node)
#     if (len(out_edges) == 0) & (len(in_edges) >= 1):
#         bounce_rates.append(1.0)
#         node_names.append(node)
#     if (len(out_edges) > 0) & (len(in_edges) == 0):
#         bounce_rates.append(0.0)
#         node_names.append(node) 
#     i += 1
#     if i % 10000 == 0:
#         print(f"{i} out of {len(G.nodes())} nodes")

# bounce_rate_df = pd.DataFrame({"node": node_names, "bounce_rate": bounce_rates})
# bounce_rate_df.to_csv("data/bounce_rates.csv")

# print(bounce_rate_df.describe())


# centrality = nx.eigenvector_centrality(G)
# print({k: v for k, v in sorted(centrality.items(), key=lambda item: item[1])})

# put this in a jupyter notebook
for idx, value in enumerate(nx.degree_histogram(G)):
    print(idx, value)

# ext_referrer_counts = ext_referrer_counts.pivot(index="curr", columns="int_or_ext_referrer", values="occurrences").fillna(1).reset_index()
ext_referrer_counts["int_visit_pct"] = ext_referrer_counts["internal_referrer_visits"] / (ext_referrer_counts["internal_referrer_visits"] + ext_referrer_counts["external_referrer_visits"])
### this code is really good at finding end points 
# number of distinct sub graphs 
all_ratios = {}
for i, comp in enumerate(nx.weakly_connected_components(G)):
    if (len(comp) > 100):# & (len(comp) < 50):
        print(i, len(comp))
        subG = nx.subgraph(G, comp)
        nds = list(subG.nodes())
        props = ext_referrer_counts.loc[ext_referrer_counts["curr"].isin(nds)].sort_values(by="int_visit_pct", ascending=True)
        likely_starters = props.head(30)
        print(likely_starters[["curr", "int_visit_pct"]])
        likely_starters[["curr", "int_visit_pct"]].to_csv("data/likely_starting_points.csv", index=False)
        
        sub_centrality = nx.closeness_centrality(subG)
        most_central = list({k: v for k, v in sorted(sub_centrality.items(), key=lambda item: item[1])})[-1]

        out_centrality = nx.out_degree_centrality(subG)
        in_centrality = nx.in_degree_centrality(subG)
        # print(out_centrality)
        ratios = ({node: in_value/max(out_centrality[node], 0.0001) for node, in_value in in_centrality.items()})
        print(most_central, in_centrality[most_central])
        sorted_ratios = {k: v for k, v in sorted(sub_centrality.items(), key=lambda item: item[1])}
        print(sorted_ratios)
# there are over 800 distinct subgraphs, each of these represent pages which connect to each other but not to any other groups

print(in_centrality["Eponym"])
print(out_centrality["Eponym"])

