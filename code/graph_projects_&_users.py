import cairo
import pymongo
import igraph
from pymongo import MongoClient
from igraph import *

#connect to local DB
client = MongoClient()
db = client.local

#initialize graphs
g1 = Graph()
g2 = Graph()
g3 = Graph(directed=True)
g_repos_users = {}
g_repos_language = {}
g_repos_forks = {}
g_repos_watchers = {}
g_repos_size = {}
g_repos_description = {}
g_users_repos = {}
g_users_followers = {}
g_users_following = {}
g_users_location = {}
g_followers = {}

#params
look_at_contributors = True
save = True
draw_projects = True
draw_users = True
draw_followers = False
limit_contributors_by = 1
limit_non_contributors_by = 1
limit_followers_by = 1

print("start...")

print("1...reading repo data...")
repos = db.repos.find({"fork":False}, projection={'name': True,'full_name': True,'language': True,'forks_count': True,'watchers': True,'description':True})
for repo in repos:
    g_repos_users[repo['full_name']] = []
    g_repos_language[repo['full_name']] = repo['language']
    g_repos_forks[repo['full_name']] = repo['forks_count']
    g_repos_watchers[repo['full_name']] = repo['watchers']
    g_repos_description[repo['full_name']] = repo['description']
    g_repos_size[repo['full_name']] = 0
    g1.add_vertices(repo['full_name'])

if(look_at_contributors):
    print("2A...reading commit data...")
    count = 0
    total = round(db.commits.find(projection={'url': True, 'committer': True}).count()*limit_contributors_by)
    commits = db.commits.find(projection={'url': True, 'committer': True});
    
    for commit in commits:
        if(total > count):
            url = commit['url']
            url_split = url.split('/')
            repo = url_split[4]+"/"+url_split[5]

            if 'committer' in commit and commit['committer'] is not None and repo in g_repos_users.keys():
                if 'login' in commit['committer'] and commit['committer']['login'] is not None:
                    user = commit['committer']['login']
                    if user not in g_users_repos:
                        user_record = db.users.find({ "login": user },projection={'followers': True, 'following': True, 'location': True})
                        if(user_record.count() and 'location' in user_record[0]):
                            g2.add_vertices(user)
                            g_users_repos[user] = []
                            g_users_followers[user] = user_record[0]['followers']
                            g_users_following[user] = user_record[0]['following']
                            g_users_location[user] = user_record[0]['location']
                    if repo in g_repos_users and user not in g_repos_users[repo]:
                        user_record = db.users.find({ "login": user },projection={'followers': True, 'following': True, 'location': True})
                        if(user_record.count() and 'location' in user_record[0]):
                            g_repos_users[repo].append(user)
            count+=1
        else:
            break

    for repo,users in g_repos_users.items():
        g_repos_size[repo] = len(users)
        
else:
    print("2B...reading non-contributor data (commit_comments)...")
    count = 0
    total = round(db.commit_comments.find(projection={'url': True, 'user': True}).count()*limit_non_contributors_by)
    commit_comments = db.commit_comments.find(projection={'url': True, 'user': True})

    for commit_comment in commit_comments:
        if(total > count):
            url = commit_comment['url']
            url_split = url.split('/')
            repo = url_split[4]+"/"+url_split[5]

            if 'user' in commit_comment and commit_comment['user'] is not None and repo in g_repos_users.keys():
                if 'login' in commit_comment['user'] and commit_comment['user']['login'] is not None:
                    user = commit_comment['user']['login']
                    if user not in g_users_repos:
                        user_record = db.users.find({ "login": user },projection={'followers': True, 'following': True, 'location': True})
                        if(user_record.count() and 'location' in user_record[0]):
                            g2.add_vertices(user)
                            g_users_repos[user] = []
                            g_users_followers[user] = user_record[0]['followers']
                            g_users_following[user] = user_record[0]['following']
                            g_users_location[user] = user_record[0]['location']
                    if repo in g_repos_users and user not in g_repos_users[repo]:
                        user_record = db.users.find({ "login": user },projection={'followers': True, 'following': True, 'location': True})
                        if(user_record.count() and 'location' in user_record[0]):
                            g_repos_users[repo].append(user)
            count+=1
        else:
            break
        
    for repo,users in g_repos_users.items():
        g_repos_size[repo] = len(users)
        
print("3...reading follower data...")
followers = db.followers.find()
count = 0
total = round(db.followers.find().count()*limit_followers_by)

for follower in followers:
    if(total > count):
        if follower['login'] not in g_followers:
            g_followers[follower['login']] = 0
            g3.add_vertices(follower['login'])
            print(follower['login'])
        if follower['follows'] not in g_followers:
            g_followers[follower['follows']] = 0
            g3.add_vertices(follower['follows'])
            print(follower['follows'])
        count+=1
    else:
        break
        
print("4...constructing followers graph")
followers = db.followers.find()
count = 0
follower_edges = {}
for follower in followers:
    if(total > count):
        if follower['login'] in g_followers and follower['follows'] in g_followers:
             key = (follower['login'],follower['follows'])
             if key not in follower_edges:
                 print(key)
                 follower_edges[key] = 1
        count+=1
    else:
        break

print("5...constructing project graph and start constructing user graph")
project_edges = {}
for repo_A, users_A in g_repos_users.items():
    for repo_B, users_B in g_repos_users.items():
        shared = set(users_A).intersection(users_B)
        if(shared):
            key = (repo_A,repo_B)
            inverse_key = (repo_B,repo_A)
            if(key not in project_edges and inverse_key not in project_edges and repo_A != repo_B):
                project_edges[key] = len(shared)
    for user in users_A:
        g_users_repos[user].append(repo_A)

print("6...constructing user graph")
user_edges = {}
count = 0
for user_A, repos_A in g_users_repos.items():
    count+=1
    print(str(count)+"/"+str(len(g_users_repos)))
    for user_B, repos_B in g_users_repos.items():
        shared = set(repos_A).intersection(repos_B)
        if(shared):
            key = (user_A,user_B)
            inverse_key = (user_B,user_A)
            if(key not in user_edges and inverse_key not in user_edges and user_A != user_B):           
                 user_edges[key] = len(shared)                 

print("7...constructing project graph: setting edges weight and vertices names")
g1.vs["name"] = list(g_repos_users.keys())
g1.vs["language"] = list(g_repos_language.values())
g1.vs["description"] = list(g_repos_description.values())
g1.vs["watchers"] = list(g_repos_watchers.values())
g1.vs["forks"] = list(g_repos_forks.values())
g1.vs["size"] = list(g_repos_size.values())
g1.add_edges(list(project_edges.keys()))
g1.es["weight"] = list(project_edges.values())

print("8...constructing user graph: setting edges weight and vertices names")
g2.vs["name"] = list(g_users_repos.keys())
g2.vs["followers"] = list(g_users_followers.values())
g2.vs["following"] = list(g_users_following.values())
g2.vs["location"] = list(g_users_location.values())
g2.add_edges(list(user_edges.keys()))
g2.es["weight"] = list(user_edges.values())

print("9...construct followers graph: setting vertice names")
g3.vs["name"] = list(g_followers.keys())
g3.add_edges(list(follower_edges.keys()))
g3.es["weight"] = list(follower_edges.values())

if(save):
    print("10...Save")
    g1.write_pickle("archive_pickle_projects")
    if(look_at_contributors):
        g2.write_pickle("archive_pickle_contributing_users")
    else:
        g2.write_pickle("archive_pickle_non_contributing_users")
    g3.write_pickle("archive_pickle_followers")

if(draw_projects):
    print("11.1...Draw Projects Graph")
    visual_style = {}
    visual_style["vertex_size"] = 2
    visual_style["vertex_label"] = g1.vs["size"]
    visual_style["vertex_color"] = "red"
    visual_style["edge_label"] = g1.es["weight"]
    visual_style["edge_width"] = 1 
    visual_style["layout"] = g1.layout("kk")
    visual_style["bbox"] = (1000, 1000)
    visual_style["margin"] = 100

    igraph.plot( g1, "visual_for_projects.pdf", **visual_style )

if(draw_users):
    print("11.2...Draw Users Graph")
    visual_style = {}
    visual_style["vertex_size"] = 2
    visual_style["vertex_label"] = g2.vs["name"]
    visual_style["vertex_color"] = "red"
    visual_style["edge_label"] = g2.es["weight"]
    visual_style["edge_width"] = 1 
    visual_style["layout"] = g2.layout("kk")
    visual_style["bbox"] = (1000, 1000)
    visual_style["margin"] = 100

    igraph.plot( g2, "visual_for_users.pdf", **visual_style )

if(draw_followers):
    print("11.3...Draw Followers Graph")
    visual_style = {}
    visual_style["vertex_size"] = 2
    visual_style["vertex_label"] = g3.vs["name"]
    visual_style["vertex_color"] = "red"
    visual_style["edge_label"] = g3.es["weight"]
    visual_style["edge_width"] = 1
    visual_style["layout"] = g3.layout("random")
    visual_style["bbox"] = (1000, 1000)
    visual_style["margin"] = 100
    
    igraph.plot( g3, "visual_for_followers.pdf", **visual_style )

print("done!")
