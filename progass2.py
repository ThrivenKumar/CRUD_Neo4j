from py2neo import Graph, Node,Relationship
from flask import Flask, jsonify, request
app = Flask(__name__)


url = "bolt://localhost:7687"
usr = "neo4j"
password = "Admin1234"

graph = Graph(url, auth = (usr,password))


@app.route("/imdb",methods=["GET"])
def getAllMovie():
    try:
        movie_data=[]
        movies_cursor=graph.run("Match(n:Movie) return n")
        for i in movies_cursor:
            movie_data.append(i)
        return jsonify(movie_data)
    except Exception as e:
        print("Exception is ", e)
        return jsonify({"status":500, "message": "Internal server error"})

@app.route("/imdb/fname",methods=["GET"])
def getOneMovie():
    try:
        movie_data=[]
        title = request.args.get("title")
        query = 'Match (n:Movie{title :"' + title + '"})<-[ACTED_IN]-(p:Person) return n,p'
        query2 = 'Match (g:Genre)<-[IN]-(n:Movie{title :"' + title + '"}) return n,g'
        movie_cursor = graph.run(query)
        for i in movie_cursor:
            movie_data.append(i)
        movie_cursor = graph.run(query2)
        for i in movie_cursor:
            movie_data.append(i)
        return jsonify({"status":200, "message": movie_data})
    except Exception as e:
        print("Exception is ", e)
        return jsonify({"status":500, "message": "Internal server error"})


@app.route("/imdb/fname",methods=["PATCH"])
def updateOneMovies():
    try:
        title = request.args.get("title")
        update_data = request.get_json()
        query="Match(m:Movie {title :'" + title +"'}) SET "
        temp=""
        if update_data.get("title")!=None:
            temp+="title:'" + update_data.get("title") +"'"
            if update_data.get("description")!=None:
                temp+=", description:'" + update_data.get("description") +"'"
            if update_data.get("rating")!=None:
                temp+=", rating:'" + str(update_data.get("rating")) +"'"
        elif update_data.get("description")!=None:
            temp+="description:'" + update_data.get("description") + "'"
            if update_data.get("rating")!=None:
                temp+=", rating:'" + str(update_data.get("rating")) + "'"
        elif update_data.get("rating")!=None:
            temp+="rating:'" + str(update_data.get("rating")) + "'"
        query += "m+={" + temp + "} return m"
        updated_movie = graph.run(query)
        print(updated_movie)
        return jsonify({"status":200, "message": "Movie Updated"})
    except Exception as e:
        print("Exception is ", e)
        return jsonify({"status":500, "message": "Internal server error"})


@app.route("/imdb",methods=["POST"])
def insertNewMovie():
    try:
        movie_data=request.get_json()
        actors = movie_data["actors"].split(",")
        directors = movie_data["director"].split(",")
        genres = movie_data["genre"].split(",")
        movie_data.pop("actors")
        movie_data.pop("director")
        movie_data.pop("genre")
        movie = '(`'+ movie_data["title"] +'`:Movie {' + 'ids:"' + str(movie_data["ids"]) + '",title:"' + movie_data["title"]+ '",rating:"' + str(movie_data["rating"]) + '",revenue:"' + str(movie_data["revenue"]) + '",runtime:"' + str(movie_data["runtime"]) + '",votes:"' + str(movie_data["votes"]) + '",year:"' + str(movie_data["year"]) + '"})'
        temp=''
        for i in actors:
            temp += ',(`' + i.strip() +'`:Person {name:"' + i.strip() +'"})-[:ACTED_IN]->(`'+ movie_data["title"] +'`)'
        
        for i in directors:
            temp += ',(`' + i.strip() +'`:Person {name:"' + i.strip() +'"})-[:DIRECTED]->(`'+ movie_data["title"] +'`)'

        for i in genres:
            temp += ',(`' + i.strip() +'`:Genre {type:"' + i.strip() +'"})<-[:IN]-(`'+ movie_data["title"] +'`)'
        
        query= 'CREATE p = ' + movie + temp + ' RETURN length(p)'
        graph.run(query)
        return jsonify({"status": 200, "message":"Inserted one document"})
    except Exception as e:
        print("Exception is ", e)
        return jsonify({"status":500, "message": "Internal server error"})


@app.route("/imdb/fname", methods=["DELETE"])
def deleteOneMovie():
    try:
        title = request.args.get("title")
        query = 'Match (n:Movie{title :"' + title + '"}) Detach Delete n'
        graph.run(query)
        return jsonify({"status": 200, "message":"Deleted movie successfully" })
    except Exception as e:
        print("Exception is ", e)
        return jsonify({"status":500, "message": "Internal server error"})


if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
