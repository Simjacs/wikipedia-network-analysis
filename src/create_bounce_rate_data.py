import pandas as pd
import numpy as np
import json
from collections import defaultdict
import networkx as nx

def default_value():
    return []

all_df = pd.read_csv("data/clickstream-enwiki-2023-06.tsv", sep="\t", nrows=1000000, names=["prev", "curr", "type", "occurrences"])

# get proportions of internal vs external referrer per page 
all_df["int_or_ext_referrer"] = np.where(all_df["type"] != "link", "internal_referrer_visits", "external_referrer_visits")
referrer_proportions = all_df.groupby(by=["curr", "int_or_ext_referrer"])["occurrences"].sum().reset_index()
referrer_proportions = referrer_proportions.pivot(index="curr", columns="int_or_ext_referrer", values="occurrences").fillna(1).reset_index()
referrer_proportions["int_visit_pct"] = referrer_proportions["internal_referrer_visits"] / (referrer_proportions["external_referrer_visits"] + referrer_proportions["internal_referrer_visits"])
df = all_df.loc[~all_df["prev"].str.startswith("other-")]
# 33 805 178 rows total


G = nx.from_pandas_edgelist(df=df, source="prev", target="curr", edge_attr="occurrences", create_using=nx.MultiDiGraph)
i = 0
print(len(G.nodes))
bounce_rates = []
node_names = []
print(G["List_of_number-one_hits_of_1973_(Mexico)"])
for node in G.nodes():
    in_edges = G.in_edges(node)
    out_edges = G.out_edges(node)
    n_in_edges = len(in_edges)
    n_out_edges = len(out_edges)
    # in_edges = [edge ÷]
    if (len(in_edges) >= 1) & (len(out_edges) >= 1):
        inbound = sum([G.get_edge_data(edge[0], edge[1])[0]["occurrences"] for edge in in_edges])
        outbound = sum([G.get_edge_data(edge[0], edge[1])[0]["occurrences"] for edge in out_edges])
        bounce_rate = abs(inbound - outbound) / inbound  # possible to have outbound > inbound if most vists come from other sites, want to see these as large values as they are v interesting
        bounce_rates.append(round(bounce_rate, 6))
        node_names.append(node)
    if (len(out_edges) == 0) & (len(in_edges) >= 1):
        bounce_rates.append(1.0)
        node_names.append(node)
    if (len(out_edges) > 0) & (len(in_edges) == 0):
        bounce_rates.append(0.0)
        node_names.append(node) 
    i += 1
    if i % 1000 == 0:
        print(f"{i} out of {len(G.nodes())} nodes")

bounce_rate_df = pd.DataFrame({"name": node_names, "bounce_rate": bounce_rates})
bounce_rate_df.to_csv("data/bounce_rates.csv")

print(bounce_rate_df.describe())


# centrality = nx.eigenvector_centrality(G)
# print({k: v for k, v in sorted(centrality.items(), key=lambda item: item[1])})

# # put this in a jupyter notebook
# for idx, value in enumerate(nx.degree_histogram(G)):
#     print(idx, value)

# ### this code is really good at finding end points 
# number of distinct sub graphs 
# for i, comp in enumerate(nx.weakly_connected_components(G)):
#     if (len(comp) > 30) & (len(comp) < 50):
#         print(i, len(comp))
#         subG = nx.subgraph(G, comp)
#         nds = list(subG.nodes())
#         props = referrer_proportions.loc[referrer_proportions["curr"].isin(nds)].sort_values(by="int_visit_pct", ascending=True)
#         likely_starters = props.head()
#         print(likely_starters[["curr", "int_visit_pct"]])
        
#         sub_centrality = nx.closeness_centrality(subG)
#         most_central = list({k: v for k, v in sorted(sub_centrality.items(), key=lambda item: item[1])})[-1]

#         out_centrality = nx.out_degree_centrality(subG)
#         in_centrality = nx.in_degree_centrality(subG)
#         # print(out_centrality)
#         ratios = ({node: out_value/max(in_centrality[node], 0.0001) for node, out_value in out_centrality.items()})
#         print(most_central, in_centrality[most_central])
#         print(ratios)

# there are over 800 distinct subgraphs, each of these represent pages which connect to each other but not to any other groups


